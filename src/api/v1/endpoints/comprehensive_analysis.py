"""
Comprehensive Market Analysis Endpoints
Multi-asset analysis and strategy generation
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.core.security import get_current_user
from src.services.market_analyzer import market_analyzer
from src.services.strategy_engine import strategy_engine

router = APIRouter()

# Request Models
class AnalysisRequest(BaseModel):
    asset_classes: Optional[list] = None  # Specific asset classes to analyze
    include_news: bool = True
    include_fundamentals: bool = True
    include_technical: bool = True


class StrategyRequest(BaseModel):
    execute_strategies: bool = False
    include_portfolio_recommendations: bool = True
    risk_assessment: bool = True


# Test endpoints (no authentication required)
@router.get("/test")
async def test_comprehensive_analysis():
    """Test comprehensive analysis endpoints"""
    return {"message": "Comprehensive Analysis endpoints working", "status": "success"}


@router.get("/market-analysis-test")
async def get_comprehensive_market_analysis_test():
    """Get comprehensive market analysis for all asset classes without authentication"""
    try:
        result = await market_analyzer.analyze_all_markets()
        return result
    except Exception as e:
        return {"error": str(e)}


@router.get("/strategy-generation-test")
async def generate_comprehensive_strategies_test():
    """Generate comprehensive trading strategies without authentication"""
    try:
        result = await strategy_engine.generate_comprehensive_strategies()
        return result
    except Exception as e:
        return {"error": str(e)}


@router.post("/strategy-execution-test")
async def execute_comprehensive_strategies_test(request: StrategyRequest):
    """Execute comprehensive trading strategies without authentication"""
    try:
        # First generate strategies
        strategies = await strategy_engine.generate_comprehensive_strategies()
        if "error" in strategies:
            return {"error": f"Strategy generation failed: {strategies['error']}"}
        
        # Execute if requested
        if request.execute_strategies:
            execution_result = await strategy_engine.execute_strategies(strategies, execute_all=False)
            return {
                "strategies": strategies,
                "execution_result": execution_result
            }
        else:
            return {
                "strategies": strategies,
                "message": "Strategies generated but not executed (execute_strategies=False)"
            }
            
    except Exception as e:
        return {"error": str(e)}


@router.get("/asset-coverage-test")
async def get_asset_coverage_test():
    """Get information about covered asset classes without authentication"""
    try:
        return {
            "asset_classes": market_analyzer.asset_classes,
            "strategy_types": strategy_engine.strategy_types,
            "asset_strategies": strategy_engine.asset_strategies,
            "position_limits": {
                "max_per_asset": strategy_engine.max_positions_per_asset,
                "max_total": strategy_engine.max_total_positions
            },
            "risk_parameters": {
                "max_risk_per_trade": strategy_engine.max_risk_per_trade,
                "max_portfolio_risk": strategy_engine.max_portfolio_risk,
                "min_confidence": strategy_engine.min_confidence_threshold
            }
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/news-sources-test")
async def get_news_sources_test():
    """Get available news and data sources without authentication"""
    try:
        return {
            "news_sources": market_analyzer.news_sources,
            "api_keys_configured": list(market_analyzer.api_keys.keys()),
            "note": "API keys should be configured in environment variables for production use"
        }
    except Exception as e:
        return {"error": str(e)}


# Authenticated endpoints
@router.get("/market-analysis")
async def get_comprehensive_market_analysis(
    request: AnalysisRequest = None,
    current_user: str = Depends(get_current_user)
):
    """Get comprehensive market analysis for all asset classes (with authentication)"""
    try:
        result = await market_analyzer.analyze_all_markets()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Market analysis failed: {str(e)}"
        )


@router.get("/strategy-generation")
async def generate_comprehensive_strategies(
    current_user: str = Depends(get_current_user)
):
    """Generate comprehensive trading strategies (with authentication)"""
    try:
        result = await strategy_engine.generate_comprehensive_strategies()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy generation failed: {str(e)}"
        )


@router.post("/strategy-execution")
async def execute_comprehensive_strategies(
    request: StrategyRequest,
    current_user: str = Depends(get_current_user)
):
    """Execute comprehensive trading strategies (with authentication)"""
    try:
        # First generate strategies
        strategies = await strategy_engine.generate_comprehensive_strategies()
        if "error" in strategies:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Strategy generation failed: {strategies['error']}"
            )
        
        # Execute if requested
        if request.execute_strategies:
            execution_result = await strategy_engine.execute_strategies(strategies, execute_all=False)
            return {
                "strategies": strategies,
                "execution_result": execution_result
            }
        else:
            return {
                "strategies": strategies,
                "message": "Strategies generated but not executed (execute_strategies=False)"
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategy execution failed: {str(e)}"
        )


@router.get("/asset-coverage")
async def get_asset_coverage(
    current_user: str = Depends(get_current_user)
):
    """Get information about covered asset classes (with authentication)"""
    try:
        return {
            "asset_classes": market_analyzer.asset_classes,
            "strategy_types": strategy_engine.strategy_types,
            "asset_strategies": strategy_engine.asset_strategies,
            "position_limits": {
                "max_per_asset": strategy_engine.max_positions_per_asset,
                "max_total": strategy_engine.max_total_positions
            },
            "risk_parameters": {
                "max_risk_per_trade": strategy_engine.max_risk_per_trade,
                "max_portfolio_risk": strategy_engine.max_portfolio_risk,
                "min_confidence": strategy_engine.min_confidence_threshold
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get asset coverage: {str(e)}"
        )


@router.get("/news-sources")
async def get_news_sources(
    current_user: str = Depends(get_current_user)
):
    """Get available news and data sources (with authentication)"""
    try:
        return {
            "news_sources": market_analyzer.news_sources,
            "api_keys_configured": list(market_analyzer.api_keys.keys()),
            "note": "API keys should be configured in environment variables for production use"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get news sources: {str(e)}"
        )
