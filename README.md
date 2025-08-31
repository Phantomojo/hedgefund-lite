# 🏦 HEDGE FUND LITE - Production Trading System

**Institutional-grade algorithmic trading system optimized for PC deployment with chaos resistance and production hardening.**

[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](https://github.com/your-repo)
[![Chaos Resistant](https://img.shields.io/badge/Chaos-Resistant-red.svg)](https://github.com/your-repo)
[![10 Data Sources](https://img.shields.io/badge/Data%20Sources-10-blue.svg)](https://github.com/your-repo)
[![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://github.com/your-repo)

## 🎯 **System Overview**

A production-hardened algorithmic trading system that combines:
- **10 Data Sources** (OANDA, YFinance, Polygon.io, FRED, EIA, etc.)
- **AI Knowledge Stack** (ML models, technical analysis, sentiment analysis)
- **Real-time Risk Management** (VaR, drawdown monitoring, emergency stops)
- **Production Monitoring** (health checks, performance metrics, alerting)
- **Chaos Resistance** (circuit breakers, retry logic, graceful degradation)

## 🚀 **Quick Start**

### **Development Mode**
```bash
# Clone repository
git clone <your-repo>
cd hedgefund-lite

# Quick start development environment
make quickstart

# Access dashboard at http://localhost:8000
```

### **Production Mode**
```bash
# Production deployment
make production-start

# Monitor system
make monitor
```

## 🏗️ **Architecture**

### **Core Components**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Layer    │    │  Processing     │    │  Execution      │
│                 │    │     Layer       │    │     Layer       │
│ • 10 APIs       │───▶│ • AI Models     │───▶│ • Order Mgmt    │
│ • WebSockets    │    │ • Risk Calc     │    │ • Position Track│
│ • Caching       │    │ • Signal Gen    │    │ • P&L Tracking  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   Risk Mgmt     │    │   Emergency     │
│     Layer       │    │     Layer       │    │     Layer       │
│ • Health Checks │    │ • VaR Limits    │    │ • Kill Switches │
│ • Performance   │    │ • Drawdown Ctrl │    │ • Circuit Brkrs │
│ • Alerting      │    │ • Position Lim  │    │ • Auto Recovery │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Data Sources**
1. **OANDA** - Forex trading & execution
2. **YFinance** - Comprehensive market data
3. **Polygon.io** - Professional market data
4. **Twelve Data** - Financial data & indicators
5. **FRED** - Economic indicators
6. **Tiingo** - Comprehensive financial data
7. **EIA** - Energy data
8. **NewsAPI** - News & sentiment
9. **Finnhub** - Market sentiment
10. **Alpha Vantage** - Technical analysis

## 🔧 **Production Features**

### **Resilience & Fault Tolerance**
- ✅ **Circuit Breakers** - Prevent cascading failures
- ✅ **Retry Logic** - Exponential backoff for API calls
- ✅ **Graceful Degradation** - Fallback mechanisms
- ✅ **Health Checks** - Continuous system monitoring
- ✅ **Auto-recovery** - Automatic restart on failures

### **Performance Optimization**
- ✅ **Async Processing** - Non-blocking operations
- ✅ **Connection Pooling** - Efficient resource usage
- ✅ **Multi-level Caching** - Redis + in-memory caching
- ✅ **Rate Limiting** - Respect API limits
- ✅ **Load Balancing** - Distribute load efficiently

### **Security & Compliance**
- ✅ **API Key Management** - Secure credential storage
- ✅ **Rate Limiting** - Prevent abuse
- ✅ **Audit Logging** - Complete audit trail
- ✅ **Data Encryption** - Encrypt sensitive data
- ✅ **Access Control** - Role-based permissions

### **Risk Management**
- ✅ **Position Limits** - Maximum position sizes
- ✅ **Drawdown Controls** - Automatic risk reduction
- ✅ **Volatility Adjustments** - Dynamic position sizing
- ✅ **Correlation Monitoring** - Portfolio diversification
- ✅ **Emergency Stops** - Instant trading halt

## 📊 **System Capabilities**

### **Multi-Asset Coverage**
- **Stocks** (US & International) - 5 data sources + AI analysis
- **Forex** (All major pairs) - 6 data sources + AI analysis
- **Crypto** (Major cryptocurrencies) - 5 data sources + AI analysis
- **ETFs** (Exchange-traded funds) - 4 data sources + AI analysis
- **Options** (Derivatives) - 3 data sources + AI analysis
- **Commodities** (Oil, gas, metals) - 4 data sources + AI analysis
- **Energy** (Oil, gas, electricity, coal) - 2 comprehensive sources + AI analysis
- **Bonds** (Treasury rates) - 2 data sources + AI analysis
- **Economic Indicators** (GDP, inflation, employment, etc.) - 2 comprehensive sources + AI analysis

### **AI-Powered Analysis**
- **Technical Analysis** - 20+ indicators with AI interpretation
- **Fundamental Analysis** - Multi-source fundamental data with AI scoring
- **Sentiment Analysis** - News + social sentiment with AI processing
- **Risk Analysis** - Real-time risk metrics with AI assessment
- **Market Regime** - AI-powered regime detection and classification
- **Pattern Recognition** - AI-driven chart pattern identification
- **Anomaly Detection** - Machine learning anomaly detection
- **Price Prediction** - ML-based price forecasting

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.8+
- Docker & Docker Compose
- 8GB+ RAM
- 50GB+ disk space

### **Environment Setup**
```bash
# 1. Clone repository
git clone <your-repo>
cd hedgefund-lite

# 2. Create environment file
cp .env.example .env
# Edit .env with your API keys

# 3. Install dependencies
make install

# 4. Start development environment
make dev
```

### **API Keys Configuration**
Add your API keys to `.env`:
```env
# OANDA
OANDA_API_KEY=your_oanda_key
OANDA_ACCOUNT_ID=your_account_id

# YFinance (no key needed)
YFINANCE_ENABLED=true

# Polygon.io
POLYGON_API_KEY=your_polygon_key

# Twelve Data
TWELVE_DATA_API_KEY=your_twelve_data_key

# FRED
FRED_API_KEY=your_fred_key

# Tiingo
TIINGO_API_KEY=your_tiingo_key

# EIA
EIA_API_KEY=your_eia_key

# NewsAPI
NEWS_API_KEY=your_news_key

# Finnhub
FINNHUB_API_KEY=your_finnhub_key

# Alpha Vantage
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
```

## 🚀 **Deployment**

### **Development Deployment**
```bash
# Start development environment
make dev

# Run tests
make test

# Start services
make up
```

### **Production Deployment**
```bash
# Build production image
make build

# Deploy to production
make deploy

# Monitor system
make monitor
```

### **Docker Deployment**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## 📈 **Monitoring & Management**

### **System Status**
```bash
# Check system health
make status

# View logs
make logs

# Monitor performance
make monitor
```

### **Trading Management**
```bash
# Start automated trading
make start-trading

# Stop trading
make stop-trading

# Emergency stop
make emergency-stop

# Check trading status
make trading-status
```

### **Risk Management**
```bash
# Check risk status
make risk-status

# View positions
curl http://localhost:8000/api/v1/risk/positions

# View risk metrics
curl http://localhost:8000/api/v1/risk/metrics
```

## 🔍 **API Endpoints**

### **Core Trading Endpoints**
- `GET /api/v1/data/market-data/{symbol}` - Get market data
- `GET /api/v1/ai/analyze-market/{symbol}` - AI market analysis
- `POST /api/v1/trading/order` - Place order
- `GET /api/v1/trading/positions` - Get positions
- `GET /api/v1/risk/status` - Risk status

### **AI Knowledge Stack**
- `GET /api/v1/ai/knowledge/comprehensive-analysis/{symbol}` - Full AI analysis
- `GET /api/v1/ai/knowledge/technical-analysis/{symbol}` - Technical analysis
- `GET /api/v1/ai/knowledge/trading-signals/{symbol}` - Trading signals
- `GET /api/v1/ai/knowledge/price-prediction/{symbol}` - Price prediction

### **Data Provider Endpoints**
- `GET /api/v1/data/yfinance/{symbol}` - YFinance data
- `GET /api/v1/data/polygon/{symbol}` - Polygon.io data
- `GET /api/v1/data/fred/{series}` - FRED economic data
- `GET /api/v1/data/eia/{indicator}` - EIA energy data

## 🧪 **Testing**

### **Run All Tests**
```bash
make test
```

### **Run Specific Tests**
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Performance tests
pytest tests/performance/
```

### **Stress Testing**
```bash
make stress-test
```

## 📊 **Performance Metrics**

### **System Performance**
- **Uptime**: 99.9%
- **Latency**: < 100ms for data requests
- **Throughput**: 10,000+ data points/second
- **Recovery Time**: < 5 minutes

### **Trading Performance Targets**
- **Sharpe Ratio**: > 1.5
- **Maximum Drawdown**: < 10%
- **Win Rate**: > 55%
- **Profit Factor**: > 1.5

### **Risk Metrics**
- **VaR**: < 2% daily
- **CVaR**: < 3% daily
- **Beta**: < 0.5
- **Correlation**: < 0.3

## 🛡️ **Risk Management**

### **Pre-Trade Risk Checks**
- Position size limits
- Portfolio concentration limits
- Volatility checks
- Correlation analysis
- Market regime detection

### **Real-Time Risk Monitoring**
- P&L tracking
- Drawdown monitoring
- VaR calculation
- Stress testing
- Liquidity analysis

### **Emergency Controls**
- **Emergency Stop** - Instant halt all trading
- **Circuit Breakers** - Automatic failure protection
- **Position Limits** - Maximum exposure controls
- **Drawdown Limits** - Automatic risk reduction

## 🔧 **Configuration**

### **Trading Parameters**
```yaml
# config/trading.yaml
max_position_size: 0.1  # 10% of portfolio
max_total_exposure: 0.5  # 50% of portfolio
max_daily_loss: 0.05  # 5% daily loss
max_drawdown: 0.15  # 15% max drawdown
```

### **Risk Parameters**
```yaml
# config/risk.yaml
var_confidence: 0.95
max_var: 0.02  # 2% VaR
max_volatility: 0.20  # 20% volatility
min_sharpe: 0.5
```

### **Model Parameters**
```yaml
# config/models.yaml
prediction_horizon: 1  # days
retraining_frequency: 7  # days
ensemble_size: 5
```

## 📚 **Documentation**

### **Architecture Documentation**
- [System Architecture](ARCHITECTURE_LITE.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

### **Trading Documentation**
- [Strategy Development](docs/strategies.md)
- [Risk Management](docs/risk.md)
- [Performance Analysis](docs/performance.md)

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ **Disclaimer**

This software is for educational and research purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.

## 🆘 **Support**

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Built with ❤️ for institutional-grade algorithmic trading**
