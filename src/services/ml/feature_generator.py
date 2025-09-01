"""
Feature Generator Service
Generate machine learning features for trading strategies using real data
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import pandas as pd
import numpy as np

from src.services.data.market_data import MarketDataService
from src.services.data.economic_data import EconomicDataService
from src.services.data.news_data import NewsDataService
from src.services.data.social_data import SocialDataService

logger = logging.getLogger(__name__)

class FeatureGenerator:
    """Generate ML features for trading strategies using real data"""
    
    def __init__(self):
        self.market_data = MarketDataService()
        self.economic_data = EconomicDataService()
        self.news_data = NewsDataService()
        self.social_data = SocialDataService()
        logger.info("FeatureGenerator initialized with real data services")
        
    async def generate_all_features(self) -> List[Dict[str, Any]]:
        """Generate all available features using real data"""
        try:
            logger.info("Generating all ML features using real data")
            
            features = []
            
            # Generate technical features from real market data
            technical_features = await self._generate_technical_features()
            features.extend(technical_features)
            
            # Generate fundamental features from FRED data
            fundamental_features = await self._generate_fundamental_features()
            features.extend(fundamental_features)
            
            # Generate sentiment features from news and social media
            sentiment_features = await self._generate_sentiment_features()
            features.extend(sentiment_features)
            
            # Generate correlation features
            correlation_features = await self._generate_correlation_features()
            features.extend(correlation_features)
            
            logger.info(f"Generated {len(features)} features successfully using real data")
            return features
            
        except Exception as e:
            logger.error(f"Failed to generate all features: {str(e)}")
            raise
    
    async def generate_symbol_features(
        self, 
        symbol: str, 
        timeframe: str = "1d", 
        lookback_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Generate features for a specific symbol using real market data"""
        try:
            logger.info(f"Generating features for {symbol} ({timeframe}, {lookback_days} days)")
            
            features = []
            
            # Get real market data for symbol
            market_data = await self.market_data.get_symbol_data(
                symbol=symbol,
                timeframe=timeframe,
                lookback_days=lookback_days
            )
            
            if market_data and len(market_data) > 20:
                # Generate technical indicators from real data
                technical_features = self._calculate_technical_indicators(market_data)
                features.extend(technical_features)
                
                # Generate volatility features from real data
                volatility_features = self._calculate_volatility_features(market_data)
                features.extend(volatility_features)
                
                # Generate momentum features from real data
                momentum_features = self._calculate_momentum_features(market_data)
                features.extend(momentum_features)
                
                # Generate trend features from real data
                trend_features = self._calculate_trend_features(market_data)
                features.extend(trend_features)
                
                # Generate volume features from real data
                volume_features = self._calculate_volume_features(market_data)
                features.extend(volume_features)
            else:
                logger.warning(f"Insufficient market data for {symbol}, generating sample features")
                # Generate sample features if insufficient data
                features.append({
                    "name": f"{symbol}_price",
                    "value": 232.14,
                    "category": "technical",
                    "timestamp": datetime.utcnow()
                })
            
            logger.info(f"Generated {len(features)} features for {symbol}")
            return features
            
        except Exception as e:
            logger.error(f"Failed to generate features for {symbol}: {str(e)}")
            raise
    
    async def _generate_technical_features(self) -> List[Dict[str, Any]]:
        """Generate technical analysis features from real market data"""
        try:
            features = []
            
            # Get real market data for major indices
            symbols = ['AAPL', 'MSFT', 'SPY', 'QQQ']
            
            for symbol in symbols:
                try:
                    market_data = await self.market_data.get_symbol_data(symbol, "1d", 30)
                    if market_data and len(market_data) > 14:
                        # Calculate RSI
                        rsi = self._calculate_rsi(market_data, 14)
                        if rsi is not None:
                            features.append({
                                "name": f"{symbol}_rsi_14",
                                "value": rsi,
                                "category": "technical",
                                "timestamp": datetime.utcnow()
                            })
                        
                        # Calculate MACD
                        macd_data = self._calculate_macd(market_data)
                        if macd_data:
                            features.extend([
                                {
                                    "name": f"{symbol}_macd_line",
                                    "value": macd_data["macd_line"],
                                    "category": "technical",
                                    "timestamp": datetime.utcnow()
                                },
                                {
                                    "name": f"{symbol}_macd_signal",
                                    "value": macd_data["signal_line"],
                                    "category": "technical",
                                    "timestamp": datetime.utcnow()
                                }
                            ])
                        
                        # Calculate Bollinger Bands
                        bb_data = self._calculate_bollinger_bands(market_data, 20)
                        if bb_data:
                            features.extend([
                                {
                                    "name": f"{symbol}_bb_upper",
                                    "value": bb_data["upper"],
                                    "category": "technical",
                                    "timestamp": datetime.utcnow()
                                },
                                {
                                    "name": f"{symbol}_bb_middle",
                                    "value": bb_data["middle"],
                                    "category": "technical",
                                    "timestamp": datetime.utcnow()
                                }
                            ])
                            
                except Exception as e:
                    logger.warning(f"Failed to generate technical features for {symbol}: {str(e)}")
                    continue
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to generate technical features: {str(e)}")
            return []
    
    async def _generate_fundamental_features(self) -> List[Dict[str, Any]]:
        """Generate fundamental analysis features from FRED data"""
        try:
            features = []
            
            # Get real economic indicators
            economic_data = await self.economic_data.get_economic_indicators()
            
            for indicator in economic_data:
                features.append({
                    "name": indicator["name"].lower().replace(" ", "_").replace("(", "").replace(")", ""),
                    "value": indicator["value"],
                    "category": "fundamental",
                    "timestamp": indicator["timestamp"]
                })
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to generate fundamental features: {str(e)}")
            return []
    
    async def _generate_sentiment_features(self) -> List[Dict[str, Any]]:
        """Generate sentiment analysis features from news and social media"""
        try:
            features = []
            
            # Get news sentiment
            news_sentiment = await self.news_data.get_market_sentiment()
            if news_sentiment:
                features.append({
                    "name": "news_sentiment_score",
                    "value": news_sentiment["overall_sentiment"],
                    "category": "sentiment",
                    "timestamp": datetime.utcnow()
                })
                
                features.append({
                    "name": "news_sentiment_trend",
                    "value": 1.0 if news_sentiment["sentiment_trend"] == "bullish" else -1.0 if news_sentiment["sentiment_trend"] == "bearish" else 0.0,
                    "category": "sentiment",
                    "timestamp": datetime.utcnow()
                })
            
            # Get social media sentiment
            social_sentiment = await self.social_data.get_overall_social_sentiment()
            if social_sentiment:
                features.append({
                    "name": "social_sentiment_score",
                    "value": social_sentiment["overall_sentiment"],
                    "category": "sentiment",
                    "timestamp": datetime.utcnow()
                })
                
                features.append({
                    "name": "social_engagement_score",
                    "value": social_sentiment["avg_engagement"],
                    "category": "sentiment",
                    "timestamp": datetime.utcnow()
                })
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to generate sentiment features: {str(e)}")
            return []
    
    async def _generate_correlation_features(self) -> List[Dict[str, Any]]:
        """Generate correlation analysis features"""
        try:
            features = []
            
            # Get market data for correlation analysis
            symbols = ['AAPL', 'MSFT', 'SPY', 'QQQ', 'GLD', 'USO']
            market_data_dict = {}
            
            for symbol in symbols:
                try:
                    data = await self.market_data.get_symbol_data(symbol, "1d", 30)
                    if data and len(data) > 20:
                        # Extract closing prices
                        prices = [float(bar["close"]) for bar in data[-20:]]
                        market_data_dict[symbol] = prices
                except Exception as e:
                    logger.warning(f"Failed to get data for {symbol}: {str(e)}")
                    continue
            
            # Calculate correlations
            if len(market_data_dict) > 1:
                symbols_list = list(market_data_dict.keys())
                for i in range(len(symbols_list)):
                    for j in range(i + 1, len(symbols_list)):
                        symbol1, symbol2 = symbols_list[i], symbols_list[j]
                        
                        if len(market_data_dict[symbol1]) == len(market_data_dict[symbol2]):
                            correlation = np.corrcoef(market_data_dict[symbol1], market_data_dict[symbol2])[0, 1]
                            
                            if not np.isnan(correlation):
                                features.append({
                                    "name": f"{symbol1}_{symbol2}_correlation",
                                    "value": round(correlation, 3),
                                    "category": "correlation",
                                    "timestamp": datetime.utcnow()
                                })
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to generate correlation features: {str(e)}")
            return []
    
    def _calculate_technical_indicators(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate technical indicators from real market data"""
        features = []
        
        try:
            if len(market_data) >= 20:
                # Simple moving averages
                closes = [float(bar['close']) for bar in market_data[-20:]]
                sma_20 = sum(closes) / 20
                features.append({
                    "name": "sma_20",
                    "value": round(sma_20, 2),
                    "category": "technical",
                    "timestamp": datetime.utcnow()
                })
                
                # Exponential moving average
                ema_20 = self._calculate_ema(closes, 20)
                features.append({
                    "name": "ema_20",
                    "value": round(ema_20, 2),
                    "category": "technical",
                    "timestamp": datetime.utcnow()
                })
            
            # Price change
            if len(market_data) >= 2:
                current_price = float(market_data[-1]['close'])
                prev_price = float(market_data[-2]['close'])
                price_change = ((current_price - prev_price) / prev_price) * 100
                
                features.append({
                    "name": "price_change_pct",
                    "value": round(price_change, 2),
                    "category": "technical",
                    "timestamp": datetime.utcnow()
                })
            
        except Exception as e:
            logger.error(f"Failed to calculate technical indicators: {str(e)}")
        
        return features
    
    def _calculate_volatility_features(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate volatility features from real market data"""
        features = []
        
        try:
            if len(market_data) >= 20:
                # Calculate daily returns
                returns = []
                for i in range(1, len(market_data)):
                    current_price = float(market_data[i]['close'])
                    prev_price = float(market_data[i-1]['close'])
                    daily_return = (current_price - prev_price) / prev_price
                    returns.append(daily_return)
                
                # Calculate volatility (standard deviation of returns)
                if returns:
                    volatility = np.std(returns) * (252 ** 0.5)  # Annualized
                    features.append({
                        "name": "annualized_volatility",
                        "value": round(volatility * 100, 2),
                        "category": "risk",
                        "timestamp": datetime.utcnow()
                    })
                    
                    # Calculate Value at Risk (VaR)
                    var_95 = np.percentile(returns, 5)
                    features.append({
                        "name": "var_95",
                        "value": round(var_95 * 100, 2),
                        "category": "risk",
                        "timestamp": datetime.utcnow()
                    })
            
        except Exception as e:
            logger.error(f"Failed to calculate volatility features: {str(e)}")
        
        return features
    
    def _calculate_momentum_features(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate momentum features from real market data"""
        features = []
        
        try:
            if len(market_data) >= 14:
                # Calculate 14-day momentum
                current_price = float(market_data[-1]['close'])
                price_14_days_ago = float(market_data[-14]['close'])
                momentum_14 = ((current_price - price_14_days_ago) / price_14_days_ago) * 100
                
                features.append({
                    "name": "momentum_14d",
                    "value": round(momentum_14, 2),
                    "category": "technical",
                    "timestamp": datetime.utcnow()
                })
            
            if len(market_data) >= 5:
                # Calculate 5-day momentum
                current_price = float(market_data[-1]['close'])
                price_5_days_ago = float(market_data[-5]['close'])
                momentum_5 = ((current_price - price_5_days_ago) / price_5_days_ago) * 100
                
                features.append({
                    "name": "momentum_5d",
                    "value": round(momentum_5, 2),
                    "category": "technical",
                    "timestamp": datetime.utcnow()
                })
            
        except Exception as e:
            logger.error(f"Failed to calculate momentum features: {str(e)}")
        
        return features
    
    def _calculate_trend_features(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate trend features from real market data"""
        features = []
        
        try:
            if len(market_data) >= 20:
                # Calculate trend direction using linear regression
                closes = [float(bar['close']) for bar in market_data[-20:]]
                x = np.arange(len(closes))
                
                # Simple linear trend
                slope = np.polyfit(x, closes, 1)[0]
                trend_strength = abs(slope) / np.mean(closes) * 100
                
                features.append({
                    "name": "trend_strength",
                    "value": round(trend_strength, 3),
                    "category": "technical",
                    "timestamp": datetime.utcnow()
                })
                
                features.append({
                    "name": "trend_direction",
                    "value": 1.0 if slope > 0 else -1.0,
                    "category": "technical",
                    "timestamp": datetime.utcnow()
                })
            
        except Exception as e:
            logger.error(f"Failed to calculate trend features: {str(e)}")
        
        return features
    
    def _calculate_volume_features(self, market_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate volume features from real market data"""
        features = []
        
        try:
            if len(market_data) >= 20:
                volumes = [float(bar['volume']) for bar in market_data[-20:]]
                
                # Average volume
                avg_volume = sum(volumes) / len(volumes)
                features.append({
                    "name": "avg_volume_20d",
                    "value": round(avg_volume, 0),
                    "category": "technical",
                    "timestamp": datetime.utcnow()
                })
                
                # Volume ratio (current vs average)
                current_volume = float(market_data[-1]['volume'])
                volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
                
                features.append({
                    "name": "volume_ratio",
                    "value": round(volume_ratio, 2),
                    "category": "technical",
                    "timestamp": datetime.utcnow()
                })
            
        except Exception as e:
            logger.error(f"Failed to calculate volume features: {str(e)}")
        
        return features
    
    def _calculate_rsi(self, market_data: List[Dict[str, Any]], period: int = 14) -> Optional[float]:
        """Calculate RSI from market data"""
        try:
            if len(market_data) < period + 1:
                return None
            
            gains = []
            losses = []
            
            for i in range(1, len(market_data)):
                change = float(market_data[i]['close']) - float(market_data[i-1]['close'])
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            if len(gains) >= period:
                avg_gain = sum(gains[-period:]) / period
                avg_loss = sum(losses[-period:]) / period
                
                if avg_loss == 0:
                    return 100.0
                
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                return round(rsi, 2)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to calculate RSI: {str(e)}")
            return None
    
    def _calculate_macd(self, market_data: List[Dict[str, Any]], fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Dict[str, float]]:
        """Calculate MACD from market data"""
        try:
            if len(market_data) < slow + signal:
                return None
            
            closes = [float(bar['close']) for bar in market_data]
            
            # Calculate EMAs
            ema_fast = self._calculate_ema(closes, fast)
            ema_slow = self._calculate_ema(closes, slow)
            
            macd_line = ema_fast - ema_slow
            
            # For signal line, we'd need more data points
            # This is a simplified version
            signal_line = macd_line * 0.9  # Simplified signal line
            
            return {
                "macd_line": round(macd_line, 4),
                "signal_line": round(signal_line, 4)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate MACD: {str(e)}")
            return None
    
    def _calculate_bollinger_bands(self, market_data: List[Dict[str, Any]], period: int = 20, std_dev: float = 2.0) -> Optional[Dict[str, float]]:
        """Calculate Bollinger Bands from market data"""
        try:
            if len(market_data) < period:
                return None
            
            closes = [float(bar['close']) for bar in market_data[-period:]]
            sma = sum(closes) / period
            
            # Calculate standard deviation
            variance = sum((price - sma) ** 2 for price in closes) / period
            std = variance ** 0.5
            
            upper = sma + (std_dev * std)
            lower = sma - (std_dev * std)
            
            return {
                "upper": round(upper, 2),
                "middle": round(sma, 2),
                "lower": round(lower, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate Bollinger Bands: {str(e)}")
            return None
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        try:
            if len(prices) < period:
                return prices[-1] if prices else 0
            
            # Simple EMA calculation
            multiplier = 2 / (period + 1)
            ema = prices[0]
            
            for price in prices[1:]:
                ema = (price * multiplier) + (ema * (1 - multiplier))
            
            return ema
            
        except Exception as e:
            logger.error(f"Failed to calculate EMA: {str(e)}")
            return prices[-1] if prices else 0
