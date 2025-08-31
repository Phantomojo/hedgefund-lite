"""
Twelve Data service for comprehensive financial data.
Provides access to stocks, forex, crypto, and economic indicators.
"""

import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

class TwelveDataService:
    """Twelve Data API service for market data."""
    
    def __init__(self):
        self.base_url = settings.external_services.twelve_data.get("base_url", "https://api.twelvedata.com")
        self.api_key = settings.external_services.twelve_data.get("api_key")
        self.enabled = settings.external_services.twelve_data.get("enabled", False)
        
        if not self.enabled or not self.api_key:
            logger.warning("Twelve Data service not configured or disabled")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to Twelve Data API."""
        if not self.enabled or not self.api_key:
            raise Exception("Twelve Data service not configured")
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["apikey"] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Twelve Data API request failed: {e}")
            raise
    
    def get_time_series(self, symbol: str, interval: str = "1day", 
                       outputsize: int = 100, format: str = "JSON") -> Dict[str, Any]:
        """Get time series data for any symbol."""
        endpoint = "/time_series"
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": outputsize,
            "format": format
        }
        return self._make_request(endpoint, params)
    
    def get_stock_data(self, symbol: str, interval: str = "1day", 
                      outputsize: int = 100) -> Dict[str, Any]:
        """Get stock data."""
        return self.get_time_series(symbol, interval, outputsize)
    
    def get_forex_data(self, symbol: str, interval: str = "1h", 
                      outputsize: int = 100) -> Dict[str, Any]:
        """Get forex data."""
        return self.get_time_series(symbol, interval, outputsize)
    
    def get_crypto_data(self, symbol: str, interval: str = "1h", 
                       outputsize: int = 100) -> Dict[str, Any]:
        """Get crypto data."""
        return self.get_time_series(symbol, interval, outputsize)
    
    def get_etf_data(self, symbol: str, interval: str = "1day", 
                    outputsize: int = 100) -> Dict[str, Any]:
        """Get ETF data."""
        return self.get_time_series(symbol, interval, outputsize)
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time quote for a symbol."""
        endpoint = "/quote"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a symbol."""
        endpoint = "/price"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_earnings(self, symbol: str) -> Dict[str, Any]:
        """Get earnings data for a symbol."""
        endpoint = "/earnings"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_income_statement(self, symbol: str) -> Dict[str, Any]:
        """Get income statement for a symbol."""
        endpoint = "/income_statement"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_balance_sheet(self, symbol: str) -> Dict[str, Any]:
        """Get balance sheet for a symbol."""
        endpoint = "/balance_sheet"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_cash_flow(self, symbol: str) -> Dict[str, Any]:
        """Get cash flow for a symbol."""
        endpoint = "/cash_flow"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_dividends(self, symbol: str) -> Dict[str, Any]:
        """Get dividends for a symbol."""
        endpoint = "/dividends"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_splits(self, symbol: str) -> Dict[str, Any]:
        """Get stock splits for a symbol."""
        endpoint = "/splits"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_technical_indicators(self, symbol: str, indicator: str, 
                               interval: str = "1day", series_type: str = "close",
                               time_period: int = 14) -> Dict[str, Any]:
        """Get technical indicators."""
        endpoint = f"/{indicator}"
        params = {
            "symbol": symbol,
            "interval": interval,
            "series_type": series_type,
            "time_period": time_period
        }
        return self._make_request(endpoint, params)
    
    def get_sma(self, symbol: str, interval: str = "1day", 
                time_period: int = 14, series_type: str = "close") -> Dict[str, Any]:
        """Get Simple Moving Average."""
        return self.get_technical_indicators(symbol, "sma", interval, series_type, time_period)
    
    def get_ema(self, symbol: str, interval: str = "1day", 
                time_period: int = 14, series_type: str = "close") -> Dict[str, Any]:
        """Get Exponential Moving Average."""
        return self.get_technical_indicators(symbol, "ema", interval, series_type, time_period)
    
    def get_rsi(self, symbol: str, interval: str = "1day", 
                time_period: int = 14, series_type: str = "close") -> Dict[str, Any]:
        """Get Relative Strength Index."""
        return self.get_technical_indicators(symbol, "rsi", interval, series_type, time_period)
    
    def get_macd(self, symbol: str, interval: str = "1day", 
                 series_type: str = "close", fast_period: int = 12, 
                 slow_period: int = 26, signal_period: int = 9) -> Dict[str, Any]:
        """Get MACD indicator."""
        endpoint = "/macd"
        params = {
            "symbol": symbol,
            "interval": interval,
            "series_type": series_type,
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period
        }
        return self._make_request(endpoint, params)
    
    def get_bollinger_bands(self, symbol: str, interval: str = "1day", 
                           time_period: int = 20, series_type: str = "close",
                           nbdevup: int = 2, nbdevdn: int = 2) -> Dict[str, Any]:
        """Get Bollinger Bands."""
        endpoint = "/bbands"
        params = {
            "symbol": symbol,
            "interval": interval,
            "time_period": time_period,
            "series_type": series_type,
            "nbdevup": nbdevup,
            "nbdevdn": nbdevdn
        }
        return self._make_request(endpoint, params)
    
    def get_stochastic(self, symbol: str, interval: str = "1day", 
                      fastk_period: int = 14, slowk_period: int = 3,
                      slowd_period: int = 3) -> Dict[str, Any]:
        """Get Stochastic Oscillator."""
        endpoint = "/stoch"
        params = {
            "symbol": symbol,
            "interval": interval,
            "fastk_period": fastk_period,
            "slowk_period": slowk_period,
            "slowd_period": slowd_period
        }
        return self._make_request(endpoint, params)
    
    def get_williams_r(self, symbol: str, interval: str = "1day", 
                      time_period: int = 14) -> Dict[str, Any]:
        """Get Williams %R."""
        endpoint = "/willr"
        params = {
            "symbol": symbol,
            "interval": interval,
            "time_period": time_period
        }
        return self._make_request(endpoint, params)
    
    def get_commodity_channels(self, symbol: str, interval: str = "1day", 
                              time_period: int = 20) -> Dict[str, Any]:
        """Get Commodity Channel Index."""
        endpoint = "/cci"
        params = {
            "symbol": symbol,
            "interval": interval,
            "time_period": time_period
        }
        return self._make_request(endpoint, params)
    
    def get_aroon(self, symbol: str, interval: str = "1day", 
                  time_period: int = 14) -> Dict[str, Any]:
        """Get Aroon indicator."""
        endpoint = "/aroon"
        params = {
            "symbol": symbol,
            "interval": interval,
            "time_period": time_period
        }
        return self._make_request(endpoint, params)
    
    def get_adx(self, symbol: str, interval: str = "1day", 
                time_period: int = 14) -> Dict[str, Any]:
        """Get Average Directional Index."""
        endpoint = "/adx"
        params = {
            "symbol": symbol,
            "interval": interval,
            "time_period": time_period
        }
        return self._make_request(endpoint, params)
    
    def get_obv(self, symbol: str, interval: str = "1day") -> Dict[str, Any]:
        """Get On Balance Volume."""
        endpoint = "/obv"
        params = {
            "symbol": symbol,
            "interval": interval
        }
        return self._make_request(endpoint, params)
    
    def get_currency_conversion(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get currency conversion rate."""
        endpoint = "/currency_conversion"
        params = {
            "from": from_currency,
            "to": to_currency
        }
        return self._make_request(endpoint, params)
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Get exchange rate."""
        endpoint = "/exchange_rate"
        params = {
            "from": from_currency,
            "to": to_currency
        }
        return self._make_request(endpoint, params)
    
    def get_symbol_search(self, symbol: str) -> Dict[str, Any]:
        """Search for symbols."""
        endpoint = "/symbol_search"
        params = {"symbol": symbol}
        return self._make_request(endpoint, params)
    
    def get_market_status(self) -> Dict[str, Any]:
        """Get market status."""
        endpoint = "/market_status"
        return self._make_request(endpoint)
    
    def get_economic_calendar(self, country: str = None) -> Dict[str, Any]:
        """Get economic calendar."""
        endpoint = "/economic_calendar"
        params = {}
        if country:
            params["country"] = country
        return self._make_request(endpoint, params)
    
    def format_time_series_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format time series data for our system."""
        if "values" not in data:
            return []
        
        formatted_data = []
        for value in data["values"]:
            formatted_data.append({
                "timestamp": value.get("datetime"),
                "open": float(value.get("open", 0)),
                "high": float(value.get("high", 0)),
                "low": float(value.get("low", 0)),
                "close": float(value.get("close", 0)),
                "volume": int(value.get("volume", 0))
            })
        
        return formatted_data

# Global instance
twelve_data_service = TwelveDataService()
