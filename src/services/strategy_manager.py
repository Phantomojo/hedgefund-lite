"""
Strategy Manager Service

Manages multiple trading strategies, coordinates signal generation,
and handles capital allocation across strategies.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import numpy as np
import pandas as pd
import structlog

from src.core.config import settings
from src.core.logging import TradingLogger
from src.strategies.base_strategy import BaseStrategy, Signal, StrategyConfig
from src.strategies.ema_crossover_strategy import create_ema_crossover_strategy
from src.models.portfolio import Portfolio


@dataclass
class StrategyPerformance:
    """Strategy performance metrics."""
    strategy_name: str
    total_pnl: float
    daily_pnl: float
    win_rate: float
    sharpe_ratio: float
    max_drawdown: float
    current_drawdown: float
    total_trades: int
    active_positions: int
    allocation_pct: float
    last_update: datetime


@dataclass
class MarketRegime:
    """Market regime classification."""
    regime: str  # trending, ranging, volatile, calm
    confidence: float
    volatility: float
    trend_strength: float
    timestamp: datetime


class StrategyManager:
    """Manages multiple trading strategies and capital allocation."""
    
    def __init__(self):
        self.logger = TradingLogger("strategy_manager")
        self.strategies: Dict[str, BaseStrategy] = {}
        self.performance_metrics: Dict[str, StrategyPerformance] = {}
        self.market_regime: MarketRegime = None
        self.is_running = False
        self.portfolio = Portfolio()
        
        # Capital allocation
        self.total_capital = 10000.0  # This would come from account
        self.min_allocation = 0.05  # 5% minimum per strategy
        self.max_allocation = 0.40  # 40% maximum per strategy
        
        # Performance tracking
        self.performance_window = timedelta(days=30)
        self.reallocation_threshold = 0.1  # 10% performance difference triggers reallocation
        
        # Initialize default strategies
        self._initialize_default_strategies()
    
    def _initialize_default_strategies(self):
        """Initialize default trading strategies."""
        try:
            # EMA Crossover Strategy
            ema_strategy = create_ema_crossover_strategy(
                name="ema_crossover_v1",
                fast_period=12,
                slow_period=26,
                risk_pct=0.5,
                max_positions=3
            )
            self.add_strategy(ema_strategy)
            
            # Add more strategies here as they are implemented
            # RSI Mean Reversion
            # Bollinger Bands Breakout
            # Carry Trade
            # etc.
            
            self.logger.logger.info("Default strategies initialized")
            
        except Exception as e:
            self.logger.logger.error("Error initializing default strategies", error=str(e))
    
    async def start(self):
        """Start the strategy manager."""
        self.is_running = True
        self.logger.logger.info("Strategy manager started")
        
        # Start all strategies
        for strategy in self.strategies.values():
            await strategy.start()
        
        # Start monitoring loop
        asyncio.create_task(self._monitoring_loop())
    
    async def stop(self):
        """Stop the strategy manager."""
        self.is_running = False
        
        # Stop all strategies
        for strategy in self.strategies.values():
            await strategy.stop()
        
        self.logger.logger.info("Strategy manager stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                # Update market regime
                await self._update_market_regime()
                
                # Update strategy performance
                await self._update_strategy_performance()
                
                # Check for reallocation
                await self._check_reallocation()
                
                # Sleep for monitoring interval
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.logger.error("Strategy monitoring error", error=str(e))
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    def add_strategy(self, strategy: BaseStrategy):
        """Add a new strategy to the manager."""
        if strategy.config.name in self.strategies:
            self.logger.logger.warning(f"Strategy {strategy.config.name} already exists, replacing")
        
        self.strategies[strategy.config.name] = strategy
        
        # Initialize performance tracking
        self.performance_metrics[strategy.config.name] = StrategyPerformance(
            strategy_name=strategy.config.name,
            total_pnl=0.0,
            daily_pnl=0.0,
            win_rate=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            current_drawdown=0.0,
            total_trades=0,
            active_positions=0,
            allocation_pct=1.0 / len(self.strategies),  # Equal allocation initially
            last_update=datetime.utcnow()
        )
        
        self.logger.logger.info(f"Strategy {strategy.config.name} added")
    
    def remove_strategy(self, strategy_name: str):
        """Remove a strategy from the manager."""
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
            if strategy_name in self.performance_metrics:
                del self.performance_metrics[strategy_name]
            self.logger.logger.info(f"Strategy {strategy_name} removed")
    
    async def update_strategies(self, market_data: Dict[str, Dict[str, pd.DataFrame]]) -> List[Signal]:
        """Update all strategies with new market data and collect signals."""
        all_signals = []
        
        for strategy_name, strategy in self.strategies.items():
            try:
                if not strategy.config.enabled:
                    continue
                
                # Update strategy
                signals = await strategy.update(market_data)
                
                # Add strategy name to signals
                for signal in signals:
                    signal.strategy = strategy_name
                
                all_signals.extend(signals)
                
            except Exception as e:
                self.logger.logger.error(f"Error updating strategy {strategy_name}", error=str(e))
        
        # Filter and rank signals
        filtered_signals = self._filter_and_rank_signals(all_signals)
        
        return filtered_signals
    
    def _filter_and_rank_signals(self, signals: List[Signal]) -> List[Signal]:
        """Filter and rank signals based on multiple criteria."""
        if not signals:
            return []
        
        # Calculate signal scores
        scored_signals = []
        for signal in signals:
            score = self._calculate_signal_score(signal)
            scored_signals.append((signal, score))
        
        # Sort by score (highest first)
        scored_signals.sort(key=lambda x: x[1], reverse=True)
        
        # Filter based on allocation and limits
        filtered_signals = []
        strategy_positions = {}
        
        for signal, score in scored_signals:
            strategy_name = signal.strategy
            
            # Check strategy allocation
            if strategy_name not in strategy_positions:
                strategy_positions[strategy_name] = 0
            
            # Check if strategy has room for more positions
            strategy = self.strategies.get(strategy_name)
            if strategy and strategy_positions[strategy_name] >= strategy.config.max_positions:
                continue
            
            # Check total allocation limit
            if strategy_positions[strategy_name] >= self.max_allocation * self.total_capital:
                continue
            
            filtered_signals.append(signal)
            strategy_positions[strategy_name] += 1
        
        return filtered_signals
    
    def _calculate_signal_score(self, signal: Signal) -> float:
        """Calculate a score for a signal based on multiple factors."""
        score = 0.0
        
        # Base confidence score (40% weight)
        score += signal.confidence * 0.4
        
        # Strategy performance score (30% weight)
        strategy_perf = self.performance_metrics.get(signal.strategy)
        if strategy_perf:
            # Normalize Sharpe ratio (assuming range -2 to 4)
            sharpe_score = (strategy_perf.sharpe_ratio + 2) / 6
            score += sharpe_score * 0.3
        
        # Market regime alignment (20% weight)
        if self.market_regime:
            regime_score = self._calculate_regime_alignment(signal, self.market_regime)
            score += regime_score * 0.2
        
        # Volatility adjustment (10% weight)
        volatility_score = self._calculate_volatility_score(signal)
        score += volatility_score * 0.1
        
        return score
    
    def _calculate_regime_alignment(self, signal: Signal, regime: MarketRegime) -> float:
        """Calculate how well a signal aligns with current market regime."""
        # This is a simplified implementation
        # In practice, you'd have more sophisticated regime detection
        
        if regime.regime == "trending":
            # Trending strategies perform better in trending markets
            if "ema" in signal.strategy.lower() or "trend" in signal.strategy.lower():
                return 1.0
            else:
                return 0.5
        elif regime.regime == "ranging":
            # Mean reversion strategies perform better in ranging markets
            if "rsi" in signal.strategy.lower() or "mean" in signal.strategy.lower():
                return 1.0
            else:
                return 0.5
        else:
            return 0.7  # Neutral score for other regimes
    
    def _calculate_volatility_score(self, signal: Signal) -> float:
        """Calculate volatility-adjusted score."""
        # Get ATR from signal metadata
        atr = signal.metadata.get('atr', 0.001)
        
        # Normalize ATR (assuming typical range 0.0005 to 0.005)
        normalized_atr = (atr - 0.0005) / 0.0045
        normalized_atr = np.clip(normalized_atr, 0, 1)
        
        # Prefer moderate volatility (not too low, not too high)
        if 0.2 <= normalized_atr <= 0.8:
            return 1.0
        else:
            return 0.5
    
    async def _update_market_regime(self):
        """Update market regime classification."""
        try:
            # This would analyze market data to determine regime
            # For now, use a simple placeholder
            
            # Get market data for analysis
            market_data = await self._get_market_data()
            
            if not market_data:
                return
            
            # Calculate regime metrics
            volatility = self._calculate_market_volatility(market_data)
            trend_strength = self._calculate_trend_strength(market_data)
            
            # Classify regime
            if trend_strength > 0.7:
                regime = "trending"
                confidence = 0.8
            elif volatility > 0.8:
                regime = "volatile"
                confidence = 0.7
            elif volatility < 0.3:
                regime = "calm"
                confidence = 0.6
            else:
                regime = "ranging"
                confidence = 0.5
            
            self.market_regime = MarketRegime(
                regime=regime,
                confidence=confidence,
                volatility=volatility,
                trend_strength=trend_strength,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.logger.error("Error updating market regime", error=str(e))
    
    async def _update_strategy_performance(self):
        """Update performance metrics for all strategies."""
        for strategy_name, strategy in self.strategies.items():
            try:
                # Get performance summary from strategy
                summary = strategy.get_performance_summary()
                
                # Update performance metrics
                if strategy_name in self.performance_metrics:
                    perf = self.performance_metrics[strategy_name]
                    perf.total_pnl = summary.get('total_pnl', 0.0)
                    perf.win_rate = summary.get('win_rate', 0.0)
                    perf.sharpe_ratio = summary.get('sharpe_ratio', 0.0)
                    perf.max_drawdown = summary.get('max_drawdown', 0.0)
                    perf.current_drawdown = summary.get('current_drawdown', 0.0)
                    perf.total_trades = summary.get('total_trades', 0)
                    perf.active_positions = summary.get('current_positions', 0)
                    perf.last_update = datetime.utcnow()
                
            except Exception as e:
                self.logger.logger.error(f"Error updating performance for {strategy_name}", error=str(e))
    
    async def _check_reallocation(self):
        """Check if capital reallocation is needed."""
        try:
            # Calculate performance differences
            performances = list(self.performance_metrics.values())
            if len(performances) < 2:
                return
            
            # Sort by Sharpe ratio
            performances.sort(key=lambda x: x.sharpe_ratio, reverse=True)
            
            # Check if top performer is significantly better
            top_performer = performances[0]
            second_performer = performances[1]
            
            performance_diff = top_performer.sharpe_ratio - second_performer.sharpe_ratio
            
            if performance_diff > self.reallocation_threshold:
                await self._reallocate_capital(performances)
                
        except Exception as e:
            self.logger.logger.error("Error checking reallocation", error=str(e))
    
    async def _reallocate_capital(self, performances: List[StrategyPerformance]):
        """Reallocate capital based on performance."""
        try:
            total_allocation = 0.0
            
            # Calculate new allocations based on Sharpe ratios
            for i, perf in enumerate(performances):
                # Weight based on Sharpe ratio (with minimum allocation)
                weight = max(perf.sharpe_ratio, 0.1)  # Minimum 0.1 weight
                total_allocation += weight
            
            # Normalize allocations
            for perf in performances:
                weight = max(perf.sharpe_ratio, 0.1)
                new_allocation = weight / total_allocation
                
                # Ensure within bounds
                new_allocation = np.clip(new_allocation, self.min_allocation, self.max_allocation)
                
                # Update allocation
                perf.allocation_pct = new_allocation
                
                # Update strategy risk percentage
                strategy = self.strategies.get(perf.strategy_name)
                if strategy:
                    strategy.config.risk_pct = new_allocation * 100
            
            self.logger.logger.info("Capital reallocation completed", 
                                  allocations={p.strategy_name: p.allocation_pct for p in performances})
            
        except Exception as e:
            self.logger.logger.error("Error reallocating capital", error=str(e))
    
    def _calculate_market_volatility(self, market_data: Dict) -> float:
        """Calculate market volatility."""
        # Placeholder implementation
        return 0.5
    
    def _calculate_trend_strength(self, market_data: Dict) -> float:
        """Calculate trend strength."""
        # Placeholder implementation
        return 0.5
    
    async def _get_market_data(self) -> Dict:
        """Get market data for analysis."""
        # Placeholder implementation
        return {}
    
    def get_strategy_summary(self) -> Dict[str, Any]:
        """Get summary of all strategies."""
        summary = {
            "total_strategies": len(self.strategies),
            "active_strategies": len([s for s in self.strategies.values() if s.config.enabled]),
            "total_capital": self.total_capital,
            "market_regime": self.market_regime.regime if self.market_regime else "unknown",
            "strategies": {}
        }
        
        for strategy_name, strategy in self.strategies.items():
            perf = self.performance_metrics.get(strategy_name)
            summary["strategies"][strategy_name] = {
                "enabled": strategy.config.enabled,
                "allocation_pct": perf.allocation_pct if perf else 0.0,
                "total_pnl": perf.total_pnl if perf else 0.0,
                "sharpe_ratio": perf.sharpe_ratio if perf else 0.0,
                "win_rate": perf.win_rate if perf else 0.0,
                "active_positions": perf.active_positions if perf else 0,
                "last_update": perf.last_update.isoformat() if perf else None
            }
        
        return summary
    
    def enable_strategy(self, strategy_name: str):
        """Enable a strategy."""
        if strategy_name in self.strategies:
            self.strategies[strategy_name].config.enabled = True
            self.logger.logger.info(f"Strategy {strategy_name} enabled")
    
    def disable_strategy(self, strategy_name: str):
        """Disable a strategy."""
        if strategy_name in self.strategies:
            self.strategies[strategy_name].config.enabled = False
            self.logger.logger.info(f"Strategy {strategy_name} disabled")
    
    def update_strategy_parameters(self, strategy_name: str, parameters: Dict[str, Any]):
        """Update strategy parameters."""
        if strategy_name in self.strategies:
            strategy = self.strategies[strategy_name]
            strategy.config.parameters.update(parameters)
            self.logger.logger.info(f"Updated parameters for strategy {strategy_name}")
    
    def get_strategy_performance(self, strategy_name: str) -> Optional[StrategyPerformance]:
        """Get performance metrics for a specific strategy."""
        return self.performance_metrics.get(strategy_name)
