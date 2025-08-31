#!/usr/bin/env python3
"""
Simple API Test Script
Tests all API connections without complex dependencies.
"""

import requests
import json
from datetime import datetime

# API Configuration
APIS = {
    "oanda": {
        "name": "OANDA API",
        "url": "https://api-fxpractice.oanda.com/v3/accounts",
        "headers": {
            "Authorization": "Bearer 1725da5aa30805b09b7c7eb0094ffff4-d6b1be348877531faa9a3253cbda3cfd",
            "Content-Type": "application/json"
        },
        "method": "GET"
    },
    "news": {
        "name": "News API",
        "url": "https://newsapi.org/v2/top-headlines",
        "params": {
            "country": "us",
            "apiKey": "a025383ef4974ff1a52d6d0484db191a"
        },
        "method": "GET"
    },
    "finnhub": {
        "name": "Finnhub API",
        "url": "https://finnhub.io/api/v1/quote",
        "params": {
            "symbol": "AAPL",
            "token": "d2q0r71r01qnf9nn12r0d2q0r71r01qnf9nn12rg"
        },
        "method": "GET"
    },
    "alpha_vantage": {
        "name": "Alpha Vantage API",
        "url": "https://www.alphavantage.co/query",
        "params": {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": "AAPL",
            "interval": "1min",
            "apikey": "HY5M3D5IDQ6UIC0Z"
        },
        "method": "GET"
    },
    "x_api": {
        "name": "X (Twitter) API",
        "url": "https://api.twitter.com/2/tweets/search/recent",
        "headers": {
            "Authorization": "Bearer AAAAAAAAAAAAAAAAAAAAAHF83wEAAAAAO0Ux7eeHiNmlc4n6tobA%2FDhZTnY%3DSl1M9ZeWNmiO9VXUZxh2SGjfWB5JUP3ujjQisYLHoLSChg8aYn",
            "Content-Type": "application/json"
        },
        "params": {
            "query": "forex",
            "max_results": 10
        },
        "method": "GET"
    },
    "nasdaq": {
        "name": "NASDAQ Data API",
        "url": "https://data.nasdaq.com/api/v3/datasets/WIKI/AAPL.json",
        "params": {
            "api_key": "bArm_eYp_sjHRvCjRz7T",
            "limit": 1
        },
        "method": "GET"
    }
}

def test_api(api_name, api_config):
    """Test a single API."""
    try:
        print(f"🔍 Testing {api_config['name']}...")
        
        if api_config['method'] == 'GET':
            response = requests.get(
                api_config['url'],
                headers=api_config.get('headers', {}),
                params=api_config.get('params', {}),
                timeout=10
            )
        
        if response.status_code == 200:
            data = response.json()
            
            # Specific success messages for each API
            if api_name == "oanda":
                accounts = len(data.get('accounts', []))
                print(f"✅ {api_config['name']}: Connected successfully")
                print(f"   Accounts: {accounts}")
                return {"status": "success", "accounts": accounts}
                
            elif api_name == "news":
                articles = len(data.get('articles', []))
                print(f"✅ {api_config['name']}: Connected successfully")
                print(f"   Articles: {articles}")
                return {"status": "success", "articles": articles}
                
            elif api_name == "finnhub":
                price = data.get('c', 'N/A')
                print(f"✅ {api_config['name']}: Connected successfully")
                print(f"   AAPL Price: ${price}")
                return {"status": "success", "price": price}
                
            elif api_name == "alpha_vantage":
                if "Error Message" not in data:
                    data_points = len(data.get('Time Series (1min)', {}))
                    print(f"✅ {api_config['name']}: Connected successfully")
                    print(f"   Data Points: {data_points}")
                    return {"status": "success", "data_points": data_points}
                else:
                    print(f"❌ {api_config['name']}: API Error - {data.get('Error Message')}")
                    return {"status": "failed", "error": data.get('Error Message')}
                    
            elif api_name == "x_api":
                tweets = len(data.get('data', []))
                print(f"✅ {api_config['name']}: Connected successfully")
                print(f"   Tweets: {tweets}")
                return {"status": "success", "tweets": tweets}
                
            elif api_name == "nasdaq":
                dataset_name = data.get('dataset', {}).get('name', 'N/A')
                print(f"✅ {api_config['name']}: Connected successfully")
                print(f"   Dataset: {dataset_name}")
                return {"status": "success", "dataset": dataset_name}
                
        else:
            print(f"❌ {api_config['name']}: Failed - {response.status_code}")
            return {"status": "failed", "error": response.text}
            
    except Exception as e:
        print(f"❌ {api_config['name']}: Error - {str(e)}")
        return {"status": "error", "error": str(e)}

def main():
    """Main function."""
    print("🚀 Starting API Tests...")
    print("=" * 50)
    
    results = {}
    
    # Test all APIs
    for api_name, api_config in APIS.items():
        results[api_name] = test_api(api_name, api_config)
        print()  # Empty line for readability
    
    # Print summary
    print("=" * 50)
    print("📊 API Test Summary")
    print("=" * 50)
    
    success_count = 0
    total_count = len(results)
    
    for api_name, result in results.items():
        status = result["status"]
        if status == "success":
            print(f"✅ {api_name.upper()}: Working")
            success_count += 1
        elif status == "failed":
            print(f"❌ {api_name.upper()}: Failed")
        else:
            print(f"⚠️  {api_name.upper()}: Error")
    
    print(f"\n🎯 Results: {success_count}/{total_count} APIs working")
    
    # Save results to file
    with open("api_test_results.json", "w") as f:
        json.dump({
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
            "summary": {
                "total": total_count,
                "success": success_count,
                "failed": total_count - success_count
            }
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: api_test_results.json")
    
    if success_count == total_count:
        print("\n🎉 All APIs are working correctly!")
        return True
    else:
        print("\n⚠️  Some APIs failed. Check the results above.")
        return False

if __name__ == "__main__":
    main()
