"""
News Data Service
Collect financial news and sentiment data
"""

import logging
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from config.api_keys import NEWS_API_KEY

logger = logging.getLogger(__name__)

class NewsDataService:
    """Service for collecting financial news and sentiment"""
    
    def __init__(self):
        self.news_api_key = NEWS_API_KEY
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_financial_news(
        self, 
        query: str = "finance", 
        page_size: int = 50,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """Get financial news articles"""
        try:
            url = "https://newsapi.org/v2/everything"
            
            # Calculate date range
            from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            params = {
                "q": query,
                "apiKey": self.news_api_key,
                "pageSize": page_size,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": "en",
                "domains": "reuters.com,bloomberg.com,cnbc.com,wsj.com,ft.com,marketwatch.com"
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "ok" and data.get("articles"):
                        articles = data["articles"]
                        
                        formatted_articles = []
                        for article in articles:
                            try:
                                # Calculate sentiment score (simple approach)
                                sentiment_score = self._calculate_sentiment(article)
                                
                                formatted_articles.append({
                                    "title": article.get("title", ""),
                                    "description": article.get("description", ""),
                                    "content": article.get("content", ""),
                                    "url": article.get("url", ""),
                                    "source": article.get("source", {}).get("name", ""),
                                    "published_at": article.get("publishedAt", ""),
                                    "sentiment_score": sentiment_score,
                                    "category": "news",
                                    "timestamp": datetime.utcnow()
                                })
                            except Exception as e:
                                logger.warning(f"Failed to format article: {str(e)}")
                                continue
                        
                        logger.info(f"Retrieved {len(formatted_articles)} news articles")
                        return formatted_articles
                    else:
                        logger.warning(f"No articles returned for query: {query}")
                        return []
                else:
                    logger.error(f"NewsAPI error: {response.status} - {await response.text()}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get financial news: {str(e)}")
            return []
    
    async def get_market_sentiment(self, symbol: str = None) -> Dict[str, Any]:
        """Get overall market sentiment"""
        try:
            # Get general financial news
            general_news = await self.get_financial_news("finance", 100, 3)
            
            # Get specific symbol news if provided
            symbol_news = []
            if symbol:
                symbol_news = await self.get_financial_news(symbol, 50, 3)
            
            # Calculate sentiment metrics
            all_news = general_news + symbol_news
            
            if all_news:
                sentiment_scores = [article["sentiment_score"] for article in all_news]
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                
                # Categorize sentiment
                positive_count = sum(1 for score in sentiment_scores if score > 0.1)
                negative_count = sum(1 for score in sentiment_scores if score < -0.1)
                neutral_count = len(sentiment_scores) - positive_count - negative_count
                
                sentiment_analysis = {
                    "overall_sentiment": avg_sentiment,
                    "positive_articles": positive_count,
                    "negative_articles": negative_count,
                    "neutral_articles": neutral_count,
                    "total_articles": len(all_news),
                    "sentiment_trend": "bullish" if avg_sentiment > 0.1 else "bearish" if avg_sentiment < -0.1 else "neutral",
                    "timestamp": datetime.utcnow(),
                    "category": "sentiment"
                }
                
                logger.info(f"Calculated market sentiment: {sentiment_analysis['sentiment_trend']}")
                return sentiment_analysis
            else:
                return {
                    "overall_sentiment": 0.0,
                    "positive_articles": 0,
                    "negative_articles": 0,
                    "neutral_articles": 0,
                    "total_articles": 0,
                    "sentiment_trend": "neutral",
                    "timestamp": datetime.utcnow(),
                    "category": "sentiment"
                }
                
        except Exception as e:
            logger.error(f"Failed to calculate market sentiment: {str(e)}")
            return {}
    
    async def get_crypto_news(self, page_size: int = 30) -> List[Dict[str, Any]]:
        """Get cryptocurrency news"""
        try:
            return await self.get_financial_news("cryptocurrency OR bitcoin OR ethereum", page_size, 3)
        except Exception as e:
            logger.error(f"Failed to get crypto news: {str(e)}")
            return []
    
    async def get_forex_news(self, page_size: int = 30) -> List[Dict[str, Any]]:
        """Get forex news"""
        try:
            return await self.get_financial_news("forex OR currency OR EUR/USD OR GBP/USD", page_size, 3)
        except Exception as e:
            logger.error(f"Failed to get forex news: {str(e)}")
            return []
    
    async def get_stock_news(self, symbol: str = None, page_size: int = 30) -> List[Dict[str, Any]]:
        """Get stock market news"""
        try:
            if symbol:
                query = f"{symbol} stock OR {symbol} shares"
            else:
                query = "stock market OR S&P 500 OR NASDAQ OR Dow Jones"
            
            return await self.get_financial_news(query, page_size, 3)
        except Exception as e:
            logger.error(f"Failed to get stock news: {str(e)}")
            return []
    
    def _calculate_sentiment(self, article: Dict[str, Any]) -> float:
        """Calculate sentiment score for an article"""
        try:
            # Simple keyword-based sentiment analysis
            positive_keywords = [
                "bullish", "surge", "rally", "gain", "positive", "growth", "profit", "strong",
                "recovery", "optimistic", "confidence", "expansion", "record", "high", "rise"
            ]
            
            negative_keywords = [
                "bearish", "crash", "decline", "loss", "negative", "recession", "weak",
                "concern", "pessimistic", "fear", "contraction", "low", "fall", "drop"
            ]
            
            # Combine title and description
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in text)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text)
            
            # Calculate sentiment score (-1 to 1)
            total_words = len(text.split())
            if total_words > 0:
                sentiment = (positive_count - negative_count) / total_words
                # Normalize to -1 to 1 range
                sentiment = max(-1.0, min(1.0, sentiment * 10))
                return round(sentiment, 3)
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"Failed to calculate sentiment: {str(e)}")
            return 0.0
    
    async def get_trending_topics(self) -> List[str]:
        """Get trending financial topics"""
        try:
            # Get recent news and extract common topics
            recent_news = await self.get_financial_news("finance", 100, 1)
            
            # Simple topic extraction (in production, you'd use NLP)
            topics = set()
            for article in recent_news:
                title = article.get("title", "").lower()
                
                # Extract common financial terms
                if "fed" in title or "federal reserve" in title:
                    topics.add("Federal Reserve")
                if "inflation" in title:
                    topics.add("Inflation")
                if "recession" in title:
                    topics.add("Recession")
                if "earnings" in title:
                    topics.add("Earnings")
                if "crypto" in title or "bitcoin" in title:
                    topics.add("Cryptocurrency")
                if "oil" in title or "energy" in title:
                    topics.add("Energy")
                if "china" in title:
                    topics.add("China")
                if "europe" in title or "eu" in title:
                    topics.add("Europe")
            
            return list(topics)
            
        except Exception as e:
            logger.error(f"Failed to get trending topics: {str(e)}")
            return []
