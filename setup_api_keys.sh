#!/bin/bash

echo "🔑 HEDGEFUND API KEYS SETUP SCRIPT"
echo "=================================="
echo ""

# Check if config directory exists
if [ ! -d "config" ]; then
    echo "📁 Creating config directory..."
    mkdir -p config
fi

# Check if api_keys.py exists
if [ ! -f "config/api_keys.py" ]; then
    echo "📝 Creating api_keys.py from template..."
    cp config/api_keys_example.py config/api_keys.py
    echo "✅ Created config/api_keys.py"
    echo "⚠️  Please edit this file with your actual API keys!"
else
    echo "✅ config/api_keys.py already exists"
fi

echo ""
echo "🚀 QUICK START GUIDE:"
echo "====================="
echo ""

echo "1. 📊 GET FREE MARKET DATA API KEYS:"
echo "   • Alpha Vantage: https://www.alphavantage.co/support/#api-key"
echo "   • Polygon.io: https://polygon.io/ (free tier)"
echo ""

echo "2. 🌍 GET FREE ECONOMIC DATA API KEYS:"
echo "   • FRED API: https://fred.stlouisfed.org/docs/api/api_key.html"
echo "   • NewsAPI: https://newsapi.org/ (free tier)"
echo ""

echo "3. 📱 GET SOCIAL SENTIMENT API KEYS:"
echo "   • Twitter: https://developer.twitter.com/ (free tier)"
echo "   • Reddit: https://www.reddit.com/prefs/apps (free)"
echo ""

echo "4. 🗄️ SETUP DATABASES:"
echo "   • PostgreSQL: Install locally or use cloud service"
echo "   • Redis: Install locally or use cloud service"
echo ""

echo "5. ⚙️ CONFIGURE API KEYS:"
echo "   • Edit config/api_keys.py with your actual keys"
echo "   • Set environment variables if needed"
echo ""

echo "6. 🧪 TEST THE SYSTEM:"
echo "   • Run: python -m pytest tests/"
echo "   • Start server: python src/main.py"
echo ""

echo "💰 COST ESTIMATE:"
echo "================="
echo "• FREE TIER: $0/month (limited requests)"
echo "• BASIC PAID: $50-200/month (unlimited requests)"
echo "• PROFESSIONAL: $500-2000/month (enterprise features)"
echo ""

echo "🎯 RECOMMENDED STARTING POINT:"
echo "=============================="
echo "1. Start with FREE APIs (Alpha Vantage, FRED, NewsAPI)"
echo "2. Get basic market data working"
echo "3. Add social sentiment later"
echo "4. Scale up as needed"
echo ""

echo "📚 NEXT STEPS:"
echo "=============="
echo "1. Edit config/api_keys.py with your API keys"
echo "2. Install required packages: pip install -r requirements.txt"
echo "3. Initialize databases: python -c 'from src.services.data_infrastructure import data_infrastructure; await data_infrastructure.initialize_databases()'"
echo "4. Test data collection: python -c 'from src.services.data_infrastructure import data_infrastructure; await data_infrastructure.collect_training_data([\"EUR_USD\", \"GBP_USD\"], \"2024-01-01\", \"2024-12-31\")'"
echo ""

echo "🔍 CURRENT STATUS:"
echo "=================="
echo "✅ Intelligent Emergency Stop System"
echo "✅ Financial Intelligence Engine"
echo "✅ Data Infrastructure Framework"
echo "❌ Real Market Data (need API keys)"
echo "❌ Production Databases (need setup)"
echo "❌ ML Models (need training data)"
echo ""

echo "🚨 IMPORTANT NOTES:"
echo "==================="
echo "• NEVER commit your actual API keys to git"
echo "• Use environment variables for production"
echo "• Start with demo accounts before live trading"
echo "• Test thoroughly before using real money"
echo ""

echo "🎉 SETUP COMPLETE!"
echo "=================="
echo "Your HEDGEFUND trading system is ready for configuration!"
echo "Get your API keys and start collecting real market data!"
