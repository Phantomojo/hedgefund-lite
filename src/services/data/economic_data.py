"""
Economic Data Service
Collect economic indicators from FRED API
"""

import logging
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from config.api_keys import FRED_API_KEY

logger = logging.getLogger(__name__)

class EconomicDataService:
    """Service for collecting economic data from FRED"""
    
    def __init__(self):
        self.fred_key = FRED_API_KEY
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_economic_indicators(self) -> List[Dict[str, Any]]:
        """Get key economic indicators"""
        try:
            indicators = []
            
            # GDP Growth Rate
            gdp_data = await self._get_series_data("GDPC1", "GDP Growth Rate")
            if gdp_data:
                indicators.extend(gdp_data)
            
            # Unemployment Rate
            unrate_data = await self._get_series_data("UNRATE", "Unemployment Rate")
            if unrate_data:
                indicators.extend(unrate_data)
            
            # Inflation Rate (CPI)
            cpi_data = await self._get_series_data("CPIAUCSL", "Inflation Rate (CPI)")
            if cpi_data:
                indicators.extend(cpi_data)
            
            # Federal Funds Rate
            fed_rate_data = await self._get_series_data("FEDFUNDS", "Federal Funds Rate")
            if fed_rate_data:
                indicators.extend(fed_rate_data)
            
            # Consumer Confidence
            consumer_conf_data = await self._get_series_data("UMCSENT", "Consumer Confidence")
            if consumer_conf_data:
                indicators.extend(consumer_conf_data)
            
            # Manufacturing PMI
            pmi_data = await self._get_series_data("NAPM", "Manufacturing PMI")
            if pmi_data:
                indicators.extend(pmi_data)
            
            logger.info(f"Retrieved {len(indicators)} economic indicators")
            return indicators
            
        except Exception as e:
            logger.error(f"Failed to get economic indicators: {str(e)}")
            return []
    
    async def _get_series_data(self, series_id: str, name: str) -> List[Dict[str, Any]]:
        """Get data for a specific FRED series"""
        try:
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.fred_key,
                "file_type": "json",
                "limit": 10,
                "sort_order": "desc"
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "observations" in data and data["observations"]:
                        observations = data["observations"]
                        
                        formatted_data = []
                        for obs in observations:
                            try:
                                value = float(obs["value"]) if obs["value"] != "." else None
                                if value is not None:
                                    formatted_data.append({
                                        "series_id": series_id,
                                        "name": name,
                                        "value": value,
                                        "date": obs["date"],
                                        "timestamp": datetime.strptime(obs["date"], "%Y-%m-%d"),
                                        "category": "economic"
                                    })
                            except (ValueError, KeyError):
                                continue
                        
                        return formatted_data
                    else:
                        logger.warning(f"No observations returned for series {series_id}")
                        return []
                else:
                    logger.error(f"FRED API error for {series_id}: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get data for series {series_id}: {str(e)}")
            return []
    
    async def get_gdp_growth(self) -> Optional[Dict[str, Any]]:
        """Get latest GDP growth rate"""
        try:
            data = await self._get_series_data("GDPC1", "GDP Growth Rate")
            if data:
                return data[0]  # Latest observation
            return None
            
        except Exception as e:
            logger.error(f"Failed to get GDP growth: {str(e)}")
            return None
    
    async def get_unemployment_rate(self) -> Optional[Dict[str, Any]]:
        """Get latest unemployment rate"""
        try:
            data = await self._get_series_data("UNRATE", "Unemployment Rate")
            if data:
                return data[0]  # Latest observation
            return None
            
        except Exception as e:
            logger.error(f"Failed to get unemployment rate: {str(e)}")
            return None
    
    async def get_inflation_rate(self) -> Optional[Dict[str, Any]]:
        """Get latest inflation rate"""
        try:
            data = await self._get_series_data("CPIAUCSL", "Inflation Rate (CPI)")
            if data:
                return data[0]  # Latest observation
            return None
            
        except Exception as e:
            logger.error(f"Failed to get inflation rate: {str(e)}")
            return None
    
    async def get_interest_rate(self) -> Optional[Dict[str, Any]]:
        """Get latest federal funds rate"""
        try:
            data = await self._get_series_data("FEDFUNDS", "Federal Funds Rate")
            if data:
                return data[0]  # Latest observation
            return None
            
        except Exception as e:
            logger.error(f"Failed to get interest rate: {str(e)}")
            return None
    
    async def get_consumer_confidence(self) -> Optional[Dict[str, Any]]:
        """Get latest consumer confidence index"""
        try:
            data = await self._get_series_data("UMCSENT", "Consumer Confidence")
            if data:
                return data[0]  # Latest observation
            return None
            
        except Exception as e:
            logger.error(f"Failed to get consumer confidence: {str(e)}")
            return None
    
    async def get_manufacturing_pmi(self) -> Optional[Dict[str, Any]]:
        """Get latest manufacturing PMI"""
        try:
            data = await self._get_series_data("NAPM", "Manufacturing PMI")
            if data:
                return data[0]  # Latest observation
            return None
            
        except Exception as e:
            logger.error(f"Failed to get manufacturing PMI: {str(e)}")
            return None
