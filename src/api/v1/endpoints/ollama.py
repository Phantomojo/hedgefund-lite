"""
Ollama API endpoints for local AI model integration
"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import asyncio

from src.services.ollama_service import ollama_service
from src.core.security import get_current_user

router = APIRouter()


class MarketDataRequest(BaseModel):
    """Request model for market data analysis"""
    symbol: str
    timeframe: str = "1h"
    data: Dict[str, Any]
    include_technical_indicators: bool = True
    include_sentiment: bool = True
    include_fundamentals: bool = True


class StrategyRequest(BaseModel):
    """Request model for strategy generation"""
    market_conditions: Dict[str, Any]
    risk_preference: str = "medium"  # low, medium, high
    time_horizon: str = "short"  # short, medium, long
    preferred_assets: List[str] = []


class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment"""
    position_data: Dict[str, Any]
    portfolio_context: Dict[str, Any] = {}
    market_conditions: Dict[str, Any] = {}


class TradingDecisionRequest(BaseModel):
    """Request model for trading decision"""
    analysis_data: Dict[str, Any]
    current_positions: List[Dict[str, Any]] = []
    account_balance: float = 0.0
    risk_tolerance: str = "medium"


class OllamaModelStatus(BaseModel):
    """Model status response"""
    name: str
    model_id: str
    role: str
    capabilities: List[str]
    is_available: bool
    temperature: float
    max_tokens: int


class OllamaStatus(BaseModel):
    """Ollama service status response"""
    status: str
    base_url: str
    available_models: List[str]
    total_models: int
    service_health: str


