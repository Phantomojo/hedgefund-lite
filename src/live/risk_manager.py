"""
Production Risk Management System
Real-time risk monitoring, position tracking, and emergency controls.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk levels for alerts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PositionSide(Enum):
    """Position sides."""
    LONG = "long"
    SHORT = "short"

@dataclass
class Position:
    """Position information."""
    symbol: str
    side: PositionSide
    size: float
    entry_price: float
    current_price: float
    entry_time: datetime
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RiskMetrics:
    """Risk metrics for portfolio."""
    total_pnl: float
    unrealized_pnl: float
    realized_pnl: float
    total_exposure: float
    max_drawdown: float
    current_drawdown: float
    var_95: float
    cvar_95: float
    sharpe_ratio: float
    volatility: float
    beta: float
    correlation: float
    timestamp: datetime

class RiskLimits:
    """Risk limits configuration."""
    
    def __init__(self):
        # Position limits
        self.max_position_size = 0.1  # 10% of portfolio
        self.max_total_exposure = 0.5  # 50% of portfolio
        self.max_sector_exposure = 0.3  # 30% per sector
        
        # P&L limits
        self.max_daily_loss = 0.05  # 5% daily loss
        self.max_drawdown = 0.15  # 15% max drawdown
        self.max_unrealized_loss = 0.10  # 10% unrealized loss
        
        # Risk metrics limits
        self.max_var = 0.02  # 2% VaR
        self.max_volatility = 0.20  # 20% volatility
        self.min_sharpe = 0.5  # Minimum Sharpe ratio
        
        # Correlation limits
        self.max_correlation = 0.7  # Maximum correlation between positions

class EmergencyStop:
    """Emergency stop mechanism."""
    
    def __init__(self, risk_manager):
        self.risk_manager = risk_manager
        self.triggered = False
        self.trigger_time = None
        self.trigger_reason = None
        self.callbacks = []
    
    def register_callback(self, callback: Callable):
        """Register emergency stop callback."""
        self.callbacks.append(callback)
    
    async def trigger(self, reason: str):
        """Trigger emergency stop."""
        if not self.triggered:
            self.triggered = True
            self.trigger_time = datetime.now(timezone.utc)
            self.trigger_reason = reason
            
            logger.critical(f"EMERGENCY STOP TRIGGERED: {reason}")
            
            # Execute callbacks
            for callback in self.callbacks:
                try:
                    await callback(reason)
                except Exception as e:
                    logger.error(f"Emergency stop callback error: {e}")
    
    def reset(self):
        """Reset emergency stop."""
        self.triggered = False
        self.trigger_time = None
        self.trigger_reason = None
        logger.info("Emergency stop reset")

class PositionTracker:
    """Real-time position tracking."""
    
    def __init__(self):
        self.positions: Dict[str, Position] = {}
        self.position_history: List[Position] = []
        self.pnl_history: List[Dict[str, Any]] = []
    
    def add_position(self, position: Position):
        """Add new position."""
        self.positions[position.symbol] = position
        self.position_history.append(position)
        logger.info(f"Added position: {position.symbol} {position.side.value} {position.size}")
    
    def update_position(self, symbol: str, current_price: float):
        """Update position with current price."""
        if symbol in self.positions:
            position = self.positions[symbol]
            position.current_price = current_price
            
            # Calculate unrealized P&L
            if position.side == PositionSide.LONG:
                position.unrealized_pnl = (current_price - position.entry_price) * position.size
            else:
                position.unrealized_pnl = (position.entry_price - current_price) * position.size
    
    def close_position(self, symbol: str, exit_price: float, exit_time: datetime):
        """Close position."""
        if symbol in self.positions:
            position = self.positions[symbol]
            
            # Calculate realized P&L
            if position.side == PositionSide.LONG:
                position.realized_pnl = (exit_price - position.entry_price) * position.size
            else:
                position.realized_pnl = (position.entry_price - exit_price) * position.size
            
            # Record P&L history
            self.pnl_history.append({
                "symbol": symbol,
                "side": position.side.value,
                "size": position.size,
                "entry_price": position.entry_price,
                "exit_price": exit_price,
                "realized_pnl": position.realized_pnl,
                "entry_time": position.entry_time,
                "exit_time": exit_time,
                "duration": (exit_time - position.entry_time).total_seconds() / 3600  # hours
            })
            
            # Remove from active positions
            del self.positions[symbol]
            logger.info(f"Closed position: {symbol}, P&L: {position.realized_pnl}")
    
    def get_total_exposure(self) -> float:
        """Get total portfolio exposure."""
        return sum(abs(pos.size * pos.current_price) for pos in self.positions.values())
    
    def get_total_pnl(self) -> float:
        """Get total P&L (realized + unrealized)."""
        realized = sum(pos.realized_pnl for pos in self.position_history)
        unrealized = sum(pos.unrealized_pnl for pos in self.positions.values())
        return realized + unrealized
    
    def get_unrealized_pnl(self) -> float:
        """Get unrealized P&L."""
        return sum(pos.unrealized_pnl for pos in self.positions.values())
    
    def get_realized_pnl(self) -> float:
        """Get realized P&L."""
        return sum(pos.realized_pnl for pos in self.position_history)

class RiskManager:
    """Production risk management system."""
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.limits = RiskLimits()
        self.position_tracker = PositionTracker()
        self.emergency_stop = EmergencyStop(self)
        self.risk_metrics = None
        self.alert_callbacks = []
        self.monitoring_task = None
        self.running = False
        
        # Performance tracking
        self.daily_pnl = defaultdict(float)
        self.max_equity = initial_capital
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        
        # Register emergency stop callbacks
        self.emergency_stop.register_callback(self.close_all_positions)
        self.emergency_stop.register_callback(self.notify_emergency)
    
    async def start_monitoring(self):
        """Start real-time risk monitoring."""
        self.running = True
        self.monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("Risk monitoring started")
    
    async def stop_monitoring(self):
        """Stop risk monitoring."""
        self.running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logger.info("Risk monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Update risk metrics
                await self.update_risk_metrics()
                
                # Check risk limits
                await self.check_risk_limits()
                
                # Update drawdown
                self._update_drawdown()
                
                # Sleep for monitoring interval
                await asyncio.sleep(1)  # 1 second monitoring interval
                
            except Exception as e:
                logger.error(f"Risk monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def update_risk_metrics(self):
        """Update risk metrics."""
        try:
            # Calculate basic metrics
            total_pnl = self.position_tracker.get_total_pnl()
            unrealized_pnl = self.position_tracker.get_unrealized_pnl()
            realized_pnl = self.position_tracker.get_realized_pnl()
            total_exposure = self.position_tracker.get_total_exposure()
            
            # Calculate returns for risk metrics
            returns = self._calculate_returns()
            
            if len(returns) > 0:
                # Calculate risk metrics
                volatility = np.std(returns) * np.sqrt(252)  # Annualized
                var_95 = np.percentile(returns, 5)
                cvar_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else 0
                
                # Calculate Sharpe ratio (assuming risk-free rate of 2%)
                risk_free_rate = 0.02 / 252  # Daily risk-free rate
                excess_returns = returns - risk_free_rate
                sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) > 0 else 0
                
                # Calculate beta (simplified - would need market data)
                beta = 1.0  # Placeholder
                
                # Calculate correlation (simplified)
                correlation = 0.0  # Placeholder
            else:
                volatility = var_95 = cvar_95 = sharpe_ratio = beta = correlation = 0.0
            
            # Update current capital
            self.current_capital = self.initial_capital + total_pnl
            
            # Create risk metrics
            self.risk_metrics = RiskMetrics(
                total_pnl=total_pnl,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl,
                total_exposure=total_exposure,
                max_drawdown=self.max_drawdown,
                current_drawdown=self.current_drawdown,
                var_95=var_95,
                cvar_95=cvar_95,
                sharpe_ratio=sharpe_ratio,
                volatility=volatility,
                beta=beta,
                correlation=correlation,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error updating risk metrics: {e}")
    
    async def check_risk_limits(self):
        """Check all risk limits."""
        if not self.risk_metrics:
            return
        
        # Check drawdown limit
        if self.current_drawdown > self.limits.max_drawdown:
            await self.emergency_stop.trigger(f"Max drawdown exceeded: {self.current_drawdown:.2%}")
            return
        
        # Check daily loss limit
        today = datetime.now(timezone.utc).date()
        daily_pnl = self.daily_pnl.get(today, 0)
        daily_loss_pct = abs(daily_pnl) / self.initial_capital if daily_pnl < 0 else 0
        
        if daily_loss_pct > self.limits.max_daily_loss:
            await self.emergency_stop.trigger(f"Daily loss limit exceeded: {daily_loss_pct:.2%}")
            return
        
        # Check VaR limit
        if abs(self.risk_metrics.var_95) > self.limits.max_var:
            await self._send_alert(RiskLevel.HIGH, f"VaR limit exceeded: {self.risk_metrics.var_95:.2%}")
        
        # Check volatility limit
        if self.risk_metrics.volatility > self.limits.max_volatility:
            await self._send_alert(RiskLevel.MEDIUM, f"High volatility: {self.risk_metrics.volatility:.2%}")
        
        # Check Sharpe ratio
        if self.risk_metrics.sharpe_ratio < self.limits.min_sharpe:
            await self._send_alert(RiskLevel.MEDIUM, f"Low Sharpe ratio: {self.risk_metrics.sharpe_ratio:.2f}")
    
    def _update_drawdown(self):
        """Update drawdown calculations."""
        if self.current_capital > self.max_equity:
            self.max_equity = self.current_capital
        
        self.current_drawdown = (self.max_equity - self.current_capital) / self.max_equity
        
        if self.current_drawdown > self.max_drawdown:
            self.max_drawdown = self.current_drawdown
    
    def _calculate_returns(self) -> np.ndarray:
        """Calculate historical returns."""
        if len(self.position_tracker.pnl_history) < 2:
            return np.array([])
        
        # Calculate daily returns from P&L history
        daily_pnl = defaultdict(float)
        for pnl_record in self.position_tracker.pnl_history:
            date = pnl_record["exit_time"].date()
            daily_pnl[date] += pnl_record["realized_pnl"]
        
        # Convert to returns
        dates = sorted(daily_pnl.keys())
        returns = []
        for date in dates:
            daily_return = daily_pnl[date] / self.initial_capital
            returns.append(daily_return)
        
        return np.array(returns)
    
    async def _send_alert(self, level: RiskLevel, message: str):
        """Send risk alert."""
        alert = {
            "level": level.value,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "risk_metrics": self.risk_metrics.__dict__ if self.risk_metrics else None
        }
        
        logger.warning(f"Risk alert [{level.value}]: {message}")
        
        # Execute alert callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def register_alert_callback(self, callback: Callable):
        """Register alert callback."""
        self.alert_callbacks.append(callback)
    
    async def close_all_positions(self, reason: str):
        """Close all positions (emergency stop)."""
        logger.critical(f"Closing all positions due to: {reason}")
        
        # This would integrate with order execution system
        # For now, just log the action
        for symbol in list(self.position_tracker.positions.keys()):
            logger.info(f"Emergency close position: {symbol}")
    
    async def notify_emergency(self, reason: str):
        """Notify emergency stop."""
        # This would send notifications (email, SMS, etc.)
        logger.critical(f"EMERGENCY NOTIFICATION: {reason}")
    
    def add_position(self, position: Position):
        """Add new position."""
        self.position_tracker.add_position(position)
        
        # Update daily P&L
        today = datetime.now(timezone.utc).date()
        self.daily_pnl[today] += position.unrealized_pnl
    
    def update_position_price(self, symbol: str, price: float):
        """Update position price."""
        self.position_tracker.update_position(symbol, price)
        
        # Update daily P&L
        if symbol in self.position_tracker.positions:
            position = self.position_tracker.positions[symbol]
            today = datetime.now(timezone.utc).date()
            self.daily_pnl[today] = position.unrealized_pnl
    
    def close_position(self, symbol: str, exit_price: float):
        """Close position."""
        if symbol in self.position_tracker.positions:
            position = self.position_tracker.positions[symbol]
            exit_time = datetime.now(timezone.utc)
            
            self.position_tracker.close_position(symbol, exit_price, exit_time)
            
            # Update daily P&L
            today = exit_time.date()
            self.daily_pnl[today] += position.realized_pnl
    
    def get_risk_summary(self) -> Dict[str, Any]:
        """Get risk summary."""
        if not self.risk_metrics:
            return {"error": "No risk metrics available"}
        
        return {
            "capital": {
                "initial": self.initial_capital,
                "current": self.current_capital,
                "total_pnl": self.risk_metrics.total_pnl,
                "unrealized_pnl": self.risk_metrics.unrealized_pnl,
                "realized_pnl": self.risk_metrics.realized_pnl
            },
            "exposure": {
                "total_exposure": self.risk_metrics.total_exposure,
                "exposure_pct": self.risk_metrics.total_exposure / self.current_capital if self.current_capital > 0 else 0,
                "active_positions": len(self.position_tracker.positions)
            },
            "risk_metrics": {
                "max_drawdown": self.risk_metrics.max_drawdown,
                "current_drawdown": self.risk_metrics.current_drawdown,
                "var_95": self.risk_metrics.var_95,
                "cvar_95": self.risk_metrics.cvar_95,
                "sharpe_ratio": self.risk_metrics.sharpe_ratio,
                "volatility": self.risk_metrics.volatility,
                "beta": self.risk_metrics.beta,
                "correlation": self.risk_metrics.correlation
            },
            "limits": {
                "max_drawdown": self.limits.max_drawdown,
                "max_daily_loss": self.limits.max_daily_loss,
                "max_position_size": self.limits.max_position_size,
                "max_total_exposure": self.limits.max_total_exposure
            },
            "emergency_stop": {
                "triggered": self.emergency_stop.triggered,
                "trigger_time": self.emergency_stop.trigger_time.isoformat() if self.emergency_stop.trigger_time else None,
                "trigger_reason": self.emergency_stop.trigger_reason
            },
            "timestamp": self.risk_metrics.timestamp.isoformat()
        }
    
    def get_positions_summary(self) -> List[Dict[str, Any]]:
        """Get positions summary."""
        positions = []
        for symbol, position in self.position_tracker.positions.items():
            positions.append({
                "symbol": symbol,
                "side": position.side.value,
                "size": position.size,
                "entry_price": position.entry_price,
                "current_price": position.current_price,
                "unrealized_pnl": position.unrealized_pnl,
                "entry_time": position.entry_time.isoformat(),
                "duration_hours": (datetime.now(timezone.utc) - position.entry_time).total_seconds() / 3600
            })
        return positions

# Global instance
risk_manager = RiskManager()
