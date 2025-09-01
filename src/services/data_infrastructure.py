"""
Comprehensive Data Infrastructure System
Training data, datasets, databases, and ML infrastructure for professional trading
"""

import asyncio
import logging
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import sqlite3
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class DataInfrastructure:
    """Complete data infrastructure for professional trading system"""
    
    def __init__(self):
        # Database paths
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Database connections
        self.market_db = None
        self.economic_db = None
        self.news_db = None
        
        # Data schemas
        self.schemas = self._initialize_schemas()
        
        # ML infrastructure
        self.ml_config = self._initialize_ml_config()
        
        logger.info("🏗️ Data Infrastructure initialized")
    
    def _initialize_schemas(self) -> Dict[str, Any]:
        """Initialize data schemas"""
        return {
            "market_data": {
                "ohlcv": ["timestamp", "symbol", "open", "high", "low", "close", "volume"],
                "tick_data": ["timestamp", "symbol", "bid", "ask", "bid_size", "ask_size"],
                "order_book": ["timestamp", "symbol", "level", "bid_price", "bid_size", "ask_price", "ask_size"]
            },
            "economic_data": {
                "indicators": ["timestamp", "indicator", "value", "unit", "frequency"],
                "central_banks": ["timestamp", "bank", "action", "rate", "details"]
            },
            "news_data": {
                "articles": ["timestamp", "title", "content", "source", "sentiment"],
                "social_media": ["timestamp", "platform", "user", "content", "sentiment"]
            }
        }
    
    def _initialize_ml_config(self) -> Dict[str, Any]:
        """Initialize ML configuration"""
        return {
            "features": {
                "technical": ["sma", "ema", "rsi", "macd", "bollinger_bands", "stochastic"],
                "market": ["volatility", "correlation", "liquidity", "momentum", "trend_strength"],
                "fundamental": ["pe_ratio", "pb_ratio", "debt_to_equity", "roe", "revenue_growth"],
                "sentiment": ["news_sentiment", "social_sentiment", "analyst_ratings"]
            },
            "models": {
                "algorithms": ["linear_regression", "random_forest", "gradient_boosting", "neural_networks"],
                "validation": ["cross_validation", "time_series_split", "walk_forward"],
                "metrics": ["sharpe_ratio", "sortino_ratio", "max_drawdown", "win_rate"]
            }
        }
    
    async def initialize_databases(self):
        """Initialize all databases"""
        try:
            logger.info("🗄️ Initializing databases...")
            
            # Initialize market data database
            await self._init_market_db()
            
            # Initialize economic data database
            await self._init_economic_db()
            
            # Initialize news data database
            await self._init_news_db()
            
            # Create tables
            await self._create_tables()
            
            logger.info("✅ Database initialization complete")
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
    
    async def _init_market_db(self):
        """Initialize market data database"""
        try:
            db_path = self.data_dir / "market_data.db"
            self.market_db = sqlite3.connect(db_path)
            logger.info("✅ Market database initialized")
        except Exception as e:
            logger.error(f"Market database error: {str(e)}")
    
    async def _init_economic_db(self):
        """Initialize economic data database"""
        try:
            db_path = self.data_dir / "economic_data.db"
            self.economic_db = sqlite3.connect(db_path)
            logger.info("✅ Economic database initialized")
        except Exception as e:
            logger.error(f"Economic database error: {str(e)}")
    
    async def _init_news_db(self):
        """Initialize news data database"""
        try:
            db_path = self.data_dir / "news_data.db"
            self.news_db = sqlite3.connect(db_path)
            logger.info("✅ News database initialized")
        except Exception as e:
            logger.error(f"News database error: {str(e)}")
    
    async def _create_tables(self):
        """Create database tables"""
        try:
            # Create market data tables
            if self.market_db:
                cursor = self.market_db.cursor()
                
                # OHLCV table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS ohlcv (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        open REAL NOT NULL,
                        high REAL NOT NULL,
                        low REAL NOT NULL,
                        close REAL NOT NULL,
                        volume INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tick data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tick_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        bid REAL NOT NULL,
                        ask REAL NOT NULL,
                        bid_size INTEGER NOT NULL,
                        ask_size INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                self.market_db.commit()
            
            # Create economic data tables
            if self.economic_db:
                cursor = self.economic_db.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS indicators (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        indicator TEXT NOT NULL,
                        value REAL NOT NULL,
                        unit TEXT NOT NULL,
                        frequency TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                self.economic_db.commit()
            
            # Create news data tables
            if self.news_db:
                cursor = self.news_db.cursor()
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        source TEXT NOT NULL,
                        sentiment REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                self.news_db.commit()
            
            logger.info("✅ Database tables created")
            
        except Exception as e:
            logger.error(f"Table creation error: {str(e)}")
    
    async def collect_training_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
        """Collect comprehensive training data"""
        try:
            logger.info(f"📊 Collecting training data for {len(symbols)} symbols...")
            
            training_data = {
                "market_data": {},
                "economic_data": {},
                "news_data": {},
                "metadata": {
                    "collection_start": datetime.now().isoformat(),
                    "symbols": symbols,
                    "date_range": f"{start_date} to {end_date}",
                    "total_records": 0
                }
            }
            
            # Collect market data for each symbol
            for symbol in symbols:
                symbol_data = await self._collect_symbol_data(symbol, start_date, end_date)
                training_data["market_data"][symbol] = symbol_data
                training_data["metadata"]["total_records"] += len(symbol_data)
            
            # Collect economic data
            training_data["economic_data"] = await self._collect_economic_data(start_date, end_date)
            
            # Collect news data
            training_data["news_data"] = await self._collect_news_data(symbols, start_date, end_date)
            
            # Store data in databases
            await self._store_training_data(training_data)
            
            logger.info(f"✅ Training data collection complete: {training_data['metadata']['total_records']} records")
            
            return training_data
            
        except Exception as e:
            logger.error(f"Training data collection error: {str(e)}")
            return {"error": f"Collection failed: {str(e)}"}
    
    async def _collect_symbol_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Collect data for a single symbol"""
        try:
            # Simulate historical data collection
            # In production, this would use real APIs like yfinance, Alpha Vantage, etc.
            
            symbol_data = []
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            current_dt = start_dt
            
            while current_dt <= end_dt:
                # Generate simulated OHLCV data
                base_price = 100.0 + np.random.normal(0, 10)
                
                data_point = {
                    "timestamp": current_dt.isoformat(),
                    "symbol": symbol,
                    "open": base_price + np.random.normal(0, 1),
                    "high": base_price + np.random.normal(2, 1),
                    "low": base_price + np.random.normal(-2, 1),
                    "close": base_price + np.random.normal(0, 1),
                    "volume": int(1000000 + np.random.normal(0, 200000))
                }
                
                symbol_data.append(data_point)
                current_dt += timedelta(days=1)
            
            return symbol_data
            
        except Exception as e:
            logger.error(f"Symbol data collection error for {symbol}: {str(e)}")
            return []
    
    async def _collect_economic_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Collect economic indicators data"""
        try:
            economic_data = {
                "gdp": [],
                "inflation": [],
                "unemployment": [],
                "interest_rates": []
            }
            
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            current_dt = start_dt
            
            while current_dt <= end_dt:
                # GDP data (quarterly)
                if current_dt.month in [3, 6, 9, 12]:
                    economic_data["gdp"].append({
                        "timestamp": current_dt.isoformat(),
                        "indicator": "GDP",
                        "value": 20000 + np.random.normal(0, 500),
                        "unit": "Billions USD",
                        "frequency": "Quarterly"
                    })
                
                # Monthly indicators
                economic_data["inflation"].append({
                    "timestamp": current_dt.isoformat(),
                    "indicator": "CPI",
                    "value": 2.5 + np.random.normal(0, 0.5),
                    "unit": "Percent",
                    "frequency": "Monthly"
                })
                
                economic_data["unemployment"].append({
                    "timestamp": current_dt.isoformat(),
                    "indicator": "Unemployment Rate",
                    "value": 3.8 + np.random.normal(0, 0.3),
                    "unit": "Percent",
                    "frequency": "Monthly"
                })
                
                economic_data["interest_rates"].append({
                    "timestamp": current_dt.isoformat(),
                    "indicator": "Federal Funds Rate",
                    "value": 5.5 + np.random.normal(0, 0.1),
                    "unit": "Percent",
                    "frequency": "Monthly"
                })
                
                current_dt += timedelta(days=1)
            
            return economic_data
            
        except Exception as e:
            logger.error(f"Economic data collection error: {str(e)}")
            return {}
    
    async def _collect_news_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
        """Collect news and sentiment data"""
        try:
            news_data = {
                "articles": [],
                "social_media": []
            }
            
            # Simulate news articles
            for symbol in symbols:
                for i in range(5):  # 5 articles per symbol
                    news_data["articles"].append({
                        "timestamp": (datetime.now() - timedelta(days=i)).isoformat(),
                        "title": f"Analysis: {symbol} shows strong momentum",
                        "content": f"Technical analysis indicates {symbol} is in an uptrend...",
                        "source": "Financial Times",
                        "sentiment": 0.7 + np.random.normal(0, 0.2)
                    })
            
            # Simulate social media data
            for symbol in symbols:
                for i in range(10):  # 10 social posts per symbol
                    news_data["social_media"].append({
                        "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                        "platform": "Twitter",
                        "user": f"trader_{i}",
                        "content": f"${symbol} looking bullish! #trading",
                        "sentiment": 0.5 + np.random.normal(0, 0.3)
                    })
            
            return news_data
            
        except Exception as e:
            logger.error(f"News data collection error: {str(e)}")
            return {}
    
    async def _store_training_data(self, training_data: Dict[str, Any]):
        """Store training data in databases"""
        try:
            # Store market data
            if self.market_db and training_data.get("market_data"):
                cursor = self.market_db.cursor()
                
                for symbol, data in training_data["market_data"].items():
                    for data_point in data:
                        cursor.execute("""
                            INSERT INTO ohlcv (timestamp, symbol, open, high, low, close, volume)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            data_point["timestamp"], data_point["symbol"],
                            data_point["open"], data_point["high"], data_point["low"],
                            data_point["close"], data_point["volume"]
                        ))
                
                self.market_db.commit()
            
            # Store economic data
            if self.economic_db and training_data.get("economic_data"):
                cursor = self.economic_db.cursor()
                
                for indicator, data in training_data["economic_data"].items():
                    for data_point in data:
                        cursor.execute("""
                            INSERT INTO indicators (timestamp, indicator, value, unit, frequency)
                            VALUES (?, ?, ?, ?, ?)
                        """, (
                            data_point["timestamp"], data_point["indicator"],
                            data_point["value"], data_point["unit"], data_point["frequency"]
                        ))
                
                self.economic_db.commit()
            
            # Store news data
            if self.news_db and training_data.get("news_data"):
                cursor = self.news_db.cursor()
                
                for article in training_data["news_data"].get("articles", []):
                    cursor.execute("""
                        INSERT INTO articles (timestamp, title, content, source, sentiment)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        article["timestamp"], article["title"], article["content"],
                        article["source"], article["sentiment"]
                    ))
                
                self.news_db.commit()
            
            logger.info("✅ Training data stored in databases")
            
        except Exception as e:
            logger.error(f"Training data storage error: {str(e)}")
    
    async def generate_features(self, symbol: str, lookback_days: int = 30) -> pd.DataFrame:
        """Generate features for machine learning models"""
        try:
            logger.info(f"🔧 Generating features for {symbol}...")
            
            # Get historical data
            historical_data = await self._get_historical_data(symbol, lookback_days)
            if not historical_data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Generate technical indicators
            df = self._add_technical_indicators(df)
            
            # Generate market features
            df = self._add_market_features(df)
            
            # Clean features
            df = self._clean_features(df)
            
            logger.info(f"✅ Features generated: {df.shape[1]} features, {df.shape[0]} samples")
            
            return df
            
        except Exception as e:
            logger.error(f"Feature generation error: {str(e)}")
            return pd.DataFrame()
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to DataFrame"""
        try:
            # Simple Moving Averages
            df['sma_5'] = df['close'].rolling(window=5).mean()
            df['sma_20'] = df['close'].rolling(window=20).mean()
            df['sma_50'] = df['close'].rolling(window=50).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            ema_12 = df['close'].ewm(span=12).mean()
            ema_26 = df['close'].ewm(span=26).mean()
            df['macd'] = ema_12 - ema_26
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            return df
            
        except Exception as e:
            logger.error(f"Technical indicators error: {str(e)}")
            return df
    
    def _add_market_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market features"""
        try:
            # Price changes
            df['price_change'] = df['close'].pct_change()
            df['price_change_abs'] = df['price_change'].abs()
            
            # Volatility
            df['volatility'] = df['price_change'].rolling(window=20).std()
            
            # Momentum
            df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
            df['momentum_20'] = df['close'] / df['close'].shift(20) - 1
            
            # Trend strength
            df['trend_strength'] = abs(df['sma_20'] - df['sma_50']) / df['sma_50']
            
            return df
            
        except Exception as e:
            logger.error(f"Market features error: {str(e)}")
            return df
    
    def _clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare features for ML"""
        try:
            # Remove rows with NaN values
            df = df.dropna()
            
            # Remove infinite values
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.dropna()
            
            # Reset index
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Feature cleaning error: {str(e)}")
            return df
    
    async def _get_historical_data(self, symbol: str, lookback_days: int) -> List[Dict[str, Any]]:
        """Get historical data from database"""
        try:
            if not self.market_db:
                return []
            
            cursor = self.market_db.cursor()
            
            # Get data from last N days
            start_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()
            
            cursor.execute("""
                SELECT timestamp, symbol, open, high, low, close, volume
                FROM ohlcv
                WHERE symbol = ? AND timestamp >= ?
                ORDER BY timestamp
            """, (symbol, start_date))
            
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                data.append({
                    "timestamp": row[0],
                    "symbol": row[1],
                    "open": row[2],
                    "high": row[3],
                    "low": row[4],
                    "close": row[5],
                    "volume": row[6]
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Historical data retrieval error: {str(e)}")
            return []
    
    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get current infrastructure status"""
        return {
            "databases": {
                "market_db": "Connected" if self.market_db else "Not Connected",
                "economic_db": "Connected" if self.economic_db else "Not Connected",
                "news_db": "Connected" if self.news_db else "Not Connected"
            },
            "data_dir": str(self.data_dir),
            "schemas": list(self.schemas.keys()),
            "ml_config": {
                "feature_types": list(self.ml_config["features"].keys()),
                "algorithms": self.ml_config["models"]["algorithms"]
            }
        }


# Global data infrastructure instance
data_infrastructure = DataInfrastructure()
