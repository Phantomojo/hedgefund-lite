"""
API Keys Configuration Example
Copy this file to config/api_keys.py and fill in your actual API keys
"""

# =============================================================================
# HEDGEFUND TRADING SYSTEM - API KEYS CONFIGURATION
# =============================================================================

# =============================================================================
# OANDA TRADING API (FOREX TRADING)
# =============================================================================
# Get from: https://www.oanda.com/account/login
OANDA_ACCESS_TOKEN = "your_oanda_access_token_here"
OANDA_ACCOUNT_ID = "your_oanda_account_id_here"
OANDA_ENVIRONMENT = "practice"  # practice or live

# =============================================================================
# MARKET DATA APIs
# =============================================================================

# Alpha Vantage - US Market Data
# Get from: https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY = "your_alpha_vantage_api_key_here"

# Polygon.io - Real-time US Markets
# Get from: https://polygon.io/
POLYGON_API_KEY = "your_polygon_api_key_here"

# Yahoo Finance (no API key needed)
# Uses yfinance library - free but limited

# =============================================================================
# ECONOMIC DATA APIs
# =============================================================================

# FRED API - Federal Reserve Economic Data
# Get from: https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY = "your_fred_api_key_here"

# NewsAPI - Financial News
# Get from: https://newsapi.org/
NEWS_API_KEY = "your_news_api_key_here"

# =============================================================================
# SOCIAL SENTIMENT APIs
# =============================================================================

# Twitter API v2
# Get from: https://developer.twitter.com/
TWITTER_BEARER_TOKEN = "your_twitter_bearer_token_here"
TWITTER_API_KEY = "your_twitter_api_key_here"
TWITTER_API_SECRET = "your_twitter_api_secret_here"

# Reddit API
# Get from: https://www.reddit.com/prefs/apps
REDDIT_CLIENT_ID = "your_reddit_client_id_here"
REDDIT_CLIENT_SECRET = "your_reddit_client_secret_here"

# =============================================================================
# CRYPTOCURRENCY APIs
# =============================================================================

# CoinGecko API (optional - free tier available)
# Get from: https://www.coingecko.com/en/api/pricing
COINGECKO_API_KEY = "your_coingecko_api_key_here"

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# PostgreSQL Database
DATABASE_URL = "postgresql://trading:password@localhost:5432/trading_db"

# Redis Cache
REDIS_URL = "redis://localhost:6379/0"

# =============================================================================
# GITHUB TOKEN (FOR AI FEATURES)
# =============================================================================
GITHUB_TOKEN = "your_github_token_here"

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================

# Trading System
TRADING_ENABLED = True
MAX_POSITIONS = 50
MAX_POSITIONS_PER_ASSET = 3
EMERGENCY_STOP_ENABLED = True

# Risk Management
MAX_PORTFOLIO_LOSS_PCT = 0.15
MAX_SINGLE_POSITION_LOSS_PCT = 0.25
POSITION_SIZE_PCT = 0.02

# Data Collection
DATA_COLLECTION_ENABLED = True
REAL_TIME_DATA_ENABLED = True
HISTORICAL_DATA_DAYS = 365

# Machine Learning
ML_MODELS_ENABLED = True
MODEL_TRAINING_ENABLED = True
FEATURE_ENGINEERING_ENABLED = True

# =============================================================================
# LOGGING & MONITORING
# =============================================================================

# Log Level
LOG_LEVEL = "INFO"

# Monitoring
METRICS_ENABLED = True
ALERTS_ENABLED = True
PERFORMANCE_TRACKING = True

# =============================================================================
# SECURITY & AUTHENTICATION
# =============================================================================

# JWT Secret
SECRET_KEY = "your_secret_key_here"

# API Rate Limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600

# =============================================================================
# EXTERNAL SERVICES
# =============================================================================

# Email Notifications (optional)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"

# Slack Notifications (optional)
SLACK_WEBHOOK_URL = "your_slack_webhook_url_here"

# Discord Notifications (optional)
DISCORD_WEBHOOK_URL = "your_discord_webhook_url_here"

# =============================================================================
# BACKTESTING & RESEARCH
# =============================================================================

# Backtesting Configuration
BACKTESTING_ENABLED = True
BACKTESTING_START_DATE = "2023-01-01"
BACKTESTING_END_DATE = "2024-01-01"
BACKTESTING_INITIAL_CAPITAL = 100000

# Research Tools
RESEARCH_ENABLED = True
CHARTING_ENABLED = True
ANALYSIS_TOOLS_ENABLED = True

# =============================================================================
# HOW TO GET THESE API KEYS
# =============================================================================

"""
STEP-BY-STEP GUIDE TO GET API KEYS:

1. MARKET DATA APIs:
   - Alpha Vantage: https://www.alphavantage.co/support/#api-key (FREE)
   - Polygon.io: https://polygon.io/ (FREE TIER)

2. ECONOMIC DATA APIs:
   - FRED API: https://fred.stlouisfed.org/docs/api/api_key.html (FREE)
   - NewsAPI: https://newsapi.org/ (FREE TIER)

3. SOCIAL SENTIMENT APIs:
   - Twitter: https://developer.twitter.com/ (FREE TIER)
   - Reddit: https://www.reddit.com/prefs/apps (FREE)

4. CRYPTOCURRENCY APIs:
   - CoinGecko: https://www.coingecko.com/en/api/pricing (FREE TIER)

5. DATABASE SETUP:
   - PostgreSQL: Install locally or use cloud service
   - Redis: Install locally or use cloud service

6. GITHUB TOKEN:
   - Go to: https://github.com/settings/tokens
   - Generate new token with repo access

COST ESTIMATE:
- FREE TIER: $0/month (limited requests)
- BASIC PAID: $50-200/month (unlimited requests)
- PROFESSIONAL: $500-2000/month (enterprise features)
"""
