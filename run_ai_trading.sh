#!/bin/bash

echo "🤖 Starting HEDGEFUND AI Autonomous Trading..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if server is running
if ! curl -s http://localhost:8000/api/v1/ai-trading/test > /dev/null; then
    echo "⚠️  Warning: Trading server not running on port 8000"
    echo "   Start it with: source venv/bin/activate && GITHUB_TOKEN='your_token' uvicorn src.main:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "Press Enter to continue anyway, or Ctrl+C to stop..."
    read
fi

echo "🤖 AI Trading System Ready!"
echo ""
echo "🎯 Available Commands:"
echo "   Press 'A' - AI Market Analysis"
echo "   Press 'T' - Execute AI Strategy"
echo "   Press 'E' - Emergency Stop"
echo "   Press 'Q' - Quit"
echo ""

echo "🚀 Starting AI Trading Dashboard..."
echo ""

# Run the dashboard
python src/tui_dashboard.py
