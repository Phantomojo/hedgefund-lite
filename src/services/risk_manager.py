"""
Real-time Risk Management System
Monitors positions, enforces risk limits, and provides emergency controls
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from src.services.trading_engine import trading_engine

logger = logging.getLogger(__name__)

class RiskManager:
    """Real-time risk management system for live trading"""
    
    def __init__(self):
        # Risk limits configuration
        self.max_drawdown = 0.15  # 15% maximum drawdown
        self.max_risk_per_trade = 0.02  # 2% risk per trade
        self.max_total_risk = 0.06  # 6% total risk
        self.max_positions = 10
        self.correlation_limit = 0.7
        
        # Risk monitoring state
        self.current_drawdown = 0.0
        self.total_risk = 0.0
        self.position_count = 0
        self.risk_alerts = []
        self.last_check = datetime.now()
        
        # Alert thresholds
        self.position_loss_threshold = 0.01  # 1% position loss triggers alert
        self.account_loss_threshold = 0.05   # 5% account loss triggers alert
        
        logger.info("Risk Manager initialized with protective limits")
    
    async def check_position_risk(self, pair: str, units: int, 
                                 current_price: float, account_balance: float) -> Dict[str, Any]:
        """Check risk for a new position before placing"""
        try:
            # Calculate position value
            position_value = abs(units) * current_price
            position_risk = position_value / account_balance
            
            # Check individual position risk
            if position_risk > self.max_risk_per_trade:
                return {
                    "approved": False,
                    "reason": f"Position risk {position_risk:.2%} exceeds maximum {self.max_risk_per_trade:.2%}",
                    "position_risk": position_risk,
                    "max_allowed": self.max_risk_per_trade
                }
            
            # Check total risk
            current_positions = await trading_engine.get_positions()
            if current_positions["success"]:
                total_exposure = 0
                for pos in current_positions["positions"]:
                    if pos["long_units"] > 0:
                        total_exposure += pos["long_units"] * float(pos["long_avg_price"])
                    if pos["short_units"] > 0:
                        total_exposure += pos["short_units"] * float(pos["short_avg_price"])
                
                new_total_risk = (total_exposure + position_value) / account_balance
                
                if new_total_risk > self.max_total_risk:
                    return {
                        "approved": False,
                        "reason": f"Total risk {new_total_risk:.2%} would exceed maximum {self.max_total_risk:.2%}",
                        "total_risk": new_total_risk,
                        "max_allowed": self.max_total_risk
                    }
            
            # Check position count
            if self.position_count >= self.max_positions:
                return {
                    "approved": False,
                    "reason": f"Maximum positions {self.max_positions} reached",
                    "current_count": self.position_count
                }
            
            return {
                "approved": True,
                "position_risk": position_risk,
                "total_risk": new_total_risk if 'new_total_risk' in locals() else position_risk,
                "message": "Position risk check passed"
            }
            
        except Exception as e:
            logger.error(f"Risk check error: {str(e)}")
            return {
                "approved": False,
                "reason": f"Risk check error: {str(e)}"
            }
    
    async def monitor_positions(self) -> Dict[str, Any]:
        """Monitor all positions for risk violations"""
        try:
            positions = await trading_engine.get_positions()
            
            if not positions["success"]:
                return {"error": "Failed to get positions for monitoring"}
            
            alerts = []
            total_pnl = 0.0
            total_exposure = 0.0
            
            for position in positions["positions"]:
                pair = position["instrument"]
                long_units = position["long_units"]
                short_units = position["short_units"]
                
                # Check long positions
                if long_units > 0:
                    long_pnl = position["long_pnl"]
                    long_avg_price = float(position["long_avg_price"])
                    total_exposure += long_units * long_avg_price
                    total_pnl += long_pnl
                    
                    # Calculate percentage loss
                    if long_pnl < 0:
                        position_value = long_units * long_avg_price
                        loss_pct = abs(long_pnl) / position_value
                        
                        if loss_pct > self.position_loss_threshold:
                            alerts.append({
                                "type": "position_loss",
                                "severity": "high" if loss_pct > 0.05 else "medium",
                                "pair": pair,
                                "side": "long",
                                "units": long_units,
                                "loss_pct": loss_pct,
                                "loss_amount": long_pnl,
                                "message": f"Long position in {pair} has {loss_pct:.2%} loss (${abs(long_pnl):.2f})"
                            })
                
                # Check short positions
                if short_units > 0:
                    short_pnl = position["short_pnl"]
                    short_avg_price = float(position["short_avg_price"])
                    total_exposure += short_units * short_avg_price
                    total_pnl += short_pnl
                    
                    # Calculate percentage loss
                    if short_pnl < 0:
                        position_value = short_units * short_avg_price
                        loss_pct = abs(short_pnl) / position_value
                        
                        if loss_pct > self.position_loss_threshold:
                            alerts.append({
                                "type": "position_loss",
                                "severity": "high" if loss_pct > 0.05 else "medium",
                                "pair": pair,
                                "side": "short",
                                "units": short_units,
                                "loss_pct": loss_pct,
                                "loss_amount": short_pnl,
                                "message": f"Short position in {pair} has {loss_pct:.2%} loss (${abs(short_pnl):.2f})"
                            })
            
            # Get account summary for overall risk assessment
            account = await trading_engine.get_account_summary()
            if account["success"]:
                account_balance = account["balance"]
                account_pnl = account["unrealized_pnl"]
                
                # Calculate account drawdown
                if account_pnl < 0:
                    drawdown_pct = abs(account_pnl) / account_balance
                    if drawdown_pct > self.account_loss_threshold:
                        alerts.append({
                            "type": "account_loss",
                            "severity": "critical" if drawdown_pct > 0.10 else "high",
                            "drawdown_pct": drawdown_pct,
                            "loss_amount": account_pnl,
                            "message": f"Account has {drawdown_pct:.2%} drawdown (${abs(account_pnl):.2f})"
                        })
                
                # Calculate total portfolio risk
                total_risk = total_exposure / account_balance if account_balance > 0 else 0
                
                return {
                    "alerts": alerts,
                    "position_count": len(positions["positions"]),
                    "total_pnl": total_pnl,
                    "total_exposure": total_exposure,
                    "total_risk": total_risk,
                    "account_balance": account_balance,
                    "account_pnl": account_pnl,
                    "drawdown_pct": abs(account_pnl) / account_balance if account_pnl < 0 else 0,
                    "timestamp": datetime.now().isoformat(),
                    "risk_level": self._calculate_risk_level(alerts, total_risk)
                }
            else:
                return {
                    "alerts": alerts,
                    "position_count": len(positions["positions"]),
                    "total_pnl": total_pnl,
                    "total_exposure": total_exposure,
                    "error": "Failed to get account summary",
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Position monitoring error: {str(e)}")
            return {"error": f"Monitoring error: {str(e)}"}
    
    def _calculate_risk_level(self, alerts: List[Dict], total_risk: float) -> str:
        """Calculate overall risk level based on alerts and exposure"""
        if any(alert["severity"] == "critical" for alert in alerts):
            return "CRITICAL"
        elif any(alert["severity"] == "high" for alert in alerts):
            return "HIGH"
        elif total_risk > self.max_total_risk * 0.8:  # 80% of max risk
            return "ELEVATED"
        elif alerts:
            return "MEDIUM"
        else:
            return "LOW"
    
    async def check_stop_loss_triggers(self) -> Dict[str, Any]:
        """Check if any positions need automatic stop-loss execution"""
        try:
            positions = await trading_engine.get_positions()
            
            if not positions["success"]:
                return {"error": "Failed to get positions for stop-loss check"}
            
            triggered_stops = []
            
            for position in positions["positions"]:
                pair = position["instrument"]
                long_units = position["long_units"]
                short_units = position["short_units"]
                
                # Check long positions for stop-loss
                if long_units > 0:
                    long_pnl = position["long_pnl"]
                    long_avg_price = float(position["long_avg_price"])
                    
                    # Calculate percentage loss
                    if long_pnl < 0:
                        loss_pct = abs(long_pnl) / (long_units * long_avg_price)
                        
                        # Auto-stop if loss exceeds 5%
                        if loss_pct > 0.05:
                            triggered_stops.append({
                                "pair": pair,
                                "side": "long",
                                "units": long_units,
                                "loss_pct": loss_pct,
                                "loss_amount": long_pnl,
                                "action": "auto_stop_loss"
                            })
                
                # Check short positions for stop-loss
                if short_units > 0:
                    short_pnl = position["short_pnl"]
                    short_avg_price = float(position["short_avg_price"])
                    
                    # Calculate percentage loss
                    if short_pnl < 0:
                        loss_pct = abs(short_pnl) / (short_units * short_avg_price)
                        
                        # Auto-stop if loss exceeds 5%
                        if loss_pct > 0.05:
                            triggered_stops.append({
                                "pair": pair,
                                "side": "short",
                                "units": short_units,
                                "loss_pct": loss_pct,
                                "loss_amount": short_pnl,
                                "action": "auto_stop_loss"
                            })
            
            return {
                "triggered_stops": triggered_stops,
                "count": len(triggered_stops),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Stop-loss check error: {str(e)}")
            return {"error": f"Stop-loss check error: {str(e)}"}
    
    async def emergency_stop(self) -> Dict[str, Any]:
        """Emergency stop all trading - close all positions immediately"""
        try:
            logger.warning("🚨 EMERGENCY STOP INITIATED - Closing all positions immediately")
            
            # Get current positions
            positions_result = await trading_engine.get_positions()
            
            if not positions_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to get positions for emergency stop"
                }
            
            closed_positions = []
            errors = []
            
            for position in positions_result["positions"]:
                pair = position["instrument"]
                
                try:
                    logger.info(f"Emergency stop: Closing position {pair}")
                    result = await trading_engine.close_position(pair)
                    
                    if result["success"]:
                        closed_positions.append(pair)
                        logger.info(f"Emergency stop: Successfully closed position {pair}")
                    else:
                        errors.append(f"Failed to close {pair}: {result.get('error')}")
                        logger.error(f"Emergency stop failed for {pair}: {result.get('error')}")
                        
                except Exception as e:
                    errors.append(f"Error closing {pair}: {str(e)}")
                    logger.error(f"Emergency stop error for {pair}: {str(e)}")
            
            # Log emergency stop completion
            if closed_positions:
                logger.warning(f"🚨 Emergency stop completed. Closed {len(closed_positions)} positions: {closed_positions}")
            if errors:
                logger.error(f"🚨 Emergency stop errors: {errors}")
            
            return {
                "success": True,
                "message": f"🚨 Emergency stop executed. Closed {len(closed_positions)} positions.",
                "closed_positions": closed_positions,
                "errors": errors,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"🚨 Emergency stop error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    async def get_risk_summary(self) -> Dict[str, Any]:
        """Get comprehensive risk summary"""
        try:
            # Get position monitoring data
            monitoring = await self.monitor_positions()
            
            # Get stop-loss triggers
            stop_loss = await self.check_stop_loss_triggers()
            
            # Get account summary
            account = await trading_engine.get_account_summary()
            
            return {
                "risk_level": monitoring.get("risk_level", "UNKNOWN"),
                "alerts": monitoring.get("alerts", []),
                "position_count": monitoring.get("position_count", 0),
                "total_pnl": monitoring.get("total_pnl", 0),
                "total_risk": monitoring.get("total_risk", 0),
                "drawdown_pct": monitoring.get("drawdown_pct", 0),
                "triggered_stops": stop_loss.get("triggered_stops", []),
                "account_balance": account.get("balance", 0) if account.get("success") else 0,
                "margin_used": account.get("margin_used", 0) if account.get("success") else 0,
                "margin_available": account.get("margin_available", 0) if account.get("success") else 0,
                "timestamp": datetime.now().isoformat(),
                "limits": {
                    "max_drawdown": self.max_drawdown,
                    "max_risk_per_trade": self.max_risk_per_trade,
                    "max_total_risk": self.max_total_risk,
                    "max_positions": self.max_positions
                }
            }
            
        except Exception as e:
            logger.error(f"Risk summary error: {str(e)}")
            return {"error": f"Risk summary error: {str(e)}"}


# Global risk manager instance
risk_manager = RiskManager()
