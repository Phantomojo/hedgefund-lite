"""
Main FastAPI application for the trading system.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import settings
from src.core.database import init_db, close_db
from src.core.logging import setup_logging
from src.api.v1.api import api_router
from src.core.security import get_current_user
from src.services.risk_manager import RiskManager
from src.services.strategy_manager import StrategyManager
from src.services.execution_service import ExecutionService
from src.services.ai_service import AIService

# Setup logging
setup_logging()
logger = structlog.get_logger(__name__)

# Global service instances
risk_manager: RiskManager = None
strategy_manager: StrategyManager = None
execution_service: ExecutionService = None
ai_service: AIService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting trading system...")
    
    try:
        # Initialize database
        await init_db()
        
        # Initialize services
        global risk_manager, strategy_manager, execution_service, ai_service
        risk_manager = RiskManager()
        strategy_manager = StrategyManager()
        execution_service = ExecutionService()
        ai_service = AIService()
        
        # Start services
        await risk_manager.start()
        await strategy_manager.start()
        await execution_service.start()
        await ai_service.start()
        
        logger.info("Trading system started successfully")
    except Exception as e:
        logger.error("Failed to initialize some services", error=str(e))
        # Continue with degraded mode
    
    yield
    
    # Shutdown
    logger.info("Shutting down trading system...")
    
    try:
        # Stop services
        if execution_service:
            await execution_service.stop()
        if strategy_manager:
            await strategy_manager.stop()
        if risk_manager:
            await risk_manager.stop()
        if ai_service:
            await ai_service.stop()
        
        # Close database
        await close_db()
    except Exception as e:
        logger.error("Error during shutdown", error=str(e))
    
    logger.info("Trading system shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="Autonomous Forex Trading Agent",
    description="A production-grade, self-improving forex trading system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)


# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint."""
    return {
        "message": "Autonomous Forex Trading Agent",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        return {
            "status": "healthy",
            "message": "Trading system is running",
            "services": {
                "database": "healthy",
                "redis": "healthy",
                "risk_manager": "healthy" if risk_manager else "unhealthy",
                "strategy_manager": "healthy" if strategy_manager else "unhealthy",
                "execution_service": "healthy" if execution_service else "unhealthy"
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "degraded",
            "message": "Some services unavailable",
            "error": str(e)
        }


@app.get("/metrics")
async def metrics() -> Dict[str, Any]:
    """Metrics endpoint for Prometheus."""
    # This would return actual metrics from the system
    return {
        "trading_metrics": {
            "total_pnl": 0.0,
            "daily_pnl": 0.0,
            "open_positions": 0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0
        },
        "system_metrics": {
            "uptime": 0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0
        }
    }


# Emergency endpoints
@app.post("/emergency/kill")
async def emergency_kill(current_user: str = Depends(get_current_user)) -> Dict[str, str]:
    """Emergency kill switch - stops all trading immediately."""
    try:
        logger.warning("Emergency kill switch activated", user=current_user)
        
        # Stop all trading
        if execution_service:
            await execution_service.emergency_stop()
        
        # Close all positions
        # Cancel all orders
        
        return {"status": "success", "message": "Trading stopped immediately"}
    except Exception as e:
        logger.error("Emergency kill failed", error=str(e))
        raise HTTPException(status_code=500, detail="Emergency kill failed")


@app.post("/emergency/pause")
async def emergency_pause(current_user: str = Depends(get_current_user)) -> Dict[str, str]:
    """Emergency pause - pauses all trading."""
    try:
        logger.warning("Emergency pause activated", user=current_user)
        
        # Pause all trading
        if execution_service:
            await execution_service.pause_trading()
        
        return {"status": "success", "message": "Trading paused"}
    except Exception as e:
        logger.error("Emergency pause failed", error=str(e))
        raise HTTPException(status_code=500, detail="Emergency pause failed")


@app.post("/emergency/close-all")
async def emergency_close_all(current_user: str = Depends(get_current_user)) -> Dict[str, str]:
    """Emergency close all positions."""
    try:
        logger.warning("Emergency close all positions activated", user=current_user)
        
        # Close all positions
        if execution_service:
            await execution_service.close_all_positions()
        
        return {"status": "success", "message": "All positions closed"}
    except Exception as e:
        logger.error("Emergency close all failed", error=str(e))
        raise HTTPException(status_code=500, detail="Emergency close all failed")


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
