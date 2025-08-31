#!/usr/bin/env python3
"""
Autonomous Algorithmic Trading System
Runs continuously and executes trades automatically based on AI analysis.
"""

import asyncio
import json
import time
import signal
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import requests
import structlog
from dataclasses import dataclass, asdict
from src.oanda_client import OANDAClient

# Configure logging
logger = structlog.get_logger()

@dataclass
class TradeSignal:
    """Trade signal from AI analysis."""
    pair: str
    side: str  # "BUY" or "SELL"
    entry_price: float
    stop_loss: float
    take_profit: float
    confidence: float
    strategy: str
    reasoning: str
    timestamp: datetime

@dataclass
class ActiveTrade:
    """Currently active trade."""
    trade_id: str
    pair: str
    side: str
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    lot_size: float
    amount_usd: float
    strategy: str
    entry_time: datetime
    pnl: float = 0.0
    status: str = "OPEN"

class AutonomousTrader:
    """Autonomous algorithmic trading system."""
    
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.active_trades: Dict[str, ActiveTrade] = {}
        self.trade_history: List[Dict] = []
        self.is_running = False
        self.trading_enabled = True
        
        # Initialize OANDA client (treating demo as live trading)
        self.oanda_client = OANDAClient(
            api_key="1725da5aa30805b09b7c7eb0094ffff4-d6b1be348877531faa9a3253cbda3cfd",
            account_id="101-001-36248121-001",
            practice=True  # Demo account but treating as live
        )
        
        # Configuration
        self.max_trades = 3  # Maximum concurrent trades
        self.min_confidence = 0.7  # Minimum AI confidence to trade
        self.max_risk_per_trade = 0.02  # 2% risk per trade
        self.total_account_risk = 0.06  # 6% total account risk
        
        # Advanced Risk Management
        self.max_correlation = 0.7  # Maximum correlation between positions
        self.max_drawdown = 0.15  # 15% maximum drawdown
        self.trailing_stop_distance = 50  # 50 pips trailing stop
        self.use_trailing_stops = True  # Enable trailing stops
        
        # Performance Tracking
        self.performance_metrics = {}
        self.correlation_matrix = {}
        self.streaming_enabled = True
        
        # Trading pairs to monitor (OANDA format)
        self.trading_pairs = ["EUR_USD", "GBP_USD", "USD_JPY"]
        
        # Strategy weights
        self.strategy_weights = {
            "trend_following": 0.4,
            "mean_reversion": 0.3,
            "momentum": 0.3
        }
        
        logger.info("Autonomous trader initialized", 
                   max_trades=self.max_trades,
                   min_confidence=self.min_confidence,
                   trading_pairs=self.trading_pairs)

    async def start(self):
        """Start the autonomous trading system."""
        logger.info("Starting autonomous trading system...")
        self.is_running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Initialize account balance
            await self.update_account_balance()
            
            # Start real-time streaming
            await self.start_streaming()
            
            # Main trading loop
            while self.is_running:
                await self.trading_cycle()
                await asyncio.sleep(60)  # Wait 1 minute between cycles
                
        except Exception as e:
            logger.error("Trading system error", error=str(e))
        finally:
            await self.shutdown()

    async def trading_cycle(self):
        """One complete trading cycle."""
        try:
            # 1. Update account balance and performance metrics
            await self.update_account_balance()
            await self.update_performance_metrics()
            
            # 2. Update correlation matrix
            await self.update_correlation_matrix()
            
            # 3. Monitor existing trades with enhanced risk management
            await self.monitor_active_trades()
            
            # 4. Check risk limits and drawdown
            if not await self.check_risk_limits():
                logger.warning("Risk limits exceeded, pausing new trades")
                return
            
            # 5. Analyze markets for new opportunities
            if len(self.active_trades) < self.max_trades:
                await self.analyze_markets()
            
            # 6. Log system status
            await self.log_system_status()
            
        except Exception as e:
            logger.error("Trading cycle error", error=str(e))

    async def update_account_balance(self):
        """Update account balance information."""
        try:
            # Use OANDA client for direct account access
            account_summary = self.oanda_client.get_account_summary()
            if account_summary:
                self.account_balance = float(account_summary.get('balance', 100000))
                logger.info("Account balance updated", balance=self.account_balance)
            else:
                # Fallback to API
                response = requests.get(f"{self.api_base}/api/v1/account/balance")
                if response.status_code == 200:
                    data = response.json()
                    self.account_balance = float(data.get('balance', 100000))
                    logger.info("Account balance updated (fallback)", balance=self.account_balance)
        except Exception as e:
            logger.error("Failed to update account balance", error=str(e))

    async def monitor_active_trades(self):
        """Monitor and manage active trades."""
        trades_to_close = []
        
        for trade_id, trade in self.active_trades.items():
            try:
                # Get current market price
                current_price = await self.get_current_price(trade.pair)
                if not current_price:
                    continue
                
                trade.current_price = current_price
                
                # Calculate P&L
                if trade.side == "BUY":
                    trade.pnl = (current_price - trade.entry_price) * trade.lot_size * 100000
                else:
                    trade.pnl = (trade.entry_price - current_price) * trade.lot_size * 100000
                
                # Check exit conditions
                should_exit = False
                exit_reason = ""
                
                # Stop loss check
                if trade.side == "BUY" and current_price <= trade.stop_loss:
                    should_exit = True
                    exit_reason = "Stop Loss"
                elif trade.side == "SELL" and current_price >= trade.stop_loss:
                    should_exit = True
                    exit_reason = "Stop Loss"
                
                # Take profit check
                elif trade.side == "BUY" and current_price >= trade.take_profit:
                    should_exit = True
                    exit_reason = "Take Profit"
                elif trade.side == "SELL" and current_price <= trade.take_profit:
                    should_exit = True
                    exit_reason = "Take Profit"
                
                # Time-based exit (4 hours max)
                elif datetime.now(timezone.utc) - trade.entry_time > timedelta(hours=4):
                    should_exit = True
                    exit_reason = "Time Limit"
                
                if should_exit:
                    trades_to_close.append((trade_id, exit_reason))
                
                logger.info("Trade monitored", 
                           trade_id=trade_id,
                           pair=trade.pair,
                           side=trade.side,
                           current_price=current_price,
                           pnl=trade.pnl,
                           status=trade.status)
                
            except Exception as e:
                logger.error("Error monitoring trade", trade_id=trade_id, error=str(e))
        
        # Close trades that meet exit conditions
        for trade_id, exit_reason in trades_to_close:
            await self.close_trade(trade_id, exit_reason)

    async def analyze_markets(self):
        """Analyze markets for new trading opportunities."""
        for pair in self.trading_pairs:
            try:
                # Get AI market analysis
                analysis = await self.get_market_analysis(pair)
                if not analysis or analysis.get('error'):
                    continue
                
                # Check if we should trade
                if await self.should_trade(analysis):
                    # Generate trading strategy
                    strategy = await self.generate_strategy(pair, analysis)
                    if strategy and strategy.get('strategy'):
                        # Execute trade
                        await self.execute_trade(pair, analysis, strategy)
                
            except Exception as e:
                logger.error("Error analyzing market", pair=pair, error=str(e))

    async def should_trade(self, analysis: Dict) -> bool:
        """Determine if we should trade based on analysis."""
        # Check confidence threshold
        if analysis.get('confidence', 0) < self.min_confidence:
            return False
        
        # Check if we have a clear recommendation
        recommendation = analysis.get('recommendation', 'HOLD')
        if recommendation == 'HOLD':
            return False
        
        # Check if we're not over-risked
        total_risk = sum(trade.amount_usd * self.max_risk_per_trade 
                        for trade in self.active_trades.values())
        if total_risk >= self.account_balance * self.total_account_risk:
            return False
        
        # Check if we don't have too many trades on this pair
        pair = analysis.get('pair', '')
        pair_trades = sum(1 for trade in self.active_trades.values() 
                         if trade.pair == pair)
        if pair_trades >= 1:  # Max 1 trade per pair
            return False
        
        # Check correlation risk
        if not await self.check_correlation_risk(pair):
            return False
        
        # Check margin requirements (will be checked again in execute_trade)
        # This is a preliminary check
        
        return True

    async def execute_trade(self, pair: str, analysis: Dict, strategy: Dict):
        """Execute a new trade."""
        try:
            # Calculate position size
            risk_amount = self.account_balance * self.max_risk_per_trade
            stop_loss_pips = strategy['strategy']['stop_loss_pips']
            
            # Calculate lot size (convert to units for OANDA)
            pip_value = 10  # For 100k lot
            lot_size = risk_amount / (stop_loss_pips * pip_value)
            lot_size = max(0.01, min(lot_size, 1.0))  # Between 0.01 and 1.0 lots
            
            # Convert to OANDA units (1000 units = 0.01 lot)
            units = int(lot_size * 100000)
            
            # Check margin requirements
            if not await self.check_margin_requirements(pair, lot_size):
                logger.warning("Insufficient margin for trade", pair=pair, lot_size=lot_size)
                return
            
            # Get current price
            current_price = await self.get_current_price(pair)
            if not current_price:
                return
            
            # Calculate stop loss and take profit
            side = analysis['recommendation']
            if side == "BUY":
                stop_loss = current_price - (stop_loss_pips * 0.0001)
                take_profit = current_price + (strategy['strategy']['take_profit_pips'] * 0.0001)
                oanda_side = "buy"
            else:
                stop_loss = current_price + (stop_loss_pips * 0.0001)
                take_profit = current_price - (strategy['strategy']['take_profit_pips'] * 0.0001)
                oanda_side = "sell"
            
            # Execute real trade via OANDA
            order_result = self.oanda_client.place_market_order(
                instrument=pair,
                units=units,
                side=oanda_side,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            if order_result and order_result.get('orderFillTransaction'):
                # Trade was executed successfully
                fill_transaction = order_result['orderFillTransaction']
                trade_id = fill_transaction.get('id', f"auto_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{pair}")
                
                trade = ActiveTrade(
                    trade_id=trade_id,
                    pair=pair,
                    side=side,
                    entry_price=float(fill_transaction.get('price', current_price)),
                    current_price=float(fill_transaction.get('price', current_price)),
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    lot_size=round(lot_size, 2),
                    amount_usd=risk_amount / self.max_risk_per_trade,
                    strategy=strategy['strategy']['name'],
                    entry_time=datetime.now(timezone.utc)
                )
                
                # Add to active trades
                self.active_trades[trade_id] = trade
                
                # Log successful trade execution
                logger.info("Real trade executed via OANDA", 
                           trade_id=trade_id,
                           pair=pair,
                           side=side,
                           entry_price=trade.entry_price,
                           units=units,
                           lot_size=lot_size,
                           strategy=strategy['strategy']['name'],
                           confidence=analysis.get('confidence', 0),
                           reasoning=analysis.get('reasoning', ''))
                
                # Add to trade history
                self.trade_history.append(asdict(trade))
                
            else:
                # Trade execution failed
                logger.warning("Trade execution failed", 
                              pair=pair,
                              side=side,
                              order_result=order_result)
            
        except Exception as e:
            logger.error("Error executing trade", pair=pair, error=str(e))

    async def close_trade(self, trade_id: str, exit_reason: str):
        """Close an active trade."""
        try:
            trade = self.active_trades[trade_id]
            trade.status = "CLOSED"
            
            # Try to close via OANDA if it's a real trade
            if trade_id.startswith("auto_"):
                # This is a paper trade, just log it
                pass
            else:
                # This is a real OANDA trade, close it
                try:
                    close_result = self.oanda_client.close_trade(trade_id)
                    if close_result:
                        logger.info("Trade closed via OANDA", 
                                   trade_id=trade_id,
                                   close_result=close_result)
                except Exception as e:
                    logger.warning("Failed to close trade via OANDA", 
                                  trade_id=trade_id, 
                                  error=str(e))
            
            # Calculate final P&L
            if trade.side == "BUY":
                final_pnl = (trade.current_price - trade.entry_price) * trade.lot_size * 100000
            else:
                final_pnl = (trade.entry_price - trade.current_price) * trade.lot_size * 100000
            
            # Log trade closure
            logger.info("Trade closed", 
                       trade_id=trade_id,
                       pair=trade.pair,
                       side=trade.side,
                       entry_price=trade.entry_price,
                       exit_price=trade.current_price,
                       pnl=final_pnl,
                       exit_reason=exit_reason,
                       duration=datetime.now(timezone.utc) - trade.entry_time)
            
            # Remove from active trades
            del self.active_trades[trade_id]
            
            # Update trade history
            for history_trade in self.trade_history:
                if history_trade['trade_id'] == trade_id:
                    history_trade['status'] = 'CLOSED'
                    history_trade['exit_price'] = trade.current_price
                    history_trade['pnl'] = final_pnl
                    history_trade['exit_reason'] = exit_reason
                    history_trade['exit_time'] = datetime.now(timezone.utc).isoformat()
                    break
            
        except Exception as e:
            logger.error("Error closing trade", trade_id=trade_id, error=str(e))

    async def get_market_analysis(self, pair: str) -> Optional[Dict]:
        """Get AI market analysis for a pair."""
        try:
            response = requests.post(
                f"{self.api_base}/api/v1/ai/analyze-market",
                headers={"Content-Type": "application/json"},
                json={"pair": pair, "timeframe": "1h"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Failed to get market analysis", 
                           pair=pair, status_code=response.status_code)
                return None
                
        except Exception as e:
            logger.error("Error getting market analysis", pair=pair, error=str(e))
            return None

    async def generate_strategy(self, pair: str, analysis: Dict) -> Optional[Dict]:
        """Generate trading strategy for a pair."""
        try:
            # Choose strategy based on market conditions
            trend = analysis.get('trend', 'sideways')
            
            if 'bullish' in trend or 'bearish' in trend:
                strategy_type = "trend_following"
            elif 'sideways' in trend:
                strategy_type = "mean_reversion"
            else:
                strategy_type = "momentum"
            
            response = requests.post(
                f"{self.api_base}/api/v1/ai/generate-strategy",
                headers={"Content-Type": "application/json"},
                json={"pair": pair, "timeframe": "1h", "type": strategy_type}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error("Failed to generate strategy", 
                           pair=pair, status_code=response.status_code)
                return None
                
        except Exception as e:
            logger.error("Error generating strategy", pair=pair, error=str(e))
            return None

    async def get_current_price(self, pair: str) -> Optional[float]:
        """Get current price for a pair."""
        try:
            # Use OANDA client for direct price access
            pricing = self.oanda_client.get_pricing([pair])
            if pricing and pricing.get('prices'):
                return float(pricing['prices'][0]['bids'][0]['price'])
            
            # Fallback to API
            response = requests.get(f"{self.api_base}/api/v1/data/market-data/{pair}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('candles') and len(data['candles']) > 0:
                    return float(data['candles'][-1]['mid']['c'])
            
            return None
            
        except Exception as e:
            logger.error("Error getting current price", pair=pair, error=str(e))
            return None

    async def log_system_status(self):
        """Log current system status."""
        total_pnl = sum(trade.pnl for trade in self.active_trades.values())
        win_rate = self.calculate_win_rate()
        
        logger.info("System status", 
                   active_trades=len(self.active_trades),
                   total_pnl=total_pnl,
                   win_rate=win_rate,
                   account_balance=self.account_balance)

    def calculate_win_rate(self) -> float:
        """Calculate win rate from trade history."""
        closed_trades = [t for t in self.trade_history if t.get('status') == 'CLOSED']
        if not closed_trades:
            return 0.0
        
        winning_trades = [t for t in closed_trades if t.get('pnl', 0) > 0]
        return len(winning_trades) / len(closed_trades) * 100

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received", signal=signum)
        self.is_running = False

    async def shutdown(self):
        """Graceful shutdown."""
        logger.info("Shutting down autonomous trading system...")
        
        # Close all active trades
        for trade_id in list(self.active_trades.keys()):
            await self.close_trade(trade_id, "System Shutdown")
        
        # Save trade history
        await self.save_trade_history()
        
        logger.info("Autonomous trading system shutdown complete")

    async def save_trade_history(self):
        """Save trade history to file."""
        try:
            with open('trade_history.json', 'w') as f:
                json.dump(self.trade_history, f, indent=2, default=str)
            logger.info("Trade history saved")
        except Exception as e:
            logger.error("Failed to save trade history", error=str(e))

    def get_system_stats(self) -> Dict:
        """Get current system statistics."""
        total_pnl = sum(trade.pnl for trade in self.active_trades.values())
        win_rate = self.calculate_win_rate()
        
        return {
            "active_trades": len(self.active_trades),
            "total_pnl": total_pnl,
            "win_rate": win_rate,
            "account_balance": self.account_balance,
            "trading_enabled": self.trading_enabled,
            "performance_metrics": self.performance_metrics,
            "correlation_matrix": self.correlation_matrix,
            "active_trades_list": [
                {
                    "trade_id": trade.trade_id,
                    "pair": trade.pair,
                    "side": trade.side,
                    "entry_price": trade.entry_price,
                    "current_price": trade.current_price,
                    "pnl": trade.pnl,
                    "strategy": trade.strategy,
                    "entry_time": trade.entry_time.isoformat()
                }
                for trade in self.active_trades.values()
            ]
        }

    async def update_performance_metrics(self):
        """Update performance metrics."""
        try:
            metrics = self.oanda_client.get_performance_metrics(days=30)
            if metrics:
                self.performance_metrics = metrics
                logger.info("Performance metrics updated", metrics=metrics)
        except Exception as e:
            logger.error("Error updating performance metrics", error=str(e))

    async def update_correlation_matrix(self):
        """Update correlation matrix for risk management."""
        try:
            correlation_data = self.oanda_client.calculate_correlation_matrix(
                self.trading_pairs, days=30
            )
            if correlation_data:
                self.correlation_matrix = correlation_data
                logger.info("Correlation matrix updated", 
                           instruments=correlation_data['instruments'])
        except Exception as e:
            logger.error("Error updating correlation matrix", error=str(e))

    async def check_risk_limits(self) -> bool:
        """Check if we're within risk limits."""
        try:
            # Check drawdown
            if self.performance_metrics:
                total_pnl = self.performance_metrics.get('total_pnl', 0)
                if total_pnl < 0:
                    drawdown = abs(total_pnl) / self.account_balance
                    if drawdown > self.max_drawdown:
                        logger.warning("Maximum drawdown exceeded", 
                                      drawdown=drawdown, 
                                      max_drawdown=self.max_drawdown)
                        return False
            
            # Check total risk exposure
            total_risk = len(self.active_trades) * self.max_risk_per_trade
            if total_risk > self.total_account_risk:
                logger.warning("Total risk exposure exceeded", 
                              total_risk=total_risk, 
                              max_risk=self.total_account_risk)
                return False
            
            return True
            
        except Exception as e:
            logger.error("Error checking risk limits", error=str(e))
            return False

    async def check_correlation_risk(self, new_pair: str) -> bool:
        """Check correlation risk for new position."""
        try:
            if not self.correlation_matrix or not self.active_trades:
                return True  # No correlation data or no active trades
            
            correlation_matrix = self.correlation_matrix.get('correlation_matrix', {})
            
            for trade in self.active_trades.values():
                if trade.pair in correlation_matrix and new_pair in correlation_matrix[trade.pair]:
                    correlation = abs(correlation_matrix[trade.pair][new_pair])
                    if correlation > self.max_correlation:
                        logger.warning("High correlation detected", 
                                      pair1=trade.pair, 
                                      pair2=new_pair, 
                                      correlation=correlation)
                        return False
            
            return True
            
        except Exception as e:
            logger.error("Error checking correlation risk", error=str(e))
            return True  # Allow trade if correlation check fails

    async def add_trailing_stop(self, trade_id: str):
        """Add trailing stop to an existing trade."""
        try:
            trade = self.active_trades.get(trade_id)
            if not trade:
                return
            
            # Calculate trailing stop price
            current_price = await self.get_current_price(trade.pair)
            if not current_price:
                return
            
            if trade.side == "BUY":
                new_stop_loss = current_price - (self.trailing_stop_distance * 0.0001)
                if new_stop_loss > trade.stop_loss:
                    # Update stop loss
                    trade.stop_loss = new_stop_loss
                    
                    # Update OANDA order if it's a real trade
                    if not trade_id.startswith("auto_"):
                        self.oanda_client.update_trade(trade_id, {
                            "stopLoss": str(new_stop_loss)
                        })
                    
                    logger.info("Trailing stop updated", 
                               trade_id=trade_id,
                               new_stop_loss=new_stop_loss)
            
            elif trade.side == "SELL":
                new_stop_loss = current_price + (self.trailing_stop_distance * 0.0001)
                if new_stop_loss < trade.stop_loss:
                    # Update stop loss
                    trade.stop_loss = new_stop_loss
                    
                    # Update OANDA order if it's a real trade
                    if not trade_id.startswith("auto_"):
                        self.oanda_client.update_trade(trade_id, {
                            "stopLoss": str(new_stop_loss)
                        })
                    
                    logger.info("Trailing stop updated", 
                               trade_id=trade_id,
                               new_stop_loss=new_stop_loss)
                    
        except Exception as e:
            logger.error("Error adding trailing stop", trade_id=trade_id, error=str(e))

    async def check_margin_requirements(self, pair: str, lot_size: float) -> bool:
        """Check if we have enough margin for a new position."""
        try:
            units = int(lot_size * 100000)
            margin_req = self.oanda_client.get_margin_requirements(pair, units)
            
            if margin_req:
                margin_required = margin_req['margin_required']
                has_margin = self.oanda_client.check_margin_availability(margin_required)
                
                if not has_margin:
                    logger.warning("Insufficient margin for trade", 
                                  pair=pair,
                                  margin_required=margin_required)
                    return False
                
                return True
            
            return True  # Allow trade if margin check fails
            
        except Exception as e:
            logger.error("Error checking margin requirements", error=str(e))
            return True  # Allow trade if margin check fails

    async def start_streaming(self):
        """Start real-time price streaming."""
        try:
            if self.streaming_enabled:
                # Start price streaming
                asyncio.create_task(
                    self.oanda_client.stream_pricing(
                        self.trading_pairs, 
                        self.handle_price_update
                    )
                )
                
                # Start transaction streaming
                asyncio.create_task(
                    self.oanda_client.stream_transactions(
                        self.handle_transaction_update
                    )
                )
                
                logger.info("Real-time streaming started")
                
        except Exception as e:
            logger.error("Error starting streaming", error=str(e))

    async def handle_price_update(self, price_data: Dict):
        """Handle real-time price updates."""
        try:
            instrument = price_data.get('instrument')
            bid = float(price_data.get('bids', [{}])[0].get('price', 0))
            ask = float(price_data.get('asks', [{}])[0].get('price', 0))
            
            # Update active trades with new prices
            for trade in self.active_trades.values():
                if trade.pair == instrument:
                    trade.current_price = (bid + ask) / 2
                    
                    # Check for trailing stop updates
                    if self.use_trailing_stops:
                        await self.add_trailing_stop(trade.trade_id)
            
            logger.debug("Price update processed", instrument=instrument, bid=bid, ask=ask)
            
        except Exception as e:
            logger.error("Error handling price update", error=str(e))

    async def handle_transaction_update(self, transaction_data: Dict):
        """Handle real-time transaction updates."""
        try:
            transaction_type = transaction_data.get('type')
            trade_id = transaction_data.get('tradeID')
            
            if transaction_type == "ORDER_FILL":
                # New trade opened
                logger.info("New trade filled via streaming", trade_id=trade_id)
                
            elif transaction_type == "TRADE_CLOSE":
                # Trade closed
                logger.info("Trade closed via streaming", trade_id=trade_id)
                
            elif transaction_type == "STOP_LOSS_FILLED":
                # Stop loss triggered
                logger.info("Stop loss triggered", trade_id=trade_id)
                
            elif transaction_type == "TAKE_PROFIT_FILLED":
                # Take profit triggered
                logger.info("Take profit triggered", trade_id=trade_id)
            
        except Exception as e:
            logger.error("Error handling transaction update", error=str(e))

async def main():
    """Main function."""
    trader = AutonomousTrader()
    await trader.start()

if __name__ == "__main__":
    asyncio.run(main())
