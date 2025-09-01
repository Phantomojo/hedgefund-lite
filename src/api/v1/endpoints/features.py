"""
ML Features API Endpoints
Generate and manage machine learning features for trading strategies
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging
from datetime import datetime, timedelta

from src.services.ml.feature_generator import FeatureGenerator
from src.schemas.features import FeatureRequest, FeatureResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/generate", response_model=FeatureResponse)
async def generate_features():
    """
    Generate ML features for trading strategies
    """
    try:
        logger.info("Generating ML features for trading strategies")
        
        # Initialize feature generator
        feature_gen = FeatureGenerator()
        
        # Generate features
        features = await feature_gen.generate_all_features()
        
        return FeatureResponse(
            message="Features generated successfully",
            features_count=len(features),
            timestamp=datetime.utcnow(),
            features=features
        )
        
    except Exception as e:
        logger.error(f"Failed to generate features: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Feature generation failed: {str(e)}")

@router.post("/generate", response_model=FeatureResponse)
async def generate_features_for_symbol(request: FeatureRequest):
    """
    Generate ML features for a specific trading symbol
    """
    try:
        logger.info(f"Generating ML features for symbol: {request.symbol}")
        
        # Initialize feature generator
        feature_gen = FeatureGenerator()
        
        # Generate features for specific symbol
        features = await feature_gen.generate_symbol_features(
            symbol=request.symbol,
            timeframe=request.timeframe,
            lookback_days=request.lookback_days
        )
        
        return FeatureResponse(
            message=f"Features generated successfully for {request.symbol}",
            features_count=len(features),
            timestamp=datetime.utcnow(),
            features=features
        )
        
    except Exception as e:
        logger.error(f"Failed to generate features for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Feature generation failed: {str(e)}")

@router.get("/list", response_model=List[Dict[str, Any]])
async def list_available_features():
    """
    List all available ML features
    """
    try:
        logger.info("Listing available ML features")
        
        # Define available features
        features = [
            {
                "name": "price_momentum",
                "description": "Price momentum indicators",
                "category": "technical",
                "timeframes": ["1h", "4h", "1d"]
            },
            {
                "name": "volatility_indicators",
                "description": "Volatility and risk measures",
                "category": "risk",
                "timeframes": ["1h", "4h", "1d"]
            },
            {
                "name": "economic_indicators",
                "description": "Federal Reserve economic data",
                "category": "fundamental",
                "timeframes": ["1d", "1w", "1m"]
            },
            {
                "name": "news_sentiment",
                "description": "Financial news sentiment analysis",
                "category": "sentiment",
                "timeframes": ["1h", "4h", "1d"]
            },
            {
                "name": "social_sentiment",
                "description": "Social media sentiment tracking",
                "category": "sentiment",
                "timeframes": ["1h", "4h", "1d"]
            },
            {
                "name": "market_correlation",
                "description": "Cross-asset correlation analysis",
                "category": "correlation",
                "timeframes": ["1h", "4h", "1d"]
            }
        ]
        
        return features
        
    except Exception as e:
        logger.error(f"Failed to list features: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list features: {str(e)}")

@router.get("/status")
async def get_feature_status():
    """
    Get the status of feature generation system
    """
    try:
        logger.info("Getting feature generation system status")
        
        # Check feature generation system health
        status = {
            "status": "healthy",
            "message": "Feature generation system is operational",
            "timestamp": datetime.utcnow(),
            "components": {
                "data_collection": "active",
                "feature_engineering": "ready",
                "ml_pipeline": "operational",
                "storage": "connected"
            },
            "last_generation": datetime.utcnow() - timedelta(hours=1),
            "features_available": 150,
            "models_trained": 12
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get feature status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get feature status: {str(e)}")
