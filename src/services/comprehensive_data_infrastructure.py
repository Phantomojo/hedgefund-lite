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
import psycopg2
from sqlalchemy import create_engine, text
import redis
import pickle
import hashlib
import os
from pathlib import Path

# Data processing libraries
import yfinance as yf
import requests
import websocket
from alpha_vantage.timeseries import TimeSeries
from fredapi import Fred

logger = logging.getLogger(__name__)

class ComprehensiveDataInfrastructure:
    """Complete data infrastructure for professional trading system"""
    
    def __init__(self):
        # Database configurations
        self.databases = {
            "time_series": None,  # InfluxDB for high-frequency data
            "relational": None,   # PostgreSQL for structured data
            "document": None,     # MongoDB for unstructured data
            "cache": None,        # Redis for real-time access
            "warehouse": None     # ClickHouse for analytics
        }
        
        # Data sources configuration
        self.data_sources = {
            "market_data": {
                "oanda": {"enabled": True, "api_key": None},
                "alpha_vantage": {"enabled": True, "api_key": None},
                "yfinance": {"enabled": True, "api_key": None},
                "polygon": {"enabled": False, "api_key": None},
                "iex": {"enabled": False, "api_key": None}
            },
            "economic_data": {
                "fred": {"enabled": True, "api_key": None},
                "bloomberg": {"enabled": False, "api_key": None},
                "reuters": {"enabled": False, "api_key": None}
            },
            "news_data": {
                "newsapi": {"enabled": True, "api_key": None},
                "twitter": {"enabled": False, "api_key": None},
                "reddit": {"enabled": False, "api_key": None}
            },
            "alternative_data": {
                "satellite": {"enabled": False, "api_key": None},
                "credit_cards": {"enabled": False, "api_key": None},
                "shipping": {"enabled": False, "api_key": None}
            }
        }
        
        # Data schemas
        self.data_schemas = self._initialize_data_schemas()
        
        # ML infrastructure
        self.ml_infrastructure = self._initialize_ml_infrastructure()
        
        # Data quality monitoring
        self.data_quality = self._initialize_data_quality()
        
        logger.info("🏗️ Comprehensive Data Infrastructure initialized")
    
    def _initialize_data_schemas(self) -> Dict[str, Any]:
        """Initialize data schemas for different data types"""
        return {
            "market_data": {
                "ohlcv": {
                    "timestamp": "TIMESTAMP",
                    "symbol": "VARCHAR(20)",
                    "open": "DECIMAL(10,5)",
                    "high": "DECIMAL(10,5)",
                    "low": "DECIMAL(10,5)",
                    "close": "DECIMAL(10,5)",
                    "volume": "BIGINT",
                    "source": "VARCHAR(50)"
                },
                "tick_data": {
                    "timestamp": "TIMESTAMP",
                    "symbol": "VARCHAR(20)",
                    "bid": "DECIMAL(10,5)",
                    "ask": "DECIMAL(10,5)",
                    "bid_size": "BIGINT",
                    "ask_size": "BIGINT",
                    "source": "VARCHAR(50)"
                },
                "order_book": {
                    "timestamp": "TIMESTAMP",
                    "symbol": "VARCHAR(20)",
                    "level": "INTEGER",
                    "bid_price": "DECIMAL(10,5)",
                    "bid_size": "BIGINT",
                    "ask_price": "DECIMAL(10,5)",
                    "ask_size": "BIGINT",
                    "source": "VARCHAR(50)"
                }
            },
            "economic_data": {
                "indicators": {
                    "timestamp": "TIMESTAMP",
                    "indicator": "VARCHAR(100)",
                    "value": "DECIMAL(15,5)",
                    "unit": "VARCHAR(20)",
                    "frequency": "VARCHAR(20)",
                    "source": "VARCHAR(50)"
                },
                "central_banks": {
                    "timestamp": "TIMESTAMP",
                    "bank": "VARCHAR(50)",
                    "action": "VARCHAR(100)",
                    "rate": "DECIMAL(5,2)",
                    "details": "TEXT",
                    "source": "VARCHAR(50)"
                }
            },
            "news_data": {
                "articles": {
                    "timestamp": "TIMESTAMP",
                    "title": "TEXT",
                    "content": "TEXT",
                    "source": "VARCHAR(100)",
                    "url": "TEXT",
                    "sentiment": "DECIMAL(3,2)",
                    "entities": "JSONB"
                },
                "social_media": {
                    "timestamp": "TIMESTAMP",
                    "platform": "VARCHAR(50)",
                    "user": "VARCHAR(100)",
                    "content": "TEXT",
                    "sentiment": "DECIMAL(3,2)",
                    "followers": "INTEGER"
                }
            },
            "alternative_data": {
                "satellite": {
                    "timestamp": "TIMESTAMP",
                    "location": "VARCHAR(100)",
                    "metric": "VARCHAR(50)",
                    "value": "DECIMAL(15,5)",
                    "unit": "VARCHAR(20)",
                    "source": "VARCHAR(50)"
                },
                "credit_cards": {
                    "timestamp": "TIMESTAMP",
                    "category": "VARCHAR(100)",
                    "spending": "DECIMAL(15,2)",
                    "transactions": "INTEGER",
                    "region": "VARCHAR(50)",
                    "source": "VARCHAR(50)"
                }
            }
        }
    
    def _initialize_ml_infrastructure(self) -> Dict[str, Any]:
        """Initialize machine learning infrastructure"""
        return {
            "feature_engineering": {
                "technical_indicators": [
                    "sma", "ema", "rsi", "macd", "bollinger_bands",
                    "stochastic", "williams_r", "cci", "adx", "atr"
                ],
                "market_features": [
                    "volatility", "correlation", "liquidity", "momentum",
                    "trend_strength", "support_resistance", "volume_profile"
                ],
                "fundamental_features": [
                    "pe_ratio", "pb_ratio", "debt_to_equity", "roe",
                    "revenue_growth", "earnings_growth", "dividend_yield"
                ],
                "sentiment_features": [
                    "news_sentiment", "social_sentiment", "analyst_ratings",
                    "insider_trading", "short_interest", "options_flow"
                ]
            },
            "model_training": {
                "algorithms": [
                    "linear_regression", "random_forest", "gradient_boosting",
                    "neural_networks", "lstm", "transformer", "ensemble"
                ],
                "validation": [
                    "cross_validation", "time_series_split", "walk_forward",
                    "out_of_sample", "stress_testing"
                ],
                "hyperparameter_tuning": [
                    "grid_search", "random_search", "bayesian_optimization",
                    "genetic_algorithms", "neural_architecture_search"
                ]
            },
            "backtesting": {
                "frameworks": [
                    "vectorized", "event_driven", "monte_carlo",
                    "walk_forward", "out_of_sample"
                ],
                "metrics": [
                    "sharpe_ratio", "sortino_ratio", "calmar_ratio",
                    "max_drawdown", "win_rate", "profit_factor"
                ]
            }
        }
    
    def _initialize_data_quality(self) -> Dict[str, Any]:
        """Initialize data quality monitoring"""
        return {
            "completeness": {
                "missing_data_threshold": 0.05,  # 5% missing data allowed
                "data_gap_threshold": 300,  # 5 minutes for 1-minute data
                "outlier_threshold": 3.0  # 3 standard deviations
            },
            "accuracy": {
                "price_validation": True,
                "volume_validation": True,
                "timestamp_validation": True,
                "cross_source_validation": True
            },
            "consistency": {
                "schema_validation": True,
                "data_type_validation": True,
                "range_validation": True,
                "business_rule_validation": True
            },
            "timeliness": {
                "real_time_latency": 100,  # 100ms for real-time data
                "batch_latency": 300,  # 5 minutes for batch data
                "historical_latency": 3600  # 1 hour for historical data
            }
        }
    
    async def initialize_databases(self):
        """Initialize all database connections"""
        try:
            logger.info("🗄️ Initializing database connections...")
            
            # Initialize PostgreSQL (relational database)
            await self._init_postgresql()
            
            # Initialize Redis (cache)
            await self._init_redis()
            
            # Initialize SQLite (local storage)
            await self._init_sqlite()
            
            # Create tables
            await self._create_database_tables()
            
            logger.info("✅ Database initialization complete")
            
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise
    
    async def _init_postgresql(self):
        """Initialize PostgreSQL connection"""
        try:
            # In production, use environment variables
            connection_string = "postgresql://trading:password@localhost:5432/trading_db"
            
            # Test connection
            conn = psycopg2.connect(connection_string)
            conn.close()
            
            self.databases["relational"] = connection_string
            logger.info("✅ PostgreSQL connection established")
            
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {str(e)}")
            logger.info("📝 Using SQLite as fallback")
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            # Test Redis connection
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
            redis_client.ping()
            
            self.databases["cache"] = redis_client
            logger.info("✅ Redis connection established")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}")
            logger.info("📝 Using in-memory cache as fallback")
    
    async def _init_sqlite(self):
        """Initialize SQLite connection"""
        try:
            db_path = "data/trading_data.db"
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            conn = sqlite3.connect(db_path)
            self.databases["local"] = conn
            
            logger.info("✅ SQLite connection established")
            
        except Exception as e:
            logger.error(f"SQLite connection failed: {str(e)}")
            raise
    
    async def _create_database_tables(self):
        """Create database tables based on schemas"""
        try:
            if self.databases["local"]:
                conn = self.databases["local"]
                cursor = conn.cursor()
                
                # Create market data tables
                for table_name, schema in self.data_schemas["market_data"].items():
                    columns = ", ".join([f"{col} {dtype}" for col, dtype in schema.items()])
                    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
                    cursor.execute(create_table_sql)
                
                # Create economic data tables
                for table_name, schema in self.data_schemas["economic_data"].items():
                    columns = ", ".join([f"{col} {dtype}" for col, dtype in schema.items()])
                    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
                    cursor.execute(create_table_sql)
                
                # Create news data tables
                for table_name, schema in self.data_schemas["news_data"].items():
                    columns = ", ".join([f"{col} {dtype}" for col, dtype in schema.items()])
                    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
                    cursor.execute(create_table_sql)
                
                # Create alternative data tables
                for table_name, schema in self.data_schemas["alternative_data"].items():
                    columns = ", ".join([f"{col} {dtype}" for col, dtype in schema.items()])
                    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
                    cursor.execute(create_table_sql)
                
                # Create ML model tables
                ml_tables = {
                    "models": """
                        CREATE TABLE IF NOT EXISTS models (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name VARCHAR(100),
                            version VARCHAR(20),
                            algorithm VARCHAR(50),
                            parameters TEXT,
                            performance_metrics TEXT,
                            created_at TIMESTAMP,
                            updated_at TIMESTAMP
                        )
                    """,
                    "training_data": """
                        CREATE TABLE IF NOT EXISTS training_data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            model_id INTEGER,
                            data_hash VARCHAR(64),
                            features TEXT,
                            labels TEXT,
                            split_type VARCHAR(20),
                            created_at TIMESTAMP
                        )
                    """,
                    "predictions": """
                        CREATE TABLE IF NOT EXISTS predictions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            model_id INTEGER,
                            symbol VARCHAR(20),
                            timestamp TIMESTAMP,
                            prediction TEXT,
                            confidence DECIMAL(5,4),
                            actual_value TEXT,
                            created_at TIMESTAMP
                        )
                    """
                }
                
                for table_name, create_sql in ml_tables.items():
                    cursor.execute(create_sql)
                
                conn.commit()
                logger.info("✅ Database tables created")
                
        except Exception as e:
            logger.error(f"Table creation error: {str(e)}")
            raise
    
    async def collect_training_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
        """Collect comprehensive training data for multiple symbols"""
        try:
            logger.info(f"📊 Collecting training data for {len(symbols)} symbols...")
            
            training_data = {
                "market_data": {},
                "economic_data": {},
                "news_data": {},
                "alternative_data": {},
                "metadata": {
                    "collection_start": datetime.now().isoformat(),
                    "symbols": symbols,
                    "date_range": f"{start_date} to {end_date}",
                    "total_records": 0
                }
            }
            
            # Collect market data
            for symbol in symbols:
                symbol_data = await self._collect_symbol_data(symbol, start_date, end_date)
                training_data["market_data"][symbol] = symbol_data
                training_data["metadata"]["total_records"] += len(symbol_data)
            
            # Collect economic data
            training_data["economic_data"] = await self._collect_economic_data(start_date, end_date)
            
            # Collect news data
            training_data["news_data"] = await self._collect_news_data(symbols, start_date, end_date)
            
            # Store training data
            await self._store_training_data(training_data)
            
            logger.info(f"✅ Training data collection complete: {training_data['metadata']['total_records']} records")
            
            return training_data
            
        except Exception as e:
            logger.error(f"Training data collection error: {str(e)}")
            return {"error": f"Collection failed: {str(e)}"}
    
    async def _collect_symbol_data(self, symbol: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Collect data for a single symbol"""
        try:
            # Use yfinance for historical data
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(start=start_date, end=end_date, interval="1d")
            
            # Convert to list of dictionaries
            symbol_data = []
            for timestamp, row in hist_data.iterrows():
                data_point = {
                    "timestamp": timestamp.isoformat(),
                    "symbol": symbol,
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                    "source": "yfinance"
                }
                symbol_data.append(data_point)
            
            return symbol_data
            
        except Exception as e:
            logger.error(f"Symbol data collection error for {symbol}: {str(e)}")
            return []
    
    async def _collect_economic_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Collect economic indicators data"""
        try:
            # Placeholder: in production, use FRED API
            economic_data = {
                "gdp": [],
                "inflation": [],
                "unemployment": [],
                "interest_rates": []
            }
            
            # Simulate economic data
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
                        "frequency": "Quarterly",
                        "source": "simulated"
                    })
                
                # Inflation data (monthly)
                economic_data["inflation"].append({
                    "timestamp": current_dt.isoformat(),
                    "indicator": "CPI",
                    "value": 2.5 + np.random.normal(0, 0.5),
                    "unit": "Percent",
                    "frequency": "Monthly",
                    "source": "simulated"
                })
                
                # Unemployment data (monthly)
                economic_data["unemployment"].append({
                    "timestamp": current_dt.isoformat(),
                    "indicator": "Unemployment Rate",
                    "value": 3.8 + np.random.normal(0, 0.3),
                    "unit": "Percent",
                    "frequency": "Monthly",
                    "source": "simulated"
                })
                
                # Interest rates (monthly)
                economic_data["interest_rates"].append({
                    "timestamp": current_dt.isoformat(),
                    "indicator": "Federal Funds Rate",
                    "value": 5.5 + np.random.normal(0, 0.1),
                    "unit": "Percent",
                    "frequency": "Monthly",
                    "source": "simulated"
                })
                
                current_dt += timedelta(days=1)
            
            return economic_data
            
        except Exception as e:
            logger.error(f"Economic data collection error: {str(e)}")
            return {}
    
    async def _collect_news_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, Any]:
        """Collect news and sentiment data"""
        try:
            # Placeholder: in production, use NewsAPI or similar
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
                        "url": f"https://example.com/news/{symbol}_{i}",
                        "sentiment": 0.7 + np.random.normal(0, 0.2),
                        "entities": json.dumps({"symbols": [symbol], "companies": ["Example Corp"]})
                    })
            
            # Simulate social media data
            for symbol in symbols:
                for i in range(10):  # 10 social posts per symbol
                    news_data["social_media"].append({
                        "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
                        "platform": "Twitter",
                        "user": f"trader_{i}",
                        "content": f"$#symbol looking bullish! #trading",
                        "sentiment": 0.5 + np.random.normal(0, 0.3),
                        "followers": 1000 + np.random.randint(0, 10000)
                    })
            
            return news_data
            
        except Exception as e:
            logger.error(f"News data collection error: {str(e)}")
            return {}
    
    async def _store_training_data(self, training_data: Dict[str, Any]):
        """Store training data in database"""
        try:
            if self.databases["local"]:
                conn = self.databases["local"]
                cursor = conn.cursor()
                
                # Store market data
                for symbol, data in training_data["market_data"].items():
                    for data_point in data:
                        cursor.execute("""
                            INSERT INTO ohlcv (timestamp, symbol, open, high, low, close, volume, source)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            data_point["timestamp"], data_point["symbol"],
                            data_point["open"], data_point["high"], data_point["low"],
                            data_point["close"], data_point["volume"], data_point["source"]
                        ))
                
                # Store economic data
                for indicator, data in training_data["economic_data"].items():
                    for data_point in data:
                        cursor.execute("""
                            INSERT INTO indicators (timestamp, indicator, value, unit, frequency, source)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            data_point["timestamp"], data_point["indicator"],
                            data_point["value"], data_point["unit"],
                            data_point["frequency"], data_point["source"]
                        ))
                
                # Store news data
                for article in training_data["news_data"].get("articles", []):
                    cursor.execute("""
                        INSERT INTO articles (timestamp, title, content, source, url, sentiment, entities)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        article["timestamp"], article["title"], article["content"],
                        article["source"], article["url"], article["sentiment"], article["entities"]
                    ))
                
                conn.commit()
                logger.info("✅ Training data stored in database")
                
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
            
            # Generate sentiment features
            df = self._add_sentiment_features(df, symbol)
            
            # Generate economic features
            df = self._add_economic_features(df)
            
            # Clean and prepare features
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
            
            # Exponential Moving Averages
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # MACD
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
            
            # Bollinger Bands
            df['bb_middle'] = df['close'].rolling(window=20).mean()
            bb_std = df['close'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
            df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # Stochastic
            low_min = df['low'].rolling(window=14).min()
            high_max = df['high'].rolling(window=14).max()
            df['stoch_k'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
            df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
            
            # ATR (Average True Range)
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            true_range = np.maximum(high_low, np.maximum(high_close, low_close))
            df['atr'] = true_range.rolling(window=14).mean()
            
            # Volume indicators
            df['volume_sma'] = df['volume'].rolling(window=20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            return df
            
        except Exception as e:
            logger.error(f"Technical indicators error: {str(e)}")
            return df
    
    def _add_market_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market microstructure features"""
        try:
            # Price changes
            df['price_change'] = df['close'].pct_change()
            df['price_change_abs'] = df['price_change'].abs()
            
            # Volatility
            df['volatility'] = df['price_change'].rolling(window=20).std()
            df['volatility_annualized'] = df['volatility'] * np.sqrt(252)
            
            # Momentum
            df['momentum_5'] = df['close'] / df['close'].shift(5) - 1
            df['momentum_20'] = df['close'] / df['close'].shift(20) - 1
            df['momentum_50'] = df['close'] / df['close'].shift(50) - 1
            
            # Trend strength
            df['trend_strength'] = abs(df['sma_20'] - df['sma_50']) / df['sma_50']
            
            # Support and resistance
            df['support'] = df['low'].rolling(window=20).min()
            df['resistance'] = df['high'].rolling(window=20).max()
            df['support_distance'] = (df['close'] - df['support']) / df['close']
            df['resistance_distance'] = (df['resistance'] - df['close']) / df['close']
            
            # Volume-price relationship
            df['volume_price_trend'] = (df['volume'] * df['price_change']).rolling(window=20).sum()
            
            return df
            
        except Exception as e:
            logger.error(f"Market features error: {str(e)}")
            return df
    
    def _add_sentiment_features(self, df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """Add sentiment features"""
        try:
            # Placeholder: in production, get real sentiment data
            # For now, simulate sentiment based on price action
            
            # Sentiment based on RSI
            df['sentiment_rsi'] = np.where(df['rsi'] > 70, -1, np.where(df['rsi'] < 30, 1, 0))
            
            # Sentiment based on price momentum
            df['sentiment_momentum'] = np.where(df['momentum_20'] > 0.05, 1, np.where(df['momentum_20'] < -0.05, -1, 0))
            
            # Sentiment based on volume
            df['sentiment_volume'] = np.where(df['volume_ratio'] > 1.5, 1, np.where(df['volume_ratio'] < 0.5, -1, 0))
            
            # Combined sentiment score
            df['sentiment_score'] = (df['sentiment_rsi'] + df['sentiment_momentum'] + df['sentiment_volume']) / 3
            
            return df
            
        except Exception as e:
            logger.error(f"Sentiment features error: {str(e)}")
            return df
    
    def _add_economic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add economic features"""
        try:
            # Placeholder: in production, get real economic data
            # For now, add time-based economic features
            
            # Day of week
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Month
            df['month'] = df['timestamp'].dt.month
            
            # Quarter
            df['quarter'] = df['timestamp'].dt.quarter
            
            # Year
            df['year'] = df['timestamp'].dt.year
            
            # Economic calendar events (simulated)
            df['fed_meeting'] = np.where(df['day_of_week'] == 2, 1, 0)  # Tuesday
            df['nfp_day'] = np.where((df['day_of_week'] == 4) & (df['timestamp'].dt.day <= 7), 1, 0)  # First Friday
            
            return df
            
        except Exception as e:
            logger.error(f"Economic features error: {str(e)}")
            return df
    
    def _clean_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare features for ML"""
        try:
            # Remove rows with NaN values
            df = df.dropna()
            
            # Remove infinite values
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.dropna()
            
            # Remove constant features
            constant_features = []
            for col in df.columns:
                if df[col].nunique() <= 1:
                    constant_features.append(col)
            
            df = df.drop(columns=constant_features)
            
            # Remove highly correlated features
            correlation_matrix = df.corr().abs()
            upper_triangle = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool))
            high_correlation_features = [column for column in upper_triangle.columns if any(upper_triangle[column] > 0.95)]
            df = df.drop(columns=high_correlation_features)
            
            # Reset index
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Feature cleaning error: {str(e)}")
            return df
    
    async def _get_historical_data(self, symbol: str, lookback_days: int) -> List[Dict[str, Any]]:
        """Get historical data from database"""
        try:
            if self.databases["local"]:
                conn = self.databases["local"]
                cursor = conn.cursor()
                
                # Get data from last N days
                start_date = (datetime.now() - timedelta(days=lookback_days)).isoformat()
                
                cursor.execute("""
                    SELECT timestamp, symbol, open, high, low, close, volume, source
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
                        "volume": row[6],
                        "source": row[7]
                    })
                
                return data
            
            return []
            
        except Exception as e:
            logger.error(f"Historical data retrieval error: {str(e)}")
            return []
    
    async def get_data_quality_report(self) -> Dict[str, Any]:
        """Generate data quality report"""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "overall_score": 0.0,
                "metrics": {},
                "issues": [],
                "recommendations": []
            }
            
            # Check data completeness
            completeness_score = await self._check_data_completeness()
            report["metrics"]["completeness"] = completeness_score
            
            # Check data accuracy
            accuracy_score = await self._check_data_accuracy()
            report["metrics"]["accuracy"] = accuracy_score
            
            # Check data consistency
            consistency_score = await self._check_data_consistency()
            report["metrics"]["consistency"] = consistency_score
            
            # Check data timeliness
            timeliness_score = await self._check_data_timeliness()
            report["metrics"]["timeliness"] = timeliness_score
            
            # Calculate overall score
            report["overall_score"] = np.mean([
                completeness_score, accuracy_score, consistency_score, timeliness_score
            ])
            
            # Generate recommendations
            report["recommendations"] = self._generate_data_quality_recommendations(report["metrics"])
            
            return report
            
        except Exception as e:
            logger.error(f"Data quality report error: {str(e)}")
            return {"error": f"Report generation failed: {str(e)}"}
    
    async def _check_data_completeness(self) -> float:
        """Check data completeness"""
        try:
            if not self.databases["local"]:
                return 0.0
            
            conn = self.databases["local"]
            cursor = conn.cursor()
            
            # Check OHLCV data completeness
            cursor.execute("SELECT COUNT(*) FROM ohlcv")
            total_records = cursor.fetchone()[0]
            
            if total_records == 0:
                return 0.0
            
            # Check for missing data points
            cursor.execute("""
                SELECT COUNT(*) FROM ohlcv 
                WHERE open IS NULL OR high IS NULL OR low IS NULL OR close IS NULL OR volume IS NULL
            """)
            missing_records = cursor.fetchone()[0]
            
            completeness = 1 - (missing_records / total_records)
            return max(0.0, min(1.0, completeness))
            
        except Exception as e:
            logger.error(f"Data completeness check error: {str(e)}")
            return 0.0
    
    async def _check_data_accuracy(self) -> float:
        """Check data accuracy"""
        try:
            if not self.databases["local"]:
                return 0.0
            
            conn = self.databases["local"]
            cursor = conn.cursor()
            
            # Check for price anomalies
            cursor.execute("""
                SELECT COUNT(*) FROM ohlcv 
                WHERE close <= 0 OR high < low OR open < 0 OR high < 0 OR low < 0
            """)
            anomaly_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ohlcv")
            total_records = cursor.fetchone()[0]
            
            if total_records == 0:
                return 0.0
            
            accuracy = 1 - (anomaly_records / total_records)
            return max(0.0, min(1.0, accuracy))
            
        except Exception as e:
            logger.error(f"Data accuracy check error: {str(e)}")
            return 0.0
    
    async def _check_data_consistency(self) -> float:
        """Check data consistency"""
        try:
            if not self.databases["local"]:
                return 0.0
            
            conn = self.databases["local"]
            cursor = conn.cursor()
            
            # Check for timestamp consistency
            cursor.execute("""
                SELECT COUNT(*) FROM ohlcv 
                WHERE timestamp IS NULL OR timestamp = ''
            """)
            invalid_timestamps = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ohlcv")
            total_records = cursor.fetchone()[0]
            
            if total_records == 0:
                return 0.0
            
            consistency = 1 - (invalid_timestamps / total_records)
            return max(0.0, min(1.0, consistency))
            
        except Exception as e:
            logger.error(f"Data consistency check error: {str(e)}")
            return 0.0
    
    async def _check_data_timeliness(self) -> float:
        """Check data timeliness"""
        try:
            if not self.databases["local"]:
                return 0.0
            
            conn = self.databases["local"]
            cursor = conn.cursor()
            
            # Check if we have recent data
            cursor.execute("SELECT MAX(timestamp) FROM ohlcv")
            latest_timestamp = cursor.fetchone()[0]
            
            if not latest_timestamp:
                return 0.0
            
            # Calculate time difference
            latest_dt = datetime.fromisoformat(latest_timestamp.replace('Z', '+00:00'))
            time_diff = datetime.now(latest_dt.tzinfo) - latest_dt
            
            # Score based on recency (within 1 hour = 1.0, within 24 hours = 0.5, >24 hours = 0.0)
            if time_diff.total_seconds() <= 3600:  # 1 hour
                timeliness = 1.0
            elif time_diff.total_seconds() <= 86400:  # 24 hours
                timeliness = 0.5
            else:
                timeliness = 0.0
            
            return timeliness
            
        except Exception as e:
            logger.error(f"Data timeliness check error: {str(e)}")
            return 0.0
    
    def _generate_data_quality_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations based on data quality metrics"""
        recommendations = []
        
        if metrics.get("completeness", 0) < 0.9:
            recommendations.append("Increase data collection frequency to improve completeness")
        
        if metrics.get("accuracy", 0) < 0.95:
            recommendations.append("Implement data validation rules to improve accuracy")
        
        if metrics.get("consistency", 0) < 0.9:
            recommendations.append("Add data consistency checks to improve reliability")
        
        if metrics.get("timeliness", 0) < 0.8:
            recommendations.append("Optimize data pipeline to improve real-time data delivery")
        
        if not recommendations:
            recommendations.append("Data quality is excellent - maintain current standards")
        
        return recommendations
    
    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get current infrastructure status"""
        return {
            "databases": {
                name: "Connected" if conn else "Not Connected" 
                for name, conn in self.databases.items()
            },
            "data_sources": self.data_sources,
            "ml_infrastructure": self.ml_infrastructure,
            "data_quality": self.data_quality
        }


# Global comprehensive data infrastructure instance
comprehensive_data_infrastructure = ComprehensiveDataInfrastructure()
