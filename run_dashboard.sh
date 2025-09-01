#!/bin/bash

echo "🚀 Starting HEDGEFUND Trading TUI Dashboard..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if server is running
if ! curl -s http://localhost:8000/api/v1/trading/test > /dev/null; then
    echo "⚠️  Warning: Trading server not running on port 8000"
    echo "   Start it with: source venv/bin/activate && GITHUB_TOKEN='your_token' uvicorn src.main:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "Press Enter to continue anyway, or Ctrl+C to stop..."
    read
fi

echo "✅ Starting TUI Dashboard..."
echo "📊 Press 'E' for Emergency Stop"
echo "📈 Press 'B' for Quick Buy EUR/USD"
echo "📉 Press 'S' for Quick Sell EUR/USD"
echo "❌ Press 'Q' to quit"
echo ""

# Run the dashboard
python src/tui_dashboard.py
