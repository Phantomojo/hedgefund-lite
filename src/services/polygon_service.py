"""
Polygon.io service for comprehensive market data.
Provides access to stocks, options, futures, forex, and crypto data.
"""

import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

class PolygonService:
    """Polygon.io API service for market data."""
    
    def __init__(self):
        self.base_url = settings.external_services.polygon.get("base_url", "https://api.polygon.io")
        self.api_key = settings.external_services.polygon.get("api_key")
        self.enabled = settings.external_services.polygon.get("enabled", False)
        
        if not self.enabled or not self.api_key:
            logger.warning("Polygon.io service not configured or disabled")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to Polygon.io API."""
        if not self.enabled or not self.api_key:
            raise Exception("Polygon.io service not configured")
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Polygon.io API request failed: {e}")
            raise
    
    def get_stock_data(self, symbol: str, from_date: str, to_date: str, 
                      timespan: str = "day") -> Dict[str, Any]:
        """Get historical stock data."""
        endpoint = f"/v2/aggs/ticker/{symbol}/range/1/{timespan}/{from_date}/{to_date}"
        return self._make_request(endpoint)
    
    def get_forex_data(self, from_currency: str, to_currency: str, 
                      from_date: str, to_date: str, timespan: str = "hour") -> Dict[str, Any]:
        """Get historical forex data."""
        pair = f"C:{from_currency}{to_currency}"
        endpoint = f"/v2/aggs/ticker/{pair}/range/1/{timespan}/{from_date}/{to_date}"
        return self._make_request(endpoint)
    
    def get_crypto_data(self, symbol: str, from_date: str, to_date: str, 
                       timespan: str = "hour") -> Dict[str, Any]:
        """Get historical crypto data."""
        endpoint = f"/v2/aggs/ticker/X:{symbol}/range/1/{timespan}/{from_date}/{to_date}"
        return self._make_request(endpoint)
    
    def get_options_data(self, underlying_asset: str, strike_price: float, 
                        expiration_date: str, contract_type: str = "call") -> Dict[str, Any]:
        """Get options data."""
        endpoint = f"/v3/reference/options/contracts"
        params = {
            "underlying_asset": underlying_asset,
            "strike_price": strike_price,
            "expiration_date": expiration_date,
            "contract_type": contract_type
        }
        return self._make_request(endpoint, params)
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get current market status."""
        endpoint = "/v1/marketstatus/now"
        return self._make_request(endpoint)
    
    def get_ticker_details(self, symbol: str) -> Dict[str, Any]:
        """Get detailed information about a ticker."""
        endpoint = f"/v3/reference/tickers/{symbol}"
        return self._make_request(endpoint)
    
    def get_news(self, symbol: str = None, published_utc: str = None, 
                order: str = "desc", limit: int = 10) -> Dict[str, Any]:
        """Get news articles."""
        endpoint = "/v2/reference/news"
        params = {
            "order": order,
            "limit": limit
        }
        if symbol:
            params["ticker"] = symbol
        if published_utc:
            params["published_utc"] = published_utc
        
        return self._make_request(endpoint, params)
    
    def get_technical_indicators(self, symbol: str, indicator: str, 
                               timespan: str = "day", window: int = 14) -> Dict[str, Any]:
        """Get technical indicators."""
        endpoint = f"/v1/indicators/{indicator}/{symbol}"
        params = {
            "timespan": timespan,
            "window": window
        }
        return self._make_request(endpoint, params)
    
    def search_tickers(self, search_term: str, type: str = None, 
                      market: str = None, active: bool = True) -> Dict[str, Any]:
        """Search for tickers."""
        endpoint = "/v3/reference/tickers"
        params = {
            "search": search_term,
            "active": active
        }
        if type:
            params["type"] = type
        if market:
            params["market"] = market
        
        return self._make_request(endpoint, params)
    
    def get_sector_performance(self) -> Dict[str, Any]:
        """Get sector performance data."""
        endpoint = "/v2/reference/sectors"
        return self._make_request(endpoint)
    
    def get_earnings(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """Get earnings data for a symbol."""
        endpoint = f"/v2/reference/financials/{symbol}"
        params = {"limit": limit}
        return self._make_request(endpoint, params)
    
    def format_forex_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format forex data for our system."""
        if "results" not in data:
            return []
        
        formatted_data = []
        for result in data["results"]:
            formatted_data.append({
                "timestamp": result.get("t"),
                "open": result.get("o"),
                "high": result.get("h"),
                "low": result.get("l"),
                "close": result.get("c"),
                "volume": result.get("v"),
                "vwap": result.get("vw"),
                "transactions": result.get("n")
            })
        
        return formatted_data
    
    def get_latest_price(self, symbol: str, asset_type: str = "stocks") -> Dict[str, Any]:
        """Get the latest price for a symbol."""
        if asset_type == "forex":
            endpoint = f"/v2/snapshot/locale/global/markets/forex/tickers/{symbol}"
        elif asset_type == "crypto":
            endpoint = f"/v2/snapshot/locale/global/markets/crypto/tickers/{symbol}"
        else:
            endpoint = f"/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}"
        
        return self._make_request(endpoint)

# Global instance
polygon_service = PolygonService()
