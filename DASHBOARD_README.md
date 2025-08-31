# 🤖 AI Trading Dashboard

## 🎯 Overview

The AI Trading Dashboard is a modern, responsive web interface for your autonomous forex trading system. It provides real-time market analysis, AI-powered trading recommendations, and a complete paper trading interface.

## 🚀 Quick Start

### 1. Start the Server
```bash
source venv/bin/activate
python3 src/simple_main.py
```

### 2. Open Dashboard
```bash
python3 scripts/open_dashboard.py
```

Or manually open: **http://localhost:8000/dashboard/index.html**

## 📊 Dashboard Features

### 🎯 Real-Time Market Analysis
- **Live Price Charts**: Interactive EUR/USD price charts with Chart.js
- **Technical Indicators**: SMA20, SMA50, trend detection
- **AI Recommendations**: Buy/Sell/Hold signals with confidence scores
- **Market Regime**: Trend and volatility analysis

### 🤖 AI Trading Interface
- **Strategy Selection**: Trend Following, Mean Reversion, Momentum
- **Risk Management**: Automatic position sizing and stop-loss calculation
- **Paper Trading**: Execute AI-powered trades with real market data
- **Trade History**: Track all executed trades with performance metrics

### 📈 System Monitoring
- **Account Balance**: Real-time OANDA account balance
- **Performance Metrics**: Total trades, win rate, AI confidence
- **System Status**: API connectivity and service health
- **Live News**: Latest market news and sentiment

### 🎨 Modern UI/UX
- **Dark Theme**: Professional dark interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Auto-refresh every 30-60 seconds
- **Interactive Elements**: Hover effects and smooth animations

## 🛠️ Technical Architecture

### Frontend
- **HTML5**: Semantic markup with Bootstrap 5
- **CSS3**: Custom dark theme with CSS variables
- **JavaScript**: ES6+ classes with async/await
- **Chart.js**: Interactive price charts
- **Font Awesome**: Professional icons

### Backend Integration
- **FastAPI**: RESTful API endpoints
- **Real-time Data**: OANDA market data integration
- **AI Analysis**: Technical analysis and strategy generation
- **Paper Trading**: Simulated trade execution

## 📱 Dashboard Sections

### 1. System Overview
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ Account Balance │ Total Trades    │ Win Rate        │ AI Confidence   │
│ $100,000        │ 0               │ 0%              │ 85%             │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

### 2. Market Analysis
- **Current Price**: Real-time EUR/USD price
- **Trend Analysis**: Bullish/Bearish/Sideways with confidence
- **Volatility**: High/Medium/Low market volatility
- **AI Recommendation**: Buy/Sell/Hold with reasoning
- **Price Chart**: Interactive 20-period price chart

### 3. Trading Interface
- **Currency Pair**: EUR/USD, GBP/USD, USD/JPY
- **Strategy Type**: Trend Following, Mean Reversion, Momentum
- **Trade Amount**: $100-$10,000 USD
- **Execute Trade**: One-click AI-powered trading

### 4. Sidebar
- **Recent Trades**: Last 10 executed trades
- **System Status**: API connectivity indicators
- **Market News**: Latest business news

## 🔧 API Endpoints

The dashboard uses these backend endpoints:

### Market Data
```bash
GET /api/v1/data/market-data/EURUSD
POST /api/v1/ai/analyze-market
POST /api/v1/ai/generate-strategy
```

### Trading
```bash
POST /api/v1/paper-trade/execute
GET /api/v1/account/balance
```

### News & Status
```bash
GET /api/v1/news/latest
GET /api/v1/system/status
```

## 🎮 Usage Guide

### 1. Market Analysis
1. **View Current Analysis**: Dashboard shows real-time EUR/USD analysis
2. **Refresh Analysis**: Click "Refresh" button to update
3. **Monitor Trends**: Watch trend indicators and confidence scores
4. **Check Volatility**: Monitor market volatility levels

### 2. Execute Trades
1. **Select Pair**: Choose currency pair (EUR/USD default)
2. **Choose Strategy**: Pick strategy type based on market conditions
3. **Set Amount**: Enter trade amount ($100-$10,000)
4. **Execute**: Click "Execute AI Trade" button
5. **Review**: Check trade details and risk parameters

### 3. Monitor Performance
1. **Track Trades**: View recent trades in sidebar
2. **Check Metrics**: Monitor win rate and total trades
3. **Watch Balance**: Real-time account balance updates
4. **System Health**: Check API status indicators

## 🎯 AI Trading Strategies

### Trend Following
- **EMA Crossover**: EMA12 vs EMA26 signals
- **Stop Loss**: 50 pips
- **Take Profit**: 100 pips
- **Risk**: 2% per trade

### Mean Reversion
- **Bollinger Bands**: Price touching bands
- **Stop Loss**: 40 pips
- **Take Profit**: 80 pips
- **Risk**: 2% per trade

### Momentum
- **MACD**: MACD vs Signal line
- **Stop Loss**: 60 pips
- **Take Profit**: 120 pips
- **Risk**: 2.5% per trade

## 🔒 Security Features

- **Paper Trading Only**: No real money at risk
- **Risk Limits**: Maximum 2.5% risk per trade
- **Position Sizing**: Automatic calculation based on account balance
- **Stop Loss**: Mandatory stop-loss on all trades

## 📊 Performance Metrics

### Real-time Updates
- **Account Balance**: Updates every 30 seconds
- **Market Analysis**: Updates every 60 seconds
- **News Feed**: Updates on page load
- **Trade History**: Updates after each trade

### Data Sources
- **Market Data**: OANDA API (real-time)
- **News**: NewsAPI.org (business news)
- **AI Analysis**: Custom technical analysis engine
- **Account Info**: OANDA demo account

## 🚀 Future Enhancements

### Planned Features
- **Multiple Timeframes**: 1m, 5m, 15m, 1h, 4h, 1d
- **Advanced Charts**: Candlestick patterns, indicators
- **Portfolio Management**: Multiple strategy coordination
- **Backtesting Interface**: Historical strategy testing
- **Alert System**: Price and news alerts
- **Mobile App**: Native mobile application

### AI Improvements
- **Machine Learning**: Enhanced prediction models
- **Sentiment Analysis**: News and social media sentiment
- **Risk Management**: Dynamic position sizing
- **Strategy Optimization**: Genetic algorithm optimization

## 🛠️ Troubleshooting

### Common Issues

**Dashboard not loading:**
```bash
# Check server status
curl http://localhost:8000/health

# Restart server
pkill -f "python3.*simple_main.py"
source venv/bin/activate && python3 src/simple_main.py
```

**API errors:**
```bash
# Check API connectivity
curl http://localhost:8000/api/v1/account/balance

# Verify OANDA credentials
python3 scripts/check_oanda_balance.py
```

**Chart not updating:**
- Refresh browser page
- Check browser console for errors
- Verify market data endpoint

### Browser Compatibility
- **Chrome**: Full support (recommended)
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support
- **Mobile**: Responsive design

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check server logs for errors
4. Verify all dependencies are installed

## 🎉 Success!

Your AI Trading Dashboard is now fully operational! 

**Next Steps:**
1. **Explore the interface**: Try different strategies and amounts
2. **Monitor performance**: Watch how AI recommendations perform
3. **Learn the system**: Understand market analysis and risk management
4. **Scale up**: Consider live trading with real money (after thorough testing)

**Remember**: This is a sophisticated AI trading system. Start with paper trading and gradually increase complexity as you gain confidence in the system's performance.

---

*Built with ❤️ for autonomous forex trading*
