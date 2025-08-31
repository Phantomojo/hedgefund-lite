"""
Backtesting endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.core.security import get_current_user

router = APIRouter()


class BacktestRequest(BaseModel):
    """Backtest request model."""
    strategy_name: str
    start_date: str
    end_date: str
    initial_balance: float = 10000.0
    pairs: list = ["EURUSD", "GBPUSD", "USDJPY"]
    parameters: Dict[str, Any] = {}


@router.post("/backtest")
async def run_backtest(
    request: BacktestRequest,
    current_user: str = Depends(get_current_user)
):
    """Run a backtest for a strategy."""
    try:
        # This would run the actual backtest
        # For now, return mock results
        return {
            "backtest_id": "bt_12345",
            "strategy_name": request.strategy_name,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "initial_balance": request.initial_balance,
            "final_balance": 11500.0,
            "total_return": 15.0,
            "sharpe_ratio": 1.5,
            "max_drawdown": 8.2,
            "win_rate": 0.68,
            "total_trades": 45,
            "profit_factor": 1.8,
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run backtest: {str(e)}"
        )


@router.get("/backtest/{backtest_id}")
async def get_backtest_results(
    backtest_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get backtest results."""
    try:
        # This would fetch from database
        return {
            "backtest_id": backtest_id,
            "strategy_name": "ema_crossover_v1",
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "initial_balance": 10000.0,
            "final_balance": 11500.0,
            "total_return": 15.0,
            "sharpe_ratio": 1.5,
            "max_drawdown": 8.2,
            "win_rate": 0.68,
            "total_trades": 45,
            "profit_factor": 1.8,
            "equity_curve": [],
            "trades": [],
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get backtest results: {str(e)}"
        )
