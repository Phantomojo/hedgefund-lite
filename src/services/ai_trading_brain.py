"""
AI Trading Brain
Uses comprehensive financial intelligence to make trading decisions
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import requests

from src.services.market_analyzer import market_analyzer
from src.services.strategy_engine import strategy_engine
from src.services.financial_intelligence_engine import financial_intelligence_engine
from src.services.trading_engine import trading_engine
from src.services.risk_manager import risk_manager

logger = logging.getLogger(__name__)

class AITradingBrain:
    """AI Trading Brain using comprehensive financial intelligence"""
    
    def __init__(self):
        # AI Configuration
        self.confidence_threshold = 0.75  # Only trade when 75%+ confident
        self.max_positions = 3  # Max 3 positions per asset as requested
        self.position_size_pct = 0.02  # 2% of account per trade
        
        # Trading State
        self.trading_enabled = False
        self.last_analysis = None
        self.last_strategies = None
        self.trade_history = []
        
        # Financial Intelligence Integration
        self.market_regime = None
        self.economic_cycle = None
        self.professional_insights = {}
        
        logger.info("🧠 AI Trading Brain initialized with financial intelligence")
    
    async def analyze_market_conditions(self) -> Dict[str, Any]:
        """Comprehensive market analysis using financial intelligence"""
        try:
            logger.info("🧠 Starting comprehensive market analysis...")
            
            # Step 1: Get market data and basic analysis
            market_analysis = await market_analyzer.analyze_all_markets()
            
            # Step 2: Analyze market regime using financial intelligence
            self.market_regime = await financial_intelligence_engine.analyze_market_regime(
                market_analysis
            )
            
            # Step 3: Analyze economic cycle
            economic_data = self._extract_economic_data(market_analysis)
            self.economic_cycle = await financial_intelligence_engine.analyze_economic_cycle(
                economic_data
            )
            
            # Step 4: Generate professional insights for key assets
            self.professional_insights = await self._generate_key_asset_insights(market_analysis)
            
            # Step 5: Compile comprehensive analysis
            comprehensive_analysis = {
                "timestamp": datetime.now().isoformat(),
                "market_analysis": market_analysis,
                "market_regime": {
                    "regime": self.market_regime.regime,
                    "volatility": self.market_regime.volatility,
                    "correlation": self.market_regime.correlation,
                    "liquidity": self.market_regime.liquidity,
                    "trend_strength": self.market_regime.trend_strength,
                    "confidence": self.market_regime.confidence
                },
                "economic_cycle": {
                    "phase": self.economic_cycle.phase,
                    "gdp_growth": self.economic_cycle.gdp_growth,
                    "inflation": self.economic_cycle.inflation,
                    "interest_rates": self.economic_cycle.interest_rates
                },
                "professional_insights": self.professional_insights,
                "trading_environment": self._assess_trading_environment()
            }
            
            self.last_analysis = comprehensive_analysis
            logger.info(f"🧠 Market analysis complete. Regime: {self.market_regime.regime}, Cycle: {self.economic_cycle.phase}")
            
            return comprehensive_analysis
            
        except Exception as e:
            logger.error(f"Market analysis error: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    async def generate_trading_signals(self, market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trading signals using financial intelligence"""
        try:
            logger.info("🧠 Generating AI trading signals...")
            
            signals = {
                "timestamp": datetime.now().isoformat(),
                "market_regime": self.market_regime.regime,
                "economic_cycle": self.economic_cycle.phase,
                "signals": [],
                "overall_sentiment": "neutral",
                "confidence": 0.0
            }
            
            # Step 1: Assess overall market conditions
            trading_environment = self._assess_trading_environment()
            
            # Step 2: Generate signals for each asset class
            for asset_class, assets in market_analysis.items():
                if asset_class in ["timestamp", "overall_market_sentiment", "risk_level", "opportunities", "warnings"]:
                    continue
                
                asset_signals = await self._generate_asset_signals(
                    asset_class, assets, trading_environment
                )
                signals["signals"].extend(asset_signals)
            
            # Step 3: Calculate overall sentiment and confidence
            signals["overall_sentiment"] = self._calculate_overall_sentiment(signals["signals"])
            signals["confidence"] = self._calculate_overall_confidence(signals["signals"])
            
            # Step 4: Filter signals based on confidence threshold
            filtered_signals = [
                signal for signal in signals["signals"] 
                if signal.get("confidence", 0) >= self.confidence_threshold
            ]
            signals["signals"] = filtered_signals
            
            logger.info(f"🧠 Generated {len(filtered_signals)} high-confidence signals")
            
            return signals
            
        except Exception as e:
            logger.error(f"Signal generation error: {str(e)}")
            return {"error": f"Signal generation failed: {str(e)}"}
    
    async def execute_ai_strategy(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Execute AI trading strategy using financial intelligence"""
        try:
            logger.info("🧠 Executing AI trading strategy...")
            
            execution_results = {
                "timestamp": datetime.now().isoformat(),
                "signals_processed": len(signals.get("signals", [])),
                "trades_executed": 0,
                "trades_rejected": 0,
                "execution_details": [],
                "risk_checks_passed": 0,
                "risk_checks_failed": 0
            }
            
            # Step 1: Get current positions and account status
            current_positions = await trading_engine.get_positions()
            account_status = await trading_engine.get_account_summary()
            
            # Step 2: Process each signal
            for signal in signals.get("signals", []):
                try:
                    # Risk check 1: Position limit check
                    if not self._check_position_limit(signal["symbol"], current_positions):
                        execution_results["trades_rejected"] += 1
                        execution_results["execution_details"].append({
                            "symbol": signal["symbol"],
                            "action": signal["action"],
                            "status": "rejected",
                            "reason": "Position limit exceeded (max 3 per asset)"
                        })
                        continue
                    
                    # Risk check 2: Market regime check
                    if not self._check_market_regime_compatibility(signal, self.market_regime):
                        execution_results["trades_rejected"] += 1
                        execution_results["execution_details"].append({
                            "symbol": signal["symbol"],
                            "action": signal["action"],
                            "status": "rejected",
                            "reason": "Incompatible with current market regime"
                        })
                        continue
                    
                    # Risk check 3: Economic cycle check
                    if not self._check_economic_cycle_compatibility(signal, self.economic_cycle):
                        execution_results["trades_rejected"] += 1
                        execution_results["execution_details"].append({
                            "symbol": signal["symbol"],
                            "action": signal["action"],
                            "status": "rejected",
                            "reason": "Incompatible with current economic cycle"
                        })
                        continue
                    
                    # Risk check 4: Professional insights validation
                    if not self._validate_with_professional_insights(signal):
                        execution_results["trades_rejected"] += 1
                        execution_results["execution_details"].append({
                            "symbol": signal["symbol"],
                            "action": signal["action"],
                            "status": "rejected",
                            "reason": "Failed professional insights validation"
                        })
                        continue
                    
                    # All risk checks passed
                    execution_results["risk_checks_passed"] += 1
                    
                    # Calculate position size using financial intelligence
                    position_size = await self._calculate_intelligent_position_size(
                        signal, account_status, self.market_regime, self.economic_cycle
                    )
                    
                    # Execute the trade
                    trade_result = await self._execute_trade(signal, position_size)
                    
                    if trade_result.get("success"):
                        execution_results["trades_executed"] += 1
                        execution_results["execution_details"].append({
                            "symbol": signal["symbol"],
                            "action": signal["action"],
                            "status": "executed",
                            "position_size": position_size,
                            "trade_id": trade_result.get("trade_id"),
                            "execution_price": trade_result.get("execution_price")
                        })
                        
                        # Update trade history
                        self.trade_history.append({
                            "timestamp": datetime.now().isoformat(),
                            "symbol": signal["symbol"],
                            "action": signal["action"],
                            "position_size": position_size,
                            "confidence": signal.get("confidence", 0),
                            "market_regime": self.market_regime.regime,
                            "economic_cycle": self.economic_cycle.phase,
                            "professional_insights": signal.get("professional_insights", {})
                        })
                    else:
                        execution_results["trades_rejected"] += 1
                        execution_results["execution_details"].append({
                            "symbol": signal["symbol"],
                            "action": signal["action"],
                            "status": "failed",
                            "reason": trade_result.get("error", "Unknown error")
                        })
                        
                except Exception as e:
                    execution_results["trades_rejected"] += 1
                    execution_results["execution_details"].append({
                        "symbol": signal.get("symbol", "unknown"),
                        "action": signal.get("action", "unknown"),
                        "status": "error",
                        "reason": str(e)
                    })
            
            logger.info(f"🧠 Strategy execution complete: {execution_results['trades_executed']} trades executed")
            
            return execution_results
            
        except Exception as e:
            logger.error(f"Strategy execution error: {str(e)}")
            return {"error": f"Strategy execution failed: {str(e)}"}
    
    async def _generate_key_asset_insights(self, market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate professional insights for key assets"""
        try:
            key_insights = {}
            
            # Focus on major assets for professional analysis
            key_assets = {
                "currencies": ["EUR_USD", "GBP_USD", "USD_JPY"],
                "commodities": ["XAU_USD", "USOIL"],
                "indices": ["SPX500", "NAS100"],
                "crypto": ["BTC_USD", "ETH_USD"]
            }
            
            for asset_class, symbols in key_assets.items():
                key_insights[asset_class] = {}
                
                for symbol in symbols:
                    # Get professional insights for each key asset
                    insights = await financial_intelligence_engine.generate_professional_insights(
                        asset_class, symbol, {"symbol": symbol}
                    )
                    key_insights[asset_class][symbol] = insights
            
            return key_insights
            
        except Exception as e:
            logger.error(f"Key asset insights error: {str(e)}")
            return {}
    
    def _assess_trading_environment(self) -> Dict[str, Any]:
        """Assess overall trading environment"""
        try:
            trading_environment = {
                "market_regime_suitable": False,
                "economic_cycle_suitable": False,
                "volatility_acceptable": False,
                "liquidity_adequate": False,
                "overall_suitability": "poor"
            }
            
            # Market regime assessment
            if self.market_regime:
                suitable_regimes = ["bull", "bear", "trending", "sideways"]
                trading_environment["market_regime_suitable"] = self.market_regime.regime in suitable_regimes
                trading_environment["volatility_acceptable"] = self.market_regime.volatility in ["low", "medium"]
                trading_environment["liquidity_adequate"] = self.market_regime.liquidity in ["abundant", "normal"]
            
            # Economic cycle assessment
            if self.economic_cycle:
                suitable_cycles = ["expansion", "peak", "recovery"]
                trading_environment["economic_cycle_suitable"] = self.economic_cycle.phase in suitable_cycles
            
            # Overall suitability
            suitable_factors = sum([
                trading_environment["market_regime_suitable"],
                trading_environment["economic_cycle_suitable"],
                trading_environment["volatility_acceptable"],
                trading_environment["liquidity_adequate"]
            ])
            
            if suitable_factors >= 3:
                trading_environment["overall_suitability"] = "excellent"
            elif suitable_factors >= 2:
                trading_environment["overall_suitability"] = "good"
            elif suitable_factors >= 1:
                trading_environment["overall_suitability"] = "fair"
            else:
                trading_environment["overall_suitability"] = "poor"
            
            return trading_environment
            
        except Exception as e:
            return {"overall_suitability": "unknown"}
    
    async def _generate_asset_signals(self, asset_class: str, assets: Dict[str, Any], trading_environment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate signals for specific asset class"""
        try:
            signals = []
            
            for category, category_assets in assets.items():
                if isinstance(category_assets, dict):
                    for symbol, analysis in category_assets.items():
                        if "error" in analysis:
                            continue
                        
                        # Generate signal using financial intelligence
                        signal = await self._generate_single_asset_signal(
                            asset_class, symbol, analysis, trading_environment
                        )
                        
                        if signal:
                            signals.append(signal)
            
            return signals
            
        except Exception as e:
            logger.error(f"Asset signal generation error for {asset_class}: {str(e)}")
            return []
    
    async def _generate_single_asset_signal(self, asset_class: str, symbol: str, analysis: Dict[str, Any], trading_environment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate signal for single asset"""
        try:
            # Get professional insights
            professional_insights = self.professional_insights.get(asset_class, {}).get(symbol, {})
            
            # Extract key analysis components
            ai_analysis = analysis.get("ai_analysis", {})
            recommendation = ai_analysis.get("action", "hold")
            confidence = ai_analysis.get("confidence", 0)
            
            # Skip if recommendation is hold or confidence too low
            if recommendation == "hold" or confidence < self.confidence_threshold:
                return None
            
            # Generate signal
            signal = {
                "symbol": symbol,
                "asset_class": asset_class,
                "action": recommendation,
                "confidence": confidence,
                "sentiment": ai_analysis.get("sentiment", "neutral"),
                "reasoning": ai_analysis.get("reasoning", ""),
                "market_regime": self.market_regime.regime if self.market_regime else "unknown",
                "economic_cycle": self.economic_cycle.phase if self.economic_cycle else "unknown",
                "professional_insights": professional_insights,
                "risk_level": analysis.get("risk_level", "medium"),
                "timestamp": datetime.now().isoformat()
            }
            
            return signal
            
        except Exception as e:
            logger.error(f"Single asset signal error for {symbol}: {str(e)}")
            return None
    
    def _check_position_limit(self, symbol: str, current_positions: List[Dict[str, Any]]) -> bool:
        """Check if position limit allows new trade"""
        try:
            # Count current positions for this symbol
            symbol_positions = [
                pos for pos in current_positions 
                if pos.get("instrument") == symbol
            ]
            
            return len(symbol_positions) < self.max_positions
            
        except Exception as e:
            logger.error(f"Position limit check error: {str(e)}")
            return False
    
    def _check_market_regime_compatibility(self, signal: Dict[str, Any], market_regime) -> bool:
        """Check if signal is compatible with current market regime"""
        try:
            if not market_regime:
                return True
            
            # Define regime compatibility rules
            regime_rules = {
                "crisis": {
                    "allowed_actions": ["sell", "hold"],
                    "allowed_assets": ["currencies", "bonds"]  # Flight to quality
                },
                "recovery": {
                    "allowed_actions": ["buy", "hold"],
                    "allowed_assets": ["indices", "commodities"]  # Growth assets
                },
                "sideways": {
                    "allowed_actions": ["buy", "sell", "hold"],
                    "allowed_assets": ["all"]  # All assets allowed
                }
            }
            
            regime_rule = regime_rules.get(market_regime.regime, {"allowed_actions": ["all"], "allowed_assets": ["all"]})
            
            # Check action compatibility
            if regime_rule["allowed_actions"] != ["all"]:
                if signal["action"] not in regime_rule["allowed_actions"]:
                    return False
            
            # Check asset compatibility
            if regime_rule["allowed_assets"] != ["all"]:
                if signal["asset_class"] not in regime_rule["allowed_assets"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Market regime compatibility check error: {str(e)}")
            return True
    
    def _check_economic_cycle_compatibility(self, signal: Dict[str, Any], economic_cycle) -> bool:
        """Check if signal is compatible with current economic cycle"""
        try:
            if not economic_cycle:
                return True
            
            # Define cycle compatibility rules
            cycle_rules = {
                "contraction": {
                    "allowed_actions": ["sell", "hold"],
                    "allowed_assets": ["bonds", "utilities"]  # Defensive assets
                },
                "trough": {
                    "allowed_actions": ["buy", "hold"],
                    "allowed_assets": ["indices", "commodities"]  # Recovery assets
                }
            }
            
            cycle_rule = cycle_rules.get(economic_cycle.phase, {"allowed_actions": ["all"], "allowed_assets": ["all"]})
            
            # Check action compatibility
            if cycle_rule["allowed_actions"] != ["all"]:
                if signal["action"] not in cycle_rule["allowed_actions"]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Economic cycle compatibility check error: {str(e)}")
            return True
    
    def _validate_with_professional_insights(self, signal: Dict[str, Any]) -> bool:
        """Validate signal using professional insights"""
        try:
            professional_insights = signal.get("professional_insights", {})
            
            # Check banker view
            banker_view = professional_insights.get("professional_analysis", {}).get("banker_view", {})
            if banker_view.get("credit_quality") == "distressed":
                return False
            
            # Check investor view
            investor_view = professional_insights.get("professional_analysis", {}).get("investor_view", {})
            if investor_view.get("risk_return_profile") == "high_risk" and signal["confidence"] < 0.9:
                return False
            
            # Check market view
            market_view = professional_insights.get("professional_analysis", {}).get("market_view", {})
            if market_view.get("technical_outlook") == "bearish" and signal["action"] == "buy":
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Professional insights validation error: {str(e)}")
            return True
    
    async def _calculate_intelligent_position_size(self, signal: Dict[str, Any], account_status: Dict[str, Any], market_regime, economic_cycle) -> int:
        """Calculate position size using financial intelligence"""
        try:
            base_balance = account_status.get("balance", 100000)
            base_position_size = int(base_balance * self.position_size_pct)
            
            # Adjust based on confidence
            confidence_multiplier = signal.get("confidence", 0.5)
            if confidence_multiplier > 0.9:
                confidence_multiplier = 1.2  # High confidence = larger position
            elif confidence_multiplier < 0.8:
                confidence_multiplier = 0.8  # Lower confidence = smaller position
            
            # Adjust based on market regime
            regime_multiplier = 1.0
            if market_regime:
                if market_regime.regime == "crisis":
                    regime_multiplier = 0.5  # Reduce position size in crisis
                elif market_regime.regime == "bull":
                    regime_multiplier = 1.2  # Increase position size in bull market
            
            # Adjust based on economic cycle
            cycle_multiplier = 1.0
            if economic_cycle:
                if economic_cycle.phase == "contraction":
                    cycle_multiplier = 0.7  # Reduce position size in contraction
                elif economic_cycle.phase == "expansion":
                    cycle_multiplier = 1.1  # Increase position size in expansion
            
            # Calculate final position size
            final_position_size = int(base_position_size * confidence_multiplier * regime_multiplier * cycle_multiplier)
            
            # Ensure minimum and maximum limits
            final_position_size = max(1000, min(final_position_size, int(base_balance * 0.1)))
            
            return final_position_size
            
        except Exception as e:
            logger.error(f"Position size calculation error: {str(e)}")
            return 1000
    
    async def _execute_trade(self, signal: Dict[str, Any], position_size: int) -> Dict[str, Any]:
        """Execute the actual trade"""
        try:
            symbol = signal["symbol"]
            action = signal["action"]
            
            if action == "buy":
                result = await trading_engine.place_market_order(
                    pair=symbol,
                    side="buy",
                    units=position_size
                )
            elif action == "sell":
                result = await trading_engine.place_market_order(
                    pair=symbol,
                    side="sell",
                    units=position_size
                )
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _calculate_overall_sentiment(self, signals: List[Dict[str, Any]]) -> str:
        """Calculate overall sentiment from signals"""
        try:
            if not signals:
                return "neutral"
            
            bullish_count = sum(1 for s in signals if s.get("sentiment") == "bullish")
            bearish_count = sum(1 for s in signals if s.get("sentiment") == "bearish")
            
            if bullish_count > bearish_count:
                return "bullish"
            elif bearish_count > bullish_count:
                return "bearish"
            else:
                return "neutral"
                
        except Exception as e:
            return "neutral"
    
    def _calculate_overall_confidence(self, signals: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence from signals"""
        try:
            if not signals:
                return 0.0
            
            confidences = [s.get("confidence", 0) for s in signals]
            return sum(confidences) / len(confidences)
            
        except Exception as e:
            return 0.0
    
    def _extract_economic_data(self, market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract economic data from market analysis"""
        try:
            # Placeholder - in production, this would extract real economic indicators
            return {
                "gdp_growth": 2.5,
                "inflation": 3.2,
                "unemployment": 3.8,
                "interest_rates": 5.5,
                "consumer_confidence": 65.0,
                "business_confidence": 70.0
            }
        except Exception as e:
            return {}
    
    async def run_autonomous_trading(self, interval_minutes: int = 15):
        """Run autonomous trading loop"""
        try:
            logger.info(f"🧠 Starting autonomous trading with {interval_minutes}-minute intervals")
            
            while self.trading_enabled:
                try:
                    # Step 1: Analyze market conditions
                    market_analysis = await self.analyze_market_conditions()
                    if "error" in market_analysis:
                        logger.error(f"Market analysis failed: {market_analysis['error']}")
                        continue
                    
                    # Step 2: Generate trading signals
                    signals = await self.generate_trading_signals(market_analysis)
                    if "error" in signals:
                        logger.error(f"Signal generation failed: {signals['error']}")
                        continue
                    
                    # Step 3: Execute AI strategy
                    if signals.get("signals"):
                        execution_result = await self.execute_ai_strategy(signals)
                        logger.info(f"Strategy execution: {execution_result.get('trades_executed', 0)} trades executed")
                    
                    # Step 4: Wait for next cycle
                    await asyncio.sleep(interval_minutes * 60)
                    
                except Exception as e:
                    logger.error(f"Autonomous trading cycle error: {str(e)}")
                    await asyncio.sleep(60)  # Wait 1 minute before retrying
            
        except Exception as e:
            logger.error(f"Autonomous trading error: {str(e)}")
    
    def enable_autonomous_trading(self):
        """Enable autonomous trading"""
        self.trading_enabled = True
        logger.info("🧠 Autonomous trading enabled")
    
    def disable_autonomous_trading(self):
        """Disable autonomous trading"""
        self.trading_enabled = False
        logger.info("🧠 Autonomous trading disabled")
    
    def get_trading_status(self) -> Dict[str, Any]:
        """Get current trading status"""
        return {
            "trading_enabled": self.trading_enabled,
            "last_analysis": self.last_analysis,
            "market_regime": self.market_regime.regime if self.market_regime else "unknown",
            "economic_cycle": self.economic_cycle.phase if self.economic_cycle else "unknown",
            "trade_history_count": len(self.trade_history),
            "confidence_threshold": self.confidence_threshold
        }


# Global AI trading brain instance
ai_trading_brain = AITradingBrain()
