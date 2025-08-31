"""
Base strategy class for all trading strategies.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
import structlog

from src.core.logging import TradingLogger


class SignalType(Enum):
    """Signal types."""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"


class Timeframe(Enum):
    """Timeframe types."""
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"


@dataclass
class Signal:
    """Trading signal."""
    type: SignalType
    pair: str
    price: float
    confidence: float
    timestamp: datetime
    strategy: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")


@dataclass
class StrategyConfig:
    """Strategy configuration."""
    name: str
    enabled: bool = True
    risk_pct: float = 0.5
    max_positions: int = 3
    timeframes: List[Timeframe] = field(default_factory=lambda: [Timeframe.H1, Timeframe.H4])
    pairs: List[str] = field(default_factory=lambda: ["EURUSD", "GBPUSD", "USDJPY"])
    parameters: Dict[str, Any] = field(default_factory=dict)


class BaseStrategy(ABC):
    """Base class for all trading strategies."""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        self.logger = TradingLogger(f"strategy.{config.name}")
        self.signals: List[Signal] = []
        self.performance_metrics: Dict[str, float] = {}
        self.is_running = False
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        
        # State management
        self._last_update = None
        self._current_positions: Dict[str, Dict] = {}
    
    @abstractmethod
    async def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """
        Generate trading signals based on market data.
        
        Args:
            data: Dictionary of market data by pair and timeframe
            
        Returns:
            List of trading signals
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: Signal, account_balance: float) -> float:
        """
        Calculate position size based on signal and risk management.
        
        Args:
            signal: Trading signal
            account_balance: Current account balance
            
        Returns:
            Position size in lots
        """
        pass
    
    @abstractmethod
    def should_exit_position(self, position: Dict, current_data: Dict[str, pd.DataFrame]) -> bool:
        """
        Determine if a position should be closed.
        
        Args:
            position: Current position data
            current_data: Current market data
            
        Returns:
            True if position should be closed
        """
        pass
    
    async def start(self):
        """Start the strategy."""
        self.is_running = True
        self.logger.logger.info(f"Strategy {self.config.name} started")
    
    async def stop(self):
        """Stop the strategy."""
        self.is_running = False
        self.logger.logger.info(f"Strategy {self.config.name} stopped")
    
    async def update(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """
        Update strategy with new market data and generate signals.
        
        Args:
            data: Market data by pair and timeframe
            
        Returns:
            List of new signals
        """
        if not self.is_running or not self.config.enabled:
            return []
        
        try:
            # Generate signals
            signals = await self.generate_signals(data)
            
            # Filter signals based on configuration
            filtered_signals = self._filter_signals(signals)
            
            # Update performance metrics
            await self._update_performance_metrics()
            
            # Log signals
            for signal in filtered_signals:
                self.logger.trade_signal({
                    "type": signal.type.value,
                    "pair": signal.pair,
                    "direction": signal.type.value,
                    "confidence": signal.confidence,
                    "strategy": signal.strategy,
                    "timestamp": signal.timestamp.isoformat()
                })
            
            return filtered_signals
            
        except Exception as e:
            self.logger.logger.error(f"Error updating strategy {self.config.name}", error=str(e))
            return []
    
    def _filter_signals(self, signals: List[Signal]) -> List[Signal]:
        """Filter signals based on strategy configuration."""
        filtered = []
        
        for signal in signals:
            # Check if pair is allowed
            if signal.pair not in self.config.pairs:
                continue
            
            # Check confidence threshold
            if signal.confidence < 0.6:  # Minimum confidence threshold
                continue
            
            # Check if we already have a position in this pair
            if signal.pair in self._current_positions:
                # Only allow exit signals or opposite direction signals
                current_position = self._current_positions[signal.pair]
                if current_position["side"] == signal.type.value:
                    continue
            
            # Check position limits
            if len(self._current_positions) >= self.config.max_positions:
                continue
            
            filtered.append(signal)
        
        return filtered
    
    def calculate_risk_adjusted_position_size(self, signal: Signal, account_balance: float, 
                                            volatility: float) -> float:
        """
        Calculate risk-adjusted position size.
        
        Args:
            signal: Trading signal
            account_balance: Account balance
            volatility: Current volatility (ATR or similar)
            
        Returns:
            Position size in lots
        """
        # Base position size from risk percentage
        base_size = self.calculate_position_size(signal, account_balance)
        
        # Adjust for volatility
        volatility_factor = 1.0 / (1.0 + volatility)  # Reduce size in high volatility
        
        # Adjust for signal confidence
        confidence_factor = signal.confidence
        
        # Final position size
        adjusted_size = base_size * volatility_factor * confidence_factor
        
        # Ensure minimum and maximum sizes
        min_size = 0.01  # Minimum lot size
        max_size = account_balance * 0.1  # Maximum 10% of balance
        
        return np.clip(adjusted_size, min_size, max_size)
    
    def calculate_stop_loss(self, signal: Signal, atr: float, multiplier: float = 2.0) -> float:
        """
        Calculate stop loss based on ATR.
        
        Args:
            signal: Trading signal
            atr: Average True Range
            multiplier: ATR multiplier for stop loss
            
        Returns:
            Stop loss price
        """
        if signal.type == SignalType.BUY:
            return signal.price - (atr * multiplier)
        else:
            return signal.price + (atr * multiplier)
    
    def calculate_take_profit(self, signal: Signal, atr: float, risk_reward_ratio: float = 2.0) -> float:
        """
        Calculate take profit based on risk-reward ratio.
        
        Args:
            signal: Trading signal
            atr: Average True Range
            risk_reward_ratio: Risk to reward ratio
            
        Returns:
            Take profit price
        """
        if signal.type == SignalType.BUY:
            return signal.price + (atr * risk_reward_ratio)
        else:
            return signal.price - (atr * risk_reward_ratio)
    
    async def _update_performance_metrics(self):
        """Update strategy performance metrics."""
        # This would be implemented to track actual performance
        # For now, just update basic metrics
        self.performance_metrics = {
            "total_trades": self.total_trades,
            "win_rate": self.winning_trades / self.total_trades if self.total_trades > 0 else 0.0,
            "total_pnl": self.total_pnl,
            "max_drawdown": self.max_drawdown,
            "current_drawdown": self.current_drawdown,
            "sharpe_ratio": self._calculate_sharpe_ratio(),
            "calmar_ratio": self._calculate_calmar_ratio()
        }
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        # This would use actual returns data
        # For now, return a placeholder
        return 0.0
    
    def _calculate_calmar_ratio(self) -> float:
        """Calculate Calmar ratio."""
        if self.max_drawdown == 0:
            return 0.0
        return self.total_pnl / self.max_drawdown
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get strategy performance summary."""
        return {
            "name": self.config.name,
            "enabled": self.config.enabled,
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "win_rate": self.performance_metrics.get("win_rate", 0.0),
            "total_pnl": self.total_pnl,
            "max_drawdown": self.max_drawdown,
            "current_drawdown": self.current_drawdown,
            "sharpe_ratio": self.performance_metrics.get("sharpe_ratio", 0.0),
            "calmar_ratio": self.performance_metrics.get("calmar_ratio", 0.0),
            "current_positions": len(self._current_positions),
            "last_update": self._last_update.isoformat() if self._last_update else None
        }
    
    def update_position(self, pair: str, position_data: Dict):
        """Update current position information."""
        self._current_positions[pair] = position_data
    
    def remove_position(self, pair: str):
        """Remove position from tracking."""
        if pair in self._current_positions:
            del self._current_positions[pair]
    
    def get_required_indicators(self) -> List[str]:
        """
        Get list of required technical indicators for this strategy.
        
        Returns:
            List of indicator names
        """
        return []
    
    def get_required_timeframes(self) -> List[Timeframe]:
        """
        Get list of required timeframes for this strategy.
        
        Returns:
            List of timeframes
        """
        return self.config.timeframes
    
    def validate_config(self) -> bool:
        """
        Validate strategy configuration.
        
        Returns:
            True if configuration is valid
        """
        try:
            # Check basic parameters
            if not self.config.name:
                return False
            
            if not 0 < self.config.risk_pct <= 5:
                return False
            
            if not 1 <= self.config.max_positions <= 10:
                return False
            
            if not self.config.pairs:
                return False
            
            if not self.config.timeframes:
                return False
            
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Configuration validation failed for {self.config.name}", error=str(e))
            return False
