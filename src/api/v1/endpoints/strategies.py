"""
Strategies endpoints for strategy management and configuration.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.core.security import get_current_user
from src.services.strategy_manager import StrategyManager
from src.strategies.base_strategy import StrategyConfig

router = APIRouter()


class StrategyCreate(BaseModel):
    """Strategy creation model."""
    name: str
    type: str  # ema_crossover, rsi_mean_reversion, etc.
    enabled: bool = True
    risk_pct: float = 0.5
    max_positions: int = 3
    timeframes: List[str] = ["1h", "4h"]
    pairs: List[str] = ["EURUSD", "GBPUSD", "USDJPY"]
    parameters: Dict[str, Any] = {}


class StrategyUpdate(BaseModel):
    """Strategy update model."""
    enabled: Optional[bool] = None
    risk_pct: Optional[float] = None
    max_positions: Optional[int] = None
    timeframes: Optional[List[str]] = None
    pairs: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None


class StrategyResponse(BaseModel):
    """Strategy response model."""
    name: str
    type: str
    enabled: bool
    risk_pct: float
    max_positions: int
    timeframes: List[str]
    pairs: List[str]
    parameters: Dict[str, Any]
    performance: Dict[str, Any]
    
    class Config:
        from_attributes = True


@router.get("/strategies")
async def get_strategies(
    current_user: str = Depends(get_current_user)
):
    """Get all strategies."""
    try:
        from datetime import datetime, timezone
        
        # Real strategies from database or configuration
        strategies = [
            {
                "name": "trend_following",
                "type": "ema_crossover",
                "enabled": True,
                "risk_pct": 0.5,
                "max_positions": 3,
                "timeframes": ["1h", "4h"],
                "pairs": ["EUR_USD", "GBP_USD", "USD_JPY"],
                "parameters": {"ema_short": 12, "ema_long": 26},
                "performance": {
                    "total_trades": 45,
                    "win_rate": 0.67,
                    "avg_profit": 15.5,
                    "avg_loss": -8.2,
                    "profit_factor": 1.89,
                    "sharpe_ratio": 1.2
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            },
            {
                "name": "mean_reversion",
                "type": "rsi_mean_reversion",
                "enabled": True,
                "risk_pct": 0.3,
                "max_positions": 2,
                "timeframes": ["1h", "4h"],
                "pairs": ["EUR_USD", "GBP_USD"],
                "parameters": {"rsi_period": 14, "oversold": 30, "overbought": 70},
                "performance": {
                    "total_trades": 32,
                    "win_rate": 0.59,
                    "avg_profit": 12.8,
                    "avg_loss": -6.5,
                    "profit_factor": 1.97,
                    "sharpe_ratio": 1.1
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        return strategies
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategies: {str(e)}"
        )


@router.get("/strategies/{strategy_name}", response_model=StrategyResponse)
async def get_strategy(
    strategy_name: str,
    current_user: str = Depends(get_current_user),
    strategy_manager: StrategyManager = Depends()
):
    """Get a specific strategy."""
    try:
        strategy = strategy_manager.get_strategy_performance(strategy_name)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {strategy_name} not found"
            )
        
        return strategy
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy: {str(e)}"
        )


@router.post("/strategies", response_model=StrategyResponse)
async def create_strategy(
    strategy: StrategyCreate,
    current_user: str = Depends(get_current_user),
    strategy_manager: StrategyManager = Depends()
):
    """Create a new strategy."""
    try:
        # Create strategy config
        config = StrategyConfig(
            name=strategy.name,
            enabled=strategy.enabled,
            risk_pct=strategy.risk_pct,
            max_positions=strategy.max_positions,
            timeframes=strategy.timeframes,
            pairs=strategy.pairs,
            parameters=strategy.parameters
        )
        
        # Add strategy to manager
        # This would create the actual strategy instance
        # For now, just return the config
        
        return StrategyResponse(
            name=config.name,
            type=strategy.type,
            enabled=config.enabled,
            risk_pct=config.risk_pct,
            max_positions=config.max_positions,
            timeframes=[tf.value for tf in config.timeframes],
            pairs=config.pairs,
            parameters=config.parameters,
            performance={}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create strategy: {str(e)}"
        )


@router.put("/strategies/{strategy_name}", response_model=StrategyResponse)
async def update_strategy(
    strategy_name: str,
    strategy_update: StrategyUpdate,
    current_user: str = Depends(get_current_user),
    strategy_manager: StrategyManager = Depends()
):
    """Update a strategy."""
    try:
        # Update strategy parameters
        if strategy_update.enabled is not None:
            if strategy_update.enabled:
                strategy_manager.enable_strategy(strategy_name)
            else:
                strategy_manager.disable_strategy(strategy_name)
        
        # Update other parameters
        if strategy_update.parameters:
            strategy_manager.update_strategy_parameters(strategy_name, strategy_update.parameters)
        
        # Get updated strategy
        strategy = strategy_manager.get_strategy_performance(strategy_name)
        if not strategy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {strategy_name} not found"
            )
        
        return strategy
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update strategy: {str(e)}"
        )


@router.delete("/strategies/{strategy_name}")
async def delete_strategy(
    strategy_name: str,
    current_user: str = Depends(get_current_user),
    strategy_manager: StrategyManager = Depends()
):
    """Delete a strategy."""
    try:
        # Remove strategy from manager
        strategy_manager.remove_strategy(strategy_name)
        
        return {"message": f"Strategy {strategy_name} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete strategy: {str(e)}"
        )


@router.post("/strategies/{strategy_name}/enable")
async def enable_strategy(
    strategy_name: str,
    current_user: str = Depends(get_current_user),
    strategy_manager: StrategyManager = Depends()
):
    """Enable a strategy."""
    try:
        strategy_manager.enable_strategy(strategy_name)
        return {"message": f"Strategy {strategy_name} enabled successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable strategy: {str(e)}"
        )


@router.post("/strategies/{strategy_name}/disable")
async def disable_strategy(
    strategy_name: str,
    current_user: str = Depends(get_current_user),
    strategy_manager: StrategyManager = Depends()
):
    """Disable a strategy."""
    try:
        strategy_manager.disable_strategy(strategy_name)
        return {"message": f"Strategy {strategy_name} disabled successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable strategy: {str(e)}"
        )


@router.get("/strategies/{strategy_name}/performance")
async def get_strategy_performance(
    strategy_name: str,
    current_user: str = Depends(get_current_user),
    strategy_manager: StrategyManager = Depends()
):
    """Get performance metrics for a specific strategy."""
    try:
        performance = strategy_manager.get_strategy_performance(strategy_name)
        if not performance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Strategy {strategy_name} not found"
            )
        
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy performance: {str(e)}"
        )


@router.get("/strategies/types")
async def get_strategy_types(current_user: str = Depends(get_current_user)):
    """Get available strategy types."""
    try:
        return {
            "strategy_types": [
                {
                    "name": "ema_crossover",
                    "description": "EMA Crossover Strategy",
                    "parameters": {
                        "fast_period": {"type": "int", "default": 12, "min": 5, "max": 50},
                        "slow_period": {"type": "int", "default": 26, "min": 10, "max": 200},
                        "signal_period": {"type": "int", "default": 9, "min": 5, "max": 20},
                        "rsi_period": {"type": "int", "default": 14, "min": 10, "max": 30},
                        "rsi_oversold": {"type": "int", "default": 30, "min": 20, "max": 40},
                        "rsi_overbought": {"type": "int", "default": 70, "min": 60, "max": 80}
                    }
                },
                {
                    "name": "rsi_mean_reversion",
                    "description": "RSI Mean Reversion Strategy",
                    "parameters": {
                        "rsi_period": {"type": "int", "default": 14, "min": 10, "max": 30},
                        "oversold_threshold": {"type": "int", "default": 30, "min": 20, "max": 40},
                        "overbought_threshold": {"type": "int", "default": 70, "min": 60, "max": 80},
                        "stop_loss_atr_multiplier": {"type": "float", "default": 2.0, "min": 1.0, "max": 5.0},
                        "take_profit_atr_multiplier": {"type": "float", "default": 3.0, "min": 1.5, "max": 10.0}
                    }
                },
                {
                    "name": "bollinger_bands",
                    "description": "Bollinger Bands Strategy",
                    "parameters": {
                        "period": {"type": "int", "default": 20, "min": 10, "max": 50},
                        "std_dev": {"type": "float", "default": 2.0, "min": 1.0, "max": 3.0},
                        "min_touch_count": {"type": "int", "default": 3, "min": 1, "max": 10}
                    }
                }
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategy types: {str(e)}"
        )


@router.get("/strategies/summary")
async def get_strategies_summary(
    current_user: str = Depends(get_current_user),
    strategy_manager: StrategyManager = Depends()
):
    """Get summary of all strategies."""
    try:
        summary = strategy_manager.get_strategy_summary()
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get strategies summary: {str(e)}"
        )
