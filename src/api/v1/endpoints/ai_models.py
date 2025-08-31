"""
AI Model Management Endpoints
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from src.core.security import get_current_user
from src.services.ai_model_manager import ai_model_manager

router = APIRouter()

class ModelDownloadRequest(BaseModel):
    model_name: str

class TextAnalysisRequest(BaseModel):
    text: str
    model_name: str = "finbert"

class TextGenerationRequest(BaseModel):
    prompt: str
    model_name: str = "tinyllama"
    max_length: int = 200

@router.get("/models")
async def get_models(
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get available AI models and their status."""
    try:
        return ai_model_manager.get_model_status()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get models: {str(e)}"
        )

@router.post("/models/download")
async def download_model(
    request: ModelDownloadRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Download an AI model."""
    try:
        # Start download in background
        background_tasks.add_task(
            ai_model_manager.download_model,
            request.model_name
        )
        
        return {
            "message": f"Download started for {request.model_name}",
            "model_name": request.model_name,
            "status": "downloading"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start download: {str(e)}"
        )

@router.post("/models/download-priority")
async def download_priority_models(
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Download priority models for trading."""
    try:
        # Start priority downloads in background
        background_tasks.add_task(
            ai_model_manager.download_priority_models
        )
        
        return {
            "message": "Priority model downloads started",
            "status": "downloading",
            "models": ["finbert", "tinyllama", "news_classifier"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start priority downloads: {str(e)}"
        )

@router.post("/sentiment")
async def analyze_sentiment(
    request: TextAnalysisRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Analyze sentiment of text."""
    try:
        result = ai_model_manager.analyze_sentiment(
            request.text,
            request.model_name
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment analysis failed: {str(e)}"
        )

@router.post("/generate")
async def generate_text(
    request: TextGenerationRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate text using AI model."""
    try:
        result = ai_model_manager.generate_text(
            request.prompt,
            request.model_name,
            request.max_length
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text generation failed: {str(e)}"
        )

@router.post("/classify")
async def classify_text(
    request: TextAnalysisRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Classify text using AI model."""
    try:
        result = ai_model_manager.classify_text(
            request.text,
            request.model_name
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Text classification failed: {str(e)}"
        )

@router.post("/entities")
async def extract_entities(
    request: TextAnalysisRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Extract named entities from text."""
    try:
        result = ai_model_manager.extract_entities(
            request.text,
            request.model_name
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Entity extraction failed: {str(e)}"
        )

@router.post("/trading-analysis")
async def analyze_trading_text(
    request: TextAnalysisRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Comprehensive trading text analysis."""
    try:
        analysis = {}
        
        # Sentiment analysis
        sentiment = ai_model_manager.analyze_sentiment(request.text, "finbert")
        analysis["sentiment"] = sentiment
        
        # Entity extraction
        entities = ai_model_manager.extract_entities(request.text, "ner_model")
        analysis["entities"] = entities
        
        # Text classification
        classification = ai_model_manager.classify_text(request.text, "news_classifier")
        analysis["classification"] = classification
        
        return {
            "text": request.text,
            "analysis": analysis,
            "summary": {
                "sentiment": sentiment.get("sentiment", "unknown"),
                "sentiment_score": sentiment.get("score", 0.0),
                "entity_count": len(entities.get("entities", [])),
                "classification": classification.get("classification", "unknown")
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Trading analysis failed: {str(e)}"
        )

@router.post("/generate-strategy")
async def generate_trading_strategy(
    request: TextGenerationRequest,
    current_user: str = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate trading strategy using AI."""
    try:
        # Create trading-specific prompt
        trading_prompt = f"""
        As a trading expert, analyze the following market condition and provide a trading strategy:
        
        Market Context: {request.prompt}
        
        Please provide:
        1. Strategy recommendation (buy/sell/hold)
        2. Entry and exit points
        3. Risk management rules
        4. Position sizing advice
        5. Key factors to monitor
        
        Be concise and actionable.
        """
        
        result = ai_model_manager.generate_text(
            trading_prompt,
            request.model_name,
            request.max_length
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
        
        return {
            "market_context": request.prompt,
            "strategy": result["generated_text"],
            "model": result["model"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Strategy generation failed: {str(e)}"
        )
