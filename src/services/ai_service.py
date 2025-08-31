"""
AI Service for the forex trading system.
Integrates GitHub models (Hugging Face) for sentiment analysis, strategy generation, and market analysis.
Inspired by Vanta-ledger's AI architecture.
"""

import asyncio
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import structlog

import pandas as pd
import numpy as np
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    AutoModelForCausalLM,
    pipeline,
    BitsAndBytesConfig
)
import torch
from torch import nn
import requests
from huggingface_hub import hf_hub_download, snapshot_download
import redis

from src.core.config import settings
from src.core.logging import TradingLogger


@dataclass
class AIModel:
    """AI model configuration and metadata."""
    name: str
    model_id: str
    type: str  # "sentiment", "text_generation", "classification", "custom"
    size_gb: float
    priority: int
    local_path: Optional[str] = None
    is_downloaded: bool = False
    last_used: Optional[datetime] = None
    performance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result."""
    text: str
    sentiment: str  # "positive", "negative", "neutral"
    confidence: float
    scores: Dict[str, float]
    model_used: str
    timestamp: datetime


@dataclass
class StrategyGeneration:
    """AI-generated strategy result."""
    strategy_name: str
    strategy_code: str
    description: str
    parameters: Dict[str, Any]
    confidence: float
    model_used: str
    timestamp: datetime


@dataclass
class MarketAnalysis:
    """AI-powered market analysis."""
    pair: str
    timeframe: str
    analysis_type: str  # "trend", "volatility", "regime", "sentiment"
    prediction: str
    confidence: float
    reasoning: str
    model_used: str
    timestamp: datetime


class ModelManager:
    """Manages AI models with dynamic selection and caching."""
    
    def __init__(self):
        self.logger = TradingLogger("model_manager")
        self.models: Dict[str, AIModel] = {}
        self.loaded_models: Dict[str, Any] = {}
        self.redis_client = redis.Redis(
            host=settings.database.redis.host,
            port=settings.database.redis.port,
            db=settings.database.redis.database
        )
        
        # Initialize models from configuration
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize models from configuration."""
        for model_config in settings.ml.models:
            model = AIModel(
                name=model_config["name"],
                model_id=model_config.get("model_id", ""),
                type=model_config.get("type", "text_generation"),
                size_gb=model_config["size_gb"],
                priority=model_config["priority"]
            )
            self.models[model.name] = model
    
    async def download_model(self, model_name: str) -> bool:
        """Download model from Hugging Face Hub."""
        try:
            model = self.models.get(model_name)
            if not model:
                self.logger.logger.error(f"Model {model_name} not found")
                return False
            
            # Create models directory
            os.makedirs(settings.ml.model_dir, exist_ok=True)
            model_path = os.path.join(settings.ml.model_dir, model_name)
            
            # Download model
            self.logger.logger.info(f"Downloading model {model_name} from {model.model_id}")
            
            if model.model_id:
                snapshot_download(
                    repo_id=model.model_id,
                    local_dir=model_path,
                    local_dir_use_symlinks=False
                )
            else:
                # Use default model IDs based on name
                default_models = {
                    "TinyLlama": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                    "Phi-3 Mini": "microsoft/Phi-3-mini-4k-instruct",
                    "Mistral 7B": "mistralai/Mistral-7B-Instruct-v0.2"
                }
                
                if model_name in default_models:
                    snapshot_download(
                        repo_id=default_models[model_name],
                        local_dir=model_path,
                        local_dir_use_symlinks=False
                    )
            
            model.local_path = model_path
            model.is_downloaded = True
            self.logger.logger.info(f"Model {model_name} downloaded successfully")
            return True
            
        except Exception as e:
            self.logger.logger.error(f"Failed to download model {model_name}: {str(e)}")
            return False
    
    async def load_model(self, model_name: str) -> Optional[Any]:
        """Load model into memory."""
        try:
            if model_name in self.loaded_models:
                return self.loaded_models[model_name]
            
            model = self.models.get(model_name)
            if not model or not model.is_downloaded:
                success = await self.download_model(model_name)
                if not success:
                    return None
            
            # Load model based on type
            if model.type == "sentiment":
                loaded_model = self._load_sentiment_model(model)
            elif model.type == "text_generation":
                loaded_model = self._load_text_generation_model(model)
            else:
                loaded_model = self._load_generic_model(model)
            
            if loaded_model:
                self.loaded_models[model_name] = loaded_model
                model.last_used = datetime.utcnow()
                self.logger.logger.info(f"Model {model_name} loaded successfully")
            
            return loaded_model
            
        except Exception as e:
            self.logger.logger.error(f"Failed to load model {model_name}: {str(e)}")
            return None
    
    def _load_sentiment_model(self, model: AIModel) -> Any:
        """Load sentiment analysis model."""
        try:
            tokenizer = AutoTokenizer.from_pretrained(model.local_path)
            model_obj = AutoModelForSequenceClassification.from_pretrained(model.local_path)
            
            return pipeline(
                "sentiment-analysis",
                model=model_obj,
                tokenizer=tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
        except Exception as e:
            self.logger.logger.error(f"Failed to load sentiment model: {str(e)}")
            return None
    
    def _load_text_generation_model(self, model: AIModel) -> Any:
        """Load text generation model."""
        try:
            # Use 4-bit quantization for memory efficiency
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16
            )
            
            tokenizer = AutoTokenizer.from_pretrained(model.local_path)
            model_obj = AutoModelForCausalLM.from_pretrained(
                model.local_path,
                quantization_config=bnb_config,
                device_map="auto"
            )
            
            return {
                "tokenizer": tokenizer,
                "model": model_obj
            }
        except Exception as e:
            self.logger.logger.error(f"Failed to load text generation model: {str(e)}")
            return None
    
    def _load_generic_model(self, model: AIModel) -> Any:
        """Load generic model."""
        try:
            tokenizer = AutoTokenizer.from_pretrained(model.local_path)
            model_obj = AutoModelForCausalLM.from_pretrained(model.local_path)
            
            return {
                "tokenizer": tokenizer,
                "model": model_obj
            }
        except Exception as e:
            self.logger.logger.error(f"Failed to load generic model: {str(e)}")
            return None
    
    def select_best_model(self, task_type: str, available_memory_gb: float) -> Optional[str]:
        """Select the best model based on task and available resources."""
        try:
            suitable_models = []
            
            for model_name, model in self.models.items():
                if model.type == task_type and model.size_gb <= available_memory_gb:
                    suitable_models.append((model_name, model))
            
            if not suitable_models:
                return None
            
            # Sort by priority and performance score
            suitable_models.sort(
                key=lambda x: (x[1].priority, x[1].performance_score),
                reverse=True
            )
            
            return suitable_models[0][0]
            
        except Exception as e:
            self.logger.logger.error(f"Failed to select best model: {str(e)}")
            return None
    
    def get_available_memory(self) -> float:
        """Get available GPU/CPU memory in GB."""
        try:
            if torch.cuda.is_available():
                return torch.cuda.get_device_properties(0).total_memory / (1024**3)
            else:
                # Estimate CPU memory (conservative)
                import psutil
                return psutil.virtual_memory().available / (1024**3) * 0.5
        except Exception:
            return 4.0  # Default fallback


