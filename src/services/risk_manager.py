"""
Risk management service for the trading system.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np
import pandas as pd
from scipy import stats
import structlog

from src.core.config import settings
from src.core.logging import TradingLogger
from src.models.trade import Trade
from src.models.position import Position
from src.models.portfolio import Portfolio


@dataclass
class RiskMetrics:
    """Risk metrics for portfolio."""
    total_pnl: float
    daily_pnl: float
    max_drawdown: float
    current_drawdown: float
    var_95: float
    var_99: float
    sharpe_ratio: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    correlation_matrix: pd.DataFrame
    leverage: float
    margin_utilization: float


@dataclass
class RiskAlert:
    """Risk alert structure."""
    type: str
    severity: str  # low, medium, high, critical
    message: str
    timestamp: datetime
    data: Dict


class RiskManager:
    """Comprehensive risk management system."""
    
    def __init__(self):
        self.logger = TradingLogger("risk_manager")
        self.portfolio = Portfolio()
        self.alerts: List[RiskAlert] = []
        self.is_running = False
        self.emergency_stop = False
        
        # Risk limits from config
        self.max_drawdown_limit = settings.risk.max_drawdown_pct / 100
        self.per_trade_risk_limit = settings.risk.per_trade_risk_pct / 100
        self.daily_loss_limit = settings.risk.daily_loss_limit_pct / 100
        self.max_leverage_limit = settings.risk.max_leverage
        self.var_limit = settings.risk.var_limit_pct / 100
        self.correlation_limit = settings.risk.correlation_limit
        self.max_positions_per_strategy = settings.risk.max_positions_per_strategy
        self.max_total_positions = settings.risk.max_total_positions
    
    async def start(self):
        """Start the risk manager."""
        self.is_running = True
        self.logger.logger.info("Risk manager started")
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop(self):
        """Stop the risk manager."""
        self.is_running = False
        self.logger.logger.info("Risk manager stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                # Calculate risk metrics
                metrics = await self.calculate_risk_metrics()
                
                # Check risk limits
                await self._check_risk_limits(metrics)
                
                # Update portfolio
                await self._update_portfolio()
                
                # Sleep for monitoring interval
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                self.logger.logger.error("Risk monitoring error", error=str(e))
                await asyncio.sleep(5)
    
    async def calculate_risk_metrics(self) -> RiskMetrics:
        """Calculate comprehensive risk metrics."""
        try:
            # Get current positions and trades
            positions = await self._get_current_positions()
            trades = await self._get_recent_trades()
            
            # Calculate basic metrics
            total_pnl = sum(pos.unrealized_pnl for pos in positions)
            daily_pnl = await self._calculate_daily_pnl()
            
            # Calculate drawdown
            equity_curve = await self._get_equity_curve()
            max_drawdown, current_drawdown = self._calculate_drawdown(equity_curve)
            
            # Calculate VaR
            var_95, var_99 = self._calculate_var(trades)
            
            # Calculate Sharpe ratio
            sharpe_ratio = self._calculate_sharpe_ratio(trades)
            
            # Calculate Calmar ratio
            calmar_ratio = self._calculate_calmar_ratio(total_pnl, max_drawdown)
            
            # Calculate win rate and profit factor
            win_rate, profit_factor = self._calculate_trading_metrics(trades)
            
            # Calculate correlation matrix
            correlation_matrix = self._calculate_correlation_matrix(positions)
            
            # Calculate leverage and margin
            leverage = self._calculate_leverage(positions)
            margin_utilization = self._calculate_margin_utilization(positions)
            
            return RiskMetrics(
                total_pnl=total_pnl,
                daily_pnl=daily_pnl,
                max_drawdown=max_drawdown,
                current_drawdown=current_drawdown,
                var_95=var_95,
                var_99=var_99,
                sharpe_ratio=sharpe_ratio,
                calmar_ratio=calmar_ratio,
                win_rate=win_rate,
                profit_factor=profit_factor,
                correlation_matrix=correlation_matrix,
                leverage=leverage,
                margin_utilization=margin_utilization
            )
            
        except Exception as e:
            self.logger.logger.error("Error calculating risk metrics", error=str(e))
            raise
    
    async def _check_risk_limits(self, metrics: RiskMetrics):
        """Check all risk limits and trigger alerts if needed."""
        alerts = []
        
        # Check drawdown limit
        if metrics.current_drawdown > self.max_drawdown_limit:
            alerts.append(RiskAlert(
                type="drawdown_limit",
                severity="critical",
                message=f"Drawdown limit exceeded: {metrics.current_drawdown:.2%}",
                timestamp=datetime.utcnow(),
                data={"current_drawdown": metrics.current_drawdown, "limit": self.max_drawdown_limit}
            ))
        
        # Check daily loss limit
        if metrics.daily_pnl < -self.daily_loss_limit:
            alerts.append(RiskAlert(
                type="daily_loss_limit",
                severity="high",
                message=f"Daily loss limit exceeded: {metrics.daily_pnl:.2%}",
                timestamp=datetime.utcnow(),
                data={"daily_pnl": metrics.daily_pnl, "limit": -self.daily_loss_limit}
            ))
        
        # Check VaR limit
        if abs(metrics.var_95) > self.var_limit:
            alerts.append(RiskAlert(
                type="var_limit",
                severity="high",
                message=f"VaR limit exceeded: {metrics.var_95:.2%}",
                timestamp=datetime.utcnow(),
                data={"var_95": metrics.var_95, "limit": self.var_limit}
            ))
        
        # Check leverage limit
        if metrics.leverage > self.max_leverage_limit:
            alerts.append(RiskAlert(
                type="leverage_limit",
                severity="high",
                message=f"Leverage limit exceeded: {metrics.leverage:.2f}x",
                timestamp=datetime.utcnow(),
                data={"leverage": metrics.leverage, "limit": self.max_leverage_limit}
            ))
        
        # Check correlation limit
        high_correlations = self._check_correlation_limits(metrics.correlation_matrix)
        if high_correlations:
            alerts.append(RiskAlert(
                type="correlation_limit",
                severity="medium",
                message=f"High correlations detected: {high_correlations}",
                timestamp=datetime.utcnow(),
                data={"correlations": high_correlations}
            ))
        
        # Process alerts
        for alert in alerts:
            await self._process_alert(alert)
    
    async def _process_alert(self, alert: RiskAlert):
        """Process a risk alert."""
        self.alerts.append(alert)
        self.logger.risk_alert({
            "type": alert.type,
            "severity": alert.severity,
            "message": alert.message,
            "timestamp": alert.timestamp.isoformat()
        })
        
        # Take action based on severity
        if alert.severity == "critical":
            await self._emergency_stop_trading()
        elif alert.severity == "high":
            await self._reduce_risk_exposure()
        elif alert.severity == "medium":
            await self._send_notification(alert)
    
    async def _emergency_stop_trading(self):
        """Emergency stop all trading."""
        self.emergency_stop = True
        self.logger.emergency_action({
            "type": "emergency_stop",
            "reason": "Risk limit exceeded",
            "user": "system",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Close all positions
        await self._close_all_positions()
        
        # Cancel all orders
        await self._cancel_all_orders()
    
    async def _reduce_risk_exposure(self):
        """Reduce risk exposure by closing some positions."""
        positions = await self._get_current_positions()
        
        # Sort by risk (largest positions first)
        positions.sort(key=lambda x: abs(x.unrealized_pnl), reverse=True)
        
        # Close top 50% of positions
        positions_to_close = positions[:len(positions)//2]
        
        for position in positions_to_close:
            await self._close_position(position)
    
    async def validate_trade(self, trade: Trade) -> Tuple[bool, str]:
        """Validate a trade against risk limits."""
        try:
            # Check if emergency stop is active
            if self.emergency_stop:
                return False, "Emergency stop active"
            
            # Check position limits
            if not await self._check_position_limits(trade):
                return False, "Position limit exceeded"
            
            # Check risk per trade
            if not await self._check_trade_risk(trade):
                return False, "Trade risk limit exceeded"
            
            # Check correlation limits
            if not await self._check_correlation_limits_for_trade(trade):
                return False, "Correlation limit exceeded"
            
            # Check leverage limits
            if not await self._check_leverage_limits(trade):
                return False, "Leverage limit exceeded"
            
            return True, "Trade validated"
            
        except Exception as e:
            self.logger.logger.error("Trade validation error", error=str(e))
            return False, f"Validation error: {str(e)}"
    
    async def _check_position_limits(self, trade: Trade) -> bool:
        """Check position limits."""
        current_positions = await self._get_current_positions()
        
        # Check total positions limit
        if len(current_positions) >= self.max_total_positions:
            return False
        
        # Check positions per strategy
        strategy_positions = [p for p in current_positions if p.strategy == trade.strategy]
        if len(strategy_positions) >= self.max_positions_per_strategy:
            return False
        
        return True
    
    async def _check_trade_risk(self, trade: Trade) -> bool:
        """Check individual trade risk."""
        account_balance = await self._get_account_balance()
        trade_risk_amount = abs(trade.size * trade.price * self.per_trade_risk_limit)
        
        return trade_risk_amount <= account_balance * self.per_trade_risk_limit
    
    async def _check_correlation_limits_for_trade(self, trade: Trade) -> bool:
        """Check correlation limits for a new trade."""
        current_positions = await self._get_current_positions()
        
        # Get correlation with existing positions
        for position in current_positions:
            correlation = self._calculate_pair_correlation(trade.pair, position.pair)
            if abs(correlation) > self.correlation_limit:
                return False
        
        return True
    
    async def _check_leverage_limits(self, trade: Trade) -> bool:
        """Check leverage limits."""
        current_positions = await self._get_current_positions()
        account_balance = await self._get_account_balance()
        
        # Calculate current leverage
        total_exposure = sum(abs(p.size * p.price) for p in current_positions)
        new_exposure = total_exposure + abs(trade.size * trade.price)
        
        leverage = new_exposure / account_balance
        
        return leverage <= self.max_leverage_limit
    
    def _calculate_drawdown(self, equity_curve: List[float]) -> Tuple[float, float]:
        """Calculate maximum and current drawdown."""
        if not equity_curve:
            return 0.0, 0.0
        
        peak = equity_curve[0]
        max_drawdown = 0.0
        current_drawdown = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            else:
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
                current_drawdown = drawdown
        
        return max_drawdown, current_drawdown
    
    def _calculate_var(self, trades: List[Trade], confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate Value at Risk."""
        if not trades:
            return 0.0, 0.0
        
        returns = [trade.pnl for trade in trades if trade.pnl is not None]
        
        if not returns:
            return 0.0, 0.0
        
        # Calculate VaR using historical simulation
        var_95 = np.percentile(returns, 5)  # 95% VaR
        var_99 = np.percentile(returns, 1)  # 99% VaR
        
        return var_95, var_99
    
    def _calculate_sharpe_ratio(self, trades: List[Trade], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if not trades:
            return 0.0
        
        returns = [trade.pnl for trade in trades if trade.pnl is not None]
        
        if not returns:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        return (mean_return - risk_free_rate) / std_return
    
    def _calculate_calmar_ratio(self, total_pnl: float, max_drawdown: float) -> float:
        """Calculate Calmar ratio."""
        if max_drawdown == 0:
            return 0.0
        
        return total_pnl / max_drawdown
    
    def _calculate_trading_metrics(self, trades: List[Trade]) -> Tuple[float, float]:
        """Calculate win rate and profit factor."""
        if not trades:
            return 0.0, 0.0
        
        winning_trades = [t for t in trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl and t.pnl < 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0.0
        
        total_profit = sum(t.pnl for t in winning_trades)
        total_loss = abs(sum(t.pnl for t in losing_trades))
        
        profit_factor = total_profit / total_loss if total_loss > 0 else 0.0
        
        return win_rate, profit_factor
    
    def _calculate_correlation_matrix(self, positions: List[Position]) -> pd.DataFrame:
        """Calculate correlation matrix for positions."""
        if not positions:
            return pd.DataFrame()
        
        # Get price data for all pairs
        price_data = {}
        for position in positions:
            # This would fetch actual price data
            # For now, return empty DataFrame
            pass
        
        return pd.DataFrame()
    
    def _check_correlation_limits(self, correlation_matrix: pd.DataFrame) -> List[str]:
        """Check correlation limits and return high correlations."""
        high_correlations = []
        
        if correlation_matrix.empty:
            return high_correlations
        
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr = correlation_matrix.iloc[i, j]
                if abs(corr) > self.correlation_limit:
                    pair1 = correlation_matrix.columns[i]
                    pair2 = correlation_matrix.columns[j]
                    high_correlations.append(f"{pair1}-{pair2}: {corr:.3f}")
        
        return high_correlations
    
    def _calculate_pair_correlation(self, pair1: str, pair2: str) -> float:
        """Calculate correlation between two currency pairs."""
        # This would fetch historical data and calculate correlation
        # For now, return 0
        return 0.0
    
    def _calculate_leverage(self, positions: List[Position]) -> float:
        """Calculate current leverage."""
        account_balance = 10000  # This would get actual balance
        total_exposure = sum(abs(p.size * p.price) for p in positions)
        
        return total_exposure / account_balance if account_balance > 0 else 0.0
    
    def _calculate_margin_utilization(self, positions: List[Position]) -> float:
        """Calculate margin utilization."""
        # This would calculate actual margin usage
        return 0.0
    
    # Placeholder methods for external integrations
    async def _get_current_positions(self) -> List[Position]:
        """Get current positions."""
        return []
    
    async def _get_recent_trades(self) -> List[Trade]:
        """Get recent trades."""
        return []
    
    async def _calculate_daily_pnl(self) -> float:
        """Calculate daily P&L."""
        return 0.0
    
    async def _get_equity_curve(self) -> List[float]:
        """Get equity curve."""
        return []
    
    async def _update_portfolio(self):
        """Update portfolio."""
        pass
    
    async def _close_all_positions(self):
        """Close all positions."""
        pass
    
    async def _cancel_all_orders(self):
        """Cancel all orders."""
        pass
    
    async def _close_position(self, position: Position):
        """Close a specific position."""
        pass
    
    async def _get_account_balance(self) -> float:
        """Get account balance."""
        return 10000.0
    
    async def _send_notification(self, alert: RiskAlert):
        """Send notification for alert."""
        pass
