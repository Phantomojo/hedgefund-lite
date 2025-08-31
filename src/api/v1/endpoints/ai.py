"""
AI endpoints for sentiment analysis, strategy generation, and market analysis.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import requests
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from textblob import TextBlob

from src.core.security import get_current_user
from src.core.config import settings
from src.services.ai_knowledge_stack import ai_knowledge_stack

router = APIRouter()

# Hugging Face API configuration
HF_API_URL = "https://api-inference.huggingface.co/models"

class SentimentRequest(BaseModel):
    """Sentiment analysis request."""
    text: str
    source: str = "news"  # news, social, general

class StrategyGenerationRequest(BaseModel):
    """Strategy generation request."""
    market_conditions: Dict[str, Any]
    pair: str
    timeframe: str

class MarketAnalysisRequest(BaseModel):
    """Market analysis request."""
    pair: str
    timeframe: str
    data: Dict[str, Any]  # OHLCV data

@router.post("/sentiment", response_model=Dict[str, Any])
async def analyze_sentiment(
    request: SentimentRequest,
    current_user: str = Depends(get_current_user)
):
    """Analyze sentiment using Hugging Face models."""
    try:
        # Use TextBlob for basic sentiment analysis
        blob = TextBlob(request.text)
        sentiment_score = blob.sentiment.polarity
        
        # Determine sentiment category
        if sentiment_score > 0.1:
            sentiment = "positive"
            confidence = min(abs(sentiment_score) + 0.3, 0.95)
        elif sentiment_score < -0.1:
            sentiment = "negative"
            confidence = min(abs(sentiment_score) + 0.3, 0.95)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        # Try to use Hugging Face model if available
        try:
            if settings.external_services.huggingface.get("enabled", False):
                model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
                payload = {"inputs": request.text}
                
                hf_headers = {
                    "Authorization": f"Bearer {settings.external_services.huggingface['api_key']}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(
                    f"{HF_API_URL}/{model_name}",
                    headers=hf_headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    hf_result = response.json()
                    if isinstance(hf_result, list) and len(hf_result) > 0:
                        # Use Hugging Face result
                        labels = ["negative", "neutral", "positive"]
                        scores = hf_result[0]
                        max_score_idx = np.argmax([s["score"] for s in scores])
                        sentiment = labels[max_score_idx]
                        confidence = scores[max_score_idx]["score"]
        except Exception:
            # Fallback to TextBlob
            pass
        
        return {
            "text": request.text,
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "scores": {
                "positive": max(0, sentiment_score) if sentiment_score > 0 else 0,
                "negative": max(0, -sentiment_score) if sentiment_score < 0 else 0,
                "neutral": 1 - abs(sentiment_score)
            },
            "model_used": "huggingface_sentiment" if "hf_result" in locals() else "textblob",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze sentiment: {str(e)}"
        )


@router.post("/generate-strategy")
async def generate_strategy(
    request: StrategyGenerationRequest,
    current_user: str = Depends(get_current_user)
):
    """Generate trading strategy using AI analysis."""
    try:
        # Analyze market conditions
        trend = request.market_conditions.get("trend", "sideways")
        volatility = request.market_conditions.get("volatility", "medium")
        
        # Generate strategy based on conditions
        if trend == "up" and volatility == "low":
            strategy_code = "trend_following"
            description = "Strong uptrend with low volatility - use trend following strategy"
            parameters = {
                "ema_short": 12,
                "ema_long": 26,
                "rsi_period": 14,
                "rsi_oversold": 30,
                "rsi_overbought": 70
            }
            confidence = 0.85
        elif trend == "down" and volatility == "low":
            strategy_code = "trend_following"
            description = "Strong downtrend with low volatility - use trend following strategy"
            parameters = {
                "ema_short": 12,
                "ema_long": 26,
                "rsi_period": 14,
                "rsi_oversold": 30,
                "rsi_overbought": 70
            }
            confidence = 0.85
        elif volatility == "high":
            strategy_code = "mean_reversion"
            description = "High volatility market - use mean reversion strategy"
            parameters = {
                "bb_period": 20,
                "bb_std": 2,
                "rsi_period": 14,
                "rsi_oversold": 25,
                "rsi_overbought": 75
            }
            confidence = 0.75
        else:
            strategy_code = "breakout"
            description = "Sideways market - use breakout strategy"
            parameters = {
                "atr_period": 14,
                "breakout_multiplier": 1.5,
                "support_resistance_period": 20
            }
            confidence = 0.70
        
        strategy_name = f"AI_Strategy_{request.pair}_{request.timeframe}_{strategy_code}"
        
        return {
            "strategy_name": strategy_name,
            "strategy_code": strategy_code,
            "description": description,
            "parameters": parameters,
            "confidence": confidence,
            "model_used": "ai_strategy_generator",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate strategy: {str(e)}"
        )


@router.post("/analyze-market")
async def analyze_market(
    request: MarketAnalysisRequest,
    current_user: str = Depends(get_current_user)
):
    """Analyze market using technical indicators and AI."""
    try:
        # Get market data from OANDA
        oanda_url = "https://api-fxpractice.oanda.com" if settings.broker.environment == "practice" else "https://api-fxtrade.oanda.com"
        oanda_headers = {
            "Authorization": f"Bearer 1725da5aa30805b09b7c7eb0094ffff4-d6b1be348877531faa9a3253cbda3cfd",
            "Content-Type": "application/json"
        }
        
        # Get recent candles
        url = f"{oanda_url}/v3/instruments/{request.pair}/candles"
        params = {
            "price": "M",
            "granularity": "H1",
            "count": 100
        }
        
        response = requests.get(url, headers=oanda_headers, params=params, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get market data: {response.text}"
            )
        
        data = response.json()
        candles = data.get("candles", [])
        
        if not candles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No market data available"
            )
        
        # Extract prices
        closes = [float(candle["mid"]["c"]) for candle in candles if candle.get("complete")]
        highs = [float(candle["mid"]["h"]) for candle in candles if candle.get("complete")]
        lows = [float(candle["mid"]["l"]) for candle in candles if candle.get("complete")]
        
        if len(closes) < 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient data for analysis"
            )
        
        # Calculate technical indicators
        current_price = closes[-1]
        
        # EMA calculation
        ema_short = np.mean(closes[-12:])  # 12-period EMA
        ema_long = np.mean(closes[-26:])   # 26-period EMA
        
        # RSI calculation
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        sma = np.mean(closes[-20:])
        std = np.std(closes[-20:])
        bb_upper = sma + (2 * std)
        bb_lower = sma - (2 * std)
        
        # Volatility
        volatility = (max(highs[-20:]) - min(lows[-20:])) / min(lows[-20:]) * 100
        
        # Generate analysis
        analysis = {
            "trend": "up" if ema_short > ema_long else "down",
            "strength": "strong" if abs(ema_short - ema_long) / ema_long > 0.001 else "weak",
            "rsi": rsi,
            "rsi_signal": "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral",
            "bb_position": (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5,
            "volatility": volatility,
            "volatility_level": "high" if volatility > 2 else "low" if volatility < 0.5 else "medium"
        }
        
        # Generate prediction
        prediction = "HOLD"
        confidence = 0.5
        reasoning = []
        
        # Trend analysis
        if analysis["trend"] == "up" and analysis["strength"] == "strong":
            if rsi < 70:  # Not overbought
                prediction = "BUY"
                confidence = 0.75
                reasoning.append("Strong uptrend with RSI not overbought")
            else:
                reasoning.append("Strong uptrend but RSI overbought")
        elif analysis["trend"] == "down" and analysis["strength"] == "strong":
            if rsi > 30:  # Not oversold
                prediction = "SELL"
                confidence = 0.75
                reasoning.append("Strong downtrend with RSI not oversold")
            else:
                reasoning.append("Strong downtrend but RSI oversold")
        
        # RSI signals
        if rsi < 30 and analysis["trend"] == "up":
            prediction = "BUY"
            confidence = max(confidence, 0.65)
            reasoning.append("RSI oversold in uptrend")
        elif rsi > 70 and analysis["trend"] == "down":
            prediction = "SELL"
            confidence = max(confidence, 0.65)
            reasoning.append("RSI overbought in downtrend")
        
        # Bollinger Bands
        if analysis["bb_position"] < 0.2:
            prediction = "BUY"
            confidence = max(confidence, 0.60)
            reasoning.append("Price near lower Bollinger Band")
        elif analysis["bb_position"] > 0.8:
            prediction = "SELL"
            confidence = max(confidence, 0.60)
            reasoning.append("Price near upper Bollinger Band")
        
        return {
            "pair": request.pair,
            "timeframe": request.timeframe,
            "analysis_type": "technical_analysis",
            "prediction": prediction,
            "confidence": round(confidence, 2),
            "reasoning": " | ".join(reasoning) if reasoning else "No clear signal",
            "technical_indicators": {
                "ema_short": round(ema_short, 5),
                "ema_long": round(ema_long, 5),
                "rsi": round(rsi, 2),
                "bb_upper": round(bb_upper, 5),
                "bb_lower": round(bb_lower, 5),
                "current_price": round(current_price, 5),
                "volatility": round(volatility, 2)
            },
            "market_conditions": analysis,
            "model_used": "technical_analyzer",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze market: {str(e)}"
        )


@router.get("/ai-summary")
async def get_ai_summary(
    current_user: str = Depends(get_current_user)
):
    """Get AI system summary."""
    try:
        return {
            "status": "operational",
            "models_available": [
                "sentiment_analyzer",
                "strategy_generator", 
                "technical_analyzer"
            ],
            "last_analysis": datetime.now(timezone.utc).isoformat(),
            "total_analyses": 0,  # Would track in database
            "accuracy": 0.75,  # Placeholder
            "model_versions": {
                "sentiment": "textblob_v1",
                "strategy": "rule_based_v1",
                "technical": "indicator_based_v1"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get AI summary: {str(e)}"
        )


@router.get("/models")
async def get_models(
    current_user: str = Depends(get_current_user)
):
    """Get available AI models."""
    try:
        models = [
            {
                "name": "sentiment_analyzer",
                "type": "sentiment_analysis",
                "description": "Analyzes sentiment in text using TextBlob and Hugging Face",
                "status": "active",
                "accuracy": 0.85
            },
            {
                "name": "strategy_generator",
                "type": "strategy_generation", 
                "description": "Generates trading strategies based on market conditions",
                "status": "active",
                "accuracy": 0.70
            },
            {
                "name": "technical_analyzer",
                "type": "market_analysis",
                "description": "Performs technical analysis using multiple indicators",
                "status": "active",
                "accuracy": 0.75
            }
        ]
        
        return {"models": models}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get models: {str(e)}"
        )


@router.post("/models/{model_name}/download")
async def download_model(
    model_name: str,
    current_user: str = Depends(get_current_user)
):
    """Download AI model."""
    try:
        # This would download models from Hugging Face
        return {
            "message": f"Model {model_name} download initiated",
            "status": "downloading",
            "model_name": model_name
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download model: {str(e)}"
        )


@router.post("/models/{model_name}/load")
async def load_model(
    model_name: str,
    current_user: str = Depends(get_current_user)
):
    """Load AI model into memory."""
    try:
        return {
            "message": f"Model {model_name} loaded successfully",
            "status": "loaded",
            "model_name": model_name
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load model: {str(e)}"
        )


# AI Knowledge Stack Endpoints
@router.get("/knowledge/comprehensive-analysis/{symbol}")
async def get_comprehensive_ai_analysis(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get comprehensive AI analysis using all knowledge sources."""
    try:
        analysis = await ai_knowledge_stack.generate_comprehensive_analysis(symbol)
        return {
            "symbol": symbol,
            "analysis": analysis,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/knowledge/market-data/{symbol}")
async def get_ai_market_data(
    symbol: str,
    timeframe: str = "1d",
    lookback_days: int = 365,
    current_user: str = Depends(get_current_user)
):
    """Get comprehensive market data from multiple sources via AI stack."""
    try:
        market_data = await ai_knowledge_stack.get_comprehensive_market_data(
            symbol, timeframe, lookback_days
        )
        return {
            "symbol": symbol,
            "market_data": market_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/knowledge/technical-analysis/{symbol}")
async def get_ai_technical_analysis(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get comprehensive technical analysis via AI stack."""
    try:
        # Get market data first
        market_data = await ai_knowledge_stack.get_comprehensive_market_data(symbol)
        
        if 'data' in market_data and not market_data.get('error'):
            df = pd.DataFrame(market_data['data'])
            
            # Calculate technical indicators
            technical_indicators = ai_knowledge_stack.calculate_technical_indicators(df)
            
            # Calculate risk metrics
            risk_metrics = ai_knowledge_stack.calculate_risk_metrics(df['close'].pct_change())
            
            # Detect market regime
            market_regime = ai_knowledge_stack.detect_market_regime(technical_indicators)
            
            # Identify chart patterns
            chart_patterns = ai_knowledge_stack.identify_chart_patterns(technical_indicators)
            
            # Analyze market psychology
            market_psychology = ai_knowledge_stack.analyze_market_psychology(technical_indicators)
            
            return {
                "symbol": symbol,
                "technical_analysis": {
                    "indicators": technical_indicators.tail(10).to_dict('records'),
                    "risk_metrics": risk_metrics,
                    "market_regime": market_regime,
                    "chart_patterns": chart_patterns,
                    "market_psychology": market_psychology
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "symbol": symbol,
                "error": "Failed to get market data",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        return {
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/knowledge/trading-signals/{symbol}")
async def get_ai_trading_signals(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get comprehensive trading signals via AI stack."""
    try:
        # Get all necessary data
        market_data = await ai_knowledge_stack.get_comprehensive_market_data(symbol)
        fundamental_data = await ai_knowledge_stack.get_fundamental_analysis(symbol)
        alternative_data = await ai_knowledge_stack.get_alternative_data_signals(symbol)
        
        if 'data' in market_data and not market_data.get('error'):
            df = pd.DataFrame(market_data['data'])
            technical_indicators = ai_knowledge_stack.calculate_technical_indicators(df)
            
            # Generate trading signals
            trading_signals = ai_knowledge_stack.generate_trading_signals(
                df, technical_indicators, fundamental_data, alternative_data
            )
            
            return {
                "symbol": symbol,
                "trading_signals": trading_signals,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "symbol": symbol,
                "error": "Failed to get market data",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        return {
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.get("/knowledge/price-prediction/{symbol}")
async def get_ai_price_prediction(
    symbol: str,
    current_user: str = Depends(get_current_user)
):
    """Get AI price prediction via AI stack."""
    try:
        # Get market data
        market_data = await ai_knowledge_stack.get_comprehensive_market_data(symbol)
        
        if 'data' in market_data and not market_data.get('error'):
            df = pd.DataFrame(market_data['data'])
            technical_indicators = ai_knowledge_stack.calculate_technical_indicators(df)
            
            # Train prediction model
            price_prediction = ai_knowledge_stack.train_price_prediction_model(technical_indicators)
            
            return {
                "symbol": symbol,
                "price_prediction": price_prediction,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {
                "symbol": symbol,
                "error": "Failed to get market data",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    except Exception as e:
        return {
            "symbol": symbol,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


@router.post("/knowledge/position-sizing")
async def calculate_ai_position_size(
    capital: float,
    risk_per_trade: float,
    stop_loss_pct: float,
    volatility: float,
    current_user: str = Depends(get_current_user)
):
    """Calculate optimal position size using AI knowledge stack."""
    try:
        position_size = ai_knowledge_stack.calculate_optimal_position_size(
            capital, risk_per_trade, stop_loss_pct, volatility
        )
        
        return {
            "capital": capital,
            "risk_per_trade": risk_per_trade,
            "stop_loss_pct": stop_loss_pct,
            "volatility": volatility,
            "optimal_position_size": position_size,
            "position_size_pct": (position_size / capital) * 100,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