class AIService:
    """Comprehensive AI service for the trading system."""
    
    def __init__(self):
        self.logger = TradingLogger("ai_service")
        self.model_manager = ModelManager()
        self.is_running = False
        
        # Cache for analysis results
        self.analysis_cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hour
    
    async def start(self):
        """Start the AI service."""
        self.is_running = True
        self.logger.logger.info("AI service started")
        
        # Preload priority models
        await self._preload_models()
    
    async def stop(self):
        """Stop the AI service."""
        self.is_running = False
        self.logger.logger.info("AI service stopped")
    
    async def _preload_models(self):
        """Preload high-priority models."""
        try:
            available_memory = self.model_manager.get_available_memory()
            
            # Load sentiment model first
            sentiment_model = self.model_manager.select_best_model("sentiment", available_memory)
            if sentiment_model:
                await self.model_manager.load_model(sentiment_model)
            
            # Load text generation model if memory allows
            remaining_memory = available_memory - 1.0  # Reserve 1GB
            if remaining_memory > 2.0:
                text_model = self.model_manager.select_best_model("text_generation", remaining_memory)
                if text_model:
                    await self.model_manager.load_model(text_model)
                    
        except Exception as e:
            self.logger.logger.error(f"Failed to preload models: {str(e)}")
    
    async def analyze_sentiment(self, text: str, source: str = "news") -> SentimentAnalysis:
        """Analyze sentiment of text using AI models."""
        try:
            # Check cache first
            cache_key = f"sentiment:{hashlib.md5(text.encode()).hexdigest()}"
            cached_result = self.analysis_cache.get(cache_key)
            if cached_result:
                return SentimentAnalysis(**cached_result)
            
            # Select best sentiment model
            available_memory = self.model_manager.get_available_memory()
            model_name = self.model_manager.select_best_model("sentiment", available_memory)
            
            if not model_name:
                # Fallback to simple rule-based sentiment
                return self._fallback_sentiment_analysis(text, source)
            
            # Load and use model
            model = await self.model_manager.load_model(model_name)
            if not model:
                return self._fallback_sentiment_analysis(text, source)
            
            # Analyze sentiment
            result = model(text[:512])  # Limit text length
            
            sentiment = SentimentAnalysis(
                text=text,
                sentiment=result[0]["label"].lower(),
                confidence=result[0]["score"],
                scores={
                    "positive": result[0]["score"] if result[0]["label"] == "POSITIVE" else 1 - result[0]["score"],
                    "negative": result[0]["score"] if result[0]["label"] == "NEGATIVE" else 1 - result[0]["score"],
                    "neutral": result[0]["score"] if result[0]["label"] == "NEUTRAL" else 1 - result[0]["score"]
                },
                model_used=model_name,
                timestamp=datetime.utcnow()
            )
            
            # Cache result
            self.analysis_cache[cache_key] = sentiment.__dict__
            
            return sentiment
            
        except Exception as e:
            self.logger.logger.error(f"Failed to analyze sentiment: {str(e)}")
            return self._fallback_sentiment_analysis(text, source)
    
    def _fallback_sentiment_analysis(self, text: str, source: str) -> SentimentAnalysis:
        """Fallback sentiment analysis using simple rules."""
        try:
            from textblob import TextBlob
            
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                sentiment = "positive"
                confidence = min(abs(polarity), 0.9)
            elif polarity < -0.1:
                sentiment = "negative"
                confidence = min(abs(polarity), 0.9)
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            return SentimentAnalysis(
                text=text,
                sentiment=sentiment,
                confidence=confidence,
                scores={
                    "positive": max(0, polarity),
                    "negative": max(0, -polarity),
                    "neutral": 1 - abs(polarity)
                },
                model_used="textblob_fallback",
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.logger.error(f"Fallback sentiment analysis failed: {str(e)}")
            return SentimentAnalysis(
                text=text,
                sentiment="neutral",
                confidence=0.5,
                scores={"positive": 0.33, "negative": 0.33, "neutral": 0.34},
                model_used="default",
                timestamp=datetime.utcnow()
            )
    
    async def generate_strategy(self, market_conditions: Dict[str, Any]) -> StrategyGeneration:
        """Generate trading strategy using AI models."""
        try:
            # Select best text generation model
            available_memory = self.model_manager.get_available_memory()
            model_name = self.model_manager.select_best_model("text_generation", available_memory)
            
            if not model_name:
                return self._fallback_strategy_generation(market_conditions)
            
            # Load model
            model_data = await self.model_manager.load_model(model_name)
            if not model_data:
                return self._fallback_strategy_generation(market_conditions)
            
            # Create prompt for strategy generation
            prompt = self._create_strategy_prompt(market_conditions)
            
            # Generate strategy
            tokenizer = model_data["tokenizer"]
            model = model_data["model"]
            
            inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=1024,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Parse generated strategy
            strategy = self._parse_generated_strategy(generated_text, market_conditions)
            
            return StrategyGeneration(
                strategy_name=f"ai_generated_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                strategy_code=strategy["code"],
                description=strategy["description"],
                parameters=strategy["parameters"],
                confidence=strategy["confidence"],
                model_used=model_name,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            self.logger.logger.error(f"Failed to generate strategy: {str(e)}")
            return self._fallback_strategy_generation(market_conditions)
    
    def _create_strategy_prompt(self, market_conditions: Dict[str, Any]) -> str:
        """Create prompt for strategy generation."""
        return f"""
        Generate a forex trading strategy based on the following market conditions:
        
        Market Conditions:
        - Trend: {market_conditions.get('trend', 'unknown')}
        - Volatility: {market_conditions.get('volatility', 'unknown')}
        - Timeframe: {market_conditions.get('timeframe', '1h')}
        - Currency Pair: {market_conditions.get('pair', 'EURUSD')}
        
        Requirements:
        1. Create a Python strategy class
        2. Include technical indicators
        3. Define entry and exit conditions
        4. Include risk management parameters
        5. Make it suitable for automated trading
        
        Strategy Code:
        """
    
    def _parse_generated_strategy(self, generated_text: str, market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Parse generated strategy text."""
        try:
            # Extract code block
            if "```python" in generated_text:
                code_start = generated_text.find("```python") + 9
                code_end = generated_text.find("```", code_start)
                code = generated_text[code_start:code_end].strip()
            else:
                code = generated_text
            
            # Extract description
            description = f"AI-generated strategy for {market_conditions.get('pair', 'EURUSD')} on {market_conditions.get('timeframe', '1h')} timeframe"
            
            # Default parameters
            parameters = {
                "risk_pct": 0.5,
                "max_positions": 3,
                "timeframes": [market_conditions.get('timeframe', '1h')],
                "pairs": [market_conditions.get('pair', 'EURUSD')]
            }
            
            return {
                "code": code,
                "description": description,
                "parameters": parameters,
                "confidence": 0.7
            }
            
        except Exception as e:
            self.logger.logger.error(f"Failed to parse generated strategy: {str(e)}")
            return {
                "code": "# Fallback strategy code",
                "description": "Fallback strategy",
                "parameters": {},
                "confidence": 0.5
            }
    
    def _fallback_strategy_generation(self, market_conditions: Dict[str, Any]) -> StrategyGeneration:
        """Fallback strategy generation."""
        return StrategyGeneration(
            strategy_name=f"fallback_strategy_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            strategy_code="# Fallback strategy - basic EMA crossover",
            description="Fallback EMA crossover strategy",
            parameters={
                "risk_pct": 0.5,
                "max_positions": 3,
                "timeframes": [market_conditions.get('timeframe', '1h')],
                "pairs": [market_conditions.get('pair', 'EURUSD')]
            },
            confidence=0.5,
            model_used="fallback",
            timestamp=datetime.utcnow()
        )
    
    async def analyze_market(self, data: pd.DataFrame, pair: str, timeframe: str) -> MarketAnalysis:
        """Analyze market conditions using AI."""
        try:
            # Calculate technical indicators
            indicators = self._calculate_technical_indicators(data)
            
            # Determine market regime
            regime = self._determine_market_regime(indicators)
            
            # Generate analysis
            analysis = MarketAnalysis(
                pair=pair,
                timeframe=timeframe,
                analysis_type="regime",
                prediction=regime["prediction"],
                confidence=regime["confidence"],
                reasoning=regime["reasoning"],
                model_used="technical_analysis",
                timestamp=datetime.utcnow()
            )
            
            return analysis
            
        except Exception as e:
            self.logger.logger.error(f"Failed to analyze market: {str(e)}")
            return MarketAnalysis(
                pair=pair,
                timeframe=timeframe,
                analysis_type="regime",
                prediction="unknown",
                confidence=0.5,
                reasoning="Analysis failed",
                model_used="fallback",
                timestamp=datetime.utcnow()
            )
    
    def _calculate_technical_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate technical indicators for analysis."""
        try:
            import talib
            
            indicators = {}
            
            # Moving averages
            indicators["sma_20"] = talib.SMA(data['close'], timeperiod=20).iloc[-1]
            indicators["sma_50"] = talib.SMA(data['close'], timeperiod=50).iloc[-1]
            indicators["ema_12"] = talib.EMA(data['close'], timeperiod=12).iloc[-1]
            indicators["ema_26"] = talib.EMA(data['close'], timeperiod=26).iloc[-1]
            
            # RSI
            indicators["rsi"] = talib.RSI(data['close'], timeperiod=14).iloc[-1]
            
            # MACD
            macd, macd_signal, macd_hist = talib.MACD(data['close'])
            indicators["macd"] = macd.iloc[-1]
            indicators["macd_signal"] = macd_signal.iloc[-1]
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(data['close'])
            indicators["bb_upper"] = bb_upper.iloc[-1]
            indicators["bb_middle"] = bb_middle.iloc[-1]
            indicators["bb_lower"] = bb_lower.iloc[-1]
            
            # ATR for volatility
            indicators["atr"] = talib.ATR(data['high'], data['low'], data['close'], timeperiod=14).iloc[-1]
            
            return indicators
            
        except Exception as e:
            self.logger.logger.error(f"Failed to calculate indicators: {str(e)}")
            return {}
    
    def _determine_market_regime(self, indicators: Dict[str, float]) -> Dict[str, Any]:
        """Determine market regime based on indicators."""
        try:
            current_price = indicators.get("sma_20", 0)
            sma_20 = indicators.get("sma_20", 0)
            sma_50 = indicators.get("sma_50", 0)
            rsi = indicators.get("rsi", 50)
            macd = indicators.get("macd", 0)
            macd_signal = indicators.get("macd_signal", 0)
            
            # Determine trend
            if sma_20 > sma_50 and macd > macd_signal:
                trend = "bullish"
                confidence = 0.8
            elif sma_20 < sma_50 and macd < macd_signal:
                trend = "bearish"
                confidence = 0.8
            else:
                trend = "sideways"
                confidence = 0.6
            
            # Determine volatility regime
            atr = indicators.get("atr", 0)
            if atr > 0.01:  # High volatility
                volatility = "high"
            elif atr > 0.005:  # Medium volatility
                volatility = "medium"
            else:
                volatility = "low"
            
            # Determine momentum
            if rsi > 70:
                momentum = "overbought"
            elif rsi < 30:
                momentum = "oversold"
            else:
                momentum = "neutral"
            
            reasoning = f"Trend: {trend}, Volatility: {volatility}, Momentum: {momentum}, RSI: {rsi:.2f}"
            
            return {
                "prediction": f"{trend}_{volatility}",
                "confidence": confidence,
                "reasoning": reasoning
            }
            
        except Exception as e:
            self.logger.logger.error(f"Failed to determine market regime: {str(e)}")
            return {
                "prediction": "unknown",
                "confidence": 0.5,
                "reasoning": "Analysis failed"
            }
    
    async def get_ai_summary(self) -> Dict[str, Any]:
        """Get AI service summary."""
        try:
            return {
                "status": "running" if self.is_running else "stopped",
                "models_loaded": len(self.model_manager.loaded_models),
                "total_models": len(self.model_manager.models),
                "cache_size": len(self.analysis_cache),
                "available_memory_gb": self.model_manager.get_available_memory(),
                "last_analysis": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.logger.error(f"Failed to get AI summary: {str(e)}")
            return {"status": "error", "error": str(e)}
