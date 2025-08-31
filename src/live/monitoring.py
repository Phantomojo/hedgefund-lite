"""
Production Monitoring System
Health checks, performance metrics, and alerting for the trading system.
"""

import asyncio
import logging
import time
import psutil
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import redis.asyncio as redis
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"

class AlertLevel(Enum):
    """Alert levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    uptime: float
    timestamp: datetime

@dataclass
class TradingMetrics:
    """Trading performance metrics."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    total_pnl: float
    timestamp: datetime

@dataclass
class HealthCheck:
    """Health check result."""
    component: str
    status: HealthStatus
    message: str
    response_time: float
    timestamp: datetime
    details: Dict[str, Any] = field(default_factory=dict)

class PerformanceMonitor:
    """System performance monitoring."""
    
    def __init__(self):
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics
        self.alert_thresholds = {
            "cpu_usage": 80.0,  # 80% CPU usage
            "memory_usage": 85.0,  # 85% memory usage
            "disk_usage": 90.0,  # 90% disk usage
            "response_time": 5.0,  # 5 seconds response time
        }
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Uptime
            uptime = time.time() - psutil.boot_time()
            
            metrics = SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                uptime=uptime,
                timestamp=datetime.now(timezone.utc)
            )
            
            self.metrics_history.append(metrics)
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return None
    
    def check_performance_alerts(self, metrics: SystemMetrics) -> List[Dict[str, Any]]:
        """Check for performance alerts."""
        alerts = []
        
        if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
            alerts.append({
                "level": AlertLevel.WARNING,
                "component": "system",
                "message": f"High CPU usage: {metrics.cpu_usage:.1f}%",
                "value": metrics.cpu_usage,
                "threshold": self.alert_thresholds["cpu_usage"]
            })
        
        if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "level": AlertLevel.WARNING,
                "component": "system",
                "message": f"High memory usage: {metrics.memory_usage:.1f}%",
                "value": metrics.memory_usage,
                "threshold": self.alert_thresholds["memory_usage"]
            })
        
        if metrics.disk_usage > self.alert_thresholds["disk_usage"]:
            alerts.append({
                "level": AlertLevel.CRITICAL,
                "component": "system",
                "message": f"High disk usage: {metrics.disk_usage:.1f}%",
                "value": metrics.disk_usage,
                "threshold": self.alert_thresholds["disk_usage"]
            })
        
        return alerts

