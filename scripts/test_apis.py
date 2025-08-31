#!/usr/bin/env python3
"""
API Testing Script
Tests all API connections to ensure they're working correctly.
"""

import asyncio
import requests
import json
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.config import settings


class APITester:
    """Test all API connections."""
    
    def __init__(self):
        self.results = {}
    
    async def test_oanda_api(self):
        """Test OANDA API connection."""
        try:
            print("🔍 Testing OANDA API...")
            
            # Test account info
            url = f"{settings.broker.base_url}/v3/accounts"
            headers = {
                "Authorization": f"Bearer {settings.broker.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ OANDA API: Connected successfully")
                print(f"   Accounts: {len(data.get('accounts', []))}")
                self.results['oanda'] = {"status": "success", "accounts": len(data.get('accounts', []))}
            else:
                print(f"❌ OANDA API: Failed - {response.status_code}")
                self.results['oanda'] = {"status": "failed", "error": response.text}
                
        except Exception as e:
            print(f"❌ OANDA API: Error - {str(e)}")
            self.results['oanda'] = {"status": "error", "error": str(e)}
    
    async def test_news_api(self):
        """Test News API connection."""
        try:
            print("🔍 Testing News API...")
            
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "country": "us",
                "apiKey": settings.external_services.news.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ News API: Connected successfully")
                print(f"   Articles: {len(data.get('articles', []))}")
                self.results['news'] = {"status": "success", "articles": len(data.get('articles', []))}
            else:
                print(f"❌ News API: Failed - {response.status_code}")
                self.results['news'] = {"status": "failed", "error": response.text}
                
        except Exception as e:
            print(f"❌ News API: Error - {str(e)}")
            self.results['news'] = {"status": "error", "error": str(e)}
    
    async def test_finnhub_api(self):
        """Test Finnhub API connection."""
        try:
            print("🔍 Testing Finnhub API...")
            
            url = "https://finnhub.io/api/v1/quote"
            params = {
                "symbol": "AAPL",
                "token": settings.external_services.finnhub.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Finnhub API: Connected successfully")
                print(f"   AAPL Price: ${data.get('c', 'N/A')}")
                self.results['finnhub'] = {"status": "success", "price": data.get('c')}
            else:
                print(f"❌ Finnhub API: Failed - {response.status_code}")
                self.results['finnhub'] = {"status": "failed", "error": response.text}
                
        except Exception as e:
            print(f"❌ Finnhub API: Error - {str(e)}")
            self.results['finnhub'] = {"status": "error", "error": str(e)}
    
    async def test_alpha_vantage_api(self):
        """Test Alpha Vantage API connection."""
        try:
            print("🔍 Testing Alpha Vantage API...")
            
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": "AAPL",
                "interval": "1min",
                "apikey": settings.external_services.alpha_vantage.api_key
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "Error Message" not in data:
                    print(f"✅ Alpha Vantage API: Connected successfully")
                    print(f"   Data Points: {len(data.get('Time Series (1min)', {}))}")
                    self.results['alpha_vantage'] = {"status": "success", "data_points": len(data.get('Time Series (1min)', {}))}
                else:
                    print(f"❌ Alpha Vantage API: API Error - {data.get('Error Message')}")
                    self.results['alpha_vantage'] = {"status": "failed", "error": data.get('Error Message')}
            else:
                print(f"❌ Alpha Vantage API: Failed - {response.status_code}")
                self.results['alpha_vantage'] = {"status": "failed", "error": response.text}
                
        except Exception as e:
            print(f"❌ Alpha Vantage API: Error - {str(e)}")
            self.results['alpha_vantage'] = {"status": "error", "error": str(e)}
    
    async def test_x_api(self):
        """Test X (Twitter) API connection."""
        try:
            print("🔍 Testing X (Twitter) API...")
            
            url = "https://api.twitter.com/2/tweets/search/recent"
            headers = {
                "Authorization": f"Bearer {settings.external_services.x_api.bearer_token}",
                "Content-Type": "application/json"
            }
            params = {
                "query": "forex",
                "max_results": 10
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ X (Twitter) API: Connected successfully")
                print(f"   Tweets: {len(data.get('data', []))}")
                self.results['x_api'] = {"status": "success", "tweets": len(data.get('data', []))}
            else:
                print(f"❌ X (Twitter) API: Failed - {response.status_code}")
                self.results['x_api'] = {"status": "failed", "error": response.text}
                
        except Exception as e:
            print(f"❌ X (Twitter) API: Error - {str(e)}")
            self.results['x_api'] = {"status": "error", "error": str(e)}
    
    async def test_nasdaq_api(self):
        """Test NASDAQ Data API connection."""
        try:
            print("🔍 Testing NASDAQ Data API...")
            
            url = "https://data.nasdaq.com/api/v3/datasets/WIKI/AAPL.json"
            params = {
                "api_key": settings.external_services.nasdaq.api_key,
                "limit": 1
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ NASDAQ Data API: Connected successfully")
                print(f"   Dataset: {data.get('dataset', {}).get('name', 'N/A')}")
                self.results['nasdaq'] = {"status": "success", "dataset": data.get('dataset', {}).get('name')}
            else:
                print(f"❌ NASDAQ Data API: Failed - {response.status_code}")
                self.results['nasdaq'] = {"status": "failed", "error": response.text}
                
        except Exception as e:
            print(f"❌ NASDAQ Data API: Error - {str(e)}")
            self.results['nasdaq'] = {"status": "error", "error": str(e)}
    
    async def run_all_tests(self):
        """Run all API tests."""
        print("🚀 Starting API Tests...")
        print("=" * 50)
        
        # Test all APIs
        await self.test_oanda_api()
        await self.test_news_api()
        await self.test_finnhub_api()
        await self.test_alpha_vantage_api()
        await self.test_x_api()
        await self.test_nasdaq_api()
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 API Test Summary")
        print("=" * 50)
        
        success_count = 0
        total_count = len(self.results)
        
        for api_name, result in self.results.items():
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
                "results": self.results,
                "summary": {
                    "total": total_count,
                    "success": success_count,
                    "failed": total_count - success_count
                }
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: api_test_results.json")
        
        return success_count == total_count


async def main():
    """Main function."""
    tester = APITester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All APIs are working correctly!")
        sys.exit(0)
    else:
        print("\n⚠️  Some APIs failed. Check the results above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
