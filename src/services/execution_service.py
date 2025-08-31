"""
Execution Service

Handles order execution, position management, and broker communication.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import structlog

from src.core.config import settings
from src.core.logging import TradingLogger
from src.strategies.base_strategy import Signal, SignalType
from src.models.trade import Trade
from src.models.position import Position
from src.models.order import Order, OrderType, OrderSide, OrderStatus


class ExecutionMode(Enum):
    """Execution modes."""
    PAPER = "paper"
    LIVE = "live"
    BACKTEST = "backtest"


@dataclass
class ExecutionResult:
    """Result of order execution."""
    success: bool
    order_id: Optional[str] = None
    fill_price: Optional[float] = None
    fill_time: Optional[datetime] = None
    slippage: Optional[float] = None
    error_message: Optional[str] = None


class ExecutionService:
    """Handles order execution and position management."""
    
    def __init__(self):
        self.logger = TradingLogger("execution_service")
        self.mode = ExecutionMode.PAPER  # Default to paper trading
        self.is_running = False
        self.is_paused = False
        
        # Order and position tracking
        self.pending_orders: Dict[str, Order] = {}
        self.active_positions: Dict[str, Position] = {}
        self.executed_trades: List[Trade] = []
        
        # Performance tracking
        self.total_executions = 0
        self.successful_executions = 0
        self.total_slippage = 0.0
        self.average_execution_time = 0.0
        
        # Broker connection (placeholder)
        self.broker = None
        
        # Risk manager reference
        self.risk_manager = None
    
    async def start(self):
        """Start the execution service."""
        self.is_running = True
        self.logger.logger.info("Execution service started")
        
        # Initialize broker connection
        await self._initialize_broker()
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop(self):
        """Stop the execution service."""
        self.is_running = False
        
        # Close all positions if in live mode
        if self.mode == ExecutionMode.LIVE:
            await self.close_all_positions()
        
        self.logger.logger.info("Execution service stopped")
    
    async def pause_trading(self):
        """Pause all trading."""
        self.is_paused = True
        self.logger.logger.warning("Trading paused")
    
    async def resume_trading(self):
        """Resume trading."""
        self.is_paused = False
        self.logger.logger.info("Trading resumed")
    
    async def emergency_stop(self):
        """Emergency stop all trading."""
        self.is_paused = True
        self.logger.emergency_action({
            "type": "emergency_stop",
            "reason": "Emergency stop triggered",
            "user": "system",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Close all positions immediately
        await self.close_all_positions()
        
        # Cancel all pending orders
        await self.cancel_all_orders()
    
    async def execute_signal(self, signal: Signal, account_balance: float) -> ExecutionResult:
        """
        Execute a trading signal.
        
        Args:
            signal: Trading signal to execute
            account_balance: Current account balance
            
        Returns:
            Execution result
        """
        if self.is_paused:
            return ExecutionResult(
                success=False,
                error_message="Trading is paused"
            )
        
        try:
            # Validate signal
            if not self._validate_signal(signal):
                return ExecutionResult(
                    success=False,
                    error_message="Invalid signal"
                )
            
            # Calculate position size
            position_size = self._calculate_position_size(signal, account_balance)
            
            # Create order
            order = self._create_order_from_signal(signal, position_size)
            
            # Validate with risk manager if available
            if self.risk_manager:
                is_valid, error_msg = await self.risk_manager.validate_trade(
                    Trade(
                        pair=signal.pair,
                        side=signal.type.value,
                        size=position_size,
                        price=signal.price,
                        strategy=signal.strategy,
                        timestamp=signal.timestamp
                    )
                )
                
                if not is_valid:
                    return ExecutionResult(
                        success=False,
                        error_message=f"Risk validation failed: {error_msg}"
                    )
            
            # Execute order
            result = await self._execute_order(order)
            
            # Log execution
            if result.success:
                self.logger.trade_executed({
                    "trade_id": result.order_id,
                    "pair": signal.pair,
                    "side": signal.type.value,
                    "size": position_size,
                    "price": result.fill_price,
                    "strategy": signal.strategy,
                    "timestamp": result.fill_time.isoformat()
                })
            
            return result
            
        except Exception as e:
            self.logger.logger.error("Error executing signal", error=str(e))
            return ExecutionResult(
                success=False,
                error_message=str(e)
            )
    
    def _validate_signal(self, signal: Signal) -> bool:
        """Validate a trading signal."""
        # Check signal type
        if signal.type not in [SignalType.BUY, SignalType.SELL]:
            return False
        
        # Check confidence
        if not 0 <= signal.confidence <= 1:
            return False
        
        # Check price
        if signal.price <= 0:
            return False
        
        # Check pair format
        if not self._is_valid_pair(signal.pair):
            return False
        
        return True
    
    def _is_valid_pair(self, pair: str) -> bool:
        """Check if currency pair is valid."""
        valid_pairs = settings.trading.allowed_pairs
        return pair in valid_pairs
    
    def _calculate_position_size(self, signal: Signal, account_balance: float) -> float:
        """Calculate position size based on signal and risk management."""
        # This would use the strategy's position sizing logic
        # For now, use a simple percentage-based approach
        
        risk_amount = account_balance * (settings.risk.per_trade_risk_pct / 100)
        
        # Simple position sizing (this should be more sophisticated)
        position_size = risk_amount / signal.price
        
        # Convert to lot size
        lot_size = position_size / 100000  # Standard lot size
        
        # Ensure within limits
        min_lot = settings.trading.min_lot_size
        max_lot = settings.trading.max_lot_size
        
        return max(min_lot, min(lot_size, max_lot))
    
    def _create_order_from_signal(self, signal: Signal, position_size: float) -> Order:
        """Create an order from a trading signal."""
        order_side = OrderSide.BUY if signal.type == SignalType.BUY else OrderSide.SELL
        
        # Calculate stop loss and take profit
        stop_loss = self._calculate_stop_loss(signal)
        take_profit = self._calculate_take_profit(signal)
        
        return Order(
            id=f"order_{datetime.utcnow().timestamp()}",
            pair=signal.pair,
            side=order_side,
            type=OrderType.MARKET,
            size=position_size,
            price=signal.price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy=signal.strategy,
            timestamp=datetime.utcnow(),
            status=OrderStatus.PENDING
        )
    
    def _calculate_stop_loss(self, signal: Signal) -> float:
        """Calculate stop loss price."""
        atr = signal.metadata.get('atr', 0.001)
        multiplier = 2.0
        
        if signal.type == SignalType.BUY:
            return signal.price - (atr * multiplier)
        else:
            return signal.price + (atr * multiplier)
    
    def _calculate_take_profit(self, signal: Signal) -> float:
        """Calculate take profit price."""
        atr = signal.metadata.get('atr', 0.001)
        risk_reward_ratio = 2.0
        
        if signal.type == SignalType.BUY:
            return signal.price + (atr * risk_reward_ratio)
        else:
            return signal.price - (atr * risk_reward_ratio)
    
    async def _execute_order(self, order: Order) -> ExecutionResult:
        """Execute an order through the broker."""
        start_time = datetime.utcnow()
        
        try:
            if self.mode == ExecutionMode.PAPER:
                result = await self._execute_paper_order(order)
            elif self.mode == ExecutionMode.LIVE:
                result = await self._execute_live_order(order)
            else:
                result = await self._execute_backtest_order(order)
            
            # Update performance metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_performance_metrics(result.success, execution_time, result.slippage)
            
            return result
            
        except Exception as e:
            self.logger.logger.error("Order execution failed", error=str(e))
            return ExecutionResult(
                success=False,
                error_message=str(e)
            )
    
    async def _execute_paper_order(self, order: Order) -> ExecutionResult:
        """Execute order in paper trading mode."""
        # Simulate execution delay
        await asyncio.sleep(0.1)
        
        # Simulate slippage
        slippage = self._simulate_slippage(order)
        fill_price = order.price + slippage
        
        # Create execution result
        result = ExecutionResult(
            success=True,
            order_id=order.id,
            fill_price=fill_price,
            fill_time=datetime.utcnow(),
            slippage=slippage
        )
        
        # Update order status
        order.status = OrderStatus.FILLED
        order.fill_price = fill_price
        order.fill_time = result.fill_time
        
        # Create position
        await self._create_position(order)
        
        return result
    
    async def _execute_live_order(self, order: Order) -> ExecutionResult:
        """Execute order in live trading mode."""
        # This would integrate with actual broker API
        # For now, return error
        return ExecutionResult(
            success=False,
            error_message="Live trading not implemented"
        )
    
    async def _execute_backtest_order(self, order: Order) -> ExecutionResult:
        """Execute order in backtest mode."""
        # Similar to paper trading but with historical data
        return await self._execute_paper_order(order)
    
    def _simulate_slippage(self, order: Order) -> float:
        """Simulate slippage for paper trading."""
        # Simple slippage simulation
        base_slippage = settings.trading.default_slippage_pips / 10000  # Convert pips to price
        
        # Add some randomness
        import random
        random_factor = random.uniform(0.5, 1.5)
        
        # Directional slippage (worse for larger orders)
        size_factor = min(order.size / 1.0, 2.0)  # Cap at 2x
        
        slippage = base_slippage * random_factor * size_factor
        
        # Make slippage negative for buy orders (worse fill)
        if order.side == OrderSide.BUY:
            slippage = abs(slippage)
        else:
            slippage = -abs(slippage)
        
        return slippage
    
    async def _create_position(self, order: Order):
        """Create a position from a filled order."""
        position = Position(
            id=f"pos_{order.id}",
            pair=order.pair,
            side=order.side.value,
            size=order.size,
            entry_price=order.fill_price,
            strategy=order.strategy,
            open_time=order.fill_time,
            stop_loss=order.stop_loss,
            take_profit=order.take_profit
        )
        
        self.active_positions[position.id] = position
        
        # Create trade record
        trade = Trade(
            id=order.id,
            pair=order.pair,
            side=order.side.value,
            size=order.size,
            price=order.fill_price,
            strategy=order.strategy,
            timestamp=order.fill_time,
            pnl=0.0  # Will be calculated when position is closed
        )
        
        self.executed_trades.append(trade)
    
    async def close_position(self, position_id: str, reason: str = "manual") -> ExecutionResult:
        """Close a specific position."""
        if position_id not in self.active_positions:
            return ExecutionResult(
                success=False,
                error_message="Position not found"
            )
        
        position = self.active_positions[position_id]
        
        # Create closing order
        close_side = OrderSide.SELL if position.side == "buy" else OrderSide.BUY
        
        order = Order(
            id=f"close_{position_id}",
            pair=position.pair,
            side=close_side,
            type=OrderType.MARKET,
            size=position.size,
            price=position.entry_price,  # This would be current market price
            strategy=position.strategy,
            timestamp=datetime.utcnow(),
            status=OrderStatus.PENDING
        )
        
        # Execute closing order
        result = await self._execute_order(order)
        
        if result.success:
            # Calculate P&L
            pnl = self._calculate_position_pnl(position, result.fill_price)
            
            # Update position
            position.close_price = result.fill_price
            position.close_time = result.fill_time
            position.pnl = pnl
            position.status = "closed"
            
            # Remove from active positions
            del self.active_positions[position_id]
            
            # Update trade record
            for trade in self.executed_trades:
                if trade.pair == position.pair and trade.strategy == position.strategy:
                    trade.pnl = pnl
                    break
        
        return result
    
    async def close_all_positions(self):
        """Close all active positions."""
        position_ids = list(self.active_positions.keys())
        
        for position_id in position_ids:
            await self.close_position(position_id, "emergency_close")
    
    async def cancel_all_orders(self):
        """Cancel all pending orders."""
        # This would cancel orders with the broker
        self.pending_orders.clear()
    
    def _calculate_position_pnl(self, position: Position, close_price: float) -> float:
        """Calculate P&L for a position."""
        if position.side == "buy":
            return (close_price - position.entry_price) * position.size * 100000
        else:
            return (position.entry_price - close_price) * position.size * 100000
    
    def _update_performance_metrics(self, success: bool, execution_time: float, slippage: float):
        """Update execution performance metrics."""
        self.total_executions += 1
        
        if success:
            self.successful_executions += 1
        
        if slippage:
            self.total_slippage += abs(slippage)
        
        # Update average execution time
        if self.total_executions == 1:
            self.average_execution_time = execution_time
        else:
            self.average_execution_time = (
                (self.average_execution_time * (self.total_executions - 1) + execution_time) 
                / self.total_executions
            )
    
    async def _initialize_broker(self):
        """Initialize broker connection."""
        # This would set up connection to actual broker
        # For now, just log
        self.logger.logger.info(f"Broker initialized in {self.mode.value} mode")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                # Check for stop loss and take profit hits
                await self._check_exit_conditions()
                
                # Update position P&L
                await self._update_position_pnl()
                
                # Sleep
                await asyncio.sleep(1)
                
            except Exception as e:
                self.logger.logger.error("Execution monitoring error", error=str(e))
                await asyncio.sleep(5)
    
    async def _check_exit_conditions(self):
        """Check if any positions should be closed due to stop loss or take profit."""
        for position_id, position in list(self.active_positions.items()):
            # Get current market price (this would come from market data)
            current_price = position.entry_price  # Placeholder
            
            # Check stop loss
            if position.stop_loss:
                if (position.side == "buy" and current_price <= position.stop_loss) or \
                   (position.side == "sell" and current_price >= position.stop_loss):
                    await self.close_position(position_id, "stop_loss")
                    continue
            
            # Check take profit
            if position.take_profit:
                if (position.side == "buy" and current_price >= position.take_profit) or \
                   (position.side == "sell" and current_price <= position.take_profit):
                    await self.close_position(position_id, "take_profit")
                    continue
    
    async def _update_position_pnl(self):
        """Update unrealized P&L for all positions."""
        for position in self.active_positions.values():
            # Get current market price (this would come from market data)
            current_price = position.entry_price  # Placeholder
            
            position.unrealized_pnl = self._calculate_position_pnl(position, current_price)
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution service summary."""
        return {
            "mode": self.mode.value,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "success_rate": self.successful_executions / self.total_executions if self.total_executions > 0 else 0.0,
            "average_execution_time": self.average_execution_time,
            "total_slippage": self.total_slippage,
            "active_positions": len(self.active_positions),
            "pending_orders": len(self.pending_orders)
        }
    
    def set_risk_manager(self, risk_manager):
        """Set reference to risk manager."""
        self.risk_manager = risk_manager
    
    def set_mode(self, mode: ExecutionMode):
        """Set execution mode."""
        self.mode = mode
        self.logger.logger.info(f"Execution mode changed to {mode.value}")
