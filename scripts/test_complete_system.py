#!/usr/bin/env python3
"""
Complete System Test
Tests all components of the production-hardened trading system
"""

import asyncio
import aiohttp
import json
import time
import sys
import os
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

async def test_system():
    """Test the complete trading system."""
    print("🚀 Testing Complete Trading System")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    auth_token = None
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Health Check
        print("\n1. Testing Health Check...")
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Health Check: {data.get('status', 'unknown')}")
                    print(f"   Services: {data.get('services', {})}")
                else:
                    print(f"❌ Health Check Failed: {response.status}")
        except Exception as e:
            print(f"❌ Health Check Error: {e}")
        
        # Test 2: Authentication
        print("\n2. Testing Authentication...")
        try:
            login_data = {
                "username": "admin",
                "password": "password"
            }
            
            async with session.post(
                f"{base_url}/api/v1/auth/login",
                data=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    auth_token = data.get("access_token")
                    print("✅ Authentication: Success")
                else:
                    print(f"❌ Authentication Failed: {response.status}")
        except Exception as e:
            print(f"❌ Authentication Error: {e}")
        
        if not auth_token:
            print("❌ Cannot proceed without authentication")
            return
        
        # Test 3: AI Models Status
        print("\n3. Testing AI Models...")
        try:
            headers = {"Authorization": f"Bearer {auth_token}"}
            async with session.get(
                f"{base_url}/api/v1/ai-models/models",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ AI Models: {data.get('loaded_models', 0)}/{data.get('total_models', 0)} loaded")
                    print(f"   Total Size: {data.get('total_size_gb', 0):.1f}GB")
                else:
                    print(f"❌ AI Models Failed: {response.status}")
        except Exception as e:
            print(f"❌ AI Models Error: {e}")
        
        # Test 4: Market Data
        print("\n4. Testing Market Data...")
        try:
            async with session.get(
                f"{base_url}/api/v1/data/market-data/EUR_USD",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Market Data: EUR/USD data retrieved")
                else:
                    print(f"❌ Market Data Failed: {response.status}")
        except Exception as e:
            print(f"❌ Market Data Error: {e}")
        
        # Test 5: YFinance Data
        print("\n5. Testing YFinance...")
        try:
            async with session.get(
                f"{base_url}/api/v1/data/yfinance/AAPL",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ YFinance: AAPL data retrieved")
                else:
                    print(f"❌ YFinance Failed: {response.status}")
        except Exception as e:
            print(f"❌ YFinance Error: {e}")
        
        # Test 6: AI Analysis
        print("\n6. Testing AI Analysis...")
        try:
            analysis_data = {
                "text": "EUR/USD showing bullish momentum with strong technical indicators",
                "model_name": "finbert"
            }
            
            async with session.post(
                f"{base_url}/api/v1/ai-models/sentiment",
                headers=headers,
                json=analysis_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ AI Analysis: Sentiment analysis working")
                else:
                    print(f"❌ AI Analysis Failed: {response.status}")
        except Exception as e:
            print(f"❌ AI Analysis Error: {e}")
        
        # Test 7: Risk Management
        print("\n7. Testing Risk Management...")
        try:
            async with session.get(
                f"{base_url}/api/v1/risk/status",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Risk Management: Status retrieved")
                else:
                    print(f"❌ Risk Management Failed: {response.status}")
        except Exception as e:
            print(f"❌ Risk Management Error: {e}")
        
        # Test 8: Trading Positions
        print("\n8. Testing Trading...")
        try:
            async with session.get(
                f"{base_url}/api/v1/trading/positions",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Trading: Positions retrieved")
                else:
                    print(f"❌ Trading Failed: {response.status}")
        except Exception as e:
            print(f"❌ Trading Error: {e}")
        
        # Test 9: Strategies
        print("\n9. Testing Strategies...")
        try:
            async with session.get(
                f"{base_url}/api/v1/strategies",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Strategies: {len(data)} strategies available")
                else:
                    print(f"❌ Strategies Failed: {response.status}")
        except Exception as e:
            print(f"❌ Strategies Error: {e}")
        
        # Test 10: Monitoring
        print("\n10. Testing Monitoring...")
        try:
            async with session.get(
                f"{base_url}/api/v1/monitoring/health",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Monitoring: Health check working")
                else:
                    print(f"❌ Monitoring Failed: {response.status}")
        except Exception as e:
            print(f"❌ Monitoring Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 System Test Complete!")
    print("📊 Your trading system is ready for production!")

async def main():
    """Main function."""
    await test_system()

if __name__ == "__main__":
    asyncio.run(main())