@router.get("/status", response_model=OllamaStatus)
async def get_ollama_status(current_user: str = Depends(get_current_user)):
    """Get Ollama service status and available models"""
    try:
        status = await ollama_service.check_ollama_status()
        return OllamaStatus(
            status=status["status"],
            base_url=ollama_service.base_url,
            available_models=status["available_models"],
            total_models=status["total_models"],
            service_health="healthy" if status["status"] == "running" else "unhealthy"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking Ollama status: {str(e)}")


@router.get("/models", response_model=List[OllamaModelStatus])
async def get_ollama_models(current_user: str = Depends(get_current_user)):
    """Get all configured Ollama models and their status"""
    try:
        # Check which models are available
        status = await ollama_service.check_ollama_status()
        available_models = status.get("available_models", [])
        
        models = []
        for model_id, model in ollama_service.ollama_models.items():
            models.append(OllamaModelStatus(
                name=model.name,
                model_id=model.model_id,
                role=model.role,
                capabilities=model.capabilities,
                is_available=model.model_id in available_models,
                temperature=model.temperature,
                max_tokens=model.max_tokens
            ))
        
        return models
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting Ollama models: {str(e)}")


@router.post("/analyze-market")
async def analyze_market_conditions(
    request: MarketDataRequest,
    current_user: str = Depends(get_current_user)
):
    """Analyze market conditions using Ollama models"""
    try:
        # Prepare market data
        market_data = {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "data": request.data,
            "include_technical_indicators": request.include_technical_indicators,
            "include_sentiment": request.include_sentiment,
            "include_fundamentals": request.include_fundamentals
        }
        
        # Perform analysis
        result = await ollama_service.analyze_market_conditions(market_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "analysis": result,
            "timestamp": result.get("timestamp")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in market analysis: {str(e)}")


@router.post("/generate-strategy")
async def generate_trading_strategy(
    request: StrategyRequest,
    current_user: str = Depends(get_current_user)
):
    """Generate trading strategy using Ollama models"""
    try:
        # Prepare market conditions
        market_conditions = {
            **request.market_conditions,
            "risk_preference": request.risk_preference,
            "time_horizon": request.time_horizon,
            "preferred_assets": request.preferred_assets
        }
        
        # Generate strategy
        result = await ollama_service.generate_trading_strategy(market_conditions)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "strategy": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in strategy generation: {str(e)}")


@router.post("/assess-risk")
async def assess_risk(
    request: RiskAssessmentRequest,
    current_user: str = Depends(get_current_user)
):
    """Assess risk using Ollama models"""
    try:
        # Prepare position data
        position_data = {
            **request.position_data,
            "portfolio_context": request.portfolio_context,
            "market_conditions": request.market_conditions
        }
        
        # Assess risk
        result = await ollama_service.assess_risk(position_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "risk_assessment": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in risk assessment: {str(e)}")


@router.post("/make-decision")
async def make_trading_decision(
    request: TradingDecisionRequest,
    current_user: str = Depends(get_current_user)
):
    """Make trading decision using Ollama models"""
    try:
        # Prepare analysis data
        analysis_data = {
            **request.analysis_data,
            "current_positions": request.current_positions,
            "account_balance": request.account_balance,
            "risk_tolerance": request.risk_tolerance
        }
        
        # Make decision
        result = await ollama_service.make_trading_decision(analysis_data)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "decision": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in trading decision: {str(e)}")


@router.post("/comprehensive-analysis")
async def comprehensive_analysis(
    request: MarketDataRequest,
    current_user: str = Depends(get_current_user)
):
    """Perform comprehensive analysis using all available Ollama models"""
    try:
        # Prepare market data
        market_data = {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "data": request.data,
            "include_technical_indicators": request.include_technical_indicators,
            "include_sentiment": request.include_sentiment,
            "include_fundamentals": request.include_fundamentals
        }
        
        # Perform comprehensive analysis
        analysis_result = await ollama_service.analyze_market_conditions(market_data)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        # Generate strategy based on analysis
        strategy_result = await ollama_service.generate_trading_strategy(analysis_result)
        
        # Assess risk
        risk_result = await ollama_service.assess_risk({
            "market_conditions": analysis_result,
            "strategy": strategy_result
        })
        
        # Make final decision
        decision_result = await ollama_service.make_trading_decision({
            "market_analysis": analysis_result,
            "strategy": strategy_result,
            "risk_assessment": risk_result
        })
        
        return {
            "success": True,
            "comprehensive_analysis": {
                "market_analysis": analysis_result,
                "strategy": strategy_result,
                "risk_assessment": risk_result,
                "trading_decision": decision_result,
                "timestamp": analysis_result.get("timestamp")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in comprehensive analysis: {str(e)}")


@router.get("/models/{model_id}/test")
async def test_ollama_model(
    model_id: str,
    current_user: str = Depends(get_current_user)
):
    """Test a specific Ollama model"""
    try:
        # Check if model exists
        if model_id not in ollama_service.ollama_models:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        model = ollama_service.ollama_models[model_id]
        
        # Check if model is available
        status = await ollama_service.check_ollama_status()
        if model_id not in status.get("available_models", []):
            return {
                "success": False,
                "error": f"Model {model_id} is not available in Ollama",
                "ollama_status": status
            }
        
        # Test the model with a simple prompt
        test_prompt = f"Hello, I am testing the {model.name}. Please respond with 'Test successful' if you can see this message."
        
        try:
            response = await ollama_service.call_ollama_model(model, test_prompt)
            
            return {
                "success": True,
                "model": model_id,
                "model_name": model.name,
                "test_response": response,
                "test_prompt": test_prompt
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Model test failed: {str(e)}",
                "model": model_id,
                "model_name": model.name
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing model: {str(e)}")


@router.post("/models/{model_id}/call")
async def call_ollama_model(
    model_id: str,
    prompt: str,
    current_user: str = Depends(get_current_user)
):
    """Call a specific Ollama model with a custom prompt"""
    try:
        # Check if model exists
        if model_id not in ollama_service.ollama_models:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        model = ollama_service.ollama_models[model_id]
        
        # Check if model is available
        status = await ollama_service.check_ollama_status()
        if model_id not in status.get("available_models", []):
            raise HTTPException(status_code=400, detail=f"Model {model_id} is not available in Ollama")
        
        # Call the model
        response = await ollama_service.call_ollama_model(model, prompt)
        
        return {
            "success": True,
            "model": model_id,
            "model_name": model.name,
            "prompt": prompt,
            "response": response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling model: {str(e)}")
