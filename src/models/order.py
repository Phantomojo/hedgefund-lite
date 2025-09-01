"""
Order model for the forex trading system.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, Field


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class Order:
    """Order data model."""
    id: str
    pair: str
    side: OrderSide
    type: OrderType
    size: float
    price: float
    strategy: str
    timestamp: datetime
    status: OrderStatus = OrderStatus.PENDING
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    fill_price: Optional[float] = None
    fill_time: Optional[datetime] = None
    filled_size: Optional[float] = None
    remaining_size: Optional[float] = None
    slippage: Optional[float] = None
    commission: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.filled_size is None:
            self.filled_size = 0.0
        if self.remaining_size is None:
            self.remaining_size = self.size


class OrderCreate(BaseModel):
    """Model for creating a new order."""
    pair: str = Field(..., description="Currency pair")
    side: OrderSide = Field(..., description="Order side")
    type: OrderType = Field(..., description="Order type")
    size: float = Field(..., gt=0, description="Order size in lots")
    price: float = Field(..., gt=0, description="Order price")
    strategy: str = Field(..., description="Strategy name")
    stop_loss: Optional[float] = Field(None, gt=0, description="Stop loss price")
    take_profit: Optional[float] = Field(None, gt=0, description="Take profit price")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class OrderUpdate(BaseModel):
    """Model for updating an order."""
    status: Optional[OrderStatus] = Field(None, description="Order status")
    fill_price: Optional[float] = Field(None, gt=0, description="Fill price")
    filled_size: Optional[float] = Field(None, ge=0, description="Filled size")
    remaining_size: Optional[float] = Field(None, ge=0, description="Remaining size")
    slippage: Optional[float] = Field(None, description="Execution slippage")
    commission: Optional[float] = Field(None, description="Commission paid")


class OrderResponse(BaseModel):
    """Model for order response."""
    id: str
    pair: str
    side: str
    type: str
    size: float
    price: float
    strategy: str
    timestamp: datetime
    status: str
    fill_price: Optional[float] = None
    fill_time: Optional[datetime] = None
    filled_size: float
    remaining_size: float
    slippage: Optional[float] = None
    commission: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    class Config:
        from_attributes = True
