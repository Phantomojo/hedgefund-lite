"""
Portfolio management endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.security import get_current_user

router = APIRouter()


@router.get("/portfolio")
async def get_portfolio(
    current_user: str = Depends(get_current_user)
):
    """Get current portfolio information."""
    try:
        # This would fetch from database
        return {
            "id": "portfolio_1",
            "name": "Main Portfolio",
            "initial_balance": 10000.0,
            "current_balance": 10500.0,
            "total_pnl": 500.0,
            "unrealized_pnl": 100.0,
            "realized_pnl": 400.0,
            "max_drawdown": 5.0,
            "current_drawdown": 2.0,
            "sharpe_ratio": 1.2,
            "calmar_ratio": 2.1,
            "win_rate": 0.65,
            "profit_factor": 1.8,
            "total_trades": 50,
            "winning_trades": 32,
            "losing_trades": 18,
            "open_positions": 3,
            "leverage": 1.5,
            "margin_utilization": 0.25
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio: {str(e)}"
        )


@router.get("/portfolio/metrics")
async def get_portfolio_metrics(
    current_user: str = Depends(get_current_user)
):
    """Get detailed portfolio metrics."""
    try:
        # This would calculate from database
        return {
            "total_return": 5.0,
            "annualized_return": 12.5,
            "volatility": 8.2,
            "sharpe_ratio": 1.2,
            "sortino_ratio": 1.8,
            "calmar_ratio": 2.1,
            "max_drawdown": 5.0,
            "current_drawdown": 2.0,
            "win_rate": 0.65,
            "profit_factor": 1.8,
            "average_win": 150.0,
            "average_loss": -80.0,
            "largest_win": 500.0,
            "largest_loss": -200.0,
            "consecutive_wins": 5,
            "consecutive_losses": 2,
            "recovery_factor": 2.5,
            "risk_reward_ratio": 1.9,
            "var_95": -3.2,
            "var_99": -5.1,
            "expected_shortfall": -4.2
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get portfolio metrics: {str(e)}"
        )
