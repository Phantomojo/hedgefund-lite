"""
Position model for the forex trading system.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field


class PositionSide(str, Enum):
    """Position side enumeration."""
    LONG = "long"
    SHORT = "short"


class PositionStatus(str, Enum):
    """Position status enumeration."""
    OPEN = "open"
    CLOSED = "closed"
    PARTIALLY_CLOSED = "partially_closed"


@dataclass
class Position:
    """Position data model."""
    id: str
    pair: str
    side: str
    size: float
    entry_price: float
    strategy: str
    open_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    close_price: Optional[float] = None
    close_time: Optional[datetime] = None
    pnl: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    status: PositionStatus = PositionStatus.OPEN
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.pnl is None:
            self.pnl = 0.0
        if self.unrealized_pnl is None:
            self.unrealized_pnl = 0.0


class PositionCreate(BaseModel):
    """Model for creating a new position."""
    pair: str = Field(..., description="Currency pair")
    side: PositionSide = Field(..., description="Position side")
    size: float = Field(..., gt=0, description="Position size in lots")
    entry_price: float = Field(..., gt=0, description="Entry price")
    strategy: str = Field(..., description="Strategy name")
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")
    take_profit: Optional[float] = Field(None, gt=0, description="Take profit price")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class PositionUpdate(BaseModel):
    """Model for updating a position."""
    close_price: Optional[float] = Field(None, gt=0, description="Close price")
    pnl: Optional[float] = Field(None, description="Realized P&L")
    unrealized_pnl: Optional[float] = Field(None, description="Unrealized P&L")
    status: Optional[PositionStatus] = Field(None, description="Position status")
    stop_loss: Optional[float] = Field(None, gt=0, description="Updated stop loss")
    take_profit: Optional[float] = Field(None, gt=0, description="Updated take profit")


class PositionResponse(BaseModel):
    """Model for position response."""
    id: str
    pair: str
    side: str
    size: float
    entry_price: float
    strategy: str
    open_time: datetime
    pnl: float
    unrealized_pnl: float
    status: str
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    close_price: Optional[float] = None
    close_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    class Config:
        from_attributes = True
