"""
Social Data Service
Collect social media sentiment data
"""

import logging
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from config.api_keys import TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET

logger = logging.getLogger(__name__)

class SocialDataService:
    """Service for collecting social media sentiment data"""
    
    def __init__(self):
        self.bearer_token = TWITTER_BEARER_TOKEN
        self.api_key = TWITTER_API_KEY
        self.api_secret = TWITTER_API_SECRET
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_twitter_sentiment(
        self, 
        query: str = "finance", 
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Get Twitter sentiment data"""
        try:
            url = "https://api.twitter.com/2/tweets/search/recent"
            
            params = {
                "query": query,
                "max_results": max_results,
                "tweet.fields": "created_at,public_metrics,lang",
                "user.fields": "username,verified",
                "expansions": "author_id"
            }
            
            headers = {
                "Authorization": f"Bearer {self.bearer_token}"
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "data" in data and data["data"]:
                        tweets = data["data"]
                        
                        formatted_tweets = []
                        for tweet in tweets:
                            try:
                                # Calculate sentiment score
                                sentiment_score = self._calculate_tweet_sentiment(tweet)
                                
                                # Get metrics
                                metrics = tweet.get("public_metrics", {})
                                
                                formatted_tweets.append({
                                    "id": tweet.get("id"),
                                    "text": tweet.get("text", ""),
                                    "created_at": tweet.get("created_at"),
                                    "sentiment_score": sentiment_score,
                                    "retweet_count": metrics.get("retweet_count", 0),
                                    "like_count": metrics.get("like_count", 0),
                                    "reply_count": metrics.get("reply_count", 0),
                                    "quote_count": metrics.get("quote_count", 0),
                                    "engagement_score": self._calculate_engagement_score(metrics),
                                    "category": "social",
                                    "timestamp": datetime.utcnow()
                                })
                            except Exception as e:
                                logger.warning(f"Failed to format tweet: {str(e)}")
                                continue
                        
                        logger.info(f"Retrieved {len(formatted_tweets)} tweets")
                        return formatted_tweets
                    else:
                        logger.warning(f"No tweets returned for query: {query}")
                        return []
                else:
                    logger.error(f"Twitter API error: {response.status} - {await response.text()}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get Twitter sentiment: {str(e)}")
            return []
    
    async def get_crypto_sentiment(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get cryptocurrency sentiment from social media"""
        try:
            return await self.get_twitter_sentiment("cryptocurrency OR bitcoin OR ethereum", max_results)
        except Exception as e:
            logger.error(f"Failed to get crypto sentiment: {str(e)}")
            return []
    
    async def get_stock_sentiment(self, symbol: str = None, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get stock market sentiment from social media"""
        try:
            if symbol:
                query = f"{symbol} stock OR {symbol} shares"
            else:
                query = "stock market OR S&P 500 OR NASDAQ"
            
            return await self.get_twitter_sentiment(query, max_results)
        except Exception as e:
            logger.error(f"Failed to get stock sentiment: {str(e)}")
            return []
    
    async def get_forex_sentiment(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get forex sentiment from social media"""
        try:
            return await self.get_twitter_sentiment("forex OR currency OR EUR/USD", max_results)
        except Exception as e:
            logger.error(f"Failed to get forex sentiment: {str(e)}")
            return []
    
    async def get_overall_social_sentiment(self) -> Dict[str, Any]:
        """Get overall social media sentiment"""
        try:
            # Get sentiment from different financial topics
            finance_tweets = await self.get_twitter_sentiment("finance", 100)
            crypto_tweets = await self.get_crypto_sentiment(50)
            stock_tweets = await self.get_stock_sentiment(None, 50)
            
            all_tweets = finance_tweets + crypto_tweets + stock_tweets
            
            if all_tweets:
                sentiment_scores = [tweet["sentiment_score"] for tweet in all_tweets]
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                
                # Calculate engagement metrics
                total_engagement = sum(tweet["engagement_score"] for tweet in all_tweets)
                avg_engagement = total_engagement / len(all_tweets)
                
                # Categorize sentiment
                positive_count = sum(1 for score in sentiment_scores if score > 0.1)
                negative_count = sum(1 for score in sentiment_scores if score < -0.1)
                neutral_count = len(sentiment_scores) - positive_count - negative_count
                
                sentiment_analysis = {
                    "overall_sentiment": avg_sentiment,
                    "positive_tweets": positive_count,
                    "negative_tweets": negative_count,
                    "neutral_tweets": neutral_count,
                    "total_tweets": len(all_tweets),
                    "avg_engagement": avg_engagement,
                    "sentiment_trend": "bullish" if avg_sentiment > 0.1 else "bearish" if avg_sentiment < -0.1 else "neutral",
                    "timestamp": datetime.utcnow(),
                    "category": "social_sentiment"
                }
                
                logger.info(f"Calculated social sentiment: {sentiment_analysis['sentiment_trend']}")
                return sentiment_analysis
            else:
                return {
                    "overall_sentiment": 0.0,
                    "positive_tweets": 0,
                    "negative_tweets": 0,
                    "neutral_tweets": 0,
                    "total_tweets": 0,
                    "avg_engagement": 0.0,
                    "sentiment_trend": "neutral",
                    "timestamp": datetime.utcnow(),
                    "category": "social_sentiment"
                }
                
        except Exception as e:
            logger.error(f"Failed to calculate social sentiment: {str(e)}")
            return {}
    
    def _calculate_tweet_sentiment(self, tweet: Dict[str, Any]) -> float:
        """Calculate sentiment score for a tweet"""
        try:
            # Simple keyword-based sentiment analysis
            positive_keywords = [
                "bullish", "surge", "rally", "gain", "positive", "growth", "profit", "strong",
                "recovery", "optimistic", "confidence", "expansion", "record", "high", "rise",
                "🚀", "📈", "💪", "🔥", "💎", "moon", "hodl", "buy", "long"
            ]
            
            negative_keywords = [
                "bearish", "crash", "decline", "loss", "negative", "recession", "weak",
                "concern", "pessimistic", "fear", "contraction", "low", "fall", "drop",
                "📉", "💩", "dump", "sell", "short", "bear", "panic"
            ]
            
            text = tweet.get("text", "").lower()
            
            positive_count = sum(1 for keyword in positive_keywords if keyword in text)
            negative_count = sum(1 for keyword in negative_keywords if keyword in text)
            
            # Calculate sentiment score (-1 to 1)
            total_words = len(text.split())
            if total_words > 0:
                sentiment = (positive_count - negative_count) / total_words
                # Normalize to -1 to 1 range
                sentiment = max(-1.0, min(1.0, sentiment * 15))  # Higher multiplier for tweets
                return round(sentiment, 3)
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"Failed to calculate tweet sentiment: {str(e)}")
            return 0.0
    
    def _calculate_engagement_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate engagement score for a tweet"""
        try:
            # Weighted engagement score
            retweet_weight = 2.0
            like_weight = 1.0
            reply_weight = 3.0
            quote_weight = 2.5
            
            engagement_score = (
                metrics.get("retweet_count", 0) * retweet_weight +
                metrics.get("like_count", 0) * like_weight +
                metrics.get("reply_count", 0) * reply_weight +
                metrics.get("quote_count", 0) * quote_weight
            )
            
            return engagement_score
            
        except Exception as e:
            logger.warning(f"Failed to calculate engagement score: {str(e)}")
            return 0.0
    
    async def get_trending_hashtags(self) -> List[str]:
        """Get trending financial hashtags"""
        try:
            # Get recent finance tweets and extract hashtags
            finance_tweets = await self.get_twitter_sentiment("finance", 100)
            
            hashtags = set()
            for tweet in finance_tweets:
                text = tweet.get("text", "")
                # Extract hashtags (simple regex-like approach)
                words = text.split()
                for word in words:
                    if word.startswith("#") and len(word) > 1:
                        hashtags.add(word.lower())
            
            # Return top hashtags by frequency
            hashtag_counts = {}
            for tweet in finance_tweets:
                text = tweet.get("text", "")
                words = text.split()
                for word in words:
                    if word.startswith("#") and len(word) > 1:
                        hashtag = word.lower()
                        hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
            
            # Sort by frequency and return top 10
            sorted_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)
            return [hashtag for hashtag, count in sorted_hashtags[:10]]
            
        except Exception as e:
            logger.error(f"Failed to get trending hashtags: {str(e)}")
            return []
