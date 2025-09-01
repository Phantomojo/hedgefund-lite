"""
Comprehensive Strategy Engine
Multi-asset strategy generation and execution
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import random

from src.services.market_analyzer import market_analyzer
from src.services.trading_engine import trading_engine
from src.services.risk_manager import risk_manager

logger = logging.getLogger(__name__)

class StrategyEngine:
    """Comprehensive strategy engine for all asset classes"""
    
    def __init__(self):
        # Strategy Types
        self.strategy_types = {
            "trend_following": "Follow established market trends",
            "mean_reversion": "Trade against extreme price movements",
            "breakout": "Trade breakouts from consolidation",
            "momentum": "Trade based on price momentum",
            "arbitrage": "Exploit price differences",
            "hedging": "Reduce portfolio risk",
            "scalping": "Quick small profit trades",
            "swing_trading": "Medium-term position holding"
        }
        
        # Asset Class Strategies
        self.asset_strategies = {
            "currencies": ["trend_following", "mean_reversion", "breakout", "scalping"],
            "commodities": ["trend_following", "mean_reversion", "breakout", "momentum"],
            "indices": ["trend_following", "mean_reversion", "breakout", "swing_trading"],
            "crypto": ["trend_following", "momentum", "breakout", "scalping"],
            "bonds": ["trend_following", "mean_reversion", "hedging"]
        }
        
        # Position Limits (3 per asset as requested)
        self.max_positions_per_asset = 3
        self.max_total_positions = 50  # Overall portfolio limit
        
        # Strategy Performance Tracking
        self.strategy_performance = {}
        self.trade_history = []
        
        # Risk Parameters
        self.max_risk_per_trade = 0.02  # 2% per trade
        self.max_portfolio_risk = 0.15  # 15% total portfolio
        self.min_confidence_threshold = 0.75
        
        logger.info("🎯 Comprehensive Strategy Engine initialized")
    
    async def generate_comprehensive_strategies(self) -> Dict[str, Any]:
        """Generate strategies for all asset classes"""
        try:
            logger.info("🎯 Generating comprehensive trading strategies...")
            
            # Get market analysis
            market_analysis = await market_analyzer.analyze_all_markets()
            if "error" in market_analysis:
                return {"error": f"Failed to get market analysis: {market_analysis['error']}"}
            
            # Generate strategies for each asset class
            strategies = {
                "timestamp": datetime.now().isoformat(),
                "currencies": await self._generate_currency_strategies(market_analysis["currencies"]),
                "commodities": await self._generate_commodity_strategies(market_analysis["commodities"]),
                "indices": await self._generate_index_strategies(market_analysis["indices"]),
                "crypto": await self._generate_crypto_strategies(market_analysis["crypto"]),
                "bonds": await self._generate_bond_strategies(market_analysis["bonds"]),
                "portfolio_recommendations": [],
                "risk_assessment": {},
                "execution_plan": {}
            }
            
            # Generate portfolio-level recommendations
            strategies["portfolio_recommendations"] = await self._generate_portfolio_recommendations(strategies)
            
            # Assess overall portfolio risk
            strategies["risk_assessment"] = await self._assess_portfolio_risk(strategies)
            
            # Create execution plan
            strategies["execution_plan"] = await self._create_execution_plan(strategies)
            
            logger.info("🎯 Comprehensive strategies generated successfully")
            
            return strategies
            
        except Exception as e:
            logger.error(f"Strategy generation error: {str(e)}")
            return {"error": f"Strategy generation failed: {str(e)}"}
    
    async def _generate_currency_strategies(self, currency_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate currency trading strategies"""
        try:
            strategies = {}
            
            for category, pairs in currency_analysis.items():
                strategies[category] = {}
                
                for pair, analysis in pairs.items():
                    if "error" in analysis:
                        continue
                    
                    # Generate strategy based on analysis
                    strategy = await self._generate_asset_strategy(
                        asset_type="currency",
                        symbol=pair,
                        analysis=analysis,
                        strategy_types=self.asset_strategies["currencies"]
                    )
                    
                    if strategy:
                        strategies[category][pair] = strategy
            
            return strategies
            
        except Exception as e:
            logger.error(f"Currency strategy generation error: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_commodity_strategies(self, commodity_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate commodity trading strategies"""
        try:
            strategies = {}
            
            for category, symbols in commodity_analysis.items():
                strategies[category] = {}
                
                for symbol, analysis in symbols.items():
                    if "error" in analysis:
                        continue
                    
                    # Generate strategy based on analysis
                    strategy = await self._generate_asset_strategy(
                        asset_type="commodity",
                        symbol=symbol,
                        analysis=analysis,
                        strategy_types=self.asset_strategies["commodities"]
                    )
                    
                    if strategy:
                        strategies[category][symbol] = strategy
            
            return strategies
            
        except Exception as e:
            logger.error(f"Commodity strategy generation error: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_index_strategies(self, index_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate index trading strategies"""
        try:
            strategies = {}
            
            for region, symbols in index_analysis.items():
                strategies[region] = {}
                
                for symbol, analysis in symbols.items():
                    if "error" in analysis:
                        continue
                    
                    # Generate strategy based on analysis
                    strategy = await self._generate_asset_strategy(
                        asset_type="index",
                        symbol=symbol,
                        analysis=analysis,
                        strategy_types=self.asset_strategies["indices"]
                    )
                    
                    if strategy:
                        strategies[region][symbol] = strategy
            
            return strategies
            
        except Exception as e:
            logger.error(f"Index strategy generation error: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_crypto_strategies(self, crypto_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate cryptocurrency trading strategies"""
        try:
            strategies = {}
            
            for symbol, analysis in crypto_analysis.items():
                if "error" in analysis:
                    continue
                
                # Generate strategy based on analysis
                strategy = await self._generate_asset_strategy(
                    asset_type="crypto",
                    symbol=symbol,
                    analysis=analysis,
                    strategy_types=self.asset_strategies["crypto"]
                )
                
                if strategy:
                    strategies[symbol] = strategy
            
            return strategies
            
        except Exception as e:
            logger.error(f"Crypto strategy generation error: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_bond_strategies(self, bond_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate bond trading strategies"""
        try:
            strategies = {}
            
            for symbol, analysis in bond_analysis.items():
                if "error" in analysis:
                    continue
                
                # Generate strategy based on analysis
                strategy = await self._generate_asset_strategy(
                    asset_type="bond",
                    symbol=symbol,
                    analysis=analysis,
                    strategy_types=self.asset_strategies["bonds"]
                )
                
                if strategy:
                    strategies[symbol] = strategy
            
            return strategies
            
        except Exception as e:
            logger.error(f"Bond strategy generation error: {str(e)}")
            return {"error": str(e)}
    
    async def _generate_asset_strategy(self, asset_type: str, symbol: str, analysis: Dict[str, Any], strategy_types: List[str]) -> Optional[Dict[str, Any]]:
        """Generate strategy for a specific asset"""
        try:
            # Check if we should generate a strategy
            if analysis.get("confidence", 0) < self.min_confidence_threshold:
                return None
            
            # Select best strategy type based on analysis
            strategy_type = self._select_strategy_type(analysis, strategy_types)
            
            # Generate strategy parameters
            strategy_params = await self._generate_strategy_parameters(
                asset_type, symbol, analysis, strategy_type
            )
            
            # Calculate position size
            position_size = await self._calculate_position_size(
                asset_type, symbol, analysis, strategy_params
            )
            
            # Generate entry/exit rules
            entry_rules = await self._generate_entry_rules(analysis, strategy_type)
            exit_rules = await self._generate_exit_rules(analysis, strategy_type)
            
            # Risk management rules
            risk_rules = await self._generate_risk_rules(asset_type, analysis, strategy_params)
            
            strategy = {
                "asset_type": asset_type,
                "symbol": symbol,
                "strategy_type": strategy_type,
                "confidence": analysis.get("confidence", 0),
                "sentiment": analysis.get("ai_analysis", {}).get("sentiment", "neutral"),
                "recommendation": analysis.get("recommendation", "hold"),
                "position_size": position_size,
                "entry_rules": entry_rules,
                "exit_rules": exit_rules,
                "risk_rules": risk_rules,
                "strategy_params": strategy_params,
                "expected_return": self._calculate_expected_return(analysis, strategy_type),
                "risk_level": analysis.get("risk_level", "medium"),
                "time_horizon": self._get_time_horizon(strategy_type),
                "generated_at": datetime.now().isoformat()
            }
            
            return strategy
            
        except Exception as e:
            logger.error(f"Asset strategy generation error for {symbol}: {str(e)}")
            return None
    
    def _select_strategy_type(self, analysis: Dict[str, Any], strategy_types: List[str]) -> str:
        """Select the best strategy type based on analysis"""
        try:
            # Simple strategy selection logic
            # In production, this would use AI to select optimal strategy
            
            sentiment = analysis.get("ai_analysis", {}).get("sentiment", "neutral")
            confidence = analysis.get("confidence", 0)
            
            if sentiment == "bullish" and confidence > 0.8:
                return "trend_following"
            elif sentiment == "bearish" and confidence > 0.8:
                return "trend_following"
            elif confidence < 0.6:
                return "mean_reversion"
            else:
                return random.choice(strategy_types)
                
        except Exception as e:
            return "trend_following"  # Default fallback
    
    async def _generate_strategy_parameters(self, asset_type: str, symbol: str, analysis: Dict[str, Any], strategy_type: str) -> Dict[str, Any]:
        """Generate strategy-specific parameters"""
        try:
            base_params = {
                "stop_loss_pct": 0.02,  # 2% stop loss
                "take_profit_pct": 0.04,  # 4% take profit
                "trailing_stop": True,
                "trailing_stop_pct": 0.01,  # 1% trailing stop
            }
            
            # Strategy-specific parameters
            if strategy_type == "trend_following":
                base_params.update({
                    "trend_confirmation_periods": 3,
                    "trend_strength_threshold": 0.7,
                    "entry_confirmation": "breakout"
                })
            elif strategy_type == "mean_reversion":
                base_params.update({
                    "reversion_threshold": 2.0,  # Standard deviations
                    "mean_calculation_periods": 20,
                    "entry_confirmation": "oversold/overbought"
                })
            elif strategy_type == "breakout":
                base_params.update({
                    "breakout_confirmation_periods": 2,
                    "volume_confirmation": True,
                    "entry_confirmation": "volume spike"
                })
            elif strategy_type == "momentum":
                base_params.update({
                    "momentum_periods": 14,
                    "momentum_threshold": 0.6,
                    "entry_confirmation": "momentum confirmation"
                })
            
            # Asset-specific adjustments
            if asset_type == "crypto":
                base_params["stop_loss_pct"] = 0.05  # Higher stop loss for crypto
                base_params["take_profit_pct"] = 0.10
            elif asset_type == "bonds":
                base_params["stop_loss_pct"] = 0.01  # Lower stop loss for bonds
                base_params["take_profit_pct"] = 0.02
            
            return base_params
            
        except Exception as e:
            logger.error(f"Strategy parameters generation error: {str(e)}")
            return {"stop_loss_pct": 0.02, "take_profit_pct": 0.04}
    
    async def _calculate_position_size(self, asset_type: str, symbol: str, analysis: Dict[str, Any], strategy_params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate optimal position size"""
        try:
            # Get account balance
            account = await trading_engine.get_account_summary()
            if not account.get("success"):
                return {"units": 0, "error": "Failed to get account balance"}
            
            balance = account.get("balance", 100000)  # Default to 100k if not available
            
            # Calculate position size based on risk
            risk_amount = balance * self.max_risk_per_trade
            stop_loss_pct = strategy_params.get("stop_loss_pct", 0.02)
            
            # Simple position sizing (in production, use Kelly Criterion, etc.)
            if asset_type == "currency":
                # For currencies, use standard lot sizes
                base_units = 1000
                if risk_amount > 1000:
                    base_units = 5000
                if risk_amount > 5000:
                    base_units = 10000
            elif asset_type == "commodity":
                base_units = 100
            elif asset_type == "index":
                base_units = 10
            elif asset_type == "crypto":
                base_units = 1
            elif asset_type == "bond":
                base_units = 1000
            
            # Adjust based on confidence
            confidence = analysis.get("confidence", 0.5)
            confidence_multiplier = min(confidence * 2, 1.5)  # Max 1.5x for high confidence
            
            final_units = int(base_units * confidence_multiplier)
            
            return {
                "units": final_units,
                "risk_amount": risk_amount,
                "confidence_multiplier": confidence_multiplier
            }
            
        except Exception as e:
            logger.error(f"Position size calculation error: {str(e)}")
            return {"units": 1000, "error": str(e)}
    
    async def _generate_entry_rules(self, analysis: Dict[str, Any], strategy_type: str) -> Dict[str, Any]:
        """Generate entry rules for the strategy"""
        try:
            entry_rules = {
                "entry_type": "market",  # market, limit, stop
                "entry_conditions": [],
                "entry_confirmation": [],
                "entry_timing": "immediate"
            }
            
            # Strategy-specific entry rules
            if strategy_type == "trend_following":
                entry_rules["entry_conditions"] = [
                    "trend direction confirmed",
                    "price above/below key moving averages",
                    "volume confirmation"
                ]
            elif strategy_type == "mean_reversion":
                entry_rules["entry_conditions"] = [
                    "price at extreme levels (RSI oversold/overbought)",
                    "divergence from trend",
                    "support/resistance test"
                ]
            elif strategy_type == "breakout":
                entry_rules["entry_conditions"] = [
                    "price breaks key resistance/support",
                    "volume spike on breakout",
                    "breakout confirmation"
                ]
            
            return entry_rules
            
        except Exception as e:
            logger.error(f"Entry rules generation error: {str(e)}")
            return {"entry_type": "market", "entry_conditions": []}
    
    async def _generate_exit_rules(self, analysis: Dict[str, Any], strategy_type: str) -> Dict[str, Any]:
        """Generate exit rules for the strategy"""
        try:
            exit_rules = {
                "stop_loss": True,
                "take_profit": True,
                "trailing_stop": True,
                "time_based_exit": False,
                "exit_conditions": []
            }
            
            # Strategy-specific exit rules
            if strategy_type == "scalping":
                exit_rules["time_based_exit"] = True
                exit_rules["max_hold_time"] = "4h"
            elif strategy_type == "swing_trading":
                exit_rules["max_hold_time"] = "1w"
            
            return exit_rules
            
        except Exception as e:
            logger.error(f"Exit rules generation error: {str(e)}")
            return {"stop_loss": True, "take_profit": True}
    
    async def _generate_risk_rules(self, asset_type: str, analysis: Dict[str, Any], strategy_params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate risk management rules"""
        try:
            risk_rules = {
                "max_position_size": self.max_positions_per_asset,
                "max_portfolio_exposure": 0.20,  # 20% max exposure per asset
                "correlation_limits": True,
                "volatility_adjustments": True,
                "dynamic_position_sizing": True
            }
            
            # Asset-specific risk rules
            if asset_type == "crypto":
                risk_rules["max_portfolio_exposure"] = 0.10  # Lower exposure for crypto
            elif asset_type == "bonds":
                risk_rules["max_portfolio_exposure"] = 0.30  # Higher exposure for bonds
            
            return risk_rules
            
        except Exception as e:
            logger.error(f"Risk rules generation error: {str(e)}")
            return {"max_position_size": 3, "max_portfolio_exposure": 0.20}
    
    def _calculate_expected_return(self, analysis: Dict[str, Any], strategy_type: str) -> Dict[str, Any]:
        """Calculate expected return for the strategy"""
        try:
            confidence = analysis.get("confidence", 0.5)
            risk_level = analysis.get("risk_level", "medium")
            
            # Base expected returns by strategy type
            base_returns = {
                "trend_following": 0.05,  # 5%
                "mean_reversion": 0.03,   # 3%
                "breakout": 0.06,         # 6%
                "momentum": 0.04,         # 4%
                "scalping": 0.02,         # 2%
                "swing_trading": 0.08     # 8%
            }
            
            base_return = base_returns.get(strategy_type, 0.04)
            
            # Adjust based on confidence and risk
            confidence_multiplier = confidence
            risk_adjustment = 1.0 if risk_level == "low" else 0.8 if risk_level == "medium" else 0.6
            
            expected_return = base_return * confidence_multiplier * risk_adjustment
            
            return {
                "expected_return_pct": expected_return * 100,
                "confidence": confidence,
                "risk_adjustment": risk_adjustment,
                "base_return": base_return
            }
            
        except Exception as e:
            return {"expected_return_pct": 4.0, "confidence": 0.5}
    
    def _get_time_horizon(self, strategy_type: str) -> str:
        """Get time horizon for the strategy"""
        time_horizons = {
            "scalping": "minutes to hours",
            "day_trading": "hours to days",
            "swing_trading": "days to weeks",
            "trend_following": "weeks to months",
            "mean_reversion": "days to weeks",
            "breakout": "days to weeks",
            "momentum": "hours to days",
            "hedging": "weeks to months"
        }
        
        return time_horizons.get(strategy_type, "days to weeks")
    
    async def _generate_portfolio_recommendations(self, strategies: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate portfolio-level recommendations"""
        try:
            recommendations = []
            
            # Analyze portfolio diversification
            asset_class_exposure = self._calculate_asset_class_exposure(strategies)
            
            # Generate diversification recommendations
            if asset_class_exposure.get("currencies", 0) > 0.4:
                recommendations.append({
                    "type": "diversification",
                    "message": "Reduce currency exposure - consider commodities or indices",
                    "priority": "high"
                })
            
            if asset_class_exposure.get("crypto", 0) > 0.2:
                recommendations.append({
                    "type": "risk_management",
                    "message": "High crypto exposure - consider reducing for portfolio stability",
                    "priority": "high"
                })
            
            # Generate correlation recommendations
            correlation_recs = await self._generate_correlation_recommendations(strategies)
            recommendations.extend(correlation_recs)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Portfolio recommendations error: {str(e)}")
            return []
    
    def _calculate_asset_class_exposure(self, strategies: Dict[str, Any]) -> Dict[str, float]:
        """Calculate exposure by asset class"""
        try:
            exposure = {
                "currencies": 0.0,
                "commodities": 0.0,
                "indices": 0.0,
                "crypto": 0.0,
                "bonds": 0.0
            }
            
            # Count strategies by asset class
            for asset_class in exposure.keys():
                if asset_class in strategies:
                    if isinstance(strategies[asset_class], dict):
                        # Count nested strategies
                        count = sum(len(inner_dict) for inner_dict in strategies[asset_class].values() if isinstance(inner_dict, dict))
                    else:
                        count = len(strategies[asset_class]) if isinstance(strategies[asset_class], list) else 0
                    
                    exposure[asset_class] = count / 50.0  # Normalize to portfolio size
            
            return exposure
            
        except Exception as e:
            return {"currencies": 0.2, "commodities": 0.2, "indices": 0.2, "crypto": 0.2, "bonds": 0.2}
    
    async def _generate_correlation_recommendations(self, strategies: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate correlation-based recommendations"""
        try:
            recommendations = []
            
            # Placeholder for correlation analysis
            # In production, this would calculate actual correlations between assets
            
            recommendations.append({
                "type": "correlation",
                "message": "Monitor EUR/USD and GBP/USD correlation - consider reducing if > 0.8",
                "priority": "medium"
            })
            
            return recommendations
            
        except Exception as e:
            return []
    
    async def _assess_portfolio_risk(self, strategies: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall portfolio risk"""
        try:
            risk_assessment = {
                "overall_risk_level": "medium",
                "risk_factors": [],
                "risk_score": 0.0,
                "recommendations": []
            }
            
            # Calculate portfolio risk score
            total_strategies = 0
            risk_scores = []
            
            for asset_class, asset_strategies in strategies.items():
                if asset_class in ["timestamp", "portfolio_recommendations", "risk_assessment", "execution_plan"]:
                    continue
                
                if isinstance(asset_strategies, dict):
                    for category, category_strategies in asset_strategies.items():
                        if isinstance(category_strategies, dict):
                            for symbol, strategy in category_strategies.items():
                                if isinstance(strategy, dict) and "risk_level" in strategy:
                                    total_strategies += 1
                                    risk_level = strategy["risk_level"]
                                    risk_score = {"low": 0.3, "medium": 0.6, "high": 0.9}.get(risk_level, 0.6)
                                    risk_scores.append(risk_score)
            
            if risk_scores:
                avg_risk_score = sum(risk_scores) / len(risk_scores)
                risk_assessment["risk_score"] = avg_risk_score
                
                if avg_risk_score < 0.4:
                    risk_assessment["overall_risk_level"] = "low"
                elif avg_risk_score > 0.7:
                    risk_assessment["overall_risk_level"] = "high"
                else:
                    risk_assessment["overall_risk_level"] = "medium"
            
            # Generate risk recommendations
            if risk_assessment["overall_risk_level"] == "high":
                risk_assessment["recommendations"].append({
                    "type": "risk_reduction",
                    "message": "Portfolio risk is high - consider reducing position sizes or adding hedges",
                    "priority": "high"
                })
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Portfolio risk assessment error: {str(e)}")
            return {"overall_risk_level": "medium", "risk_score": 0.6}
    
    async def _create_execution_plan(self, strategies: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution plan for strategies"""
        try:
            execution_plan = {
                "execution_priority": "high",
                "execution_timing": "immediate",
                "execution_steps": [],
                "risk_checks": [],
                "monitoring_plan": {}
            }
            
            # Create execution steps
            for asset_class, asset_strategies in strategies.items():
                if asset_class in ["timestamp", "portfolio_recommendations", "risk_assessment", "execution_plan"]:
                    continue
                
                if isinstance(asset_strategies, dict):
                    for category, category_strategies in asset_strategies.items():
                        if isinstance(category_strategies, dict):
                            for symbol, strategy in category_strategies.items():
                                if isinstance(strategy, dict) and strategy.get("recommendation") != "hold":
                                    execution_plan["execution_steps"].append({
                                        "asset": symbol,
                                        "action": strategy.get("recommendation", "hold"),
                                        "position_size": strategy.get("position_size", {}).get("units", 0),
                                        "priority": "high" if strategy.get("confidence", 0) > 0.8 else "medium",
                                        "timing": "immediate" if strategy.get("confidence", 0) > 0.9 else "wait_for_confirmation"
                                    })
            
            # Sort by priority and confidence
            execution_plan["execution_steps"].sort(
                key=lambda x: (x["priority"] == "high", x["timing"] == "immediate"),
                reverse=True
            )
            
            return execution_plan
            
        except Exception as e:
            logger.error(f"Execution plan creation error: {str(e)}")
            return {"execution_priority": "medium", "execution_steps": []}
    
    async def execute_strategies(self, strategies: Dict[str, Any], execute_all: bool = False) -> Dict[str, Any]:
        """Execute generated strategies"""
        try:
            logger.info("🎯 Executing trading strategies...")
            
            execution_results = {
                "timestamp": datetime.now().isoformat(),
                "strategies_executed": 0,
                "trades_placed": 0,
                "errors": [],
                "execution_summary": {}
            }
            
            execution_plan = strategies.get("execution_plan", {})
            execution_steps = execution_plan.get("execution_steps", [])
            
            for step in execution_steps:
                try:
                    if not execute_all and step["timing"] == "wait_for_confirmation":
                        continue
                    
                    # Execute the trade
                    result = await self._execute_strategy_step(step)
                    
                    if result.get("success"):
                        execution_results["trades_placed"] += 1
                        execution_results["execution_summary"][step["asset"]] = result
                    else:
                        execution_results["errors"].append({
                            "asset": step["asset"],
                            "error": result.get("error", "Unknown error")
                        })
                    
                    execution_results["strategies_executed"] += 1
                    
                except Exception as e:
                    execution_results["errors"].append({
                        "asset": step.get("asset", "unknown"),
                        "error": str(e)
                    })
            
            logger.info(f"🎯 Strategy execution complete: {execution_results['trades_placed']} trades placed")
            
            return execution_results
            
        except Exception as e:
            logger.error(f"Strategy execution error: {str(e)}")
            return {"error": f"Strategy execution failed: {str(e)}"}
    
    async def _execute_strategy_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single strategy step"""
        try:
            asset = step["asset"]
            action = step["action"]
            units = step["position_size"]
            
            if action == "buy":
                result = await trading_engine.place_market_order(
                    pair=asset,
                    side="buy",
                    units=units
                )
            elif action == "sell":
                result = await trading_engine.place_market_order(
                    pair=asset,
                    side="sell",
                    units=units
                )
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# Global strategy engine instance
strategy_engine = StrategyEngine()
