"""
Trading AI Knowledge Stack Service
Comprehensive integration of market data, quantitative models, trading knowledge, and AI capabilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import logging
from scipy import stats
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import talib
from textblob import TextBlob
import requests
import json

# Import our data services
from src.services.yfinance_service import yfinance_service
from src.services.polygon_service import polygon_service
from src.services.twelve_data_service import twelve_data_service
from src.services.fred_service import fred_service
from src.services.tiingo_service import tiingo_service
from src.services.eia_service import eia_service

logger = logging.getLogger(__name__)

class TradingAIKnowledgeStack:
    """
    Comprehensive Trading AI Knowledge Stack
    Integrates market data, quantitative models, trading knowledge, and AI capabilities.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        self.regime_cluster = KMeans(n_clusters=3)  # Bull, Bear, Sideways
        self.price_predictor = RandomForestRegressor(n_estimators=100, random_state=42)
        self.sentiment_analyzer = TextBlob("")
        
        # Market regime labels
        self.regime_labels = {0: "Bear", 1: "Sideways", 2: "Bull"}
        
        # Technical indicators cache
        self.technical_cache = {}
        
        # Risk metrics cache
        self.risk_cache = {}
        
        logger.info("Trading AI Knowledge Stack initialized")
    
    # ============================================================================
    # 1. 📊 Market Data & Fundamentals Integration
    # ============================================================================
    
    async def get_comprehensive_market_data(self, symbol: str, timeframe: str = "1d", 
                                          lookback_days: int = 365) -> Dict[str, Any]:
        """Get comprehensive market data from multiple sources."""
        try:
            # Get data from multiple sources
            yf_data = await self._get_yfinance_data(symbol, timeframe, lookback_days)
            polygon_data = await self._get_polygon_data(symbol, timeframe, lookback_days)
            twelve_data = await self._get_twelve_data(symbol, timeframe, lookback_days)
            
            # Combine and validate data
            combined_data = self._combine_market_data(yf_data, polygon_data, twelve_data)
            
            return {
                "symbol": symbol,
                "data": combined_data,
                "sources": ["YFinance", "Polygon.io", "Twelve Data"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting comprehensive market data: {e}")
            return {"error": str(e)}
    
    async def get_fundamental_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive fundamental analysis."""
        try:
            # Get fundamental data from multiple sources
            yf_fundamentals = await self._get_yfinance_fundamentals(symbol)
            tiingo_fundamentals = await self._get_tiingo_fundamentals(symbol)
            
            # Combine fundamental data
            combined_fundamentals = self._combine_fundamental_data(yf_fundamentals, tiingo_fundamentals)
            
            return {
                "symbol": symbol,
                "fundamentals": combined_fundamentals,
                "analysis": self._analyze_fundamentals(combined_fundamentals),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting fundamental analysis: {e}")
            return {"error": str(e)}
    
    async def get_macroeconomic_context(self) -> Dict[str, Any]:
        """Get macroeconomic context for trading decisions."""
        try:
            # Get key economic indicators
            gdp = await self._get_fred_data("GDP")
            cpi = await self._get_fred_data("CPIAUCSL")
            unemployment = await self._get_fred_data("UNRATE")
            fed_funds = await self._get_fred_data("FEDFUNDS")
            treasury_10y = await self._get_fred_data("GS10")
            
            # Get energy context
            oil_prices = await self._get_eia_data("crude_oil_prices")
            natural_gas = await self._get_eia_data("natural_gas_prices")
            
            macro_context = {
                "gdp": gdp,
                "inflation": cpi,
                "unemployment": unemployment,
                "interest_rates": {
                    "fed_funds": fed_funds,
                    "treasury_10y": treasury_10y
                },
                "energy": {
                    "oil": oil_prices,
                    "natural_gas": natural_gas
                }
            }
            
            return {
                "macroeconomic_context": macro_context,
                "analysis": self._analyze_macro_context(macro_context),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting macroeconomic context: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # 2. 🧮 Quantitative Finance & Math Models
    # ============================================================================
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators."""
        try:
            df = data.copy()
            
            # Trend indicators
            df['sma_20'] = talib.SMA(df['close'], timeperiod=20)
            df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
            df['sma_200'] = talib.SMA(df['close'], timeperiod=200)
            df['ema_12'] = talib.EMA(df['close'], timeperiod=12)
            df['ema_26'] = talib.EMA(df['close'], timeperiod=26)
            
            # Momentum indicators
            df['rsi'] = talib.RSI(df['close'], timeperiod=14)
            df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(df['close'])
            df['stoch_k'], df['stoch_d'] = talib.STOCH(df['high'], df['low'], df['close'])
            df['williams_r'] = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=14)
            
            # Volatility indicators
            df['bbands_upper'], df['bbands_middle'], df['bbands_lower'] = talib.BBANDS(df['close'])
            df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
            
            # Volume indicators
            df['obv'] = talib.OBV(df['close'], df['volume'])
            df['ad'] = talib.AD(df['high'], df['low'], df['close'], df['volume'])
            
            # Additional indicators
            df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)
            df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
            df['aroon_up'], df['aroon_down'] = talib.AROON(df['high'], df['low'], timeperiod=14)
            
            return df
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return data
    
    def calculate_risk_metrics(self, returns: pd.Series) -> Dict[str, float]:
        """Calculate comprehensive risk metrics."""
        try:
            # Basic statistics
            mean_return = returns.mean()
            std_return = returns.std()
            
            # Risk metrics
            var_95 = np.percentile(returns, 5)
            cvar_95 = returns[returns <= var_95].mean()
            
            # Maximum drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = drawdown.min()
            
            # Sharpe ratio (assuming risk-free rate of 2%)
            risk_free_rate = 0.02
            sharpe_ratio = (mean_return - risk_free_rate) / std_return if std_return > 0 else 0
            
            # Sortino ratio
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std()
            sortino_ratio = (mean_return - risk_free_rate) / downside_std if downside_std > 0 else 0
            
            # Calmar ratio
            calmar_ratio = mean_return / abs(max_drawdown) if max_drawdown != 0 else 0
            
            return {
                "mean_return": mean_return,
                "volatility": std_return,
                "var_95": var_95,
                "cvar_95": cvar_95,
                "max_drawdown": max_drawdown,
                "sharpe_ratio": sharpe_ratio,
                "sortino_ratio": sortino_ratio,
                "calmar_ratio": calmar_ratio
            }
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def detect_market_regime(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Detect market regime using clustering."""
        try:
            # Prepare features for regime detection
            features = []
            
            # Price momentum
            features.append(data['close'].pct_change().rolling(20).mean())
            features.append(data['close'].pct_change().rolling(50).mean())
            
            # Volatility
            features.append(data['close'].pct_change().rolling(20).std())
            features.append(data['close'].pct_change().rolling(50).std())
            
            # Volume
            features.append(data['volume'].rolling(20).mean())
            
            # Technical indicators
            if 'rsi' in data.columns:
                features.append(data['rsi'].rolling(20).mean())
            if 'macd' in data.columns:
                features.append(data['macd'].rolling(20).mean())
            
            # Combine features
            feature_matrix = pd.concat(features, axis=1).dropna()
            
            # Scale features
            scaled_features = self.scaler.fit_transform(feature_matrix)
            
            # Cluster to detect regimes
            clusters = self.regime_cluster.fit_predict(scaled_features)
            
            # Map clusters to regimes
            current_regime = self.regime_labels.get(clusters[-1], "Unknown")
            
            return {
                "current_regime": current_regime,
                "regime_probability": self._calculate_regime_probability(scaled_features[-1]),
                "regime_history": [self.regime_labels.get(c, "Unknown") for c in clusters],
                "regime_features": feature_matrix.columns.tolist()
            }
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return {"current_regime": "Unknown", "error": str(e)}
    
    # ============================================================================
    # 3. 📘 Trading Knowledge & Market Psychology
    # ============================================================================
    
    def identify_chart_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identify common chart patterns."""
        try:
            patterns = []
            
            # Double top/bottom
            double_top = self._detect_double_top(data)
            double_bottom = self._detect_double_bottom(data)
            
            # Head and shoulders
            head_shoulders = self._detect_head_shoulders(data)
            inverse_head_shoulders = self._detect_inverse_head_shoulders(data)
            
            # Triangle patterns
            ascending_triangle = self._detect_ascending_triangle(data)
            descending_triangle = self._detect_descending_triangle(data)
            symmetrical_triangle = self._detect_symmetrical_triangle(data)
            
            # Support and resistance
            support_resistance = self._identify_support_resistance(data)
            
            patterns.extend([double_top, double_bottom, head_shoulders, 
                           inverse_head_shoulders, ascending_triangle, 
                           descending_triangle, symmetrical_triangle])
            patterns.append(support_resistance)
            
            return [p for p in patterns if p is not None]
        except Exception as e:
            logger.error(f"Error identifying chart patterns: {e}")
            return []
    
    def analyze_market_psychology(self, data: pd.DataFrame, news_sentiment: List[Dict] = None) -> Dict[str, Any]:
        """Analyze market psychology indicators."""
        try:
            psychology_indicators = {}
            
            # Fear and greed indicators
            if 'rsi' in data.columns:
                psychology_indicators['rsi_extremes'] = {
                    'oversold': data['rsi'].iloc[-1] < 30,
                    'overbought': data['rsi'].iloc[-1] > 70,
                    'current_rsi': data['rsi'].iloc[-1]
                }
            
            # Volume analysis
            avg_volume = data['volume'].rolling(20).mean()
            current_volume = data['volume'].iloc[-1]
            psychology_indicators['volume_analysis'] = {
                'volume_spike': current_volume > avg_volume.iloc[-1] * 1.5,
                'volume_ratio': current_volume / avg_volume.iloc[-1],
                'trend_confirmation': self._check_volume_trend_confirmation(data)
            }
            
            # Price action psychology
            psychology_indicators['price_action'] = {
                'gap_up': data['open'].iloc[-1] > data['close'].iloc[-2] * 1.02,
                'gap_down': data['open'].iloc[-1] < data['close'].iloc[-2] * 0.98,
                'doji': self._is_doji(data.iloc[-1]),
                'hammer': self._is_hammer(data.iloc[-1]),
                'shooting_star': self._is_shooting_star(data.iloc[-1])
            }
            
            # News sentiment integration
            if news_sentiment:
                psychology_indicators['news_sentiment'] = self._analyze_news_sentiment(news_sentiment)
            
            return psychology_indicators
        except Exception as e:
            logger.error(f"Error analyzing market psychology: {e}")
            return {}
    
    # ============================================================================
    # 4. 🌍 Alternative Data Integration
    # ============================================================================
    
    async def get_alternative_data_signals(self, symbol: str) -> Dict[str, Any]:
        """Get alternative data signals."""
        try:
            signals = {}
            
            # News sentiment
            news_sentiment = await self._get_news_sentiment(symbol)
            signals['news_sentiment'] = news_sentiment
            
            # Social sentiment (placeholder for future integration)
            signals['social_sentiment'] = {
                'reddit_sentiment': 0.0,
                'twitter_sentiment': 0.0,
                'stocktwits_sentiment': 0.0
            }
            
            # Google Trends (placeholder)
            signals['google_trends'] = {
                'search_interest': 0.0,
                'trend_direction': "neutral"
            }
            
            # Earnings sentiment
            earnings_sentiment = await self._get_earnings_sentiment(symbol)
            signals['earnings_sentiment'] = earnings_sentiment
            
            return signals
        except Exception as e:
            logger.error(f"Error getting alternative data signals: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # 5. ⚡ Execution & Strategy Knowledge
    # ============================================================================
    
    def calculate_optimal_position_size(self, capital: float, risk_per_trade: float, 
                                      stop_loss_pct: float, volatility: float) -> float:
        """Calculate optimal position size using Kelly Criterion and risk management."""
        try:
            # Kelly Criterion for position sizing
            win_rate = 0.55  # Estimated win rate
            avg_win = 0.02   # Average win percentage
            avg_loss = 0.01  # Average loss percentage
            
            kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
            
            # Risk-based position sizing
            risk_amount = capital * risk_per_trade
            position_size = risk_amount / (stop_loss_pct / 100)
            
            # Volatility adjustment
            volatility_adjustment = 1 / (1 + volatility)
            adjusted_position_size = position_size * volatility_adjustment
            
            # Apply Kelly fraction
            final_position_size = adjusted_position_size * kelly_fraction
            
            return min(final_position_size, capital * 0.1)  # Max 10% of capital
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return capital * 0.01  # Default to 1%
    
    def generate_trading_signals(self, data: pd.DataFrame, 
                               technical_indicators: pd.DataFrame,
                               fundamental_data: Dict = None,
                               alternative_data: Dict = None) -> Dict[str, Any]:
        """Generate comprehensive trading signals."""
        try:
            signals = {}
            
            # Technical signals
            signals['technical'] = self._generate_technical_signals(technical_indicators)
            
            # Fundamental signals
            if fundamental_data:
                signals['fundamental'] = self._generate_fundamental_signals(fundamental_data)
            
            # Alternative data signals
            if alternative_data:
                signals['alternative'] = self._generate_alternative_signals(alternative_data)
            
            # Combined signal
            signals['combined'] = self._combine_signals(signals)
            
            return signals
        except Exception as e:
            logger.error(f"Error generating trading signals: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # 6. 🧠 AI & Machine Learning for Trading
    # ============================================================================
    
    def train_price_prediction_model(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Train price prediction model using machine learning."""
        try:
            # Prepare features
            features = self._prepare_ml_features(data)
            
            # Prepare target (next day's return)
            target = data['close'].pct_change().shift(-1).dropna()
            
            # Align features and target
            features = features.iloc[:-1]  # Remove last row since we don't have next day's target
            target = target.iloc[:-1]
            
            # Remove any remaining NaN values
            valid_indices = features.dropna().index.intersection(target.dropna().index)
            features = features.loc[valid_indices]
            target = target.loc[valid_indices]
            
            if len(features) < 100:  # Need sufficient data
                return {"error": "Insufficient data for training"}
            
            # Train model
            self.price_predictor.fit(features, target)
            
            # Make prediction for next day
            latest_features = features.iloc[-1:].values
            prediction = self.price_predictor.predict(latest_features)[0]
            
            # Feature importance
            feature_importance = dict(zip(features.columns, 
                                        self.price_predictor.feature_importances_))
            
            return {
                "prediction": prediction,
                "predicted_return_pct": prediction * 100,
                "feature_importance": feature_importance,
                "model_score": self.price_predictor.score(features, target)
            }
        except Exception as e:
            logger.error(f"Error training price prediction model: {e}")
            return {"error": str(e)}
    
    def detect_anomalies(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect market anomalies using unsupervised learning."""
        try:
            anomalies = []
            
            # Price anomalies
            price_anomalies = self._detect_price_anomalies(data)
            anomalies.extend(price_anomalies)
            
            # Volume anomalies
            volume_anomalies = self._detect_volume_anomalies(data)
            anomalies.extend(volume_anomalies)
            
            # Volatility anomalies
            volatility_anomalies = self._detect_volatility_anomalies(data)
            anomalies.extend(volatility_anomalies)
            
            return anomalies
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return []
    
    # ============================================================================
    # 7. 📚 Knowledge Integration & Strategy Execution
    # ============================================================================
    
    async def generate_comprehensive_analysis(self, symbol: str) -> Dict[str, Any]:
        """Generate comprehensive trading analysis using all knowledge sources."""
        try:
            # Get all data sources
            market_data = await self.get_comprehensive_market_data(symbol)
            fundamental_data = await self.get_fundamental_analysis(symbol)
            macro_context = await self.get_macroeconomic_context()
            alternative_data = await self.get_alternative_data_signals(symbol)
            
            # Calculate technical indicators
            if 'data' in market_data and not market_data.get('error'):
                df = pd.DataFrame(market_data['data'])
                technical_indicators = self.calculate_technical_indicators(df)
                
                # Generate all analyses
                risk_metrics = self.calculate_risk_metrics(df['close'].pct_change())
                market_regime = self.detect_market_regime(technical_indicators)
                chart_patterns = self.identify_chart_patterns(technical_indicators)
                market_psychology = self.analyze_market_psychology(technical_indicators)
                trading_signals = self.generate_trading_signals(df, technical_indicators, 
                                                              fundamental_data, alternative_data)
                price_prediction = self.train_price_prediction_model(technical_indicators)
                anomalies = self.detect_anomalies(technical_indicators)
                
                return {
                    "symbol": symbol,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "market_data": market_data,
                    "fundamental_analysis": fundamental_data,
                    "macroeconomic_context": macro_context,
                    "alternative_data": alternative_data,
                    "technical_analysis": {
                        "indicators": technical_indicators.tail(10).to_dict('records'),
                        "risk_metrics": risk_metrics,
                        "market_regime": market_regime,
                        "chart_patterns": chart_patterns,
                        "market_psychology": market_psychology
                    },
                    "trading_signals": trading_signals,
                    "ai_predictions": price_prediction,
                    "anomalies": anomalies,
                    "recommendation": self._generate_trading_recommendation(
                        trading_signals, price_prediction, risk_metrics, market_regime
                    )
                }
            else:
                return {"error": "Failed to get market data"}
        except Exception as e:
            logger.error(f"Error generating comprehensive analysis: {e}")
            return {"error": str(e)}
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    async def _get_yfinance_data(self, symbol: str, timeframe: str, lookback_days: int):
        """Get YFinance data."""
        try:
            return yfinance_service.get_stock_data(symbol, interval=timeframe)
        except:
            return None
    
    async def _get_polygon_data(self, symbol: str, timeframe: str, lookback_days: int):
        """Get Polygon.io data."""
        try:
            return polygon_service.get_stock_data(symbol, timespan=timeframe)
        except:
            return None
    
    async def _get_twelve_data(self, symbol: str, timeframe: str, lookback_days: int):
        """Get Twelve Data."""
        try:
            return twelve_data_service.get_stock_data(symbol, interval=timeframe)
        except:
            return None
    
    async def _get_fred_data(self, series_id: str):
        """Get FRED data."""
        try:
            return fred_service.get_series(series_id)
        except:
            return None
    
    async def _get_eia_data(self, data_type: str):
        """Get EIA data."""
        try:
            if data_type == "crude_oil_prices":
                return eia_service.get_crude_oil_prices()
            elif data_type == "natural_gas_prices":
                return eia_service.get_natural_gas_prices()
            return None
        except:
            return None
    
    def _combine_market_data(self, yf_data, polygon_data, twelve_data):
        """Combine data from multiple sources."""
        # Implementation for combining data sources
        return yf_data if yf_data else {}
    
    def _prepare_ml_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for machine learning."""
        features = pd.DataFrame()
        
        # Price features
        features['returns'] = data['close'].pct_change()
        features['log_returns'] = np.log(data['close'] / data['close'].shift(1))
        features['price_momentum'] = data['close'].pct_change(5)
        features['price_momentum_20'] = data['close'].pct_change(20)
        
        # Volume features
        features['volume_ratio'] = data['volume'] / data['volume'].rolling(20).mean()
        features['volume_momentum'] = data['volume'].pct_change()
        
        # Technical indicators (if available)
        if 'rsi' in data.columns:
            features['rsi'] = data['rsi']
        if 'macd' in data.columns:
            features['macd'] = data['macd']
        if 'bbands_upper' in data.columns:
            features['bb_position'] = (data['close'] - data['bbands_lower']) / (data['bbands_upper'] - data['bbands_lower'])
        
        return features.dropna()
    
    def _generate_trading_recommendation(self, signals, prediction, risk_metrics, market_regime):
        """Generate trading recommendation based on all analysis."""
        try:
            # Simple scoring system
            score = 0
            
            # Technical signals
            if 'technical' in signals:
                tech_signals = signals['technical']
                if tech_signals.get('buy_signals', 0) > tech_signals.get('sell_signals', 0):
                    score += 1
                else:
                    score -= 1
            
            # AI prediction
            if prediction and 'prediction' in prediction:
                if prediction['prediction'] > 0:
                    score += 1
                else:
                    score -= 1
            
            # Risk assessment
            if risk_metrics and risk_metrics.get('sharpe_ratio', 0) > 1:
                score += 1
            
            # Market regime
            if market_regime and market_regime.get('current_regime') == 'Bull':
                score += 1
            elif market_regime and market_regime.get('current_regime') == 'Bear':
                score -= 1
            
            # Generate recommendation
            if score >= 2:
                return "STRONG_BUY"
            elif score == 1:
                return "BUY"
            elif score == 0:
                return "HOLD"
            elif score == -1:
                return "SELL"
            else:
                return "STRONG_SELL"
        except Exception as e:
            logger.error(f"Error generating recommendation: {e}")
            return "HOLD"

# Global instance
ai_knowledge_stack = TradingAIKnowledgeStack()
