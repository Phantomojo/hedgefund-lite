#!/usr/bin/env python3
"""
Script to open the AI Trading Dashboard in a web browser.
"""

import webbrowser
import time
import requests
import sys
import os

def check_server():
    """Check if the server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    print("🤖 AI Trading Dashboard Launcher")
    print("=" * 40)
    
    # Check if server is running
    print("Checking server status...")
    if not check_server():
        print("❌ Server is not running!")
        print("Please start the server first:")
        print("  source venv/bin/activate && python3 src/main.py")
        sys.exit(1)
    
    print("✅ Server is running!")
    
    # Dashboard URL
    dashboard_url = "http://localhost:8000/dashboard/index.html"
    
    print(f"🌐 Opening dashboard: {dashboard_url}")
    print("📊 Dashboard features:")
    print("  • Real-time market analysis")
    print("  • AI-powered trading recommendations")
    print("  • Interactive price charts")
    print("  • Paper trading interface")
    print("  • Live market news")
    print("  • System status monitoring")
    
    # Open in browser
    try:
        webbrowser.open(dashboard_url)
        print("\n🎉 Dashboard opened in your browser!")
        print("\n💡 Tips:")
        print("  • Click 'Refresh' to update market analysis")
        print("  • Use the trading interface to execute AI trades")
        print("  • Monitor real-time metrics and news")
        print("  • Check system status indicators")
        
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"Please manually open: {dashboard_url}")

if __name__ == "__main__":
    main()