class HealthChecker:
    """Component health checking."""
    
    def __init__(self):
        self.health_checks = {}
        self.health_history = deque(maxlen=100)
    
    async def check_database_health(self) -> HealthCheck:
        """Check database health."""
        start_time = time.time()
        
        try:
            # This would check actual database connection
            # For now, simulate a health check
            await asyncio.sleep(0.1)  # Simulate DB check
            
            response_time = time.time() - start_time
            
            # Simulate database status (replace with actual check)
            db_healthy = True  # This would be actual DB check
            
            if db_healthy:
                return HealthCheck(
                    component="database",
                    status=HealthStatus.HEALTHY,
                    message="Database connection healthy",
                    response_time=response_time,
                    timestamp=datetime.now(timezone.utc)
                )
            else:
                return HealthCheck(
                    component="database",
                    status=HealthStatus.UNHEALTHY,
                    message="Database connection failed",
                    response_time=response_time,
                    timestamp=datetime.now(timezone.utc)
                )
        
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                component="database",
                status=HealthStatus.CRITICAL,
                message=f"Database health check error: {str(e)}",
                response_time=response_time,
                timestamp=datetime.now(timezone.utc)
            )
    
    async def check_redis_health(self) -> HealthCheck:
        """Check Redis health."""
        start_time = time.time()
        
        try:
            # This would check actual Redis connection
            # For now, simulate a health check
            await asyncio.sleep(0.05)  # Simulate Redis check
            
            response_time = time.time() - start_time
            
            # Simulate Redis status (replace with actual check)
            redis_healthy = True  # This would be actual Redis check
            
            if redis_healthy:
                return HealthCheck(
                    component="redis",
                    status=HealthStatus.HEALTHY,
                    message="Redis connection healthy",
                    response_time=response_time,
                    timestamp=datetime.now(timezone.utc)
                )
            else:
                return HealthCheck(
                    component="redis",
                    status=HealthStatus.UNHEALTHY,
                    message="Redis connection failed",
                    response_time=response_time,
                    timestamp=datetime.now(timezone.utc)
                )
        
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                component="redis",
                status=HealthStatus.CRITICAL,
                message=f"Redis health check error: {str(e)}",
                response_time=response_time,
                timestamp=datetime.now(timezone.utc)
            )
    
    async def check_api_health(self) -> HealthCheck:
        """Check API health."""
        start_time = time.time()
        
        try:
            # Check if API is responding
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health", timeout=5) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        return HealthCheck(
                            component="api",
                            status=HealthStatus.HEALTHY,
                            message="API responding normally",
                            response_time=response_time,
                            timestamp=datetime.now(timezone.utc)
                        )
                    else:
                        return HealthCheck(
                            component="api",
                            status=HealthStatus.DEGRADED,
                            message=f"API returned status {response.status}",
                            response_time=response_time,
                            timestamp=datetime.now(timezone.utc)
                        )
        
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheck(
                component="api",
                status=HealthStatus.CRITICAL,
                message=f"API health check error: {str(e)}",
                response_time=response_time,
                timestamp=datetime.now(timezone.utc)
            )
    
    async def run_all_health_checks(self) -> List[HealthCheck]:
        """Run all health checks."""
        checks = []
        
        # Run health checks concurrently
        tasks = [
            self.check_database_health(),
            self.check_redis_health(),
            self.check_api_health()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                checks.append(HealthCheck(
                    component=f"component_{i}",
                    status=HealthStatus.CRITICAL,
                    message=f"Health check failed: {str(result)}",
                    response_time=0.0,
                    timestamp=datetime.now(timezone.utc)
                ))
            else:
                checks.append(result)
        
        # Store in history
        self.health_history.extend(checks)
        
        return checks

class AlertManager:
    """Alert management system."""
    
    def __init__(self):
        self.alert_callbacks = []
        self.alert_history = deque(maxlen=1000)
        self.alert_counts = defaultdict(int)
    
    def register_alert_callback(self, callback: Callable):
        """Register alert callback."""
        self.alert_callbacks.append(callback)
    
    async def send_alert(self, level: AlertLevel, component: str, message: str, 
                        details: Dict[str, Any] = None):
        """Send alert."""
        alert = {
            "level": level.value,
            "component": component,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in history
        self.alert_history.append(alert)
        
        # Update alert counts
        self.alert_counts[level.value] += 1
        
        # Log alert
        log_level = {
            AlertLevel.INFO: logger.info,
            AlertLevel.WARNING: logger.warning,
            AlertLevel.ERROR: logger.error,
            AlertLevel.CRITICAL: logger.critical
        }
        
        log_level[level](f"Alert [{level.value}] {component}: {message}")
        
        # Execute callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get alert summary."""
        return {
            "total_alerts": len(self.alert_history),
            "alert_counts": dict(self.alert_counts),
            "recent_alerts": list(self.alert_history)[-10:],  # Last 10 alerts
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

class MonitoringSystem:
    """Production monitoring system."""
    
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.health_checker = HealthChecker()
        self.alert_manager = AlertManager()
        self.monitoring_task = None
        self.running = False
        
        # Monitoring intervals
        self.system_metrics_interval = 30  # seconds
        self.health_check_interval = 60    # seconds
        
        # Register alert callbacks
        self.alert_manager.register_alert_callback(self._log_alert)
        self.alert_manager.register_alert_callback(self._send_notification)
    
    async def start_monitoring(self):
        """Start monitoring system."""
        self.running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Monitoring system started")
    
    async def stop_monitoring(self):
        """Stop monitoring system."""
        self.running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logger.info("Monitoring system stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        last_health_check = 0
        
        while self.running:
            try:
                current_time = time.time()
                
                # Collect system metrics
                system_metrics = await self.performance_monitor.collect_system_metrics()
                if system_metrics:
                    # Check for performance alerts
                    alerts = self.performance_monitor.check_performance_alerts(system_metrics)
                    for alert in alerts:
                        await self.alert_manager.send_alert(
                            alert["level"],
                            alert["component"],
                            alert["message"],
                            {"value": alert["value"], "threshold": alert["threshold"]}
                        )
                
                # Run health checks periodically
                if current_time - last_health_check >= self.health_check_interval:
                    health_checks = await self.health_checker.run_all_health_checks()
                    
                    for check in health_checks:
                        if check.status == HealthStatus.CRITICAL:
                            await self.alert_manager.send_alert(
                                AlertLevel.CRITICAL,
                                check.component,
                                check.message,
                                {"response_time": check.response_time}
                            )
                        elif check.status == HealthStatus.UNHEALTHY:
                            await self.alert_manager.send_alert(
                                AlertLevel.ERROR,
                                check.component,
                                check.message,
                                {"response_time": check.response_time}
                            )
                        elif check.status == HealthStatus.DEGRADED:
                            await self.alert_manager.send_alert(
                                AlertLevel.WARNING,
                                check.component,
                                check.message,
                                {"response_time": check.response_time}
                            )
                    
                    last_health_check = current_time
                
                # Sleep for monitoring interval
                await asyncio.sleep(self.system_metrics_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(10)
    
    async def _log_alert(self, alert: Dict[str, Any]):
        """Log alert to file."""
        # This would write to a log file or database
        logger.info(f"Alert logged: {alert}")
    
    async def _send_notification(self, alert: Dict[str, Any]):
        """Send notification (email, SMS, etc.)."""
        # This would send actual notifications
        if alert["level"] in ["error", "critical"]:
            logger.warning(f"Notification sent: {alert}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        # Get latest health checks
        latest_health_checks = list(self.health_checker.health_history)[-10:]
        
        # Get latest system metrics
        latest_metrics = list(self.performance_monitor.metrics_history)[-1] if self.performance_monitor.metrics_history else None
        
        # Determine overall status
        overall_status = HealthStatus.HEALTHY
        if any(check.status == HealthStatus.CRITICAL for check in latest_health_checks):
            overall_status = HealthStatus.CRITICAL
        elif any(check.status == HealthStatus.UNHEALTHY for check in latest_health_checks):
            overall_status = HealthStatus.UNHEALTHY
        elif any(check.status == HealthStatus.DEGRADED for check in latest_health_checks):
            overall_status = HealthStatus.DEGRADED
        
        return {
            "status": overall_status.value,
            "running": self.running,
            "uptime": latest_metrics.uptime if latest_metrics else 0,
            "system_metrics": {
                "cpu_usage": latest_metrics.cpu_usage if latest_metrics else 0,
                "memory_usage": latest_metrics.memory_usage if latest_metrics else 0,
                "disk_usage": latest_metrics.disk_usage if latest_metrics else 0
            },
            "health_checks": [
                {
                    "component": check.component,
                    "status": check.status.value,
                    "message": check.message,
                    "response_time": check.response_time,
                    "timestamp": check.timestamp.isoformat()
                }
                for check in latest_health_checks
            ],
            "alerts": self.alert_manager.get_alert_summary(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if not self.performance_monitor.metrics_history:
            return {"error": "No metrics available"}
        
        metrics = list(self.performance_monitor.metrics_history)
        
        return {
            "current": {
                "cpu_usage": metrics[-1].cpu_usage,
                "memory_usage": metrics[-1].memory_usage,
                "disk_usage": metrics[-1].disk_usage,
                "uptime": metrics[-1].uptime
            },
            "average": {
                "cpu_usage": sum(m.cpu_usage for m in metrics) / len(metrics),
                "memory_usage": sum(m.memory_usage for m in metrics) / len(metrics),
                "disk_usage": sum(m.disk_usage for m in metrics) / len(metrics)
            },
            "max": {
                "cpu_usage": max(m.cpu_usage for m in metrics),
                "memory_usage": max(m.memory_usage for m in metrics),
                "disk_usage": max(m.disk_usage for m in metrics)
            },
            "min": {
                "cpu_usage": min(m.cpu_usage for m in metrics),
                "memory_usage": min(m.memory_usage for m in metrics),
                "disk_usage": min(m.disk_usage for m in metrics)
            },
            "history": [
                {
                    "timestamp": m.timestamp.isoformat(),
                    "cpu_usage": m.cpu_usage,
                    "memory_usage": m.memory_usage,
                    "disk_usage": m.disk_usage
                }
                for m in metrics[-50:]  # Last 50 metrics
            ]
        }

# Global instance
monitoring_system = MonitoringSystem()
