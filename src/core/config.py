"""
Configuration management for the trading system.
"""

import os
from typing import List, Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    url: str = Field(default="postgresql://trading:trading@localhost:5432/trading")
    pool_size: int = Field(default=10)
    max_overflow: int = Field(default=20)
    echo: bool = Field(default=False)
    
    class Config:
        env_prefix = "DATABASE_"


class RedisSettings(BaseSettings):
    """Redis configuration."""
    url: str = Field(default="redis://localhost:6379")
    db: int = Field(default=0)
    password: Optional[str] = None
    
    class Config:
        env_prefix = "REDIS_"


class BrokerSettings(BaseSettings):
    """Broker configuration."""
    name: str = Field(default="oanda")
    api_key: str = Field(default="")
    api_secret: str = Field(default="")
    account_id: str = Field(default="")
    environment: str = Field(default="practice")  # practice or live
    base_url: str = Field(default="https://api-fxpractice.oanda.com")
    
    class Config:
        env_prefix = "BROKER_"


class RiskSettings(BaseSettings):
    """Risk management configuration."""
    max_drawdown_pct: float = Field(default=15.0)
    per_trade_risk_pct: float = Field(default=0.75)
    daily_loss_limit_pct: float = Field(default=5.0)
    max_leverage: float = Field(default=10.0)
    var_limit_pct: float = Field(default=5.0)
    correlation_limit: float = Field(default=0.7)
    max_positions_per_strategy: int = Field(default=3)
    max_total_positions: int = Field(default=10)
    
    @validator("max_drawdown_pct", "per_trade_risk_pct", "daily_loss_limit_pct", "var_limit_pct")
    def validate_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        return v
    
    @validator("correlation_limit")
    def validate_correlation(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Correlation must be between 0 and 1")
        return v


class TradingSettings(BaseSettings):
    """Trading configuration."""
    allowed_pairs: List[str] = Field(default=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD"])
    default_timeframes: List[str] = Field(default=["H1", "H4", "D1"])
    min_lot_size: float = Field(default=0.01)
    max_lot_size: float = Field(default=10.0)
    default_slippage_pips: float = Field(default=2.0)
    commission_per_lot: float = Field(default=7.0)  # USD per lot
    
    # Data service settings
    update_interval: int = Field(default=60)  # seconds
    history_days: int = Field(default=30)  # days
    
    class Config:
        env_prefix = "TRADING_"


class MLSettings(BaseSettings):
    """Machine learning configuration."""
    model_dir: str = Field(default="./models")
    experiment_tracking: str = Field(default="mlflow")  # mlflow or wandb
    mlflow_tracking_uri: str = Field(default="http://localhost:5000")
    wandb_project: str = Field(default="forex-trading")
    
    # Genetic algorithm settings
    population_size: int = Field(default=100)
    generations: int = Field(default=50)
    mutation_rate: float = Field(default=0.1)
    crossover_rate: float = Field(default=0.8)
    
    # RL settings
    rl_episodes: int = Field(default=1000)
    rl_learning_rate: float = Field(default=0.001)
    rl_batch_size: int = Field(default=64)
    
    class Config:
        env_prefix = "ML_"


class MonitoringSettings(BaseSettings):
    """Monitoring configuration."""
    prometheus_port: int = Field(default=9090)
    grafana_port: int = Field(default=3001)
    dashboard_port: int = Field(default=3000)
    
    # Alert settings
    alert_webhook_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Logging
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="./logs/trading.log")
    
    class Config:
        env_prefix = "MONITORING_"


class ExternalServicesSettings(BaseSettings):
    """External services configuration."""
    news: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "a025383ef4974ff1a52d6d0484db191a"
    })
    finnhub: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "d2q0r71r01qnf9nn12r0d2q0r71r01qnf9nn12rg"
    })
    huggingface: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "hf_your_token_here"
    })
    alpha_vantage: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "HY5M3D5IDQ6UIC0Z"
    })
    twitter: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "EHdQ8vvVuZHxbnGq9OS4nAb7clftr2fLzgCNrus35n7xposOog",
        "bearer_token": "AAAAAAAAAAAAAAAAAAAAAHF83wEAAAAAO0Ux7eeHiNmlc4n6tobA%2FDhZTnY%3DSl1M9ZeWNmiO9VXUZxh2SGjfWB5JUP3ujjQisYLHoLSChg8aYn"
    })
    nasdaq: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "bArm_eYp_sjHRvCjRz7T"
    })
    polygon: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "YSLFV_SJjpqWSU2sTWJpUsAEWrUIM_km",
        "base_url": "https://api.polygon.io"
    })
    twelve_data: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "8d1cf6b2ebcb4ff5a0f372ab0a734399",
        "base_url": "https://api.twelvedata.com"
    })
    fred: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "e2ecac5b81a3427a1aae465526417f39",
        "base_url": "https://api.stlouisfed.org/fred"
    })
    tiingo: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "09f02aff2ae8bd123f0d00031eae718398617a7f",
        "base_url": "https://api.tiingo.com"
    })
    eia: Dict[str, Any] = Field(default={
        "enabled": True,
        "api_key": "UNeIv1tdcbaSlcZJnMcAfuRPfImzgmEm1c3AXtOf",
        "base_url": "https://api.eia.gov/v2"
    })
    
    class Config:
        env_prefix = "EXTERNAL_"


class SecuritySettings(BaseSettings):
    """Security configuration."""
    secret_key: str = Field(default="your-secret-key-here")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    
    # API security
    allowed_hosts: List[str] = Field(default=["*"])
    cors_origins: List[str] = Field(default=["*"])
    
    class Config:
        env_prefix = "SECURITY_"


class Settings(BaseSettings):
    """Main application settings."""
    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=True)
    
    # Services
    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    broker: BrokerSettings = BrokerSettings()
    risk: RiskSettings = RiskSettings()
    trading: TradingSettings = TradingSettings()
    ml: MLSettings = MLSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    security: SecuritySettings = SecuritySettings()
    external_services: ExternalServicesSettings = ExternalServicesSettings()
    
    # Computed properties
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        return self.security.allowed_hosts
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.security.cors_origins
    
    @property
    def IS_DEVELOPMENT(self) -> bool:
        return self.environment == "development"
    
    @property
    def IS_PRODUCTION(self) -> bool:
        return self.environment == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance."""
    return settings
