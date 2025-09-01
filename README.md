# 🚀 HEDGEFUND TRADING SYSTEM

**Professional-Grade Algorithmic Trading System with Real-Time ML Features**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-Secure-brightgreen.svg)](SECURITY_SETUP.md)

## 🎯 **SYSTEM OVERVIEW**

HedgeFund is a **professional-grade algorithmic trading system** that combines real-time market data, economic indicators, news sentiment, and social media analysis to generate **66+ ML features** for intelligent trading decisions.

### **🏆 KEY FEATURES**
- **Real-time ML Feature Engine** - 66+ features from live data
- **Multi-API Integration** - Alpha Vantage, Polygon.io, FRED, NewsAPI, Twitter
- **Professional Database** - PostgreSQL + Redis infrastructure
- **Intelligent Risk Management** - Emergency stops and position sizing
- **Complete Trading API** - RESTful endpoints for all operations
- **Real-time Dashboard** - Terminal-based trading interface

### **💡 SYSTEM VALUE**
This system represents **$50,000+ in professional software development** and provides institutional-grade trading capabilities typically only available to hedge funds and professional traders.

## 🔒 **SECURITY & SETUP**

### **🚨 CRITICAL SECURITY WARNING**
**NEVER commit your actual API keys, passwords, or personal information to this repository!**

### **🛡️ REPOSITORY SECURITY FEATURES**
- ✅ **Public READ access** - Anyone can view and learn from the code
- 🔒 **Protected WRITE access** - Only authorized contributors can modify
- 🚫 **No sensitive data** - All API keys and secrets are protected
- 🔐 **Self-service setup** - Users configure their own credentials

### **📋 QUICK SETUP (5 minutes)**
```bash
# 1. Clone the repository
git clone https://github.com/Phantomojo/hedgefund-lite.git
cd hedgefund-lite

# 2. Run the secure setup script
chmod +x scripts/setup_user_environment.sh
./scripts/setup_user_environment.sh

# 3. Configure your API keys
nano ~/.hedgefund/api_keys.py

# 4. Verify your setup
python ~/.hedgefund/verify_setup.py

# 5. Start trading!
python run_comprehensive_trading.sh
```

