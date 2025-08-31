#!/usr/bin/env python3
"""
Start Autonomous Trading System
Launches the AI-powered autonomous trading system.
"""

import requests
import time
import sys
import os

def check_server():
    """Check if the server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_autonomous_trading():
    """Start the autonomous trading system."""
    try:
        response = requests.post("http://localhost:8000/api/v1/autonomous/start")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'started':
                return True, "Autonomous trading system started successfully!"
            else:
                return False, data.get('error', 'Unknown error')
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_status():
    """Get autonomous trading system status."""
    try:
        response = requests.get("http://localhost:8000/api/v1/autonomous/status")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

def main():
    print("🤖 Autonomous Trading System Launcher")
    print("=" * 50)
    
    # Check if server is running
    print("Checking server status...")
    if not check_server():
        print("❌ Server is not running!")
        print("Please start the server first:")
        print("  source venv/bin/activate && python3 src/simple_main.py")
        sys.exit(1)
    
    print("✅ Server is running!")
    
    # Check current status
    print("\nChecking current autonomous trading status...")
    status = get_status()
    if status and status.get('status') == 'running':
        print("⚠️  Autonomous trading system is already running!")
        print("Stats:")
        stats = status.get('stats', {})
        print(f"  • Active trades: {stats.get('active_trades', 0)}")
        print(f"  • Total P&L: ${stats.get('total_pnl', 0):.2f}")
        print(f"  • Win rate: {stats.get('win_rate', 0):.1f}%")
        
        response = input("\nDo you want to restart it? (y/N): ")
        if response.lower() != 'y':
            print("Keeping current system running.")
            return
    else:
        print("✅ System is ready to start.")
    
    # Start autonomous trading
    print("\n🚀 Starting autonomous trading system...")
    success, message = start_autonomous_trading()
    
    if success:
        print("✅ " + message)
        print("\n🤖 Autonomous Trading System is now running!")
        print("\n📊 What the AI will do:")
        print("  • Monitor EUR/USD, GBP/USD, USD/JPY")
        print("  • Analyze markets every minute")
        print("  • Execute trades automatically")
        print("  • Manage risk (2% per trade)")
        print("  • Set stop-loss and take-profit")
        print("  • Close trades based on conditions")
        
        print("\n📈 Monitor your system:")
        print("  • Dashboard: http://localhost:8000/dashboard/index.html")
        print("  • API Status: http://localhost:8000/api/v1/autonomous/status")
        
        print("\n🛑 To stop the system:")
        print("  • Use the dashboard 'Stop Auto Trading' button")
        print("  • Or run: python3 scripts/stop_autonomous_trading.py")
        
        print("\n💡 The system will:")
        print("  • Trade automatically based on AI analysis")
        print("  • Manage up to 3 concurrent trades")
        print("  • Use 70%+ confidence signals only")
        print("  • Apply strict risk management")
        print("  • Log all activities for review")
        
    else:
        print("❌ Failed to start autonomous trading system:")
        print(f"   {message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
