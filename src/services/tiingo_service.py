"""
Tiingo service for comprehensive financial data.
Provides access to end-of-day stock prices, cryptocurrency data, forex data, and more.
"""

import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

class TiingoService:
    """Tiingo API service for financial data."""
    
    def __init__(self):
        self.base_url = settings.external_services.tiingo.get("base_url", "https://api.tiingo.com")
        self.api_key = settings.external_services.tiingo.get("api_key")
        self.enabled = settings.external_services.tiingo.get("enabled", False)
        
        if not self.enabled or not self.api_key:
            logger.warning("Tiingo service not configured or disabled")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to Tiingo API."""
        if not self.enabled or not self.api_key:
            raise Exception("Tiingo service not configured")
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.api_key}"
        }
        params = params or {}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Tiingo API request failed: {e}")
            raise
    
    def get_stock_eod_prices(self, ticker: str, start_date: str = None, 
                            end_date: str = None, resample_freq: str = None) -> Dict[str, Any]:
        """Get end-of-day stock prices."""
        endpoint = f"/tiingo/daily/{ticker}/prices"
        params = {}
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if resample_freq:
            params["resampleFreq"] = resample_freq
        
        return self._make_request(endpoint, params)
    
    def get_stock_metadata(self, ticker: str) -> Dict[str, Any]:
        """Get stock metadata."""
        endpoint = f"/tiingo/daily/{ticker}"
        return self._make_request(endpoint)
    
    def get_stock_news(self, ticker: str = None, start_date: str = None, 
                      end_date: str = None, limit: int = 100) -> Dict[str, Any]:
        """Get stock news."""
        endpoint = "/news"
        params = {"limit": limit}
        
        if ticker:
            params["tickers"] = ticker
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        
        return self._make_request(endpoint, params)
    
    def get_crypto_prices(self, ticker: str, start_date: str = None, 
                         end_date: str = None, resample_freq: str = None) -> Dict[str, Any]:
        """Get cryptocurrency prices."""
        endpoint = f"/tiingo/crypto/prices"
        params = {"tickers": ticker}
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if resample_freq:
            params["resampleFreq"] = resample_freq
        
        return self._make_request(endpoint, params)
    
    def get_crypto_metadata(self, ticker: str) -> Dict[str, Any]:
        """Get cryptocurrency metadata."""
        endpoint = f"/tiingo/crypto/{ticker}"
        return self._make_request(endpoint)
    
    def get_crypto_top_of_book(self, ticker: str) -> Dict[str, Any]:
        """Get cryptocurrency top of book."""
        endpoint = f"/tiingo/crypto/top/{ticker}"
        return self._make_request(endpoint)
    
    def get_forex_prices(self, base_currency: str, quote_currency: str, 
                        start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get forex prices."""
        endpoint = f"/tiingo/fx/{base_currency}/{quote_currency}/prices"
        params = {}
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        
        return self._make_request(endpoint, params)
    
    def get_forex_top_of_book(self, base_currency: str, quote_currency: str) -> Dict[str, Any]:
        """Get forex top of book."""
        endpoint = f"/tiingo/fx/{base_currency}/{quote_currency}/top"
        return self._make_request(endpoint)
    
    def get_iex_prices(self, ticker: str, start_date: str = None, 
                      end_date: str = None) -> Dict[str, Any]:
        """Get IEX prices."""
        endpoint = f"/iex/{ticker}/prices"
        params = {}
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        
        return self._make_request(endpoint, params)
    
    def get_iex_metadata(self, ticker: str) -> Dict[str, Any]:
        """Get IEX metadata."""
        endpoint = f"/iex/{ticker}"
        return self._make_request(endpoint)
    
    def get_iex_top_of_book(self, ticker: str) -> Dict[str, Any]:
        """Get IEX top of book."""
        endpoint = f"/iex/{ticker}/top"
        return self._make_request(endpoint)
    
    def get_iex_quotes(self, ticker: str) -> Dict[str, Any]:
        """Get IEX quotes."""
        endpoint = f"/iex/{ticker}/quotes"
        return self._make_request(endpoint)
    
    def get_iex_trades(self, ticker: str) -> Dict[str, Any]:
        """Get IEX trades."""
        endpoint = f"/iex/{ticker}/trades"
        return self._make_request(endpoint)
    
    def get_iex_news(self, ticker: str = None, start_date: str = None, 
                    end_date: str = None, limit: int = 100) -> Dict[str, Any]:
        """Get IEX news."""
        endpoint = "/iex/news"
        params = {"limit": limit}
        
        if ticker:
            params["tickers"] = ticker
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        
        return self._make_request(endpoint, params)
    
    def get_iex_company_info(self, ticker: str) -> Dict[str, Any]:
        """Get IEX company information."""
        endpoint = f"/iex/{ticker}/company"
        return self._make_request(endpoint)
    
    def get_iex_financials(self, ticker: str) -> Dict[str, Any]:
        """Get IEX financials."""
        endpoint = f"/iex/{ticker}/financials"
        return self._make_request(endpoint)
    
    def get_iex_earnings(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings."""
        endpoint = f"/iex/{ticker}/earnings"
        return self._make_request(endpoint)
    
    def get_iex_dividends(self, ticker: str) -> Dict[str, Any]:
        """Get IEX dividends."""
        endpoint = f"/iex/{ticker}/dividends"
        return self._make_request(endpoint)
    
    def get_iex_splits(self, ticker: str) -> Dict[str, Any]:
        """Get IEX splits."""
        endpoint = f"/iex/{ticker}/splits"
        return self._make_request(endpoint)
    
    def get_iex_volume_by_venue(self, ticker: str) -> Dict[str, Any]:
        """Get IEX volume by venue."""
        endpoint = f"/iex/{ticker}/volume"
        return self._make_request(endpoint)
    
    def get_iex_short_interest(self, ticker: str) -> Dict[str, Any]:
        """Get IEX short interest."""
        endpoint = f"/iex/{ticker}/short-interest"
        return self._make_request(endpoint)
    
    def get_iex_institutional_ownership(self, ticker: str) -> Dict[str, Any]:
        """Get IEX institutional ownership."""
        endpoint = f"/iex/{ticker}/institutional-ownership"
        return self._make_request(endpoint)
    
    def get_iex_insider_transactions(self, ticker: str) -> Dict[str, Any]:
        """Get IEX insider transactions."""
        endpoint = f"/iex/{ticker}/insider-transactions"
        return self._make_request(endpoint)
    
    def get_iex_insider_roster(self, ticker: str) -> Dict[str, Any]:
        """Get IEX insider roster."""
        endpoint = f"/iex/{ticker}/insider-roster"
        return self._make_request(endpoint)
    
    def get_iex_key_stats(self, ticker: str) -> Dict[str, Any]:
        """Get IEX key stats."""
        endpoint = f"/iex/{ticker}/stats"
        return self._make_request(endpoint)
    
    def get_iex_peers(self, ticker: str) -> Dict[str, Any]:
        """Get IEX peers."""
        endpoint = f"/iex/{ticker}/peers"
        return self._make_request(endpoint)
    
    def get_iex_relevant_stocks(self, ticker: str) -> Dict[str, Any]:
        """Get IEX relevant stocks."""
        endpoint = f"/iex/{ticker}/relevant"
        return self._make_request(endpoint)
    
    def get_iex_ceo_compensation(self, ticker: str) -> Dict[str, Any]:
        """Get IEX CEO compensation."""
        endpoint = f"/iex/{ticker}/ceo-compensation"
        return self._make_request(endpoint)
    
    def get_iex_analyst_recommendations(self, ticker: str) -> Dict[str, Any]:
        """Get IEX analyst recommendations."""
        endpoint = f"/iex/{ticker}/recommendations"
        return self._make_request(endpoint)
    
    def get_iex_price_target(self, ticker: str) -> Dict[str, Any]:
        """Get IEX price target."""
        endpoint = f"/iex/{ticker}/price-target"
        return self._make_request(endpoint)
    
    def get_iex_ratings(self, ticker: str) -> Dict[str, Any]:
        """Get IEX ratings."""
        endpoint = f"/iex/{ticker}/ratings"
        return self._make_request(endpoint)
    
    def get_iex_estimates(self, ticker: str) -> Dict[str, Any]:
        """Get IEX estimates."""
        endpoint = f"/iex/{ticker}/estimates"
        return self._make_request(endpoint)
    
    def get_iex_earnings_announcements(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings announcements."""
        endpoint = f"/iex/{ticker}/earnings-announcements"
        return self._make_request(endpoint)
    
    def get_iex_earnings_estimates(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings estimates."""
        endpoint = f"/iex/{ticker}/earnings-estimates"
        return self._make_request(endpoint)
    
    def get_iex_revenue_estimates(self, ticker: str) -> Dict[str, Any]:
        """Get IEX revenue estimates."""
        endpoint = f"/iex/{ticker}/revenue-estimates"
        return self._make_request(endpoint)
    
    def get_iex_earnings_guidance(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings guidance."""
        endpoint = f"/iex/{ticker}/earnings-guidance"
        return self._make_request(endpoint)
    
    def get_iex_revenue_guidance(self, ticker: str) -> Dict[str, Any]:
        """Get IEX revenue guidance."""
        endpoint = f"/iex/{ticker}/revenue-guidance"
        return self._make_request(endpoint)
    
    def get_iex_earnings_quality_score(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings quality score."""
        endpoint = f"/iex/{ticker}/earnings-quality-score"
        return self._make_request(endpoint)
    
    def get_iex_earnings_quality_score_history(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings quality score history."""
        endpoint = f"/iex/{ticker}/earnings-quality-score-history"
        return self._make_request(endpoint)
    
    def get_iex_earnings_quality_score_components(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings quality score components."""
        endpoint = f"/iex/{ticker}/earnings-quality-score-components"
        return self._make_request(endpoint)
    
    def get_iex_earnings_quality_score_components_history(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings quality score components history."""
        endpoint = f"/iex/{ticker}/earnings-quality-score-components-history"
        return self._make_request(endpoint)
    
    def get_iex_earnings_quality_score_components_summary(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings quality score components summary."""
        endpoint = f"/iex/{ticker}/earnings-quality-score-components-summary"
        return self._make_request(endpoint)
    
    def get_iex_earnings_quality_score_components_summary_history(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings quality score components summary history."""
        endpoint = f"/iex/{ticker}/earnings-quality-score-components-summary-history"
        return self._make_request(endpoint)
    
    def get_iex_earnings_quality_score_components_summary_summary(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings quality score components summary summary."""
        endpoint = f"/iex/{ticker}/earnings-quality-score-components-summary-summary"
        return self._make_request(endpoint)
    
    def get_iex_earnings_quality_score_components_summary_summary_history(self, ticker: str) -> Dict[str, Any]:
        """Get IEX earnings quality score components summary summary history."""
        endpoint = f"/iex/{ticker}/earnings-quality-score-components-summary-summary-history"
        return self._make_request(endpoint)
    
    def format_eod_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format end-of-day data for our system."""
        formatted_data = []
        for item in data:
            formatted_data.append({
                "date": item.get("date"),
                "open": item.get("open"),
                "high": item.get("high"),
                "low": item.get("low"),
                "close": item.get("close"),
                "volume": item.get("volume"),
                "adj_open": item.get("adjOpen"),
                "adj_high": item.get("adjHigh"),
                "adj_low": item.get("adjLow"),
                "adj_close": item.get("adjClose"),
                "adj_volume": item.get("adjVolume"),
                "div_cash": item.get("divCash"),
                "split_factor": item.get("splitFactor")
            })
        return formatted_data

# Global instance
tiingo_service = TiingoService()
