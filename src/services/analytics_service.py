"""
Analytics Service for performance analysis, reporting, and business intelligence.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
import structlog

from src.core.logging import TradingLogger
from src.models.trade import Trade
from src.models.position import Position
from src.models.portfolio import Portfolio, PortfolioMetrics


@dataclass
class PerformanceMetrics:
    """Performance metrics for analysis."""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    current_drawdown: float
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    largest_win: float
    largest_loss: float
    consecutive_wins: int
    consecutive_losses: int
    recovery_factor: float
    risk_reward_ratio: float
    var_95: float
    var_99: float
    expected_shortfall: float
    beta: float
    alpha: float
    information_ratio: float
    treynor_ratio: float
    jensen_alpha: float
    tracking_error: float
    correlation: float
    skewness: float
    kurtosis: float
    timestamp: datetime


@dataclass
class StrategyAnalysis:
    """Strategy performance analysis."""
    strategy_name: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    average_pnl: float
    sharpe_ratio: float
    max_drawdown: float
    profit_factor: float
    average_win: float
    average_loss: float
    best_trade: float
    worst_trade: float
    consecutive_wins: int
    consecutive_losses: int
    active_positions: int
    last_trade_date: datetime


@dataclass
class MarketAnalysis:
    """Market analysis and insights."""
    pair: str
    current_price: float
    price_change_24h: float
    price_change_pct_24h: float
    volatility_24h: float
    volatility_7d: float
    trend_direction: str  # up, down, sideways
    trend_strength: float
    support_level: float
    resistance_level: float
    rsi: float
    macd: float
    bollinger_position: float  # 0-1, where 0 is lower band, 1 is upper band
    sentiment_score: float
    news_impact: str
    timestamp: datetime


class AnalyticsService:
    """Comprehensive analytics service for trading performance and market analysis."""
    
    def __init__(self):
        self.logger = TradingLogger("analytics_service")
        self.is_running = False
        
        # Data storage
        self.performance_history: List[PerformanceMetrics] = []
        self.strategy_analyses: Dict[str, StrategyAnalysis] = {}
        self.market_analyses: Dict[str, MarketAnalysis] = {}
        
        # Configuration
        self.update_interval = 300  # 5 minutes
        self.risk_free_rate = 0.02  # 2% annual risk-free rate
    
    async def start(self):
        """Start the analytics service."""
        self.is_running = True
        self.logger.logger.info("Analytics service started")
        
        # Start analytics loop
        asyncio.create_task(self._analytics_loop())
    
    async def stop(self):
        """Stop the analytics service."""
        self.is_running = False
        self.logger.logger.info("Analytics service stopped")
    
    async def _analytics_loop(self):
        """Main analytics loop."""
        while self.is_running:
            try:
                # Update performance metrics
                await self._update_performance_metrics()
                
                # Update strategy analyses
                await self._update_strategy_analyses()
                
                # Update market analyses
                await self._update_market_analyses()
                
                # Sleep for update interval
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.logger.error("Error in analytics loop", error=str(e))
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _update_performance_metrics(self):
        """Update portfolio performance metrics."""
        try:
            # Get portfolio data (this would come from database)
            portfolio = await self._get_portfolio_data()
            trades = await self._get_trades_data()
            
            if portfolio and trades:
                metrics = self._calculate_performance_metrics(portfolio, trades)
                self.performance_history.append(metrics)
                
                # Keep only recent history
                cutoff_time = datetime.utcnow() - timedelta(days=365)
                self.performance_history = [
                    m for m in self.performance_history 
                    if m.timestamp > cutoff_time
                ]
                
        except Exception as e:
            self.logger.logger.error("Error updating performance metrics", error=str(e))
    
    async def _update_strategy_analyses(self):
        """Update strategy performance analyses."""
        try:
            # Get strategy data (this would come from database)
            strategies_data = await self._get_strategies_data()
            
            for strategy_name, data in strategies_data.items():
                analysis = self._calculate_strategy_analysis(strategy_name, data)
                self.strategy_analyses[strategy_name] = analysis
                
        except Exception as e:
            self.logger.logger.error("Error updating strategy analyses", error=str(e))
    
    async def _update_market_analyses(self):
        """Update market analyses."""
        try:
            # Get market data (this would come from data service)
            market_data = await self._get_market_data()
            
            for pair, data in market_data.items():
                analysis = self._calculate_market_analysis(pair, data)
                self.market_analyses[pair] = analysis
                
        except Exception as e:
            self.logger.logger.error("Error updating market analyses", error=str(e))
    
    def _calculate_performance_metrics(self, portfolio: Portfolio, trades: List[Trade]) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics."""
        try:
            # Calculate basic metrics
            total_return = portfolio.total_pnl
            initial_balance = portfolio.initial_balance
            current_balance = portfolio.current_balance
            
            # Calculate returns
            if initial_balance > 0:
                total_return_pct = (current_balance - initial_balance) / initial_balance
            else:
                total_return_pct = 0.0
            
            # Calculate annualized return
            days_active = (datetime.utcnow() - portfolio.created_at).days
            if days_active > 0:
                annualized_return = ((1 + total_return_pct) ** (365 / days_active)) - 1
            else:
                annualized_return = 0.0
            
            # Calculate volatility
            returns = self._calculate_returns(trades)
            volatility = np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0.0
            
            # Calculate Sharpe ratio
            if volatility > 0:
                sharpe_ratio = (annualized_return - self.risk_free_rate) / volatility
            else:
                sharpe_ratio = 0.0
            
            # Calculate Sortino ratio
            negative_returns = [r for r in returns if r < 0]
            if negative_returns:
                downside_deviation = np.std(negative_returns) * np.sqrt(252)
                sortino_ratio = (annualized_return - self.risk_free_rate) / downside_deviation if downside_deviation > 0 else 0.0
            else:
                sortino_ratio = float('inf') if annualized_return > self.risk_free_rate else 0.0
            
            # Calculate drawdown
            max_drawdown, current_drawdown = self._calculate_drawdown(portfolio)
            
            # Calculate Calmar ratio
            calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0.0
            
            # Calculate trading metrics
            winning_trades = [t for t in trades if t.pnl and t.pnl > 0]
            losing_trades = [t for t in trades if t.pnl and t.pnl < 0]
            
            win_rate = len(winning_trades) / len(trades) if trades else 0.0
            
            total_profit = sum(t.pnl for t in winning_trades)
            total_loss = abs(sum(t.pnl for t in losing_trades))
            
            profit_factor = total_profit / total_loss if total_loss > 0 else 0.0
            
            average_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0.0
            average_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0.0
            
            largest_win = max([t.pnl for t in winning_trades]) if winning_trades else 0.0
            largest_loss = min([t.pnl for t in losing_trades]) if losing_trades else 0.0
            
            # Calculate consecutive wins/losses
            consecutive_wins, consecutive_losses = self._calculate_consecutive_trades(trades)
            
            # Calculate recovery factor
            recovery_factor = total_return / max_drawdown if max_drawdown > 0 else 0.0
            
            # Calculate risk-reward ratio
            risk_reward_ratio = average_win / abs(average_loss) if average_loss != 0 else 0.0
            
            # Calculate VaR
            var_95, var_99 = self._calculate_var(returns)
            
            # Calculate expected shortfall (Conditional VaR)
            expected_shortfall = self._calculate_expected_shortfall(returns, var_95)
            
            # Calculate beta and alpha (assuming benchmark is risk-free rate)
            beta = 1.0  # Placeholder - would need benchmark data
            alpha = annualized_return - (self.risk_free_rate + beta * (0.0 - self.risk_free_rate))
            
            # Calculate information ratio
            tracking_error = volatility  # Placeholder - would need benchmark data
            information_ratio = (annualized_return - self.risk_free_rate) / tracking_error if tracking_error > 0 else 0.0
            
            # Calculate Treynor ratio
            treynor_ratio = (annualized_return - self.risk_free_rate) / beta if beta > 0 else 0.0
            
            # Calculate Jensen's alpha
            jensen_alpha = alpha  # Same as alpha for now
            
            # Calculate correlation (placeholder)
            correlation = 0.0  # Would need benchmark data
            
            # Calculate skewness and kurtosis
            skewness = self._calculate_skewness(returns)
            kurtosis = self._calculate_kurtosis(returns)
            
            return PerformanceMetrics(
                total_return=total_return,
                annualized_return=annualized_return,
                volatility=volatility,
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                calmar_ratio=calmar_ratio,
                max_drawdown=max_drawdown,
                current_drawdown=current_drawdown,
                win_rate=win_rate,
                profit_factor=profit_factor,
                average_win=average_win,
                average_loss=average_loss,
                largest_win=largest_win,
                largest_loss=largest_loss,
                consecutive_wins=consecutive_wins,
                consecutive_losses=consecutive_losses,
                recovery_factor=recovery_factor,
                risk_reward_ratio=risk_reward_ratio,
                var_95=var_95,
                var_99=var_99,
                expected_shortfall=expected_shortfall,
                beta=beta,
                alpha=alpha,
                information_ratio=information_ratio,
                treynor_ratio=treynor_ratio,
                jensen_alpha=jensen_alpha,
                tracking_error=tracking_error,
                correlation=correlation,
                skewness=skewness,
                kurtosis=kurtosis,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.logger.error("Error calculating performance metrics", error=str(e))
            # Return default metrics
            return PerformanceMetrics(
                total_return=0.0,
                annualized_return=0.0,
                volatility=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                calmar_ratio=0.0,
                max_drawdown=0.0,
                current_drawdown=0.0,
                win_rate=0.0,
                profit_factor=0.0,
                average_win=0.0,
                average_loss=0.0,
                largest_win=0.0,
                largest_loss=0.0,
                consecutive_wins=0,
                consecutive_losses=0,
                recovery_factor=0.0,
                risk_reward_ratio=0.0,
                var_95=0.0,
                var_99=0.0,
                expected_shortfall=0.0,
                beta=1.0,
                alpha=0.0,
                information_ratio=0.0,
                treynor_ratio=0.0,
                jensen_alpha=0.0,
                tracking_error=0.0,
                correlation=0.0,
                skewness=0.0,
                kurtosis=0.0,
                timestamp=datetime.utcnow()
            )
    
    def _calculate_returns(self, trades: List[Trade]) -> List[float]:
        """Calculate returns from trades."""
        if not trades:
            return []
        
        # Sort trades by timestamp
        sorted_trades = sorted(trades, key=lambda x: x.timestamp)
        
        returns = []
        for trade in sorted_trades:
            if trade.pnl is not None:
                returns.append(trade.pnl)
        
        return returns
    
    def _calculate_drawdown(self, portfolio: Portfolio) -> Tuple[float, float]:
        """Calculate maximum and current drawdown."""
        # This would use actual equity curve data
        # For now, use portfolio data
        max_drawdown = portfolio.max_drawdown
        current_drawdown = portfolio.current_drawdown
        
        return max_drawdown, current_drawdown
    
    def _calculate_consecutive_trades(self, trades: List[Trade]) -> Tuple[int, int]:
        """Calculate consecutive wins and losses."""
        if not trades:
            return 0, 0
        
        # Sort trades by timestamp
        sorted_trades = sorted(trades, key=lambda x: x.timestamp)
        
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_wins = 0
        current_losses = 0
        
        for trade in sorted_trades:
            if trade.pnl is None:
                continue
            
            if trade.pnl > 0:
                current_wins += 1
                current_losses = 0
                max_consecutive_wins = max(max_consecutive_wins, current_wins)
            else:
                current_losses += 1
                current_wins = 0
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
        
        return max_consecutive_wins, max_consecutive_losses
    
    def _calculate_var(self, returns: List[float], confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate Value at Risk."""
        if not returns:
            return 0.0, 0.0
        
        var_95 = np.percentile(returns, 5)  # 95% VaR
        var_99 = np.percentile(returns, 1)  # 99% VaR
        
        return var_95, var_99
    
    def _calculate_expected_shortfall(self, returns: List[float], var: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)."""
        if not returns:
            return 0.0
        
        # Returns below VaR
        tail_returns = [r for r in returns if r <= var]
        
        if tail_returns:
            return np.mean(tail_returns)
        else:
            return var
    
    def _calculate_skewness(self, returns: List[float]) -> float:
        """Calculate skewness of returns."""
        if len(returns) < 3:
            return 0.0
        
        return float(pd.Series(returns).skew())
    
    def _calculate_kurtosis(self, returns: List[float]) -> float:
        """Calculate kurtosis of returns."""
        if len(returns) < 4:
            return 0.0
        
        return float(pd.Series(returns).kurtosis())
    
    def _calculate_strategy_analysis(self, strategy_name: str, data: Dict) -> StrategyAnalysis:
        """Calculate strategy performance analysis."""
        try:
            trades = data.get('trades', [])
            positions = data.get('positions', [])
            
            # Calculate basic metrics
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t.pnl and t.pnl > 0])
            losing_trades = len([t for t in trades if t.pnl and t.pnl < 0])
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
            
            total_pnl = sum(t.pnl for t in trades if t.pnl is not None)
            average_pnl = total_pnl / total_trades if total_trades > 0 else 0.0
            
            # Calculate Sharpe ratio (simplified)
            returns = [t.pnl for t in trades if t.pnl is not None]
            if returns:
                sharpe_ratio = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0.0
            else:
                sharpe_ratio = 0.0
            
            # Calculate max drawdown
            max_drawdown = 0.0  # Would need equity curve
            
            # Calculate profit factor
            winning_pnl = sum(t.pnl for t in trades if t.pnl and t.pnl > 0)
            losing_pnl = abs(sum(t.pnl for t in trades if t.pnl and t.pnl < 0))
            profit_factor = winning_pnl / losing_pnl if losing_pnl > 0 else 0.0
            
            # Calculate average win/loss
            winning_trades_list = [t for t in trades if t.pnl and t.pnl > 0]
            losing_trades_list = [t for t in trades if t.pnl and t.pnl < 0]
            
            average_win = np.mean([t.pnl for t in winning_trades_list]) if winning_trades_list else 0.0
            average_loss = np.mean([t.pnl for t in losing_trades_list]) if losing_trades_list else 0.0
            
            # Calculate best/worst trades
            pnl_values = [t.pnl for t in trades if t.pnl is not None]
            best_trade = max(pnl_values) if pnl_values else 0.0
            worst_trade = min(pnl_values) if pnl_values else 0.0
            
            # Calculate consecutive trades
            consecutive_wins, consecutive_losses = self._calculate_consecutive_trades(trades)
            
            # Count active positions
            active_positions = len([p for p in positions if p.status == "open"])
            
            # Get last trade date
            last_trade_date = max(t.timestamp for t in trades) if trades else datetime.utcnow()
            
            return StrategyAnalysis(
                strategy_name=strategy_name,
                total_trades=total_trades,
                winning_trades=winning_trades,
                losing_trades=losing_trades,
                win_rate=win_rate,
                total_pnl=total_pnl,
                average_pnl=average_pnl,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                profit_factor=profit_factor,
                average_win=average_win,
                average_loss=average_loss,
                best_trade=best_trade,
                worst_trade=worst_trade,
                consecutive_wins=consecutive_wins,
                consecutive_losses=consecutive_losses,
                active_positions=active_positions,
                last_trade_date=last_trade_date
            )
            
        except Exception as e:
            self.logger.logger.error(f"Error calculating strategy analysis for {strategy_name}", error=str(e))
            return StrategyAnalysis(
                strategy_name=strategy_name,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                average_pnl=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                profit_factor=0.0,
                average_win=0.0,
                average_loss=0.0,
                best_trade=0.0,
                worst_trade=0.0,
                consecutive_wins=0,
                consecutive_losses=0,
                active_positions=0,
                last_trade_date=datetime.utcnow()
            )
    
    def _calculate_market_analysis(self, pair: str, data: Dict) -> MarketAnalysis:
        """Calculate market analysis for a currency pair."""
        try:
            # Extract price data
            prices = data.get('prices', [])
            if not prices:
                return None
            
            current_price = prices[-1]['close']
            price_24h_ago = prices[-24]['close'] if len(prices) >= 24 else prices[0]['close']
            
            # Calculate price changes
            price_change_24h = current_price - price_24h_ago
            price_change_pct_24h = (price_change_24h / price_24h_ago) * 100
            
            # Calculate volatility
            returns_24h = []
            for i in range(1, min(24, len(prices))):
                ret = (prices[i]['close'] - prices[i-1]['close']) / prices[i-1]['close']
                returns_24h.append(ret)
            
            volatility_24h = np.std(returns_24h) * np.sqrt(24) if returns_24h else 0.0
            
            # Calculate 7-day volatility
            returns_7d = []
            for i in range(1, min(168, len(prices))):  # 7 days * 24 hours
                ret = (prices[i]['close'] - prices[i-1]['close']) / prices[i-1]['close']
                returns_7d.append(ret)
            
            volatility_7d = np.std(returns_7d) * np.sqrt(168) if returns_7d else 0.0
            
            # Determine trend direction
            if price_change_pct_24h > 0.5:
                trend_direction = "up"
            elif price_change_pct_24h < -0.5:
                trend_direction = "down"
            else:
                trend_direction = "sideways"
            
            # Calculate trend strength
            trend_strength = abs(price_change_pct_24h) / 10  # Normalize to 0-1
            
            # Calculate support and resistance (simplified)
            highs = [p['high'] for p in prices[-24:]]
            lows = [p['low'] for p in prices[-24:]]
            
            resistance_level = max(highs) if highs else current_price
            support_level = min(lows) if lows else current_price
            
            # Calculate technical indicators
            closes = [p['close'] for p in prices]
            
            # RSI (simplified)
            rsi = self._calculate_rsi(closes)
            
            # MACD (simplified)
            macd = self._calculate_macd(closes)
            
            # Bollinger Bands position
            bb_position = self._calculate_bollinger_position(closes, current_price)
            
            # Sentiment and news (placeholders)
            sentiment_score = 0.0  # Would come from sentiment service
            news_impact = "neutral"  # Would come from news analysis
            
            return MarketAnalysis(
                pair=pair,
                current_price=current_price,
                price_change_24h=price_change_24h,
                price_change_pct_24h=price_change_pct_24h,
                volatility_24h=volatility_24h,
                volatility_7d=volatility_7d,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                support_level=support_level,
                resistance_level=resistance_level,
                rsi=rsi,
                macd=macd,
                bollinger_position=bb_position,
                sentiment_score=sentiment_score,
                news_impact=news_impact,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.logger.error(f"Error calculating market analysis for {pair}", error=str(e))
            return None
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI (simplified)."""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50.0
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> float:
        """Calculate MACD (simplified)."""
        if len(prices) < 26:
            return 0.0
        
        # Calculate EMA12 and EMA26
        ema12 = self._calculate_ema(prices, 12)
        ema26 = self._calculate_ema(prices, 26)
        
        # MACD line
        macd_line = ema12 - ema26
        
        return macd_line
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average."""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        alpha = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = alpha * price + (1 - alpha) * ema
        
        return ema
    
    def _calculate_bollinger_position(self, prices: List[float], current_price: float) -> float:
        """Calculate position within Bollinger Bands (0-1)."""
        if len(prices) < 20:
            return 0.5
        
        # Calculate 20-period SMA and standard deviation
        sma = np.mean(prices[-20:])
        std = np.std(prices[-20:])
        
        # Bollinger Bands
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        
        # Calculate position (0 = lower band, 1 = upper band)
        if upper_band == lower_band:
            return 0.5
        
        position = (current_price - lower_band) / (upper_band - lower_band)
        return max(0.0, min(1.0, position))
    
    # Placeholder methods for data retrieval
    async def _get_portfolio_data(self) -> Optional[Portfolio]:
        """Get portfolio data from database."""
        # This would fetch from database
        return None
    
    async def _get_trades_data(self) -> List[Trade]:
        """Get trades data from database."""
        # This would fetch from database
        return []
    
    async def _get_strategies_data(self) -> Dict[str, Dict]:
        """Get strategies data from database."""
        # This would fetch from database
        return {}
    
    async def _get_market_data(self) -> Dict[str, Dict]:
        """Get market data from data service."""
        # This would fetch from data service
        return {}
    
    # Public methods for accessing analytics
    def get_performance_metrics(self, days: int = 30) -> Optional[PerformanceMetrics]:
        """Get performance metrics for the last N days."""
        if not self.performance_history:
            return None
        
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        recent_metrics = [m for m in self.performance_history if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return self.performance_history[-1] if self.performance_history else None
        
        return recent_metrics[-1]
    
    def get_strategy_analysis(self, strategy_name: str) -> Optional[StrategyAnalysis]:
        """Get analysis for a specific strategy."""
        return self.strategy_analyses.get(strategy_name)
    
    def get_all_strategy_analyses(self) -> Dict[str, StrategyAnalysis]:
        """Get analyses for all strategies."""
        return self.strategy_analyses.copy()
    
    def get_market_analysis(self, pair: str) -> Optional[MarketAnalysis]:
        """Get market analysis for a specific pair."""
        return self.market_analyses.get(pair)
    
    def get_all_market_analyses(self) -> Dict[str, MarketAnalysis]:
        """Get market analyses for all pairs."""
        return self.market_analyses.copy()
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics service summary."""
        latest_metrics = self.performance_history[-1] if self.performance_history else None
        
        return {
            "is_running": self.is_running,
            "performance_metrics_count": len(self.performance_history),
            "strategy_analyses_count": len(self.strategy_analyses),
            "market_analyses_count": len(self.market_analyses),
            "latest_sharpe_ratio": latest_metrics.sharpe_ratio if latest_metrics else 0.0,
            "latest_win_rate": latest_metrics.win_rate if latest_metrics else 0.0,
            "latest_total_return": latest_metrics.total_return if latest_metrics else 0.0,
            "last_update": datetime.utcnow().isoformat()
        }
