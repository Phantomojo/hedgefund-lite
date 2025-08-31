"""
EMA Crossover Strategy

A simple moving average crossover strategy that generates buy/sell signals
when a fast EMA crosses above/below a slow EMA.
"""

from datetime import datetime
from typing import Dict, List
import pandas as pd
import numpy as np
import ta

from src.strategies.base_strategy import (
    BaseStrategy, StrategyConfig, Signal, SignalType, Timeframe
)


class EMACrossoverStrategy(BaseStrategy):
    """EMA Crossover Strategy implementation."""
    
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        
        # Strategy-specific parameters
        self.fast_period = config.parameters.get("fast_period", 12)
        self.slow_period = config.parameters.get("slow_period", 26)
        self.signal_period = config.parameters.get("signal_period", 9)
        self.rsi_period = config.parameters.get("rsi_period", 14)
        self.rsi_oversold = config.parameters.get("rsi_oversold", 30)
        self.rsi_overbought = config.parameters.get("rsi_overbought", 70)
        
        # Validate parameters
        if not self._validate_parameters():
            raise ValueError("Invalid EMA crossover strategy parameters")
    
    def _validate_parameters(self) -> bool:
        """Validate strategy parameters."""
        return (
            self.fast_period > 0 and
            self.slow_period > 0 and
            self.fast_period < self.slow_period and
            self.signal_period > 0 and
            self.rsi_period > 0 and
            0 < self.rsi_oversold < self.rsi_overbought < 100
        )
    
    async def generate_signals(self, data: Dict[str, pd.DataFrame]) -> List[Signal]:
        """Generate trading signals based on EMA crossover."""
        signals = []
        
        for pair in self.config.pairs:
            if pair not in data:
                continue
            
            # Get data for the primary timeframe (H1)
            primary_data = data[pair].get(Timeframe.H1.value)
            if primary_data is None or len(primary_data) < self.slow_period:
                continue
            
            # Calculate indicators
            indicators = self._calculate_indicators(primary_data)
            
            # Generate signal
            signal = self._generate_signal_for_pair(pair, primary_data, indicators)
            if signal:
                signals.append(signal)
        
        return signals
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict[str, pd.Series]:
        """Calculate technical indicators."""
        indicators = {}
        
        # Calculate EMAs
        indicators['ema_fast'] = ta.trend.ema_indicator(data['close'], self.fast_period)
        indicators['ema_slow'] = ta.trend.ema_indicator(data['close'], self.slow_period)
        
        # Calculate MACD
        indicators['macd'] = ta.trend.macd_diff(data['close'], self.fast_period, self.slow_period, self.signal_period)
        
        # Calculate RSI
        indicators['rsi'] = ta.momentum.rsi(data['close'], self.rsi_period)
        
        # Calculate ATR for volatility
        indicators['atr'] = ta.volatility.average_true_range(data['high'], data['low'], data['close'], 14)
        
        # Calculate Bollinger Bands
        bb = ta.volatility.BollingerBands(data['close'], 20, 2)
        indicators['bb_upper'] = bb.bollinger_hband()
        indicators['bb_lower'] = bb.bollinger_lband()
        indicators['bb_middle'] = bb.bollinger_mavg()
        
        return indicators
    
    def _generate_signal_for_pair(self, pair: str, data: pd.DataFrame, 
                                indicators: Dict[str, pd.Series]) -> Signal:
        """Generate signal for a specific pair."""
        if len(data) < 2:
            return None
        
        current_idx = -1
        prev_idx = -2
        
        # Get current and previous values
        ema_fast_current = indicators['ema_fast'].iloc[current_idx]
        ema_fast_prev = indicators['ema_fast'].iloc[prev_idx]
        ema_slow_current = indicators['ema_slow'].iloc[current_idx]
        ema_slow_prev = indicators['ema_slow'].iloc[prev_idx]
        
        rsi_current = indicators['rsi'].iloc[current_idx]
        macd_current = indicators['macd'].iloc[current_idx]
        atr_current = indicators['atr'].iloc[current_idx]
        
        current_price = data['close'].iloc[current_idx]
        
        # Check for EMA crossover
        ema_cross_up = (ema_fast_prev <= ema_slow_prev and ema_fast_current > ema_slow_current)
        ema_cross_down = (ema_fast_prev >= ema_slow_prev and ema_fast_current < ema_slow_current)
        
        # Calculate signal confidence
        confidence = self._calculate_signal_confidence(
            ema_fast_current, ema_slow_current, rsi_current, macd_current, atr_current
        )
        
        # Generate buy signal
        if ema_cross_up and self._validate_buy_conditions(rsi_current, macd_current):
            return Signal(
                type=SignalType.BUY,
                pair=pair,
                price=current_price,
                confidence=confidence,
                timestamp=datetime.utcnow(),
                strategy=self.config.name,
                metadata={
                    'ema_fast': ema_fast_current,
                    'ema_slow': ema_slow_current,
                    'rsi': rsi_current,
                    'macd': macd_current,
                    'atr': atr_current,
                    'signal_type': 'ema_crossover_buy'
                }
            )
        
        # Generate sell signal
        elif ema_cross_down and self._validate_sell_conditions(rsi_current, macd_current):
            return Signal(
                type=SignalType.SELL,
                pair=pair,
                price=current_price,
                confidence=confidence,
                timestamp=datetime.utcnow(),
                strategy=self.config.name,
                metadata={
                    'ema_fast': ema_fast_current,
                    'ema_slow': ema_slow_current,
                    'rsi': rsi_current,
                    'macd': macd_current,
                    'atr': atr_current,
                    'signal_type': 'ema_crossover_sell'
                }
            )
        
        return None
    
    def _validate_buy_conditions(self, rsi: float, macd: float) -> bool:
        """Validate buy signal conditions."""
        # RSI not overbought
        if rsi > self.rsi_overbought:
            return False
        
        # MACD positive (optional confirmation)
        if macd < 0:
            return False
        
        return True
    
    def _validate_sell_conditions(self, rsi: float, macd: float) -> bool:
        """Validate sell signal conditions."""
        # RSI not oversold
        if rsi < self.rsi_oversold:
            return False
        
        # MACD negative (optional confirmation)
        if macd > 0:
            return False
        
        return True
    
    def _calculate_signal_confidence(self, ema_fast: float, ema_slow: float, 
                                   rsi: float, macd: float, atr: float) -> float:
        """Calculate signal confidence based on multiple factors."""
        confidence = 0.5  # Base confidence
        
        # EMA strength (how far apart the EMAs are)
        ema_diff = abs(ema_fast - ema_slow) / ema_slow
        ema_confidence = min(ema_diff * 100, 0.3)  # Max 30% from EMA difference
        confidence += ema_confidence
        
        # RSI confidence
        if 30 <= rsi <= 70:
            rsi_confidence = 0.2  # Neutral RSI is good
        elif 20 <= rsi <= 80:
            rsi_confidence = 0.1  # Moderate RSI
        else:
            rsi_confidence = 0.0  # Extreme RSI reduces confidence
        
        confidence += rsi_confidence
        
        # MACD confidence
        macd_confidence = min(abs(macd) * 10, 0.2)  # Max 20% from MACD strength
        confidence += macd_confidence
        
        # Volatility adjustment (lower volatility = higher confidence)
        volatility_factor = 1.0 / (1.0 + atr)
        confidence *= volatility_factor
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def calculate_position_size(self, signal: Signal, account_balance: float) -> float:
        """Calculate position size based on risk management."""
        # Calculate risk amount
        risk_amount = account_balance * (self.config.risk_pct / 100)
        
        # Get ATR for stop loss calculation
        atr = signal.metadata.get('atr', 0.001)  # Default to 1 pip if not available
        
        # Calculate stop loss distance (2 * ATR)
        stop_distance = atr * 2
        
        # Calculate position size
        position_size = risk_amount / stop_distance
        
        # Convert to lot size (assuming 100,000 units per lot)
        lot_size = position_size / 100000
        
        # Ensure minimum and maximum sizes
        min_lot = 0.01
        max_lot = account_balance * 0.1 / 100000  # Max 10% of balance
        
        return np.clip(lot_size, min_lot, max_lot)
    
    def should_exit_position(self, position: Dict, current_data: Dict[str, pd.DataFrame]) -> bool:
        """Determine if a position should be closed."""
        pair = position.get('pair')
        if pair not in current_data:
            return False
        
        # Get current data
        data = current_data[pair].get(Timeframe.H1.value)
        if data is None or len(data) < self.slow_period:
            return False
        
        # Calculate indicators
        indicators = self._calculate_indicators(data)
        
        # Get current values
        ema_fast = indicators['ema_fast'].iloc[-1]
        ema_slow = indicators['ema_slow'].iloc[-1]
        rsi = indicators['rsi'].iloc[-1]
        
        position_side = position.get('side')
        
        # Exit long position if EMA crosses down or RSI overbought
        if position_side == 'buy':
            if ema_fast < ema_slow or rsi > self.rsi_overbought:
                return True
        
        # Exit short position if EMA crosses up or RSI oversold
        elif position_side == 'sell':
            if ema_fast > ema_slow or rsi < self.rsi_oversold:
                return True
        
        return False
    
    def get_required_indicators(self) -> List[str]:
        """Get list of required technical indicators."""
        return ['ema', 'macd', 'rsi', 'atr', 'bollinger_bands']
    
    def get_required_timeframes(self) -> List[Timeframe]:
        """Get list of required timeframes."""
        return [Timeframe.H1, Timeframe.H4]  # Primary and confirmation timeframes


def create_ema_crossover_strategy(
    name: str = "ema_crossover",
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    rsi_period: int = 14,
    risk_pct: float = 0.5,
    max_positions: int = 3
) -> EMACrossoverStrategy:
    """Factory function to create EMA crossover strategy."""
    
    config = StrategyConfig(
        name=name,
        enabled=True,
        risk_pct=risk_pct,
        max_positions=max_positions,
        timeframes=[Timeframe.H1, Timeframe.H4],
        pairs=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"],
        parameters={
            "fast_period": fast_period,
            "slow_period": slow_period,
            "signal_period": signal_period,
            "rsi_period": rsi_period,
            "rsi_oversold": 30,
            "rsi_overbought": 70
        }
    )
    
    return EMACrossoverStrategy(config)
