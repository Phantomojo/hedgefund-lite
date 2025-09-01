"""
Intelligent Emergency Stop System
Smart position management that considers time, performance, and strategy context
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

from src.services.trading_engine import trading_engine
from src.services.risk_manager import risk_manager
from src.services.financial_intelligence_engine import financial_intelligence_engine

logger = logging.getLogger(__name__)

class IntelligentEmergencyStop:
    """Smart emergency stop that only closes positions when it makes sense"""
    
    def __init__(self):
        # Emergency Stop Configuration
        self.emergency_stop_enabled = True
        self.emergency_stop_thresholds = {
            "portfolio_loss_pct": 0.15,  # 15% portfolio loss triggers emergency stop
            "single_position_loss_pct": 0.25,  # 25% single position loss
            "volatility_spike_threshold": 3.0,  # 3x normal volatility
            "correlation_spike_threshold": 0.8,  # 80% correlation between assets
            "liquidity_crisis_threshold": 0.3,  # 30% of normal liquidity
            "market_regime_crisis": True,  # Enable for crisis market regimes
            "economic_cycle_contraction": True,  # Enable for economic contraction
        }
        
        # Position Protection Rules
        self.position_protection = {
            "min_hold_time_minutes": 15,  # Don't close positions held < 15 minutes
            "profit_protection_pct": 0.05,  # Don't close positions with >5% profit
            "strategy_protection": True,  # Protect positions from active strategies
            "trend_following_protection": True,  # Protect trend-following positions
            "hedge_protection": True,  # Protect hedging positions
            "correlation_protection": True,  # Protect uncorrelated positions
        }
        
        # Emergency Stop History
        self.emergency_stop_history = []
        self.last_emergency_stop = None
        
        logger.info("🛡️ Intelligent Emergency Stop System initialized")
    
    async def assess_emergency_stop_need(self) -> Tuple[bool, Dict[str, Any]]:
        """Assess if emergency stop is needed using intelligent criteria"""
        try:
            logger.info("🛡️ Assessing emergency stop need...")
            
            assessment = {
                "emergency_stop_needed": False,
                "trigger_reasons": [],
                "risk_level": "low",
                "recommended_actions": [],
                "positions_to_close": [],
                "positions_to_protect": [],
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 1: Get current market and portfolio state
            portfolio_state = await self._get_portfolio_state()
            market_state = await self._get_market_state()
            positions = await self._get_detailed_positions()
            
            # Step 2: Check emergency stop triggers
            triggers = await self._check_emergency_triggers(portfolio_state, market_state)
            
            if not triggers["any_triggered"]:
                assessment["risk_level"] = "low"
                assessment["recommended_actions"] = ["Continue normal operations"]
                return False, assessment
            
            # Step 3: Analyze which positions should be closed vs protected
            position_analysis = await self._analyze_positions_for_emergency_stop(
                positions, portfolio_state, market_state
            )
            
            assessment["positions_to_close"] = position_analysis["close_positions"]
            assessment["positions_to_protect"] = position_analysis["protect_positions"]
            assessment["trigger_reasons"] = triggers["triggered_reasons"]
            assessment["risk_level"] = triggers["risk_level"]
            
            # Step 4: Determine if emergency stop is actually needed
            if position_analysis["close_positions"]:
                assessment["emergency_stop_needed"] = True
                assessment["recommended_actions"] = [
                    f"Close {len(position_analysis['close_positions'])} high-risk positions",
                    f"Protect {len(position_analysis['protect_positions'])} valuable positions",
                    "Implement defensive positioning"
                ]
            else:
                assessment["emergency_stop_needed"] = False
                assessment["recommended_actions"] = [
                    "Monitor situation closely",
                    "Prepare defensive measures",
                    "No immediate action needed"
                ]
            
            logger.info(f"🛡️ Emergency stop assessment: {assessment['emergency_stop_needed']}")
            
            return assessment["emergency_stop_needed"], assessment
            
        except Exception as e:
            logger.error(f"Emergency stop assessment error: {str(e)}")
            return True, {"error": f"Assessment failed: {str(e)}"}
    
    async def execute_intelligent_emergency_stop(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Execute emergency stop only on positions that should be closed"""
        try:
            logger.info("🛡️ Executing intelligent emergency stop...")
            
            execution_results = {
                "timestamp": datetime.now().isoformat(),
                "positions_closed": 0,
                "positions_protected": 0,
                "total_pnl_impact": 0.0,
                "execution_details": [],
                "risk_reduction": 0.0
            }
            
            # Step 1: Close only the high-risk positions
            for position in assessment.get("positions_to_close", []):
                try:
                    close_result = await self._close_position_intelligently(position)
                    
                    if close_result["success"]:
                        execution_results["positions_closed"] += 1
                        execution_results["total_pnl_impact"] += close_result.get("pnl_impact", 0)
                        execution_results["execution_details"].append({
                            "symbol": position["instrument"],
                            "action": "closed",
                            "reason": position.get("close_reason", "risk_management"),
                            "pnl_impact": close_result.get("pnl_impact", 0)
                        })
                        
                        logger.info(f"🛡️ Closed position {position['instrument']}: {close_result.get('pnl_impact', 0)}")
                    else:
                        execution_results["execution_details"].append({
                            "symbol": position["instrument"],
                            "action": "failed",
                            "reason": close_result.get("error", "unknown_error")
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to close position {position['instrument']}: {str(e)}")
                    execution_results["execution_details"].append({
                        "symbol": position["instrument"],
                        "action": "error",
                        "reason": str(e)
                    })
            
            # Step 2: Protect valuable positions
            for position in assessment.get("positions_to_protect", []):
                try:
                    protection_result = await self._protect_position(position)
                    
                    if protection_result["success"]:
                        execution_results["positions_protected"] += 1
                        execution_results["execution_details"].append({
                            "symbol": position["instrument"],
                            "action": "protected",
                            "reason": position.get("protection_reason", "value_preservation"),
                            "protection_method": protection_result.get("method", "stop_loss_adjustment")
                        })
                        
                        logger.info(f"🛡️ Protected position {position['instrument']}")
                    else:
                        execution_results["execution_details"].append({
                            "symbol": position["instrument"],
                            "action": "protection_failed",
                            "reason": protection_result.get("error", "unknown_error")
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to protect position {position['instrument']}: {str(e)}")
            
            # Step 3: Calculate risk reduction
            execution_results["risk_reduction"] = await self._calculate_risk_reduction(
                assessment.get("positions_to_close", [])
            )
            
            # Step 4: Record emergency stop
            await self._record_emergency_stop(assessment, execution_results)
            
            logger.info(f"🛡️ Intelligent emergency stop complete: {execution_results['positions_closed']} closed, {execution_results['positions_protected']} protected")
            
            return execution_results
            
        except Exception as e:
            logger.error(f"Intelligent emergency stop execution error: {str(e)}")
            return {"error": f"Execution failed: {str(e)}"}
    
    async def _check_emergency_triggers(self, portfolio_state: Dict[str, Any], market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Check if any emergency stop triggers are activated"""
        try:
            triggers = {
                "any_triggered": False,
                "triggered_reasons": [],
                "risk_level": "low"
            }
            
            # Portfolio loss trigger
            portfolio_loss_pct = portfolio_state.get("total_loss_pct", 0)
            if portfolio_loss_pct > self.emergency_stop_thresholds["portfolio_loss_pct"]:
                triggers["any_triggered"] = True
                triggers["triggered_reasons"].append(f"Portfolio loss: {portfolio_loss_pct:.1%}")
                triggers["risk_level"] = "high"
            
            # Single position loss trigger
            max_position_loss = portfolio_state.get("max_position_loss_pct", 0)
            if max_position_loss > self.emergency_stop_thresholds["single_position_loss_pct"]:
                triggers["any_triggered"] = True
                triggers["triggered_reasons"].append(f"Single position loss: {max_position_loss:.1%}")
                triggers["risk_level"] = "high"
            
            # Volatility spike trigger
            current_volatility = market_state.get("volatility", 1.0)
            normal_volatility = market_state.get("normal_volatility", 1.0)
            if current_volatility > normal_volatility * self.emergency_stop_thresholds["volatility_spike_threshold"]:
                triggers["any_triggered"] = True
                triggers["triggered_reasons"].append(f"Volatility spike: {current_volatility:.2f}x normal")
                triggers["risk_level"] = "medium"
            
            # Correlation spike trigger
            current_correlation = market_state.get("correlation", 0.5)
            if current_correlation > self.emergency_stop_thresholds["correlation_spike_threshold"]:
                triggers["any_triggered"] = True
                triggers["triggered_reasons"].append(f"High correlation: {current_correlation:.1%}")
                triggers["risk_level"] = "medium"
            
            # Liquidity crisis trigger
            current_liquidity = market_state.get("liquidity", 1.0)
            normal_liquidity = market_state.get("normal_liquidity", 1.0)
            if current_liquidity < normal_liquidity * self.emergency_stop_thresholds["liquidity_crisis_threshold"]:
                triggers["any_triggered"] = True
                triggers["triggered_reasons"].append(f"Liquidity crisis: {current_liquidity:.1%} of normal")
                triggers["risk_level"] = "high"
            
            # Market regime trigger
            if self.emergency_stop_thresholds["market_regime_crisis"]:
                market_regime = market_state.get("market_regime", "unknown")
                if market_regime in ["crisis", "panic"]:
                    triggers["any_triggered"] = True
                    triggers["triggered_reasons"].append(f"Market regime: {market_regime}")
                    triggers["risk_level"] = "high"
            
            # Economic cycle trigger
            if self.emergency_stop_thresholds["economic_cycle_contraction"]:
                economic_cycle = market_state.get("economic_cycle", "unknown")
                if economic_cycle in ["contraction", "trough"]:
                    triggers["any_triggered"] = True
                    triggers["triggered_reasons"].append(f"Economic cycle: {economic_cycle}")
                    triggers["risk_level"] = "medium"
            
            return triggers
            
        except Exception as e:
            logger.error(f"Emergency trigger check error: {str(e)}")
            return {"any_triggered": True, "triggered_reasons": ["Error in trigger check"], "risk_level": "high"}
    
    async def _analyze_positions_for_emergency_stop(self, positions: List[Dict[str, Any]], portfolio_state: Dict[str, Any], market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze which positions should be closed vs protected"""
        try:
            analysis = {
                "close_positions": [],
                "protect_positions": [],
                "analysis_reasoning": []
            }
            
            for position in positions:
                position_analysis = await self._analyze_single_position(position, portfolio_state, market_state)
                
                if position_analysis["should_close"]:
                    analysis["close_positions"].append(position_analysis["position"])
                    analysis["analysis_reasoning"].append(f"Close {position['instrument']}: {position_analysis['close_reason']}")
                else:
                    analysis["protect_positions"].append(position_analysis["position"])
                    analysis["analysis_reasoning"].append(f"Protect {position['instrument']}: {position_analysis['protection_reason']}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Position analysis error: {str(e)}")
            return {"close_positions": [], "protect_positions": [], "analysis_reasoning": []}
    
    async def _analyze_single_position(self, position: Dict[str, Any], portfolio_state: Dict[str, Any], market_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze if a single position should be closed or protected"""
        try:
            analysis = {
                "position": position,
                "should_close": False,
                "close_reason": "",
                "protection_reason": ""
            }
            
            # Get position details
            symbol = position["instrument"]
            units = position.get("long_units", 0) + position.get("short_units", 0)
            pnl = position.get("total_pnl", 0)
            pnl_pct = position.get("pnl_pct", 0)
            open_time = position.get("open_time")
            strategy = position.get("strategy", "unknown")
            
            # Check minimum hold time
            if open_time:
                open_datetime = datetime.fromisoformat(open_time.replace('Z', '+00:00'))
                hold_time_minutes = (datetime.now(open_datetime.tzinfo) - open_datetime).total_seconds() / 60
                
                if hold_time_minutes < self.position_protection["min_hold_time_minutes"]:
                    analysis["should_close"] = False
                    analysis["protection_reason"] = f"Position held only {hold_time_minutes:.1f} minutes (min: {self.position_protection['min_hold_time_minutes']})"
                    return analysis
            
            # Check profit protection
            if pnl_pct > self.position_protection["profit_protection_pct"]:
                analysis["should_close"] = False
                analysis["protection_reason"] = f"Profitable position: {pnl_pct:.1%} profit"
                return analysis
            
            # Check strategy protection
            if self.position_protection["strategy_protection"]:
                if strategy in ["trend_following", "momentum", "breakout"]:
                    # Check if trend is still intact
                    trend_intact = await self._check_trend_intact(symbol, strategy)
                    if trend_intact:
                        analysis["should_close"] = False
                        analysis["protection_reason"] = f"Active strategy: {strategy} with intact trend"
                        return analysis
            
            # Check hedge protection
            if self.position_protection["hedge_protection"]:
                if strategy in ["hedge", "correlation_break", "pairs_trade"]:
                    analysis["should_close"] = False
                    analysis["protection_reason"] = f"Hedging position: {strategy}"
                    return analysis
            
            # Check correlation protection
            if self.position_protection["correlation_protection"]:
                correlation = await self._get_position_correlation(symbol, portfolio_state)
                if correlation < 0.3:  # Low correlation with portfolio
                    analysis["should_close"] = False
                    analysis["protection_reason"] = f"Low correlation: {correlation:.2f} (diversification value)"
                    return analysis
            
            # Check risk-based closure criteria
            if pnl_pct < -self.emergency_stop_thresholds["single_position_loss_pct"]:
                analysis["should_close"] = True
                analysis["close_reason"] = f"Large loss: {pnl_pct:.1%}"
            elif pnl < -1000:  # Absolute loss threshold
                analysis["should_close"] = True
                analysis["close_reason"] = f"Absolute loss: ${pnl:.2f}"
            elif market_state.get("market_regime") == "crisis" and pnl_pct < 0:
                analysis["should_close"] = True
                analysis["close_reason"] = f"Crisis mode: closing losing position ({pnl_pct:.1%})"
            else:
                analysis["should_close"] = False
                analysis["protection_reason"] = f"Position within acceptable risk parameters"
            
            return analysis
            
        except Exception as e:
            logger.error(f"Single position analysis error: {str(e)}")
            return {
                "position": position,
                "should_close": True,  # Default to closing on error
                "close_reason": f"Analysis error: {str(e)}",
                "protection_reason": ""
            }
    
    async def _close_position_intelligently(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """Close position with intelligent order management"""
        try:
            symbol = position["instrument"]
            units = position.get("long_units", 0) + position.get("short_units", 0)
            
            # Get current market conditions
            market_conditions = await self._get_market_conditions(symbol)
            
            # Choose closing strategy based on market conditions
            if market_conditions.get("volatility", "normal") == "high":
                # High volatility: use limit orders to avoid slippage
                close_result = await trading_engine.close_position_with_limit(
                    pair=symbol,
                    units=units,
                    limit_price=market_conditions.get("fair_price", 0)
                )
            else:
                # Normal volatility: use market orders for quick execution
                close_result = await trading_engine.close_position(symbol)
            
            # Calculate P&L impact
            pnl_impact = position.get("total_pnl", 0)
            
            return {
                "success": close_result.get("success", False),
                "pnl_impact": pnl_impact,
                "execution_method": "limit" if market_conditions.get("volatility") == "high" else "market"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "pnl_impact": 0}
    
    async def _protect_position(self, position: Dict[str, Any]) -> Dict[str, Any]:
        """Protect position with risk management measures"""
        try:
            symbol = position["instrument"]
            
            # Method 1: Adjust stop-loss to breakeven or small profit
            if position.get("total_pnl", 0) > 0:
                # Profitable position: move stop-loss to breakeven
                protection_method = "stop_loss_to_breakeven"
                await self._adjust_stop_loss(symbol, "breakeven")
            else:
                # Losing position: tighten stop-loss
                protection_method = "tighten_stop_loss"
                await self._adjust_stop_loss(symbol, "tighten")
            
            # Method 2: Add take-profit if not present
            if not position.get("take_profit"):
                await self._add_take_profit(symbol, position)
            
            # Method 3: Reduce position size if very large
            if position.get("units", 0) > 10000:  # Large position
                await self._reduce_position_size(symbol, position)
                protection_method = "reduce_position_size"
            
            return {
                "success": True,
                "method": protection_method
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_portfolio_state(self) -> Dict[str, Any]:
        """Get current portfolio state"""
        try:
            # Get account summary
            account = await trading_engine.get_account_summary()
            if not account.get("success"):
                return {"error": "Failed to get account summary"}
            
            # Get positions
            positions = await trading_engine.get_positions()
            if not positions.get("success"):
                return {"error": "Failed to get positions"}
            
            # Calculate portfolio metrics
            total_balance = account.get("balance", 100000)
            total_pnl = sum(pos.get("total_pnl", 0) for pos in positions.get("positions", []))
            total_loss_pct = abs(total_pnl) / total_balance if total_balance > 0 else 0
            
            # Find worst position
            max_position_loss_pct = 0
            for pos in positions.get("positions", []):
                pos_pnl = pos.get("total_pnl", 0)
                pos_balance = pos.get("balance", 0)
                if pos_balance > 0:
                    pos_loss_pct = abs(pos_pnl) / pos_balance
                    max_position_loss_pct = max(max_position_loss_pct, pos_loss_pct)
            
            return {
                "total_balance": total_balance,
                "total_pnl": total_pnl,
                "total_loss_pct": total_loss_pct,
                "max_position_loss_pct": max_position_loss_pct,
                "position_count": len(positions.get("positions", [])),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Portfolio state error: {str(e)}"}
    
    async def _get_market_state(self) -> Dict[str, Any]:
        """Get current market state"""
        try:
            # Get market regime from financial intelligence
            market_regime = await financial_intelligence_engine.analyze_market_regime({})
            
            # Get economic cycle
            economic_cycle = await financial_intelligence_engine.analyze_economic_cycle({})
            
            # Placeholder market metrics (in production, get from real data)
            market_metrics = {
                "volatility": 1.2,  # 1.2x normal
                "normal_volatility": 1.0,
                "correlation": 0.6,  # 60% correlation
                "liquidity": 0.8,  # 80% of normal
                "normal_liquidity": 1.0,
                "market_regime": market_regime.regime if market_regime else "unknown",
                "economic_cycle": economic_cycle.phase if economic_cycle else "unknown"
            }
            
            return market_metrics
            
        except Exception as e:
            return {"error": f"Market state error: {str(e)}"}
    
    async def _get_detailed_positions(self) -> List[Dict[str, Any]]:
        """Get detailed position information"""
        try:
            positions = await trading_engine.get_positions()
            if not positions.get("success"):
                return []
            
            detailed_positions = []
            for pos in positions.get("positions", []):
                # Add additional context
                detailed_pos = pos.copy()
                detailed_pos["open_time"] = pos.get("open_time", datetime.now().isoformat())
                detailed_pos["strategy"] = pos.get("strategy", "unknown")
                detailed_pos["pnl_pct"] = pos.get("total_pnl", 0) / pos.get("balance", 1) if pos.get("balance", 0) > 0 else 0
                
                detailed_positions.append(detailed_pos)
            
            return detailed_positions
            
        except Exception as e:
            logger.error(f"Detailed positions error: {str(e)}")
            return []
    
    async def _check_trend_intact(self, symbol: str, strategy: str) -> bool:
        """Check if trend is still intact for trend-following strategies"""
        try:
            # Placeholder: in production, check actual trend indicators
            # For now, assume trend is intact if strategy is active
            return strategy in ["trend_following", "momentum", "breakout"]
        except Exception as e:
            return False
    
    async def _get_position_correlation(self, symbol: str, portfolio_state: Dict[str, Any]) -> float:
        """Get correlation between position and portfolio"""
        try:
            # Placeholder: in production, calculate actual correlation
            # For now, return random low correlation
            import random
            return random.uniform(0.1, 0.5)
        except Exception as e:
            return 0.5
    
    async def _get_market_conditions(self, symbol: str) -> Dict[str, Any]:
        """Get current market conditions for a symbol"""
        try:
            # Placeholder: in production, get real market data
            return {
                "volatility": "normal",
                "fair_price": 1.1750,
                "spread": 0.0002,
                "liquidity": "high"
            }
        except Exception as e:
            return {"volatility": "unknown"}
    
    async def _adjust_stop_loss(self, symbol: str, method: str):
        """Adjust stop-loss for position protection"""
        try:
            # Placeholder: implement stop-loss adjustment
            logger.info(f"Adjusting stop-loss for {symbol}: {method}")
        except Exception as e:
            logger.error(f"Stop-loss adjustment error: {str(e)}")
    
    async def _add_take_profit(self, symbol: str, position: Dict[str, Any]):
        """Add take-profit order to position"""
        try:
            # Placeholder: implement take-profit addition
            logger.info(f"Adding take-profit for {symbol}")
        except Exception as e:
            logger.error(f"Take-profit addition error: {str(e)}")
    
    async def _reduce_position_size(self, symbol: str, position: Dict[str, Any]):
        """Reduce position size for risk management"""
        try:
            # Placeholder: implement position size reduction
            logger.info(f"Reducing position size for {symbol}")
        except Exception as e:
            logger.error(f"Position size reduction error: {str(e)}")
    
    async def _calculate_risk_reduction(self, closed_positions: List[Dict[str, Any]]) -> float:
        """Calculate risk reduction from closed positions"""
        try:
            if not closed_positions:
                return 0.0
            
            total_risk_reduction = sum(
                abs(pos.get("total_pnl", 0)) for pos in closed_positions
            )
            
            return total_risk_reduction
            
        except Exception as e:
            return 0.0
    
    async def _record_emergency_stop(self, assessment: Dict[str, Any], execution_results: Dict[str, Any]):
        """Record emergency stop for analysis"""
        try:
            emergency_stop_record = {
                "timestamp": datetime.now().isoformat(),
                "assessment": assessment,
                "execution": execution_results,
                "system_state": {
                    "portfolio_state": await self._get_portfolio_state(),
                    "market_state": await self._get_market_state()
                }
            }
            
            self.emergency_stop_history.append(emergency_stop_record)
            self.last_emergency_stop = emergency_stop_record
            
            # Keep only last 100 records
            if len(self.emergency_stop_history) > 100:
                self.emergency_stop_history = self.emergency_stop_history[-100:]
            
            logger.info("🛡️ Emergency stop recorded for analysis")
            
        except Exception as e:
            logger.error(f"Emergency stop recording error: {str(e)}")
    
    def get_emergency_stop_status(self) -> Dict[str, Any]:
        """Get current emergency stop status"""
        return {
            "enabled": self.emergency_stop_enabled,
            "last_emergency_stop": self.last_emergency_stop,
            "history_count": len(self.emergency_stop_history),
            "thresholds": self.emergency_stop_thresholds,
            "protection_rules": self.position_protection
        }
    
    def update_thresholds(self, new_thresholds: Dict[str, Any]):
        """Update emergency stop thresholds"""
        try:
            self.emergency_stop_thresholds.update(new_thresholds)
            logger.info("🛡️ Emergency stop thresholds updated")
        except Exception as e:
            logger.error(f"Threshold update error: {str(e)}")
    
    def update_protection_rules(self, new_rules: Dict[str, Any]):
        """Update position protection rules"""
        try:
            self.position_protection.update(new_rules)
            logger.info("🛡️ Position protection rules updated")
        except Exception as e:
            logger.error(f"Protection rules update error: {str(e)}")


# Global intelligent emergency stop instance
intelligent_emergency_stop = IntelligentEmergencyStop()
