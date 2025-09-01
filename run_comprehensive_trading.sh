#!/bin/bash

echo "🚀 Starting HEDGEFUND Comprehensive Multi-Asset Trading System..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if server is running
if ! curl -s http://localhost:8000/api/v1/comprehensive-analysis/test > /dev/null; then
    echo "⚠️  Warning: Trading server not running on port 8000"
    echo "   Start it with: source venv/bin/activate && GITHUB_TOKEN='your_token' uvicorn src.main:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "Press Enter to continue anyway, or Ctrl+C to stop..."
    read
fi

echo "🌍 COMPREHENSIVE ASSET COVERAGE:"
echo "   💰 Currencies: EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, NZD/USD"
echo "   🥇 Commodities: Gold, Silver, Oil, Natural Gas, Corn, Wheat, Coffee"
echo "   📈 Indices: S&P 500, NASDAQ, DAX, FTSE, Nikkei, Hang Seng"
echo "   🪙 Crypto: Bitcoin, Ethereum, Litecoin, Ripple, Cardano"
echo "   📊 Bonds: US Treasuries, German Bunds"
echo ""

echo "🧠 AI-POWERED ANALYSIS:"
echo "   🔍 Technical Analysis: Multiple timeframes & indicators"
echo "   📊 Fundamental Analysis: Economic data & earnings"
echo "   📰 News Sentiment: Real-time sentiment analysis"
echo "   🤖 AI Models: GitHub AI Team + Local AI"
echo "   🎯 Strategy Generation: 8 strategy types"
echo ""

echo "🛡️ RISK MANAGEMENT:"
echo "   📊 Max 3 positions per asset (as requested)"
echo "   🎯 2% risk per trade, 15% portfolio max"
echo "   🔒 Position limits & correlation monitoring"
echo "   🚨 Real-time risk alerts & emergency controls"
echo ""

echo "🎮 AVAILABLE COMMANDS:"
echo "   Press 'A' - AI Market Analysis (All Assets)"
echo "   Press 'S' - Generate Trading Strategies"
echo "   Press 'E' - Execute AI Strategies"
echo "   Press 'M' - Market Overview Dashboard"
echo "   Press 'R' - Risk Assessment"
echo "   Press 'Q' - Quit"
echo ""

echo "🚀 Starting Comprehensive Trading Dashboard..."
echo ""

# Run the dashboard
python src/tui_dashboard.py
