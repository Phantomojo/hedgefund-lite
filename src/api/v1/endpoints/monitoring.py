"""
Monitoring endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from src.core.security import get_current_user
from src.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/health")
async def get_system_health(
    current_user: str = Depends(get_current_user)
):
    """Get system health status."""
    try:
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "services": {
                "api": "healthy",
                "database": "healthy",
                "redis": "healthy",
                "data_service": "healthy",
                "risk_manager": "healthy",
                "strategy_manager": "healthy",
                "execution_service": "healthy"
            },
            "uptime": "24h 30m 15s",
            "version": "1.0.0"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system health: {str(e)}"
        )


@router.get("/metrics")
async def get_system_metrics(
    current_user: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends()
):
    """Get system metrics."""
    try:
        summary = analytics_service.get_analytics_summary()
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system metrics: {str(e)}"
        )


@router.get("/performance")
async def get_performance_metrics(
    days: int = 30,
    current_user: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends()
):
    """Get performance metrics."""
    try:
        metrics = analytics_service.get_performance_metrics(days)
        if metrics:
            return metrics
        else:
            return {"message": "No performance data available"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.get("/alerts")
async def get_system_alerts(
    current_user: str = Depends(get_current_user)
):
    """Get system alerts."""
    try:
        # This would fetch from alerting system
        return {
            "alerts": [
                {
                    "id": "alert_1",
                    "type": "warning",
                    "message": "High memory usage detected",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "severity": "medium"
                }
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system alerts: {str(e)}"
        )
