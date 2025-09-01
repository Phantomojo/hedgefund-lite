"""
Trading models for orders, positions, and trades.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class PositionSide(str, Enum):
    """Position side enumeration."""
    LONG = "LONG"
    SHORT = "SHORT"


class PositionStatus(str, Enum):
    """Position status enumeration."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class TradeStatus(str, Enum):
    """Trade status enumeration."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class OrderCreate(BaseModel):
    """Create order request model."""
    pair: str = Field(..., description="Currency pair")
    side: OrderSide = Field(..., description="Order side")
    type: OrderType = Field(..., description="Order type")
    units: int = Field(..., description="Number of units")
    price: Optional[float] = Field(None, description="Order price (for limit orders)")
    stop_loss: Optional[float] = Field(None, description="Stop loss price")
    take_profit: Optional[float] = Field(None, description="Take profit price")
    strategy: str = Field("manual", description="Trading strategy")


class OrderResponse(BaseModel):
    """Order response model."""
    id: str = Field(..., description="Order ID")
    pair: str = Field(..., description="Currency pair")
    side: OrderSide = Field(..., description="Order side")
    type: OrderType = Field(..., description="Order type")
    units: int = Field(..., description="Number of units")
    price: float = Field(..., description="Fill price")
    status: OrderStatus = Field(..., description="Order status")
    strategy: str = Field(..., description="Trading strategy")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class PositionResponse(BaseModel):
    """Position response model."""
    id: str = Field(..., description="Position ID")
    pair: str = Field(..., description="Currency pair")
    side: PositionSide = Field(..., description="Position side")
    units: int = Field(..., description="Number of units")
    entry_price: float = Field(..., description="Entry price")
    current_price: float = Field(..., description="Current market price")
    unrealized_pnl: float = Field(..., description="Unrealized P&L")
    realized_pnl: float = Field(..., description="Realized P&L")
    strategy: str = Field(..., description="Trading strategy")
    status: PositionStatus = Field(..., description="Position status")
    opened_at: str = Field(..., description="Opening timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class TradeResponse(BaseModel):
    """Trade response model."""
    id: str = Field(..., description="Trade ID")
    pair: str = Field(..., description="Currency pair")
    side: OrderSide = Field(..., description="Trade side")
    units: int = Field(..., description="Number of units")
    entry_price: float = Field(..., description="Entry price")
    exit_price: float = Field(..., description="Exit price")
    pnl: float = Field(..., description="Profit/Loss")
    strategy: str = Field(..., description="Trading strategy")
    entry_time: str = Field(..., description="Entry timestamp")
    exit_time: str = Field(..., description="Exit timestamp")
    status: TradeStatus = Field(..., description="Trade status")


class SignalRequest(BaseModel):
    """Trading signal request model."""
    pair: str = Field(..., description="Currency pair")
    side: OrderSide = Field(..., description="Signal side")
    units: int = Field(..., description="Number of units")
    strategy: str = Field(..., description="Trading strategy")
    confidence: float = Field(..., description="Signal confidence")
    reasoning: str = Field(..., description="Signal reasoning")
