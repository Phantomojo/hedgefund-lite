#!/bin/bash

echo "🧠 Starting HEDGEFUND Wall Street Intelligence System..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if server is running
if ! curl -s http://localhost:8000/api/v1/financial-intelligence/test > /dev/null; then
    echo "⚠️  Warning: Trading server not running on port 8000"
    echo "   Start it with: source venv/bin/activate && GITHUB_TOKEN='your_token' uvicorn src.main:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "Press Enter to continue anyway, or Ctrl+C to stop..."
    read
fi

echo "🏦 WALL STREET PROFESSIONAL KNOWLEDGE:"
echo "   🏛️  Banker Intelligence: Credit analysis, risk assessment, capital markets"
echo "   💼 Investor Wisdom: Portfolio theory, asset allocation, risk management"
echo "   📊 Market Expertise: Technical analysis, fundamental analysis, microstructure"
echo "   🌍 Economic Intelligence: Central banks, macro trends, geopolitical analysis"
echo ""

echo "🧠 FINANCIAL INTELLIGENCE FEATURES:"
echo "   📈 Market Regime Detection: Bull, Bear, Sideways, Crisis, Recovery"
echo "   🔄 Economic Cycle Analysis: Expansion, Peak, Contraction, Trough"
echo "   🎯 Professional Insights: Banker, Investor, Market Professional views"
echo "   🏭 Sector Rotation: Early, Mid, Late cycle, Recession positioning"
echo "   💱 Currency Intelligence: Interest rate differentials, carry trades"
echo "   🥇 Commodity Analysis: Supply-demand, geopolitical, weather factors"
echo ""

echo "🎯 ASSET CLASS COVERAGE:"
echo "   💰 Currencies: 7 major pairs, 4 minor pairs, 4 exotic pairs"
echo "   🥇 Commodities: Precious metals, Energy, Agricultural"
echo "   📈 Indices: US, European, Asian markets"
echo "   🪙 Crypto: Bitcoin, Ethereum, Litecoin, Ripple, Cardano"
echo "   📊 Bonds: US Treasuries, German Bunds"
echo ""

echo "🛡️ RISK MANAGEMENT:"
echo "   📊 Max 3 positions per asset (as requested)"
echo "   🎯 Professional risk assessment from multiple perspectives"
echo "   🔒 Credit quality analysis and liquidity assessment"
echo "   🚨 Market regime-aware position sizing"
echo ""

echo "🎮 AVAILABLE COMMANDS:"
echo "   Press 'A' - AI Market Analysis (All Assets)"
echo "   Press 'S' - Generate Trading Strategies"
echo "   Press 'E' - Execute AI Strategies"
echo "   Press 'M' - Market Overview Dashboard"
echo "   Press 'R' - Risk Assessment"
echo "   Press 'I' - Financial Intelligence Dashboard"
echo "   Press 'Q' - Quit"
echo ""

echo "🧠 FINANCIAL INTELLIGENCE ENDPOINTS:"
echo "   📚 Knowledge Base: /api/v1/financial-intelligence/knowledge-base-test"
echo "   📈 Market Regime: /api/v1/financial-intelligence/market-regime-test"
echo "   🔄 Economic Cycle: /api/v1/financial-intelligence/economic-cycle-test"
echo "   💼 Professional Insights: /api/v1/financial-intelligence/professional-insights-test"
echo "   🏛️  Central Bank Policies: /api/v1/financial-intelligence/central-bank-policies-test"
echo "   🏭 Sector Rotation: /api/v1/financial-intelligence/sector-rotation-test"
echo ""

echo "🚀 Starting Wall Street Intelligence Dashboard..."
echo ""

# Run the dashboard
python src/tui_dashboard.py
