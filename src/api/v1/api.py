"""
Main API router for version 1.
"""

from fastapi import APIRouter

from src.api.v1.endpoints import (
    trading,
    strategies,
    risk,
    portfolio,
    data,
    backtest,
    monitoring,
    auth,
    ai,
    ai_models
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(trading.router, prefix="/trading", tags=["trading"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(data.router, prefix="/data", tags=["data"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(ai_models.router, prefix="/ai-models", tags=["ai models"])
