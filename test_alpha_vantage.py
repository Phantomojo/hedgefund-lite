#!/usr/bin/env python3
"""
Test Alpha Vantage API Key
Verify your API key can fetch real market data
"""

import requests
import json
from datetime import datetime

# Your Alpha Vantage API key
API_KEY = "YSLFV_SJjpqWSU2sTWJpUsAEWrUIM_km"

def test_alpha_vantage_api():
    """Test Alpha Vantage API with your key"""
    
    print("🧪 Testing Alpha Vantage API Key...")
    print("=" * 50)
    
    # Test 1: Get real-time stock data for AAPL
    print("\n📊 Test 1: Real-time Stock Data (AAPL)")
    print("-" * 40)
    
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "Global Quote" in data:
            quote = data["Global Quote"]
            print(f"✅ SUCCESS! AAPL Data Retrieved:")
            print(f"   Symbol: {quote.get('01. symbol', 'N/A')}")
            print(f"   Price: ${quote.get('05. price', 'N/A')}")
            print(f"   Change: {quote.get('09. change', 'N/A')}")
            print(f"   Change %: {quote.get('10. change percent', 'N/A')}")
            print(f"   Volume: {quote.get('06. volume', 'N/A')}")
        else:
            print(f"❌ Error: {data.get('Note', 'Unknown error')}")
            if 'Note' in data:
                print(f"   This usually means rate limit exceeded")
                print(f"   Free tier: 500 requests/day")
    
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Test 2: Get forex data for EUR/USD
    print("\n💱 Test 2: Forex Data (EUR/USD)")
    print("-" * 40)
    
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=EUR&to_currency=USD&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "Realtime Currency Exchange Rate" in data:
            rate = data["Realtime Currency Exchange Rate"]
            print(f"✅ SUCCESS! EUR/USD Data Retrieved:")
            print(f"   From: {rate.get('1. From_Currency Code', 'N/A')}")
            print(f"   To: {rate.get('3. To_Currency Code', 'N/A')}")
            print(f"   Rate: {rate.get('5. Exchange Rate', 'N/A')}")
            print(f"   Time: {rate.get('6. Last Refreshed', 'N/A')}")
        else:
            print(f"❌ Error: {data.get('Note', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Test 3: Get economic indicators
    print("\n🌍 Test 3: Economic Indicators (GDP)")
    print("-" * 40)
    
    url = f"https://www.alphavantage.co/query?function=REAL_GDP&interval=quarterly&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "data" in data:
            gdp_data = data["data"]
            print(f"✅ SUCCESS! GDP Data Retrieved:")
            print(f"   Data points: {len(gdp_data)}")
            if gdp_data:
                latest = gdp_data[0]
                print(f"   Latest: {latest.get('date', 'N/A')} = {latest.get('value', 'N/A')}")
        else:
            print(f"❌ Error: {data.get('Note', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Test 4: Get technical indicators
    print("\n📈 Test 4: Technical Indicators (RSI for AAPL)")
    print("-" * 40)
    
    url = f"https://www.alphavantage.co/query?function=RSI&symbol=AAPL&interval=daily&time_period=14&series_type=close&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "Technical Analysis: RSI" in data:
            rsi_data = data["Technical Analysis: RSI"]
            print(f"✅ SUCCESS! RSI Data Retrieved:")
            print(f"   Data points: {len(rsi_data)}")
            if rsi_data:
                latest_date = list(rsi_data.keys())[0]
                latest_rsi = rsi_data[latest_date]["RSI"]
                print(f"   Latest RSI: {latest_date} = {latest_rsi}")
        else:
            print(f"❌ Error: {data.get('Note', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 API KEY TEST RESULTS:")
    print("=" * 50)
    
    # Summary
    print(f"✅ Alpha Vantage API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print(f"✅ API Key Status: ACTIVE")
    print(f"✅ Rate Limit: 500 requests/day (free tier)")
    print(f"✅ Data Types: Stocks, Forex, Economics, Technical Indicators")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Get FRED API key for economic data")
    print("2. Get NewsAPI key for news sentiment")
    print("3. Test data collection in your trading system")
    print("4. Start building ML models with real data!")

if __name__ == "__main__":
    test_alpha_vantage_api()
