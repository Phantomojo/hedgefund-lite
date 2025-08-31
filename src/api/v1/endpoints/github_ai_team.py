"""
GitHub AI Team API Endpoints
Provides access to the multi-model AI ensemble for trading analysis
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging

from src.services.github_ai_team import GitHubAITeam
from src.core.auth import get_current_user
from src.core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


class MarketDataRequest(BaseModel):
    """Market data for AI analysis"""
    symbol: str
    timeframe: str = "1h"
    data: Dict[str, Any]
    include_news: bool = True
    include_sentiment: bool = True
    include_technical: bool = True


class StrategyRequest(BaseModel):
    """Strategy generation request"""
    market_conditions: Dict[str, Any]
    risk_tolerance: str = "medium"  # low, medium, high
    investment_horizon: str = "short"  # short, medium, long
    capital_allocation: float = 10000.0
    preferred_assets: Optional[List[str]] = None


class RiskAssessmentRequest(BaseModel):
    """Risk assessment request"""
    position_data: Dict[str, Any]
    portfolio_context: Optional[Dict[str, Any]] = None
    market_conditions: Optional[Dict[str, Any]] = None


class TradingDecisionRequest(BaseModel):
    """Trading decision request"""
    analysis_data: Dict[str, Any]
    current_positions: Optional[List[Dict[str, Any]]] = None
    available_capital: float = 10000.0
    risk_limits: Optional[Dict[str, Any]] = None


class AIAgentStatus(BaseModel):
    """AI agent status information"""
    name: str
    model: str
    role: str
    capabilities: List[str]
    is_active: bool
    last_used: Optional[str] = None


class AITeamStatus(BaseModel):
    """AI team overall status"""
    total_agents: int
    active_agents: int
    agents: List[AIAgentStatus]
    endpoint: str
    token_configured: bool


# Initialize GitHub AI Team
try:
    github_ai_team = GitHubAITeam()
    ai_team_available = True
    logger.info("GitHub AI Team initialized successfully")
except Exception as e:
    github_ai_team = None
    ai_team_available = False
    logger.error(f"Failed to initialize GitHub AI Team: {e}")


@router.get("/status", response_model=AITeamStatus)
async def get_ai_team_status():
    """
    Get the status of the GitHub AI Team
    """
    if not ai_team_available:
        raise HTTPException(status_code=503, detail="GitHub AI Team not available")
    
    agents_status = []
    for agent_id, agent in github_ai_team.ai_agents.items():
        agents_status.append(AIAgentStatus(
            name=agent.name,
            model=agent.model,
            role=agent.role,
            capabilities=agent.capabilities,
            is_active=agent.is_active,
            last_used=None  # TODO: Track last usage
        ))
    
    return AITeamStatus(
        total_agents=len(github_ai_team.ai_agents),
        active_agents=len([a for a in github_ai_team.ai_agents.values() if a.is_active]),
        agents=agents_status,
        endpoint=github_ai_team.endpoint,
        token_configured=bool(github_ai_team.token)
    )


@router.post("/analyze-market")
async def analyze_market_conditions(
    request: MarketDataRequest,
    current_user = Depends(get_current_user)
):
    """
    Analyze market conditions using the GitHub AI Team
    """
    if not ai_team_available:
        raise HTTPException(status_code=503, detail="GitHub AI Team not available")
    
    try:
        logger.info(f"Starting market analysis for {request.symbol} by user {current_user.username}")
        
        # Prepare market data
        market_data = {
            "symbol": request.symbol,
            "timeframe": request.timeframe,
            "price_data": request.data,
            "include_news": request.include_news,
            "include_sentiment": request.include_sentiment,
            "include_technical": request.include_technical
        }
        
        # Run comprehensive analysis
        analysis_result = await github_ai_team.analyze_market_conditions(market_data)
        
        logger.info(f"Market analysis completed for {request.symbol}")
        
        return {
            "status": "success",
            "symbol": request.symbol,
            "analysis": analysis_result,
            "timestamp": analysis_result.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error in market analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/generate-strategy")
async def generate_trading_strategy(
    request: StrategyRequest,
    current_user = Depends(get_current_user)
):
    """
    Generate trading strategy using AI team consensus
    """
    if not ai_team_available:
        raise HTTPException(status_code=503, detail="GitHub AI Team not available")
    
    try:
        logger.info(f"Generating trading strategy for user {current_user.username}")
        
        # Prepare strategy data
        strategy_data = {
            "market_conditions": request.market_conditions,
            "risk_tolerance": request.risk_tolerance,
            "investment_horizon": request.investment_horizon,
            "capital_allocation": request.capital_allocation,
            "preferred_assets": request.preferred_assets or []
        }
        
        # Generate strategy
        strategy_result = await github_ai_team.generate_trading_strategy(strategy_data)
        
        logger.info(f"Strategy generation completed for user {current_user.username}")
        
        return {
            "status": "success",
            "strategy": strategy_result,
            "risk_tolerance": request.risk_tolerance,
            "investment_horizon": request.investment_horizon,
            "capital_allocation": request.capital_allocation
        }
        
    except Exception as e:
        logger.error(f"Error in strategy generation: {e}")
        raise HTTPException(status_code=500, detail=f"Strategy generation failed: {str(e)}")


@router.post("/assess-risk")
async def assess_risk(
    request: RiskAssessmentRequest,
    current_user = Depends(get_current_user)
):
    """
    Assess risk using AI team analysis
    """
    if not ai_team_available:
        raise HTTPException(status_code=503, detail="GitHub AI Team not available")
    
    try:
        logger.info(f"Assessing risk for user {current_user.username}")
        
        # Prepare risk assessment data
        risk_data = {
            "position_data": request.position_data,
            "portfolio_context": request.portfolio_context or {},
            "market_conditions": request.market_conditions or {}
        }
        
        # Assess risk
        risk_result = await github_ai_team.assess_risk(risk_data)
        
        logger.info(f"Risk assessment completed for user {current_user.username}")
        
        return {
            "status": "success",
            "risk_assessment": risk_result,
            "timestamp": risk_result.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error in risk assessment: {e}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")


@router.post("/make-decision")
async def make_trading_decision(
    request: TradingDecisionRequest,
    current_user = Depends(get_current_user)
):
    """
    Make trading decision using AI team consensus
    """
    if not ai_team_available:
        raise HTTPException(status_code=503, detail="GitHub AI Team not available")
    
    try:
        logger.info(f"Making trading decision for user {current_user.username}")
        
        # Prepare decision data
        decision_data = {
            "analysis_data": request.analysis_data,
            "current_positions": request.current_positions or [],
            "available_capital": request.available_capital,
            "risk_limits": request.risk_limits or {}
        }
        
        # Make decision
        decision_result = await github_ai_team.make_trading_decision(decision_data)
        
        logger.info(f"Trading decision completed for user {current_user.username}")
        
        return {
            "status": "success",
            "decision": decision_result,
            "timestamp": decision_result.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error in trading decision: {e}")
        raise HTTPException(status_code=500, detail=f"Trading decision failed: {str(e)}")


@router.post("/comprehensive-analysis")
async def comprehensive_analysis(
    background_tasks: BackgroundTasks,
    market_request: MarketDataRequest,
    strategy_request: Optional[StrategyRequest] = None,
    current_user = Depends(get_current_user)
):
    """
    Perform comprehensive analysis including market analysis and strategy generation
    """
    if not ai_team_available:
        raise HTTPException(status_code=503, detail="GitHub AI Team not available")
    
    try:
        logger.info(f"Starting comprehensive analysis for user {current_user.username}")
        
        # Market analysis
        market_data = {
            "symbol": market_request.symbol,
            "timeframe": market_request.timeframe,
            "price_data": market_request.data,
            "include_news": market_request.include_news,
            "include_sentiment": market_request.include_sentiment,
            "include_technical": market_request.include_technical
        }
        
        market_analysis = await github_ai_team.analyze_market_conditions(market_data)
        
        # Strategy generation (if requested)
        strategy_result = None
        if strategy_request:
            strategy_data = {
                "market_conditions": market_analysis,
                "risk_tolerance": strategy_request.risk_tolerance,
                "investment_horizon": strategy_request.investment_horizon,
                "capital_allocation": strategy_request.capital_allocation,
                "preferred_assets": strategy_request.preferred_assets or []
            }
            strategy_result = await github_ai_team.generate_trading_strategy(strategy_data)
        
        # Risk assessment
        risk_data = {
            "position_data": {"symbol": market_request.symbol},
            "market_conditions": market_analysis
        }
        risk_assessment = await github_ai_team.assess_risk(risk_data)
        
        # Trading decision
        decision_data = {
            "analysis_data": market_analysis,
            "available_capital": strategy_request.capital_allocation if strategy_request else 10000.0
        }
        trading_decision = await github_ai_team.make_trading_decision(decision_data)
        
        logger.info(f"Comprehensive analysis completed for user {current_user.username}")
        
        return {
            "status": "success",
            "comprehensive_analysis": {
                "market_analysis": market_analysis,
                "strategy": strategy_result,
                "risk_assessment": risk_assessment,
                "trading_decision": trading_decision
            },
            "timestamp": market_analysis.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Error in comprehensive analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")


@router.get("/agents/{agent_id}")
async def get_agent_info(agent_id: str):
    """
    Get information about a specific AI agent
    """
    if not ai_team_available:
        raise HTTPException(status_code=503, detail="GitHub AI Team not available")
    
    if agent_id not in github_ai_team.ai_agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    agent = github_ai_team.ai_agents[agent_id]
    
    return {
        "agent_id": agent_id,
        "name": agent.name,
        "model": agent.model,
        "role": agent.role,
        "capabilities": agent.capabilities,
        "temperature": agent.temperature,
        "max_tokens": agent.max_tokens,
        "is_active": agent.is_active
    }


@router.post("/agents/{agent_id}/test")
async def test_agent(
    agent_id: str,
    test_prompt: str = "Hello, can you help me with trading analysis?",
    current_user = Depends(get_current_user)
):
    """
    Test a specific AI agent with a custom prompt
    """
    if not ai_team_available:
        raise HTTPException(status_code=503, detail="GitHub AI Team not available")
    
    if agent_id not in github_ai_team.ai_agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    try:
        agent = github_ai_team.ai_agents[agent_id]
        
        # Test the agent
        response = await github_ai_team._call_ai_model(agent, test_prompt)
        
        return {
            "status": "success",
            "agent_id": agent_id,
            "agent_name": agent.name,
            "test_prompt": test_prompt,
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Error testing agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Agent test failed: {str(e)}")


@router.get("/models")
async def get_available_models():
    """
    Get list of available GitHub AI models
    """
    if not ai_team_available:
        raise HTTPException(status_code=503, detail="GitHub AI Team not available")
    
    models = {}
    for agent_id, agent in github_ai_team.ai_agents.items():
        if agent.model not in models:
            models[agent.model] = {
                "model_id": agent.model,
                "agents": []
            }
        models[agent.model]["agents"].append({
            "agent_id": agent_id,
            "name": agent.name,
            "role": agent.role
        })
    
    return {
        "status": "success",
        "total_models": len(models),
        "models": models
    }