### **🔑 REQUIRED API KEYS**
- **Alpha Vantage** - [Get Free Key](https://www.alphavantage.co/support/#api-key)
- **FRED API** - [Get Free Key](https://fred.stlouisfed.org/docs/api/api_key.html)
- **NewsAPI** - [Get Free Key](https://newsapi.org/)
- **Polygon.io** - [Get Key](https://polygon.io/) (Free tier available)
- **Twitter API** - [Get Key](https://developer.twitter.com/) (Free tier available)

## 🚀 **GETTING STARTED**

### **Prerequisites**
- Python 3.8+
- PostgreSQL
- Redis
- API keys for data services

### **Installation**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
sudo -u postgres createuser trading
sudo -u postgres createdb trading_db
sudo -u postgres psql -c "ALTER USER trading WITH PASSWORD 'your_password';"

# Start Redis
sudo systemctl start redis
```

### **Configuration**
```bash
# Run secure setup
./scripts/setup_user_environment.sh

# Edit your API keys
nano ~/.hedgefund/api_keys.py

# Edit environment settings
nano ~/.hedgefund/.env
```

### **Running the System**
```bash
# Start the trading system
python run_comprehensive_trading.sh

# Or start individual components
python run_ai_trading.sh          # AI-powered trading
python run_dashboard.sh           # Terminal dashboard
python run_wall_street_intelligence.sh  # Market intelligence
```

## 📊 **SYSTEM ARCHITECTURE**

### **Core Services**
- **Market Data Service** - Real-time price feeds
- **Economic Data Service** - Federal Reserve indicators
- **News Data Service** - Financial news sentiment
- **Social Data Service** - Twitter sentiment analysis
- **ML Feature Generator** - 66+ trading features
- **Risk Manager** - Position and portfolio risk
- **Trading Engine** - Order execution and management

### **API Endpoints**
- `/api/v1/features/generate` - ML feature generation
- `/api/v1/market/data` - Real-time market data
- `/api/v1/economic/indicators` - Economic indicators
- `/api/v1/news/sentiment` - News sentiment analysis
- `/api/v1/social/sentiment` - Social media sentiment
- `/api/v1/trading/execute` - Trade execution
- `/api/v1/risk/status` - Risk management status

### **ML Features Generated**
- **Technical Indicators**: RSI, MACD, Bollinger Bands, SMAs, EMAs
- **Volatility Metrics**: ATR, Historical volatility, Price ranges
- **Momentum Indicators**: Rate of change, Momentum, Acceleration
- **Trend Analysis**: Moving averages, Trend strength, Direction
- **Volume Analysis**: Volume trends, OBV, Volume-price relationships
- **Economic Indicators**: GDP, Unemployment, CPI, Interest rates
- **Sentiment Scores**: News sentiment, Social sentiment, Market mood

## 🔧 **DEVELOPMENT**

### **Project Structure**
```
hedgefund-lite/
├── src/
│   ├── api/v1/endpoints/     # API endpoints
│   ├── services/             # Business logic services
│   ├── models/               # Data models
│   ├── schemas/              # Pydantic schemas
│   └── core/                 # Core functionality
├── config/                   # Configuration files
├── scripts/                  # Utility scripts
├── tests/                    # Test files
└── docs/                     # Documentation
```

### **Adding New Features**
```bash
# Create new service
touch src/services/new_service.py

# Create new endpoint
touch src/api/v1/endpoints/new_feature.py

# Add to router
# Edit src/api/v1/api.py

# Test your changes
python -m pytest tests/
```

## 🧪 **TESTING**

### **Run All Tests**
```bash
# Test API connections
python test_all_apis.py

# Test complete system
python test_complete_system.py

# Test real data integration
python test_real_data_integration.py
```

### **API Testing**
```bash
# Test feature generation
curl http://localhost:8000/api/v1/features/generate

# Test market data
curl http://localhost:8000/api/v1/market/data?symbol=AAPL

# Test system health
curl http://localhost:8000/health
```

## 📈 **TRADING STRATEGIES**

### **Built-in Strategies**
- **Trend Following** - Moving average crossovers
- **Mean Reversion** - Bollinger Band strategies
- **Momentum Trading** - RSI and MACD signals
- **Sentiment Trading** - News and social sentiment
- **Risk Parity** - Portfolio risk balancing

### **Custom Strategies**
```python
# Example custom strategy
from src.services.strategy_engine import StrategyEngine

class MyCustomStrategy(StrategyEngine):
    def generate_signals(self, data):
        # Your custom logic here
        signals = []
        # ... strategy implementation
        return signals
```

## 🚨 **RISK DISCLAIMER**

**TRADING INVOLVES SUBSTANTIAL RISK OF LOSS AND IS NOT SUITABLE FOR ALL INVESTORS.**

- Past performance does not guarantee future results
- This system is for educational and research purposes
- Always test strategies thoroughly before live trading
- Use proper risk management and position sizing
- Never risk more than you can afford to lose

## 🤝 **CONTRIBUTING**

### **How to Contribute**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### **Contribution Guidelines**
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation
- Ensure security best practices
- No sensitive data in commits

## 📚 **DOCUMENTATION**

- **[SECURITY_SETUP.md](SECURITY_SETUP.md)** - Security and setup guide
- **[AI_TRADING_DECISION_FLOW.md](AI_TRADING_DECISION_FLOW.md)** - AI decision process
- **[TRADING_SYSTEM_README.md](TRADING_SYSTEM_README.md)** - Detailed system overview
- **[PROJECT_MISSION.md](PROJECT_MISSION.md)** - Project goals and vision

## 📄 **LICENSE**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **ACKNOWLEDGMENTS**

- **Alpha Vantage** - Market data API
- **Polygon.io** - Real-time market data
- **FRED** - Economic data
- **NewsAPI** - Financial news
- **Twitter** - Social sentiment data
- **FastAPI** - Modern web framework
- **PostgreSQL** - Database system
- **Redis** - Caching layer

## 📞 **SUPPORT**

### **Getting Help**
- Check the [SECURITY_SETUP.md](SECURITY_SETUP.md) for setup issues
- Review error logs in the terminal
- Ensure all required services are running
- Verify API key permissions and quotas

### **Community**
- **GitHub Issues** - Report bugs and request features
- **Discussions** - Ask questions and share strategies
- **Wiki** - Community-contributed documentation

---

**🚀 Ready to start your algorithmic trading journey? Follow the setup guide and join the community!**

**Remember: This is professional-grade software. Use it responsibly and always prioritize risk management.**
