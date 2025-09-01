"""
Trade model for the forex trading system.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field


class TradeSide(str, Enum):
    """Trade side enumeration."""
    BUY = "buy"
    SELL = "sell"


class TradeStatus(str, Enum):
    """Trade status enumeration."""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Trade:
    """Trade data model."""
    id: str
    pair: str
    side: str
    size: float
    price: float
    strategy: str
    timestamp: datetime
    pnl: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    fill_price: Optional[float] = None
    fill_time: Optional[datetime] = None
    status: TradeStatus = TradeStatus.PENDING
    slippage: Optional[float] = None
    commission: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.pnl is None:
            self.pnl = 0.0


class TradeCreate(BaseModel):
    """Model for creating a new trade."""
    pair: str = Field(..., description="Currency pair")
    side: TradeSide = Field(..., description="Trade side")
    size: float = Field(..., gt=0, description="Position size in lots")
    price: float = Field(..., gt=0, description="Entry price")
    strategy: str = Field(..., description="Strategy name")
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")
    take_profit: Optional[float] = Field(None, gt=0, description="Take profit price")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TradeUpdate(BaseModel):
    """Model for updating a trade."""
    status: Optional[TradeStatus] = Field(None, description="Trade status")
    fill_price: Optional[float] = Field(None, gt=0, description="Fill price")
    pnl: Optional[float] = Field(None, description="Realized P&L")
    slippage: Optional[float] = Field(None, description="Execution slippage")
    commission: Optional[float] = Field(None, description="Commission paid")


class TradeResponse(BaseModel):
    """Model for trade response."""
    id: str
    pair: str
    side: str
    size: float
    price: float
    strategy: str
    timestamp: datetime
    pnl: float
    status: str
    fill_price: Optional[float] = None
    fill_time: Optional[datetime] = None
    slippage: Optional[float] = None
    commission: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    class Config:
        from_attributes = True
