"""
Data Service for market data collection, news, and sentiment analysis.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import structlog
from dataclasses import dataclass

import ccxt
import yfinance as yf
import requests
from textblob import TextBlob

from src.core.config import settings
from src.core.logging import TradingLogger
from src.strategies.base_strategy import Timeframe


@dataclass
class MarketData:
    """Market data structure."""
    pair: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    metadata: Dict[str, Any] = None


@dataclass
class NewsItem:
    """News item structure."""
    id: str
    title: str
    content: str
    source: str
    published_at: datetime
    sentiment_score: float
    relevance_score: float
    currency_pairs: List[str]
    impact: str  # high, medium, low


@dataclass
class SentimentData:
    """Sentiment analysis data."""
    pair: str
    timestamp: datetime
    news_sentiment: float
    social_sentiment: float
    overall_sentiment: float
    confidence: float
    sources_count: int


class DataService:
    """Comprehensive data service for market data, news, and sentiment."""
    
    def __init__(self):
        self.logger = TradingLogger("data_service")
        self.is_running = False
        
        # Data sources
        self.broker_api = None
        self.news_api = None
        self.sentiment_api = None
        
        # Data storage
        self.market_data_cache: Dict[str, pd.DataFrame] = {}
        self.news_cache: List[NewsItem] = []
        self.sentiment_cache: Dict[str, SentimentData] = {}
        
        # Configuration
        self.update_interval = settings.trading.update_interval
        self.history_days = settings.trading.history_days
        
        # Initialize data sources
        self._initialize_data_sources()
    
    def _initialize_data_sources(self):
        """Initialize data source connections."""
        try:
            # Initialize broker API (OANDA)
            if settings.broker.name.lower() == "oanda":
                self._initialize_oanda_api()
            
            # Initialize news API
            if hasattr(settings, 'external_services') and hasattr(settings.external_services, 'news'):
                if settings.external_services.news.enabled:
                    self._initialize_news_api()
            
            # Initialize Finnhub API
            if hasattr(settings, 'external_services') and hasattr(settings.external_services, 'finnhub'):
                if settings.external_services.finnhub.enabled:
                    self._initialize_finnhub_api()
            
            # Initialize Alpha Vantage API
            if hasattr(settings, 'external_services') and hasattr(settings.external_services, 'alpha_vantage'):
                if settings.external_services.alpha_vantage.enabled:
                    self._initialize_alpha_vantage_api()
            
            # Initialize X (Twitter) API
            if hasattr(settings, 'external_services') and hasattr(settings.external_services, 'x_api'):
                if settings.external_services.x_api.enabled:
                    self._initialize_x_api()
            
            # Initialize NASDAQ API
            if hasattr(settings, 'external_services') and hasattr(settings.external_services, 'nasdaq'):
                if settings.external_services.nasdaq.enabled:
                    self._initialize_nasdaq_api()
            
            self.logger.logger.info("Data sources initialized successfully")
            
        except Exception as e:
            self.logger.logger.error("Error initializing data sources", error=str(e))
    
    def _initialize_oanda_api(self):
        """Initialize OANDA API connection."""
        try:
            import oandapyV20
            from oandapyV20 import API
            
            self.broker_api = API(
                access_token=settings.broker.api_key,
                environment=settings.broker.environment
            )
            
            self.logger.logger.info("OANDA API initialized")
            
        except ImportError:
            self.logger.logger.warning("OANDA library not installed, using fallback")
            self.broker_api = None
    
    def _initialize_news_api(self):
        """Initialize news API connection."""
        if settings.external_services.news.api_key:
            self.news_api = {
                "api_key": settings.external_services.news.api_key,
                "base_url": settings.external_services.news.base_url
            }
            self.logger.logger.info("News API initialized")
    
    def _initialize_sentiment_api(self):
        """Initialize sentiment API connection."""
        if settings.external_services.sentiment.api_key:
            self.sentiment_api = {
                "api_key": settings.external_services.sentiment.api_key,
                "base_url": settings.external_services.sentiment.base_url
            }
            self.logger.logger.info("Sentiment API initialized")
    
    def _initialize_finnhub_api(self):
        """Initialize Finnhub API connection."""
        try:
            self.finnhub_api = {
                "api_key": settings.external_services.finnhub.api_key,
                "secret": settings.external_services.finnhub.secret,
                "base_url": "https://finnhub.io/api/v1"
            }
            self.logger.logger.info("Finnhub API initialized")
        except Exception as e:
            self.logger.logger.error(f"Failed to initialize Finnhub API: {str(e)}")
    
    def _initialize_alpha_vantage_api(self):
        """Initialize Alpha Vantage API connection."""
        try:
            self.alpha_vantage_api = {
                "api_key": settings.external_services.alpha_vantage.api_key,
                "base_url": "https://www.alphavantage.co/query"
            }
            self.logger.logger.info("Alpha Vantage API initialized")
        except Exception as e:
            self.logger.logger.error(f"Failed to initialize Alpha Vantage API: {str(e)}")
    
    def _initialize_x_api(self):
        """Initialize X (Twitter) API connection."""
        try:
            self.x_api = {
                "api_key": settings.external_services.x_api.api_key,
                "api_secret": settings.external_services.x_api.api_secret,
                "bearer_token": settings.external_services.x_api.bearer_token,
                "access_token": settings.external_services.x_api.access_token,
                "access_token_secret": settings.external_services.x_api.access_token_secret,
                "base_url": "https://api.twitter.com/2"
            }
            self.logger.logger.info("X (Twitter) API initialized")
        except Exception as e:
            self.logger.logger.error(f"Failed to initialize X API: {str(e)}")
    
    def _initialize_nasdaq_api(self):
        """Initialize NASDAQ Data API connection."""
        try:
            self.nasdaq_api = {
                "api_key": settings.external_services.nasdaq.api_key,
                "base_url": "https://data.nasdaq.com/api/v3"
            }
            self.logger.logger.info("NASDAQ Data API initialized")
        except Exception as e:
            self.logger.logger.error(f"Failed to initialize NASDAQ API: {str(e)}")
    
    async def start(self):
        """Start the data service."""
        self.is_running = True
        self.logger.logger.info("Data service started")
        
        # Start data collection loop
        asyncio.create_task(self._data_collection_loop())
    
    async def stop(self):
        """Stop the data service."""
        self.is_running = False
        self.logger.logger.info("Data service stopped")
    
    async def _data_collection_loop(self):
        """Main data collection loop."""
        while self.is_running:
            try:
                # Collect market data
                await self._collect_market_data()
                
                # Collect news data
                await self._collect_news_data()
                
                # Collect sentiment data
                await self._collect_sentiment_data()
                
                # Sleep for update interval
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.logger.error("Error in data collection loop", error=str(e))
                await asyncio.sleep(30)  # Wait longer on error
    
    async def _collect_market_data(self):
        """Collect market data for all pairs."""
        for pair in settings.trading.allowed_pairs:
            try:
                for timeframe in settings.trading.default_timeframes:
                    data = await self._fetch_market_data(pair, timeframe)
                    if data is not None:
                        self._update_market_data_cache(pair, timeframe, data)
                        
            except Exception as e:
                self.logger.logger.error(f"Error collecting market data for {pair}", error=str(e))
    
    async def _fetch_market_data(self, pair: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Fetch market data from broker or external source."""
        try:
            if self.broker_api:
                # Use broker API
                return await self._fetch_from_broker(pair, timeframe)
            else:
                # Use fallback source (Yahoo Finance)
                return await self._fetch_from_yahoo(pair, timeframe)
                
        except Exception as e:
            self.logger.logger.error(f"Error fetching market data for {pair}", error=str(e))
            return None
    
    async def _fetch_from_broker(self, pair: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Fetch market data from broker API."""
        try:
            # Convert timeframe to broker format
            broker_timeframe = self._convert_timeframe(timeframe)
            
            # Fetch candles from OANDA
            import oandapyV20.endpoints.instruments as instruments
            
            params = {
                "count": 1000,
                "granularity": broker_timeframe
            }
            
            r = instruments.InstrumentsCandles(instrument=pair, params=params)
            response = self.broker_api.request(r)
            
            # Parse response
            candles = response['candles']
            data = []
            
            for candle in candles:
                data.append({
                    'timestamp': pd.to_datetime(candle['time']),
                    'open': float(candle['mid']['o']),
                    'high': float(candle['mid']['h']),
                    'low': float(candle['mid']['l']),
                    'close': float(candle['mid']['c']),
                    'volume': float(candle['volume']) if 'volume' in candle else 0
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            self.logger.logger.error(f"Error fetching from broker: {str(e)}")
            return None
    
    async def _fetch_from_yahoo(self, pair: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Fetch market data from Yahoo Finance as fallback."""
        try:
            # Convert forex pair to Yahoo Finance format
            yahoo_symbol = self._convert_to_yahoo_symbol(pair)
            
            # Fetch data
            ticker = yf.Ticker(yahoo_symbol)
            data = ticker.history(period=f"{self.history_days}d", interval=self._convert_yahoo_timeframe(timeframe))
            
            # Reset index to get timestamp as column
            data = data.reset_index()
            data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            return data
            
        except Exception as e:
            self.logger.logger.error(f"Error fetching from Yahoo: {str(e)}")
            return None
    
    def _convert_timeframe(self, timeframe: str) -> str:
        """Convert internal timeframe to broker format."""
        timeframe_map = {
            "1m": "M1",
            "5m": "M5",
            "15m": "M15",
            "30m": "M30",
            "1h": "H1",
            "4h": "H4",
            "1d": "D"
        }
        return timeframe_map.get(timeframe, "H1")
    
    def _convert_yahoo_timeframe(self, timeframe: str) -> str:
        """Convert internal timeframe to Yahoo Finance format."""
        timeframe_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "1h",  # Yahoo doesn't support 4h, use 1h
            "1d": "1d"
        }
        return timeframe_map.get(timeframe, "1h")
    
    def _convert_to_yahoo_symbol(self, pair: str) -> str:
        """Convert forex pair to Yahoo Finance symbol."""
        # For forex pairs, Yahoo uses format like "EURUSD=X"
        return f"{pair}=X"
    
    def _update_market_data_cache(self, pair: str, timeframe: str, data: pd.DataFrame):
        """Update market data cache."""
        cache_key = f"{pair}_{timeframe}"
        self.market_data_cache[cache_key] = data
        
        # Keep only recent data to manage memory
        if len(data) > 10000:
            self.market_data_cache[cache_key] = data.tail(5000)
    
    async def _collect_news_data(self):
        """Collect news data from various sources."""
        if not self.news_api:
            return
        
        try:
            # Fetch news from API
            news_items = await self._fetch_news()
            
            # Process and store news
            for news in news_items:
                processed_news = self._process_news_item(news)
                self.news_cache.append(processed_news)
            
            # Keep only recent news
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            self.news_cache = [news for news in self.news_cache if news.published_at > cutoff_time]
            
        except Exception as e:
            self.logger.logger.error("Error collecting news data", error=str(e))
    
    async def _fetch_news(self) -> List[Dict]:
        """Fetch news from API."""
        try:
            # This would integrate with actual news API
            # For now, return empty list
            return []
            
        except Exception as e:
            self.logger.logger.error("Error fetching news", error=str(e))
            return []
    
    def _process_news_item(self, news_data: Dict) -> NewsItem:
        """Process raw news data into NewsItem."""
        # Extract text for sentiment analysis
        text = f"{news_data.get('title', '')} {news_data.get('content', '')}"
        
        # Calculate sentiment score
        sentiment_score = self._calculate_sentiment(text)
        
        # Determine relevance and impact
        relevance_score = self._calculate_relevance(news_data)
        impact = self._determine_impact(sentiment_score, relevance_score)
        
        # Extract currency pairs mentioned
        currency_pairs = self._extract_currency_pairs(text)
        
        return NewsItem(
            id=news_data.get('id', ''),
            title=news_data.get('title', ''),
            content=news_data.get('content', ''),
            source=news_data.get('source', ''),
            published_at=pd.to_datetime(news_data.get('published_at')),
            sentiment_score=sentiment_score,
            relevance_score=relevance_score,
            currency_pairs=currency_pairs,
            impact=impact
        )
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score for text."""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except:
            return 0.0
    
    def _calculate_relevance(self, news_data: Dict) -> float:
        """Calculate relevance score for news item."""
        # Simple relevance calculation
        # In practice, this would use more sophisticated NLP
        return 0.5
    
    def _determine_impact(self, sentiment_score: float, relevance_score: float) -> str:
        """Determine impact level of news item."""
        combined_score = abs(sentiment_score) * relevance_score
        
        if combined_score > 0.7:
            return "high"
        elif combined_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _extract_currency_pairs(self, text: str) -> List[str]:
        """Extract currency pairs mentioned in text."""
        # Simple regex-based extraction
        # In practice, this would use more sophisticated NLP
        import re
        
        pairs = []
        for pair in settings.trading.allowed_pairs:
            if pair.lower() in text.lower():
                pairs.append(pair)
        
        return pairs
    
    async def _collect_sentiment_data(self):
        """Collect sentiment data for currency pairs."""
        try:
            for pair in settings.trading.allowed_pairs:
                sentiment_data = await self._calculate_pair_sentiment(pair)
                if sentiment_data:
                    self.sentiment_cache[pair] = sentiment_data
                    
        except Exception as e:
            self.logger.logger.error("Error collecting sentiment data", error=str(e))
    
    async def _calculate_pair_sentiment(self, pair: str) -> Optional[SentimentData]:
        """Calculate sentiment for a specific currency pair."""
        try:
            # Get relevant news for this pair
            relevant_news = [news for news in self.news_cache if pair in news.currency_pairs]
            
            if not relevant_news:
                return None
            
            # Calculate news sentiment
            news_sentiment = np.mean([news.sentiment_score for news in relevant_news])
            
            # Calculate social sentiment (placeholder)
            social_sentiment = 0.0
            
            # Calculate overall sentiment
            overall_sentiment = (news_sentiment + social_sentiment) / 2
            
            # Calculate confidence
            confidence = min(len(relevant_news) / 10, 1.0)  # More news = higher confidence
            
            return SentimentData(
                pair=pair,
                timestamp=datetime.utcnow(),
                news_sentiment=news_sentiment,
                social_sentiment=social_sentiment,
                overall_sentiment=overall_sentiment,
                confidence=confidence,
                sources_count=len(relevant_news)
            )
            
        except Exception as e:
            self.logger.logger.error(f"Error calculating sentiment for {pair}", error=str(e))
            return None
    
    def get_market_data(self, pair: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Get market data for a specific pair and timeframe."""
        cache_key = f"{pair}_{timeframe}"
        
        if cache_key in self.market_data_cache:
            data = self.market_data_cache[cache_key]
            return data.tail(limit)
        
        return None
    
    def get_all_market_data(self) -> Dict[str, pd.DataFrame]:
        """Get all market data."""
        return self.market_data_cache.copy()
    
    def get_news_data(self, pair: Optional[str] = None, limit: int = 100) -> List[NewsItem]:
        """Get news data, optionally filtered by pair."""
        if pair:
            news = [item for item in self.news_cache if pair in item.currency_pairs]
        else:
            news = self.news_cache
        
        return news[-limit:]
    
    def get_sentiment_data(self, pair: Optional[str] = None) -> Dict[str, SentimentData]:
        """Get sentiment data, optionally filtered by pair."""
        if pair:
            return {pair: self.sentiment_cache.get(pair)} if pair in self.sentiment_cache else {}
        else:
            return self.sentiment_cache.copy()
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get data service summary."""
        return {
            "is_running": self.is_running,
            "market_data_pairs": len(self.market_data_cache),
            "news_items": len(self.news_cache),
            "sentiment_pairs": len(self.sentiment_cache),
            "last_update": datetime.utcnow().isoformat()
        }
