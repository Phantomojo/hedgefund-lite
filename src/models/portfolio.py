"""
Portfolio model for the forex trading system.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pydantic import BaseModel, Field


@dataclass
class Portfolio:
    """Portfolio data model."""
    id: str
    name: str
    initial_balance: float
    current_balance: float
    total_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    max_drawdown: float = 0.0
    current_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    calmar_ratio: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    open_positions: int = 0
    leverage: float = 1.0
    margin_utilization: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class PortfolioCreate(BaseModel):
    """Model for creating a new portfolio."""
    name: str = Field(..., description="Portfolio name")
    initial_balance: float = Field(..., gt=0, description="Initial balance")
    leverage: float = Field(1.0, gt=0, le=100, description="Leverage ratio")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PortfolioUpdate(BaseModel):
    """Model for updating a portfolio."""
    name: Optional[str] = Field(None, description="Portfolio name")
    current_balance: Optional[float] = Field(None, gt=0, description="Current balance")
    leverage: Optional[float] = Field(None, gt=0, le=100, description="Leverage ratio")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PortfolioResponse(BaseModel):
    """Model for portfolio response."""
    id: str
    name: str
    initial_balance: float
    current_balance: float
    total_pnl: float
    unrealized_pnl: float
    realized_pnl: float
    max_drawdown: float
    current_drawdown: float
    sharpe_ratio: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    open_positions: int
    leverage: float
    margin_utilization: float
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    class Config:
        from_attributes = True


@dataclass
class PortfolioMetrics:
    """Portfolio performance metrics."""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    current_drawdown: float
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    recovery_factor: float
    risk_reward_ratio: float
    var_95: float
    var_99: float
    expected_shortfall: float
    beta: float
    alpha: float
    information_ratio: float
    treynor_ratio: float
    jensen_alpha: float
    tracking_error: float
    correlation: float
    skewness: float
    kurtosis: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PortfolioMetricsResponse(BaseModel):
    """Model for portfolio metrics response."""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    current_drawdown: float
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    recovery_factor: float
    risk_reward_ratio: float
    var_95: float
    var_99: float
    expected_shortfall: float
    beta: float
    alpha: float
    information_ratio: float
    treynor_ratio: float
    jensen_alpha: float
    tracking_error: float
    correlation: float
    skewness: float
    kurtosis: float
    timestamp: datetime
    
    class Config:
        from_attributes = True
