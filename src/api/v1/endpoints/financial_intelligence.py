"""
Financial Intelligence Endpoints
Professional insights from bankers, investors, and market professionals
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.core.security import get_current_user
from src.services.financial_intelligence_engine import financial_intelligence_engine

router = APIRouter()

# Request Models
class ProfessionalInsightsRequest(BaseModel):
    asset_class: str
    symbol: str
    include_market_regime: bool = True
    include_economic_cycle: bool = True


class MarketRegimeRequest(BaseModel):
    include_volatility: bool = True
    include_correlation: bool = True
    include_liquidity: bool = True


# Test endpoints (no authentication required)
@router.get("/test")
async def test_financial_intelligence():
    """Test financial intelligence endpoints"""
    return {"message": "Financial Intelligence endpoints working", "status": "success"}


@router.get("/knowledge-base-test")
async def get_knowledge_base_test():
    """Get financial intelligence knowledge base without authentication"""
    try:
        return {
            "market_psychology": financial_intelligence_engine.market_psychology,
            "banker_knowledge": financial_intelligence_engine.banker_knowledge,
            "investor_wisdom": financial_intelligence_engine.investor_wisdom,
            "market_expertise": financial_intelligence_engine.market_expertise,
            "economic_intelligence": financial_intelligence_engine.economic_intelligence,
            "sector_analysis": financial_intelligence_engine.sector_analysis,
            "currency_commodity_intelligence": financial_intelligence_engine.currency_commodity_intelligence
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/market-regime-test")
async def get_market_regime_test():
    """Get current market regime analysis without authentication"""
    try:
        # Placeholder market data
        market_data = {"prices": [], "volumes": [], "indicators": {}}
        
        market_regime = await financial_intelligence_engine.analyze_market_regime(market_data)
        
        return {
            "current_regime": {
                "regime": market_regime.regime,
                "volatility": market_regime.volatility,
                "correlation": market_regime.correlation,
                "liquidity": market_regime.liquidity,
                "trend_strength": market_regime.trend_strength,
                "duration_days": market_regime.duration_days,
                "confidence": market_regime.confidence
            },
            "regime_explanation": {
                "bull": "Strong upward trend with high confidence",
                "bear": "Strong downward trend with high confidence",
                "sideways": "No clear trend, range-bound trading",
                "crisis": "High volatility, flight to quality",
                "recovery": "Rebounding from crisis, improving conditions",
                "trending": "Moderate trend with some uncertainty",
                "choppy": "High volatility, no clear direction",
                "transitional": "Changing from one regime to another"
            }
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/economic-cycle-test")
async def get_economic_cycle_test():
    """Get current economic cycle analysis without authentication"""
    try:
        # Placeholder economic data
        economic_data = {
            "gdp_growth": 2.5,
            "inflation": 3.2,
            "unemployment": 3.8,
            "interest_rates": 5.5,
            "consumer_confidence": 65.0,
            "business_confidence": 70.0
        }
        
        economic_cycle = await financial_intelligence_engine.analyze_economic_cycle(economic_data)
        
        return {
            "current_cycle": {
                "phase": economic_cycle.phase,
                "gdp_growth": economic_cycle.gdp_growth,
                "inflation": economic_cycle.inflation,
                "unemployment": economic_cycle.unemployment,
                "interest_rates": economic_cycle.interest_rates,
                "consumer_confidence": economic_cycle.consumer_confidence,
                "business_confidence": economic_cycle.business_confidence
            },
            "cycle_explanation": {
                "expansion": "Strong growth, low unemployment, rising confidence",
                "peak": "Growth slowing, inflation rising, confidence plateauing",
                "contraction": "Negative growth, rising unemployment, falling confidence",
                "trough": "Bottom of cycle, preparing for recovery",
                "transitional": "Unclear phase, mixed signals"
            }
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/professional-insights-test")
async def get_professional_insights_test(request: ProfessionalInsightsRequest):
    """Get professional insights without authentication"""
    try:
        # Placeholder market data
        market_data = {
            "prices": [],
            "volumes": [],
            "indicators": {},
            "symbol": request.symbol
        }
        
        insights = await financial_intelligence_engine.generate_professional_insights(
            request.asset_class, request.symbol, market_data
        )
        
        return insights
    except Exception as e:
        return {"error": str(e)}


@router.get("/central-bank-policies-test")
async def get_central_bank_policies_test():
    """Get central bank policy information without authentication"""
    try:
        return {
            "federal_reserve": {
                "mandate": "Dual mandate: price stability and maximum employment",
                "policy_tools": [
                    "Federal Funds Rate",
                    "Open Market Operations",
                    "Quantitative Easing",
                    "Forward Guidance"
                ],
                "current_focus": "Inflation control and employment stability"
            },
            "european_central_bank": {
                "mandate": "Price stability (inflation target ~2%)",
                "policy_tools": [
                    "Refinancing Rate",
                    "Deposit Rate",
                    "Asset Purchase Program",
                    "Long-Term Refinancing Operations (LTRO)"
                ],
                "current_focus": "Inflation targeting and economic recovery"
            },
            "bank_of_japan": {
                "mandate": "Price stability and economic growth",
                "policy_tools": [
                    "Policy Rate",
                    "Yield Curve Control",
                    "ETF Purchases",
                    "Quantitative and Qualitative Easing (QQE)"
                ],
                "current_focus": "Deflation prevention and growth stimulation"
            }
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/sector-rotation-test")
async def get_sector_rotation_test():
    """Get sector rotation analysis without authentication"""
    try:
        return {
            "sector_rotation": financial_intelligence_engine.sector_analysis["sector_rotation"],
            "rotation_explanation": {
                "early_cycle": "Consumer discretionary, financials, technology lead recovery",
                "mid_cycle": "Industrials, materials, energy benefit from growth",
                "late_cycle": "Consumer staples, healthcare, utilities provide stability",
                "recession": "Defensive sectors and government bonds outperform"
            },
            "current_cycle_position": "mid_cycle",
            "recommended_sectors": ["industrials", "materials", "energy"],
            "avoid_sectors": ["utilities", "consumer_staples"]
        }
    except Exception as e:
        return {"error": str(e)}


# Authenticated endpoints
@router.get("/knowledge-base")
async def get_knowledge_base(
    current_user: str = Depends(get_current_user)
):
    """Get financial intelligence knowledge base (with authentication)"""
    try:
        return {
            "market_psychology": financial_intelligence_engine.market_psychology,
            "banker_knowledge": financial_intelligence_engine.banker_knowledge,
            "investor_wisdom": financial_intelligence_engine.investor_wisdom,
            "market_expertise": financial_intelligence_engine.market_expertise,
            "economic_intelligence": financial_intelligence_engine.economic_intelligence,
            "sector_analysis": financial_intelligence_engine.sector_analysis,
            "currency_commodity_intelligence": financial_intelligence_engine.currency_commodity_intelligence
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge base: {str(e)}"
        )


@router.get("/market-regime")
async def get_market_regime(
    request: MarketRegimeRequest = None,
    current_user: str = Depends(get_current_user)
):
    """Get current market regime analysis (with authentication)"""
    try:
        # Placeholder market data
        market_data = {"prices": [], "volumes": [], "indicators": {}}
        
        market_regime = await financial_intelligence_engine.analyze_market_regime(market_data)
        
        return {
            "current_regime": {
                "regime": market_regime.regime,
                "volatility": market_regime.volatility,
                "correlation": market_regime.correlation,
                "liquidity": market_regime.liquidity,
                "trend_strength": market_regime.trend_strength,
                "duration_days": market_regime.duration_days,
                "confidence": market_regime.confidence
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze market regime: {str(e)}"
        )


@router.get("/economic-cycle")
async def get_economic_cycle(
    current_user: str = Depends(get_current_user)
):
    """Get current economic cycle analysis (with authentication)"""
    try:
        # Placeholder economic data
        economic_data = {
            "gdp_growth": 2.5,
            "inflation": 3.2,
            "unemployment": 3.8,
            "interest_rates": 5.5,
            "consumer_confidence": 65.0,
            "business_confidence": 70.0
        }
        
        economic_cycle = await financial_intelligence_engine.analyze_economic_cycle(economic_data)
        
        return {
            "current_cycle": {
                "phase": economic_cycle.phase,
                "gdp_growth": economic_cycle.gdp_growth,
                "inflation": economic_cycle.inflation,
                "unemployment": economic_cycle.unemployment,
                "interest_rates": economic_cycle.interest_rates,
                "consumer_confidence": economic_cycle.consumer_confidence,
                "business_confidence": economic_cycle.business_confidence
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze economic cycle: {str(e)}"
        )


@router.post("/professional-insights")
async def get_professional_insights(
    request: ProfessionalInsightsRequest,
    current_user: str = Depends(get_current_user)
):
    """Get professional insights (with authentication)"""
    try:
        # Placeholder market data
        market_data = {
            "prices": [],
            "volumes": [],
            "indicators": {},
            "symbol": request.symbol
        }
        
        insights = await financial_intelligence_engine.generate_professional_insights(
            request.asset_class, request.symbol, market_data
        )
        
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate professional insights: {str(e)}"
        )
