"""
Structured logging configuration.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from src.core.config import settings


def setup_logging():
    """Setup structured logging."""
    # Create logs directory
    log_path = Path(settings.monitoring.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.monitoring.log_level.upper()),
    )
    
    # Add file handler
    file_handler = logging.FileHandler(settings.monitoring.log_file)
    file_handler.setLevel(logging.INFO)
    
    # Get root logger and add file handler
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger."""
    return structlog.get_logger(name)


class TradingLogger:
    """Trading-specific logger with additional context."""
    
    def __init__(self, name: str):
        self.logger = structlog.get_logger(name)
    
    def trade_signal(self, signal: Dict[str, Any]):
        """Log trading signal."""
        self.logger.info(
            "Trading signal generated",
            signal_type=signal.get("type"),
            pair=signal.get("pair"),
            direction=signal.get("direction"),
            confidence=signal.get("confidence"),
            strategy=signal.get("strategy"),
            timestamp=signal.get("timestamp")
        )
    
    def trade_executed(self, trade: Dict[str, Any]):
        """Log trade execution."""
        self.logger.info(
            "Trade executed",
            trade_id=trade.get("id"),
            pair=trade.get("pair"),
            side=trade.get("side"),
            size=trade.get("size"),
            price=trade.get("price"),
            strategy=trade.get("strategy"),
            timestamp=trade.get("timestamp")
        )
    
    def risk_alert(self, alert: Dict[str, Any]):
        """Log risk alert."""
        self.logger.warning(
            "Risk alert triggered",
            alert_type=alert.get("type"),
            severity=alert.get("severity"),
            message=alert.get("message"),
            timestamp=alert.get("timestamp")
        )
    
    def strategy_performance(self, performance: Dict[str, Any]):
        """Log strategy performance."""
        self.logger.info(
            "Strategy performance update",
            strategy=performance.get("strategy"),
            pnl=performance.get("pnl"),
            sharpe=performance.get("sharpe"),
            drawdown=performance.get("drawdown"),
            win_rate=performance.get("win_rate"),
            timestamp=performance.get("timestamp")
        )
    
    def system_health(self, health: Dict[str, Any]):
        """Log system health."""
        self.logger.info(
            "System health check",
            status=health.get("status"),
            services=health.get("services"),
            memory_usage=health.get("memory_usage"),
            cpu_usage=health.get("cpu_usage"),
            timestamp=health.get("timestamp")
        )
    
    def emergency_action(self, action: Dict[str, Any]):
        """Log emergency action."""
        self.logger.error(
            "Emergency action taken",
            action_type=action.get("type"),
            reason=action.get("reason"),
            user=action.get("user"),
            timestamp=action.get("timestamp")
        )
