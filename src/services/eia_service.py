"""
EIA (Energy Information Administration) service for comprehensive energy data.
Provides access to oil, natural gas, electricity, and other energy commodities data.
"""

import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

class EIAService:
    """EIA API service for energy data."""
    
    def __init__(self):
        self.base_url = settings.external_services.eia.get("base_url", "https://api.eia.gov/v2")
        self.api_key = settings.external_services.eia.get("api_key")
        self.enabled = settings.external_services.eia.get("enabled", False)
        
        if not self.enabled or not self.api_key:
            logger.warning("EIA service not configured or disabled")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to EIA API."""
        if not self.enabled or not self.api_key:
            raise Exception("EIA service not configured")
        
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        params["api_key"] = self.api_key
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"EIA API request failed: {e}")
            raise
    
    def get_petroleum_data(self, series_id: str, frequency: str = "monthly", 
                          start: str = None, end: str = None, 
                          sort: List[str] = None, offset: int = 0, 
                          length: int = 5000) -> Dict[str, Any]:
        """Get petroleum data."""
        endpoint = "/petroleum"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    def get_natural_gas_data(self, series_id: str, frequency: str = "monthly", 
                            start: str = None, end: str = None, 
                            sort: List[str] = None, offset: int = 0, 
                            length: int = 5000) -> Dict[str, Any]:
        """Get natural gas data."""
        endpoint = "/natural-gas"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    def get_electricity_data(self, series_id: str, frequency: str = "monthly", 
                            start: str = None, end: str = None, 
                            sort: List[str] = None, offset: int = 0, 
                            length: int = 5000) -> Dict[str, Any]:
        """Get electricity data."""
        endpoint = "/electricity"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    def get_coal_data(self, series_id: str, frequency: str = "monthly", 
                      start: str = None, end: str = None, 
                      sort: List[str] = None, offset: int = 0, 
                      length: int = 5000) -> Dict[str, Any]:
        """Get coal data."""
        endpoint = "/coal"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    def get_total_energy_data(self, series_id: str, frequency: str = "monthly", 
                             start: str = None, end: str = None, 
                             sort: List[str] = None, offset: int = 0, 
                             length: int = 5000) -> Dict[str, Any]:
        """Get total energy data."""
        endpoint = "/total-energy"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    def get_steo_data(self, series_id: str, frequency: str = "monthly", 
                      start: str = None, end: str = None, 
                      sort: List[str] = None, offset: int = 0, 
                      length: int = 5000) -> Dict[str, Any]:
        """Get STEO (Short-Term Energy Outlook) data."""
        endpoint = "/steo"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    def get_aeo_data(self, series_id: str, frequency: str = "monthly", 
                     start: str = None, end: str = None, 
                     sort: List[str] = None, offset: int = 0, 
                     length: int = 5000) -> Dict[str, Any]:
        """Get AEO (Annual Energy Outlook) data."""
        endpoint = "/aeo"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    def get_ieo_data(self, series_id: str, frequency: str = "monthly", 
                     start: str = None, end: str = None, 
                     sort: List[str] = None, offset: int = 0, 
                     length: int = 5000) -> Dict[str, Any]:
        """Get IEO (International Energy Outlook) data."""
        endpoint = "/ieo"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    def get_emissions_data(self, series_id: str, frequency: str = "monthly", 
                          start: str = None, end: str = None, 
                          sort: List[str] = None, offset: int = 0, 
                          length: int = 5000) -> Dict[str, Any]:
        """Get emissions data."""
        endpoint = "/emissions"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    def get_state_energy_data(self, series_id: str, frequency: str = "monthly", 
                             start: str = None, end: str = None, 
                             sort: List[str] = None, offset: int = 0, 
                             length: int = 5000) -> Dict[str, Any]:
        """Get state energy data."""
        endpoint = "/state"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    def get_international_energy_data(self, series_id: str, frequency: str = "monthly", 
                                     start: str = None, end: str = None, 
                                     sort: List[str] = None, offset: int = 0, 
                                     length: int = 5000) -> Dict[str, Any]:
        """Get international energy data."""
        endpoint = "/international"
        params = {
            "frequency": frequency,
            "data[]": series_id,
            "offset": offset,
            "length": length
        }
        
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if sort:
            params["sort[0][column]"] = sort[0]
            params["sort[0][direction]"] = sort[1] if len(sort) > 1 else "desc"
        
        return self._make_request(endpoint, params)
    
    # Common energy series
    def get_crude_oil_prices(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get crude oil prices (WTI and Brent)."""
        series_ids = ["PET.RWTC.D", "PET.RBRTE.D"]  # WTI and Brent
        return self.get_petroleum_data(series_ids, "daily", start, end)
    
    def get_gasoline_prices(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get gasoline prices."""
        series_ids = ["PET.EMM_EPMRU_PTE_NUS_DPG.D", "PET.EMM_EPMRU_PTE_NUS_DPG.W"]
        return self.get_petroleum_data(series_ids, "daily", start, end)
    
    def get_diesel_prices(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get diesel fuel prices."""
        series_ids = ["PET.EMM_EPD2D_PTE_NUS_DPG.D", "PET.EMM_EPD2D_PTE_NUS_DPG.W"]
        return self.get_petroleum_data(series_ids, "daily", start, end)
    
    def get_natural_gas_prices(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get natural gas prices."""
        series_ids = ["NG.RNGWHHD.D", "NG.RNGWHHD.W"]
        return self.get_natural_gas_data(series_ids, "daily", start, end)
    
    def get_electricity_prices(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get electricity prices."""
        series_ids = ["ELEC.PRICE.US-ALL.M", "ELEC.PRICE.US-ALL.A"]
        return self.get_electricity_data(series_ids, "monthly", start, end)
    
    def get_crude_oil_production(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get crude oil production."""
        series_ids = ["PET.MCRFPUS2.M", "PET.MCRFPUS2.A"]
        return self.get_petroleum_data(series_ids, "monthly", start, end)
    
    def get_natural_gas_production(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get natural gas production."""
        series_ids = ["NG.MNGFPUS2.M", "NG.MNGFPUS2.A"]
        return self.get_natural_gas_data(series_ids, "monthly", start, end)
    
    def get_electricity_generation(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get electricity generation."""
        series_ids = ["ELEC.GEN.ALL-US-99.M", "ELEC.GEN.ALL-US-99.A"]
        return self.get_electricity_data(series_ids, "monthly", start, end)
    
    def get_crude_oil_imports(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get crude oil imports."""
        series_ids = ["PET.MCRIMUS2.M", "PET.MCRIMUS2.A"]
        return self.get_petroleum_data(series_ids, "monthly", start, end)
    
    def get_crude_oil_exports(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get crude oil exports."""
        series_ids = ["PET.MCREXUS2.M", "PET.MCREXUS2.A"]
        return self.get_petroleum_data(series_ids, "monthly", start, end)
    
    def get_gasoline_consumption(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get gasoline consumption."""
        series_ids = ["PET.MGFUPUS2.M", "PET.MGFUPUS2.A"]
        return self.get_petroleum_data(series_ids, "monthly", start, end)
    
    def get_diesel_consumption(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get diesel fuel consumption."""
        series_ids = ["PET.MDFUPUS2.M", "PET.MDFUPUS2.A"]
        return self.get_petroleum_data(series_ids, "monthly", start, end)
    
    def get_natural_gas_consumption(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get natural gas consumption."""
        series_ids = ["NG.MNGFPUS2.M", "NG.MNGFPUS2.A"]
        return self.get_natural_gas_data(series_ids, "monthly", start, end)
    
    def get_electricity_consumption(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get electricity consumption."""
        series_ids = ["ELEC.CONS_TOT.US-99.M", "ELEC.CONS_TOT.US-99.A"]
        return self.get_electricity_data(series_ids, "monthly", start, end)
    
    def get_coal_production(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get coal production."""
        series_ids = ["COAL.PROD_TOT.US-1.M", "COAL.PROD_TOT.US-1.A"]
        return self.get_coal_data(series_ids, "monthly", start, end)
    
    def get_coal_consumption(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get coal consumption."""
        series_ids = ["COAL.CONS_TOT.US-1.M", "COAL.CONS_TOT.US-1.A"]
        return self.get_coal_data(series_ids, "monthly", start, end)
    
    def get_total_energy_consumption(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get total energy consumption."""
        series_ids = ["TOTAL.TETCBUS.M", "TOTAL.TETCBUS.A"]
        return self.get_total_energy_data(series_ids, "monthly", start, end)
    
    def get_total_energy_production(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get total energy production."""
        series_ids = ["TOTAL.TEPRBUS.M", "TOTAL.TEPRBUS.A"]
        return self.get_total_energy_data(series_ids, "monthly", start, end)
    
    def get_energy_imports(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get energy imports."""
        series_ids = ["TOTAL.TEIMBUS.M", "TOTAL.TEIMBUS.A"]
        return self.get_total_energy_data(series_ids, "monthly", start, end)
    
    def get_energy_exports(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get energy exports."""
        series_ids = ["TOTAL.TEEXBUS.M", "TOTAL.TEEXBUS.A"]
        return self.get_total_energy_data(series_ids, "monthly", start, end)
    
    def get_emissions_co2(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get CO2 emissions."""
        series_ids = ["EMISS.CO2-TOTV-EC-TO-US.M", "EMISS.CO2-TOTV-EC-TO-US.A"]
        return self.get_emissions_data(series_ids, "monthly", start, end)
    
    def get_emissions_methane(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get methane emissions."""
        series_ids = ["EMISS.CH4-TOTV-EC-TO-US.M", "EMISS.CH4-TOTV-EC-TO-US.A"]
        return self.get_emissions_data(series_ids, "monthly", start, end)
    
    def get_emissions_nitrous_oxide(self, start: str = None, end: str = None) -> Dict[str, Any]:
        """Get nitrous oxide emissions."""
        series_ids = ["EMISS.N2O-TOTV-EC-TO-US.M", "EMISS.N2O-TOTV-EC-TO-US.A"]
        return self.get_emissions_data(series_ids, "monthly", start, end)
    
    def format_energy_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format energy data for our system."""
        if "response" not in data or "data" not in data["response"]:
            return []
        
        formatted_data = []
        for item in data["response"]["data"]:
            formatted_data.append({
                "period": item.get("period"),
                "value": item.get("value"),
                "units": item.get("units"),
                "series_id": item.get("series_id"),
                "series_name": item.get("series_name"),
                "frequency": item.get("frequency"),
                "updated": item.get("updated")
            })
        
        return formatted_data

# Global instance
eia_service = EIAService()
