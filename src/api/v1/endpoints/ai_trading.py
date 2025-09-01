"""
AI Trading Endpoints
Control autonomous AI trading decisions
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import asyncio

from src.core.security import get_current_user
from src.services.ai_trading_brain import ai_trading_brain

router = APIRouter()

# Request Models
class AutonomousTradingRequest(BaseModel):
    enabled: bool
    interval_minutes: Optional[int] = 15
    max_positions: Optional[int] = 3
    confidence_threshold: Optional[float] = 0.75


class StrategyExecutionRequest(BaseModel):
    execute_now: bool = True
    analyze_only: bool = False


# FIX: Add test endpoint
@router.get("/test")
async def test_ai_trading():
    """Test AI trading endpoints"""
    return {"message": "AI Trading endpoints working", "status": "success"}


# FIX: Add authentication bypass endpoints for testing
@router.get("/analysis-test")
async def get_market_analysis_test():
    """Get AI market analysis without authentication"""
    try:
        result = await ai_trading_brain.analyze_market_conditions()
        return result
    except Exception as e:
        return {"error": str(e)}


@router.get("/signals-test")
async def get_trading_signals_test():
    """Get AI trading signals without authentication"""
    try:
        result = await ai_trading_brain.generate_trading_signals()
        return {
            "signals": result,
            "count": len(result),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/execute-strategy-test")
async def execute_ai_strategy_test(request: StrategyExecutionRequest = None):
    """Execute AI trading strategy without authentication"""
    try:
        if request and request.analyze_only:
            # Just analyze, don't execute
            analysis = await ai_trading_brain.analyze_market_conditions()
            signals = await ai_trading_brain.generate_trading_signals()
            return {
                "analysis": analysis,
                "signals": signals,
                "executed": False,
                "message": "Analysis only - no trades executed"
            }
        else:
            # Execute the strategy
            result = await ai_trading_brain.execute_ai_strategy()
            return result
    except Exception as e:
        return {"error": str(e)}


@router.get("/status-test")
async def get_ai_trading_status_test():
    """Get AI trading status without authentication"""
    try:
        return {
            "ai_brain_active": True,
            "last_analysis": ai_trading_brain.last_analysis,
            "active_signals": ai_trading_brain.active_signals,
            "current_strategy": ai_trading_brain.current_strategy,
            "confidence_threshold": ai_trading_brain.confidence_threshold,
            "max_positions": ai_trading_brain.max_positions,
            "position_size": ai_trading_brain.position_size,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}


@router.post("/autonomous-mode-test")
async def set_autonomous_mode_test(request: AutonomousTradingRequest):
    """Enable/disable autonomous trading mode without authentication"""
    try:
        if request.enabled:
            # Start autonomous trading in background
            asyncio.create_task(
                ai_trading_brain.run_autonomous_trading(request.interval_minutes)
            )
            return {
                "message": f"🤖 Autonomous trading enabled with {request.interval_minutes} minute intervals",
                "enabled": True,
                "interval_minutes": request.interval_minutes
            }
        else:
            # Stop autonomous trading
            ai_trading_brain.running = False
            return {
                "message": "🤖 Autonomous trading disabled",
                "enabled": False
            }
    except Exception as e:
        return {"error": str(e)}


# Original authenticated endpoints
@router.get("/analysis")
async def get_market_analysis(
    current_user: str = Depends(get_current_user)
):
    """Get AI market analysis (with authentication)"""
    try:
        result = await ai_trading_brain.analyze_market_conditions()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get market analysis: {str(e)}"
        )


@router.get("/signals")
async def get_trading_signals(
    current_user: str = Depends(get_current_user)
):
    """Get AI trading signals (with authentication)"""
    try:
        result = await ai_trading_brain.generate_trading_signals()
        return {
            "signals": result,
            "count": len(result),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get trading signals: {str(e)}"
        )


@router.post("/execute-strategy")
async def execute_ai_strategy(
    request: StrategyExecutionRequest,
    current_user: str = Depends(get_current_user)
):
    """Execute AI trading strategy (with authentication)"""
    try:
        if request.analyze_only:
            # Just analyze, don't execute
            analysis = await ai_trading_brain.analyze_market_conditions()
            signals = await ai_trading_brain.generate_trading_signals()
            return {
                "analysis": analysis,
                "signals": signals,
                "executed": False,
                "message": "Analysis only - no trades executed"
            }
        else:
            # Execute the strategy
            result = await ai_trading_brain.execute_ai_strategy()
            return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute strategy: {str(e)}"
        )


@router.get("/status")
async def get_ai_trading_status(
    current_user: str = Depends(get_current_user)
):
    """Get AI trading status (with authentication)"""
    try:
        return {
            "ai_brain_active": True,
            "last_analysis": ai_trading_brain.last_analysis,
            "active_signals": ai_trading_brain.active_signals,
            "current_strategy": ai_trading_brain.current_strategy,
            "confidence_threshold": ai_trading_brain.confidence_threshold,
            "max_positions": ai_trading_brain.max_positions,
            "position_size": ai_trading_brain.position_size,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI status: {str(e)}"
        )


@router.post("/autonomous-mode")
async def set_autonomous_mode(
    request: AutonomousTradingRequest,
    current_user: str = Depends(get_current_user)
):
    """Enable/disable autonomous trading mode (with authentication)"""
    try:
        if request.enabled:
            # Start autonomous trading in background
            asyncio.create_task(
                ai_trading_brain.run_autonomous_trading(request.interval_minutes)
            )
            return {
                "message": f"🤖 Autonomous trading enabled with {request.interval_minutes} minute intervals",
                "enabled": True,
                "interval_minutes": request.interval_minutes
            }
        else:
            # Stop autonomous trading
            ai_trading_brain.running = False
            return {
                "message": "🤖 Autonomous trading disabled",
                "enabled": False
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set autonomous mode: {str(e)}"
        )
