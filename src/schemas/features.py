"""
Feature Schemas
Data models for ML feature generation and management
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class FeatureRequest(BaseModel):
    """Request model for feature generation"""
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL, EUR_USD)")
    timeframe: str = Field(default="1d", description="Timeframe for features (1h, 4h, 1d, 1w)")
    lookback_days: int = Field(default=30, description="Number of days to look back for feature generation")
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "AAPL",
                "timeframe": "1d",
                "lookback_days": 30
            }
        }

class FeatureResponse(BaseModel):
    """Response model for feature generation"""
    message: str = Field(..., description="Status message")
    features_count: int = Field(..., description="Number of features generated")
    timestamp: datetime = Field(..., description="Timestamp of feature generation")
    features: List[Dict[str, Any]] = Field(default=[], description="Generated features")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Features generated successfully",
                "features_count": 150,
                "timestamp": "2024-01-01T00:00:00Z",
                "features": [
                    {
                        "name": "rsi_14",
                        "value": 65.4,
                        "category": "technical",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                ]
            }
        }

class FeatureDefinition(BaseModel):
    """Model for feature definitions"""
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Feature description")
    category: str = Field(..., description="Feature category (technical, fundamental, sentiment)")
    timeframes: List[str] = Field(..., description="Supported timeframes")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Feature parameters")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "rsi_14",
                "description": "Relative Strength Index with 14-period lookback",
                "category": "technical",
                "timeframes": ["1h", "4h", "1d"],
                "parameters": {"period": 14}
            }
        }

class FeatureStatus(BaseModel):
    """Model for feature generation system status"""
    status: str = Field(..., description="System status")
    message: str = Field(..., description="Status message")
    timestamp: datetime = Field(..., description="Status timestamp")
    components: Dict[str, str] = Field(..., description="Component statuses")
    last_generation: datetime = Field(..., description="Last feature generation time")
    features_available: int = Field(..., description="Number of available features")
    models_trained: int = Field(..., description="Number of trained models")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "message": "Feature generation system is operational",
                "timestamp": "2024-01-01T00:00:00Z",
                "components": {
                    "data_collection": "active",
                    "feature_engineering": "ready",
                    "ml_pipeline": "operational"
                },
                "last_generation": "2024-01-01T00:00:00Z",
                "features_available": 150,
                "models_trained": 12
            }
        }
