"""
Market Data Service
Collect real-time market data from multiple sources
"""

import logging
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from config.api_keys import ALPHA_VANTAGE_API_KEY, POLYGON_API_KEY

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service for collecting real-time market data"""
    
    def __init__(self):
        self.alpha_vantage_key = ALPHA_VANTAGE_API_KEY
        self.polygon_key = POLYGON_API_KEY
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_symbol_data(
        self, 
        symbol: str, 
        timeframe: str = "1d", 
        lookback_days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get market data for a specific symbol"""
        try:
            logger.info(f"Fetching {timeframe} data for {symbol} ({lookback_days} days)")
            
            # Try Polygon.io first (better for US markets)
            if symbol in ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'SPY', 'QQQ']:
                data = await self._get_polygon_data(symbol, timeframe, lookback_days)
                if data:
                    return data
            
            # Fallback to Alpha Vantage
            data = await self._get_alpha_vantage_data(symbol, timeframe, lookback_days)
            return data
            
        except Exception as e:
            logger.error(f"Failed to get data for {symbol}: {str(e)}")
            return []
    
    async def _get_polygon_data(
        self, 
        symbol: str, 
        timeframe: str, 
        lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Get data from Polygon.io"""
        try:
            # Convert timeframe to Polygon format
            timespan_map = {
                "1m": "minute",
                "5m": "minute", 
                "15m": "minute",
                "30m": "minute",
                "1h": "hour",
                "1d": "day"
            }
            
            timespan = timespan_map.get(timeframe, "day")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)
            
            url = f"https://api.polygon.io/v2/aggs/ticker/{symbol}/range/1/{timespan}/{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            
            params = {
                "adjusted": "true",
                "sort": "desc",
                "limit": 5000,
                "apiKey": self.polygon_key
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "OK" and data.get("results"):
                        results = data["results"]
                        
                        # Convert to standard format
                        formatted_data = []
                        for bar in results:
                            formatted_data.append({
                                "timestamp": datetime.fromtimestamp(bar["t"] / 1000),
                                "open": bar["o"],
                                "high": bar["h"],
                                "low": bar["l"],
                                "close": bar["c"],
                                "volume": bar["v"],
                                "vwap": bar.get("vw", 0),
                                "transactions": bar.get("n", 0)
                            })
                        
                        logger.info(f"Retrieved {len(formatted_data)} bars from Polygon.io for {symbol}")
                        return formatted_data
                    else:
                        logger.warning(f"No data returned from Polygon.io for {symbol}")
                        return []
                else:
                    logger.error(f"Polygon.io API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get Polygon.io data for {symbol}: {str(e)}")
            return []
    
    async def _get_alpha_vantage_data(
        self, 
        symbol: str, 
        timeframe: str, 
        lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Get data from Alpha Vantage"""
        try:
            # Alpha Vantage function mapping
            function_map = {
                "1d": "TIME_SERIES_DAILY",
                "1h": "TIME_SERIES_INTRADAY",
                "5m": "TIME_SERIES_INTRADAY"
            }
            
            function = function_map.get(timeframe, "TIME_SERIES_DAILY")
            
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": function,
                "symbol": symbol,
                "apikey": self.alpha_vantage_key,
                "outputsize": "full" if lookback_days > 100 else "compact"
            }
            
            if timeframe in ["1h", "5m"]:
                params["interval"] = "60min" if timeframe == "1h" else "5min"
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract time series data
                    time_series_key = None
                    for key in data.keys():
                        if "Time Series" in key:
                            time_series_key = key
                            break
                    
                    if time_series_key and data[time_series_key]:
                        time_series = data[time_series_key]
                        
                        # Convert to standard format
                        formatted_data = []
                        for timestamp_str, values in time_series.items():
                            # Parse timestamp
                            if ":" in timestamp_str:
                                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            else:
                                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
                            
                            # Check if within lookback period
                            if timestamp >= datetime.now() - timedelta(days=lookback_days):
                                formatted_data.append({
                                    "timestamp": timestamp,
                                    "open": float(values["1. open"]),
                                    "high": float(values["2. high"]),
                                    "low": float(values["3. low"]),
                                    "close": float(values["4. close"]),
                                    "volume": int(values["5. volume"])
                                })
                        
                        # Sort by timestamp
                        formatted_data.sort(key=lambda x: x["timestamp"])
                        
                        logger.info(f"Retrieved {len(formatted_data)} bars from Alpha Vantage for {symbol}")
                        return formatted_data
                    else:
                        logger.warning(f"No time series data returned from Alpha Vantage for {symbol}")
                        return []
                else:
                    logger.error(f"Alpha Vantage API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get Alpha Vantage data for {symbol}: {str(e)}")
            return []
    
    async def get_real_time_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get real-time quote for a symbol"""
        try:
            # Try Alpha Vantage global quote
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.alpha_vantage_key
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "Global Quote" in data:
                        quote = data["Global Quote"]
                        return {
                            "symbol": quote.get("01. symbol"),
                            "price": float(quote.get("05. price", 0)),
                            "change": float(quote.get("09. change", 0)),
                            "change_percent": quote.get("10. change percent", "0%"),
                            "volume": int(quote.get("06. volume", 0)),
                            "timestamp": datetime.utcnow()
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get real-time quote for {symbol}: {str(e)}")
            return None
    
    async def get_forex_rate(self, from_currency: str, to_currency: str) -> Optional[Dict[str, Any]]:
        """Get real-time forex exchange rate"""
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": from_currency,
                "to_currency": to_currency,
                "apikey": self.alpha_vantage_key
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "Realtime Currency Exchange Rate" in data:
                        rate = data["Realtime Currency Exchange Rate"]
                        return {
                            "from_currency": rate.get("1. From_Currency Code"),
                            "to_currency": rate.get("3. To_Currency Code"),
                            "exchange_rate": float(rate.get("5. Exchange Rate", 0)),
                            "last_refreshed": rate.get("6. Last Refreshed"),
                            "timezone": rate.get("7. Time Zone"),
                            "timestamp": datetime.utcnow()
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get forex rate for {from_currency}/{to_currency}: {str(e)}")
            return None
