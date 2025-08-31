"""
FRED (Federal Reserve Economic Data) service for economic indicators.
Provides access to interest rates, GDP, employment, inflation, and other economic data.
"""

import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

class FredService:
    """FRED API service for economic data."""
    
    def __init__(self):
        self.base_url = settings.external_services.fred.get("base_url", "https://api.stlouisfed.org/fred")
        self.api_key = settings.external_services.fred.get("api_key")
        self.enabled = settings.external_services.fred.get("enabled", False)
        
        if not self.enabled or not self.api_key:
            logger.warning("FRED service not configured or disabled")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to FRED API."""
        if not self.enabled or not self.api_key:
            raise Exception("FRED service not configured")
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["api_key"] = self.api_key
        params["file_type"] = "json"
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"FRED API request failed: {e}")
            raise
    
    def get_series(self, series_id: str, observation_start: str = None, 
                   observation_end: str = None, frequency: str = None, 
                   aggregation_method: str = "avg") -> Dict[str, Any]:
        """Get economic data series."""
        endpoint = "/series/observations"
        params = {
            "series_id": series_id,
            "aggregation_method": aggregation_method
        }
        
        if observation_start:
            params["observation_start"] = observation_start
        if observation_end:
            params["observation_end"] = observation_end
        if frequency:
            params["frequency"] = frequency
        
        return self._make_request(endpoint, params)
    
    def get_series_info(self, series_id: str) -> Dict[str, Any]:
        """Get information about a series."""
        endpoint = "/series"
        params = {"series_id": series_id}
        return self._make_request(endpoint, params)
    
    def search_series(self, search_text: str, limit: int = 1000) -> Dict[str, Any]:
        """Search for economic series."""
        endpoint = "/series/search"
        params = {
            "search_text": search_text,
            "limit": limit
        }
        return self._make_request(endpoint, params)
    
    def get_category_series(self, category_id: int, limit: int = 1000) -> Dict[str, Any]:
        """Get series in a category."""
        endpoint = "/category/series"
        params = {
            "category_id": category_id,
            "limit": limit
        }
        return self._make_request(endpoint, params)
    
    def get_categories(self, parent_id: int = None) -> Dict[str, Any]:
        """Get FRED categories."""
        endpoint = "/category"
        params = {}
        if parent_id:
            params["parent_id"] = parent_id
        return self._make_request(endpoint, params)
    
    def get_releases(self, limit: int = 1000) -> Dict[str, Any]:
        """Get FRED releases."""
        endpoint = "/releases"
        params = {"limit": limit}
        return self._make_request(endpoint, params)
    
    def get_release_series(self, release_id: int, limit: int = 1000) -> Dict[str, Any]:
        """Get series in a release."""
        endpoint = "/release/series"
        params = {
            "release_id": release_id,
            "limit": limit
        }
        return self._make_request(endpoint, params)
    
    def get_source_series(self, source_id: int, limit: int = 1000) -> Dict[str, Any]:
        """Get series from a source."""
        endpoint = "/source/series"
        params = {
            "source_id": source_id,
            "limit": limit
        }
        return self._make_request(endpoint, params)
    
    def get_sources(self, limit: int = 1000) -> Dict[str, Any]:
        """Get FRED sources."""
        endpoint = "/sources"
        params = {"limit": limit}
        return self._make_request(endpoint, params)
    
    def get_tags(self, series_search_text: str = None, tag_names: str = None, 
                 tag_group_id: str = None, limit: int = 1000) -> Dict[str, Any]:
        """Get FRED tags."""
        endpoint = "/tags"
        params = {"limit": limit}
        
        if series_search_text:
            params["series_search_text"] = series_search_text
        if tag_names:
            params["tag_names"] = tag_names
        if tag_group_id:
            params["tag_group_id"] = tag_group_id
        
        return self._make_request(endpoint, params)
    
    def get_related_tags(self, series_search_text: str, tag_names: str, 
                        limit: int = 1000) -> Dict[str, Any]:
        """Get related tags."""
        endpoint = "/related_tags"
        params = {
            "series_search_text": series_search_text,
            "tag_names": tag_names,
            "limit": limit
        }
        return self._make_request(endpoint, params)
    
    def get_series_tags(self, series_search_text: str, limit: int = 1000) -> Dict[str, Any]:
        """Get tags for a series."""
        endpoint = "/series/tags"
        params = {
            "series_search_text": series_search_text,
            "limit": limit
        }
        return self._make_request(endpoint, params)
    
    # Common economic indicators
    def get_federal_funds_rate(self, observation_start: str = None, 
                              observation_end: str = None) -> Dict[str, Any]:
        """Get Federal Funds Rate (FEDFUNDS)."""
        return self.get_series("FEDFUNDS", observation_start, observation_end)
    
    def get_gdp(self, observation_start: str = None, 
                observation_end: str = None) -> Dict[str, Any]:
        """Get Gross Domestic Product (GDP)."""
        return self.get_series("GDP", observation_start, observation_end)
    
    def get_unemployment_rate(self, observation_start: str = None, 
                             observation_end: str = None) -> Dict[str, Any]:
        """Get Unemployment Rate (UNRATE)."""
        return self.get_series("UNRATE", observation_start, observation_end)
    
    def get_cpi(self, observation_start: str = None, 
                observation_end: str = None) -> Dict[str, Any]:
        """Get Consumer Price Index (CPIAUCSL)."""
        return self.get_series("CPIAUCSL", observation_start, observation_end)
    
    def get_core_cpi(self, observation_start: str = None, 
                     observation_end: str = None) -> Dict[str, Any]:
        """Get Core Consumer Price Index (CPILFESL)."""
        return self.get_series("CPILFESL", observation_start, observation_end)
    
    def get_pce(self, observation_start: str = None, 
                observation_end: str = None) -> Dict[str, Any]:
        """Get Personal Consumption Expenditures (PCEPI)."""
        return self.get_series("PCEPI", observation_start, observation_end)
    
    def get_core_pce(self, observation_start: str = None, 
                     observation_end: str = None) -> Dict[str, Any]:
        """Get Core Personal Consumption Expenditures (PCEPILFE)."""
        return self.get_series("PCEPILFE", observation_start, observation_end)
    
    def get_10_year_treasury_rate(self, observation_start: str = None, 
                                 observation_end: str = None) -> Dict[str, Any]:
        """Get 10-Year Treasury Constant Maturity Rate (GS10)."""
        return self.get_series("GS10", observation_start, observation_end)
    
    def get_2_year_treasury_rate(self, observation_start: str = None, 
                                observation_end: str = None) -> Dict[str, Any]:
        """Get 2-Year Treasury Constant Maturity Rate (GS2)."""
        return self.get_series("GS2", observation_start, observation_end)
    
    def get_30_year_treasury_rate(self, observation_start: str = None, 
                                 observation_end: str = None) -> Dict[str, Any]:
        """Get 30-Year Treasury Constant Maturity Rate (GS30)."""
        return self.get_series("GS30", observation_start, observation_end)
    
    def get_3_month_treasury_rate(self, observation_start: str = None, 
                                 observation_end: str = None) -> Dict[str, Any]:
        """Get 3-Month Treasury Bill Rate (TB3MS)."""
        return self.get_series("TB3MS", observation_start, observation_end)
    
    def get_6_month_treasury_rate(self, observation_start: str = None, 
                                 observation_end: str = None) -> Dict[str, Any]:
        """Get 6-Month Treasury Bill Rate (TB6MS)."""
        return self.get_series("TB6MS", observation_start, observation_end)
    
    def get_1_year_treasury_rate(self, observation_start: str = None, 
                                observation_end: str = None) -> Dict[str, Any]:
        """Get 1-Year Treasury Bill Rate (TB1YR)."""
        return self.get_series("TB1YR", observation_start, observation_end)
    
    def get_5_year_treasury_rate(self, observation_start: str = None, 
                                observation_end: str = None) -> Dict[str, Any]:
        """Get 5-Year Treasury Constant Maturity Rate (GS5)."""
        return self.get_series("GS5", observation_start, observation_end)
    
    def get_20_year_treasury_rate(self, observation_start: str = None, 
                                 observation_end: str = None) -> Dict[str, Any]:
        """Get 20-Year Treasury Constant Maturity Rate (GS20)."""
        return self.get_series("GS20", observation_start, observation_end)
    
    def get_effective_federal_funds_rate(self, observation_start: str = None, 
                                        observation_end: str = None) -> Dict[str, Any]:
        """Get Effective Federal Funds Rate (DFF)."""
        return self.get_series("DFF", observation_start, observation_end)
    
    def get_industrial_production(self, observation_start: str = None, 
                                 observation_end: str = None) -> Dict[str, Any]:
        """Get Industrial Production Index (INDPRO)."""
        return self.get_series("INDPRO", observation_start, observation_end)
    
    def get_capacity_utilization(self, observation_start: str = None, 
                                observation_end: str = None) -> Dict[str, Any]:
        """Get Capacity Utilization (TCU)."""
        return self.get_series("TCU", observation_start, observation_end)
    
    def get_retail_sales(self, observation_start: str = None, 
                        observation_end: str = None) -> Dict[str, Any]:
        """Get Retail Sales (RSAFS)."""
        return self.get_series("RSAFS", observation_start, observation_end)
    
    def get_consumer_confidence(self, observation_start: str = None, 
                               observation_end: str = None) -> Dict[str, Any]:
        """Get Consumer Confidence Index (UMCSENT)."""
        return self.get_series("UMCSENT", observation_start, observation_end)
    
    def get_manufacturing_pmi(self, observation_start: str = None, 
                             observation_end: str = None) -> Dict[str, Any]:
        """Get Manufacturing PMI (NAPM)."""
        return self.get_series("NAPM", observation_start, observation_end)
    
    def get_services_pmi(self, observation_start: str = None, 
                        observation_end: str = None) -> Dict[str, Any]:
        """Get Services PMI (NAPMNUI)."""
        return self.get_series("NAPMNUI", observation_start, observation_end)
    
    def get_housing_starts(self, observation_start: str = None, 
                          observation_end: str = None) -> Dict[str, Any]:
        """Get Housing Starts (HOUST)."""
        return self.get_series("HOUST", observation_start, observation_end)
    
    def get_building_permits(self, observation_start: str = None, 
                            observation_end: str = None) -> Dict[str, Any]:
        """Get Building Permits (PERMIT)."""
        return self.get_series("PERMIT", observation_start, observation_end)
    
    def get_existing_home_sales(self, observation_start: str = None, 
                               observation_end: str = None) -> Dict[str, Any]:
        """Get Existing Home Sales (EXHOSLUSM495S)."""
        return self.get_series("EXHOSLUSM495S", observation_start, observation_end)
    
    def get_new_home_sales(self, observation_start: str = None, 
                          observation_end: str = None) -> Dict[str, Any]:
        """Get New Home Sales (HSN1F)."""
        return self.get_series("HSN1F", observation_start, observation_end)
    
    def get_durable_goods_orders(self, observation_start: str = None, 
                                observation_end: str = None) -> Dict[str, Any]:
        """Get Durable Goods Orders (DGORDER)."""
        return self.get_series("DGORDER", observation_start, observation_end)
    
    def get_trade_balance(self, observation_start: str = None, 
                         observation_end: str = None) -> Dict[str, Any]:
        """Get Trade Balance (BOPGSTB)."""
        return self.get_series("BOPGSTB", observation_start, observation_end)
    
    def get_budget_deficit(self, observation_start: str = None, 
                          observation_end: str = None) -> Dict[str, Any]:
        """Get Federal Budget Deficit (FYFSD)."""
        return self.get_series("FYFSD", observation_start, observation_end)
    
    def get_money_supply_m1(self, observation_start: str = None, 
                           observation_end: str = None) -> Dict[str, Any]:
        """Get Money Supply M1 (M1SL)."""
        return self.get_series("M1SL", observation_start, observation_end)
    
    def get_money_supply_m2(self, observation_start: str = None, 
                           observation_end: str = None) -> Dict[str, Any]:
        """Get Money Supply M2 (M2SL)."""
        return self.get_series("M2SL", observation_start, observation_end)
    
    def get_money_supply_m3(self, observation_start: str = None, 
                           observation_end: str = None) -> Dict[str, Any]:
        """Get Money Supply M3 (MABMM301USM189S)."""
        return self.get_series("MABMM301USM189S", observation_start, observation_end)
    
    def get_velocity_of_money(self, observation_start: str = None, 
                             observation_end: str = None) -> Dict[str, Any]:
        """Get Velocity of M2 Money Stock (M2V)."""
        return self.get_series("M2V", observation_start, observation_end)
    
    def get_balance_of_payments(self, observation_start: str = None, 
                               observation_end: str = None) -> Dict[str, Any]:
        """Get Balance of Payments (BOPGSTB)."""
        return self.get_series("BOPGSTB", observation_start, observation_end)
    
    def get_current_account_balance(self, observation_start: str = None, 
                                   observation_end: str = None) -> Dict[str, Any]:
        """Get Current Account Balance (BOPBCA)."""
        return self.get_series("BOPBCA", observation_start, observation_end)
    
    def get_capital_account_balance(self, observation_start: str = None, 
                                   observation_end: str = None) -> Dict[str, Any]:
        """Get Capital Account Balance (BOPBCA)."""
        return self.get_series("BOPBCA", observation_start, observation_end)
    
    def get_foreign_exchange_reserves(self, observation_start: str = None, 
                                     observation_end: str = None) -> Dict[str, Any]:
        """Get Foreign Exchange Reserves (TRESEGUSM052N)."""
        return self.get_series("TRESEGUSM052N", observation_start, observation_end)
    
    def get_gold_reserves(self, observation_start: str = None, 
                         observation_end: str = None) -> Dict[str, Any]:
        """Get Gold Reserves (GOLDPMGBD228NLBM)."""
        return self.get_series("GOLDPMGBD228NLBM", observation_start, observation_end)
    
    def get_oil_prices(self, observation_start: str = None, 
                      observation_end: str = None) -> Dict[str, Any]:
        """Get Crude Oil Prices (DCOILWTICO)."""
        return self.get_series("DCOILWTICO", observation_start, observation_end)
    
    def get_gas_prices(self, observation_start: str = None, 
                      observation_end: str = None) -> Dict[str, Any]:
        """Get Gasoline Prices (GASREGW)."""
        return self.get_series("GASREGW", observation_start, observation_end)
    
    def get_natural_gas_prices(self, observation_start: str = None, 
                              observation_end: str = None) -> Dict[str, Any]:
        """Get Natural Gas Prices (DNGASWUSDM)."""
        return self.get_series("DNGASWUSDM", observation_start, observation_end)
    
    def get_copper_prices(self, observation_start: str = None, 
                         observation_end: str = None) -> Dict[str, Any]:
        """Get Copper Prices (PCOPPUSDM)."""
        return self.get_series("PCOPPUSDM", observation_start, observation_end)
    
    def get_gold_prices(self, observation_start: str = None, 
                       observation_end: str = None) -> Dict[str, Any]:
        """Get Gold Prices (GOLDPMGBD228NLBM)."""
        return self.get_series("GOLDPMGBD228NLBM", observation_start, observation_end)
    
    def get_silver_prices(self, observation_start: str = None, 
                         observation_end: str = None) -> Dict[str, Any]:
        """Get Silver Prices (PSILVERUSDM)."""
        return self.get_series("PSILVERUSDM", observation_start, observation_end)
    
    def get_platinum_prices(self, observation_start: str = None, 
                           observation_end: str = None) -> Dict[str, Any]:
        """Get Platinum Prices (PPLATINUSDM)."""
        return self.get_series("PPLATINUSDM", observation_start, observation_end)
    
    def get_palladium_prices(self, observation_start: str = None, 
                            observation_end: str = None) -> Dict[str, Any]:
        """Get Palladium Prices (PPALLUSDM)."""
        return self.get_series("PPALLUSDM", observation_start, observation_end)
    
    def get_rhodium_prices(self, observation_start: str = None, 
                          observation_end: str = None) -> Dict[str, Any]:
        """Get Rhodium Prices (PRHODUSDM)."""
        return self.get_series("PRHODUSDM", observation_start, observation_end)
    
    def get_iridium_prices(self, observation_start: str = None, 
                          observation_end: str = None) -> Dict[str, Any]:
        """Get Iridium Prices (PIRIDUSDM)."""
        return self.get_series("PIRIDUSDM", observation_start, observation_end)
    
    def get_ruthenium_prices(self, observation_start: str = None, 
                            observation_end: str = None) -> Dict[str, Any]:
        """Get Ruthenium Prices (PRUTHUSDM)."""
        return self.get_series("PRUTHUSDM", observation_start, observation_end)
    
    def get_osmium_prices(self, observation_start: str = None, 
                         observation_end: str = None) -> Dict[str, Any]:
        """Get Osmium Prices (POSMIUSDM)."""
        return self.get_series("POSMIUSDM", observation_start, observation_end)
    
    def get_rhenium_prices(self, observation_start: str = None, 
                          observation_end: str = None) -> Dict[str, Any]:
        """Get Rhenium Prices (PRHENUSDM)."""
        return self.get_series("PRHENUSDM", observation_start, observation_end)
    
    def format_series_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format series data for our system."""
        if "observations" not in data:
            return []
        
        formatted_data = []
        for obs in data["observations"]:
            formatted_data.append({
                "date": obs.get("date"),
                "value": float(obs.get("value", 0)) if obs.get("value") != "." else 0,
                "realtime_start": obs.get("realtime_start"),
                "realtime_end": obs.get("realtime_end")
            })
        
        return formatted_data

# Global instance
fred_service = FredService()
