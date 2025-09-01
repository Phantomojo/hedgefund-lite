#!/usr/bin/env python3
"""
Test What Actually Works - Honest Assessment
"""

import requests
import json
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_server_status():
    """Test if the server is responding"""
    print("🔍 Testing Server Status...")
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running and responding")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not accessible: {e}")
        return False

def test_oanda_connection():
    """Test OANDA connection"""
    print("\n💰 Testing OANDA Connection...")
    try:
        from scripts.check_oanda_balance import check_account_details
        check_account_details()
        print("✅ OANDA connection working")
        return True
    except Exception as e:
        print(f"❌ OANDA connection failed: {e}")
        return False

def test_ai_models():
    """Test AI models"""
    print("\n🤖 Testing AI Models...")
    
    # Test GitHub AI Team
    try:
        response = requests.get("http://localhost:8000/api/v1/github-ai-team/status", timeout=10)
        if response.status_code == 200:
            print("✅ GitHub AI Team endpoint responding")
        else:
            print(f"❌ GitHub AI Team endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ GitHub AI Team test failed: {e}")
    
    # Test Ollama
    try:
        response = requests.get("http://localhost:8000/api/v1/ollama/status", timeout=10)
        if response.status_code == 200:
            print("✅ Ollama endpoint responding")
        else:
            print(f"❌ Ollama endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Ollama test failed: {e}")

def test_market_data():
    """Test market data endpoints"""
    print("\n📊 Testing Market Data...")
    
    endpoints = [
        "/api/v1/data/market-data/EUR_USD",
        "/api/v1/data/yfinance/AAPL",
        "/api/v1/trading/account",
        "/api/v1/trading/positions"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Working")
            else:
                print(f"❌ {endpoint} - Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")

def test_database():
    """Test database connection"""
    print("\n🗄️ Testing Database...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            database="hedgefund",
            user="trading",
            password="trading123"
        )
        print("✅ Database connection working")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 HONEST ASSESSMENT - WHAT'S ACTUALLY WORKING")
    print("=" * 60)
    
    # Test all components
    server_ok = test_server_status()
    oanda_ok = test_oanda_connection()
    test_ai_models()
    test_market_data()
    db_ok = test_database()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FUNCTIONALITY SUMMARY")
    print("=" * 60)
    
    print(f"✅ Server Running: {server_ok}")
    print(f"✅ OANDA Connected: {oanda_ok}")
    print(f"✅ Database Working: {db_ok}")
    
    print("\n🎯 WHAT WE CAN DO RIGHT NOW:")
    if server_ok and oanda_ok:
        print("✅ Access OANDA platform and place manual trades")
        print("✅ Use AI models for analysis (if endpoints work)")
        print("✅ Monitor positions manually")
        print("✅ Get account balance and status")
    else:
        print("❌ Need to fix basic connectivity first")
    
    print("\n🔧 WHAT NEEDS TO BE FIXED:")
    if not db_ok:
        print("❌ Database connection (PostgreSQL)")
    print("❌ Live market data feeds")
    print("❌ Automated trading execution")
    print("❌ Real-time risk management")
    
    print("\n💡 RECOMMENDATION:")
    if server_ok and oanda_ok:
        print("✅ Start with manual trading on OANDA")
        print("✅ Use AI for analysis when available")
        print("✅ Build automation gradually")
    else:
        print("❌ Fix basic infrastructure first")

if __name__ == "__main__":
    main()
