#!/usr/bin/env python3
"""
Production System Test Suite
Comprehensive testing of the hardened trading system
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionSystemTester:
    """Comprehensive production system tester."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.test_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> bool:
        """Authenticate with the system."""
        try:
            login_data = {
                "username": "admin",
                "password": "password"
            }
            
            async with self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    logger.info("✅ Authentication successful")
                    return True
                else:
                    logger.error(f"❌ Authentication failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Authentication error: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def test_health_endpoint(self) -> bool:
        """Test health endpoint."""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Health check passed: {data.get('status', 'unknown')}")
                    return True
                else:
                    logger.error(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False
    
    async def test_data_endpoints(self) -> Dict[str, bool]:
        """Test data endpoints."""
        results = {}
        
        # Test market data
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/data/market-data/EUR_USD",
                headers=self.get_headers()
            ) as response:
                results["market_data"] = response.status == 200
                if response.status == 200:
                    logger.info("✅ Market data endpoint working")
                else:
                    logger.error(f"❌ Market data endpoint failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Market data error: {e}")
            results["market_data"] = False
        
        # Test YFinance data
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/data/yfinance/AAPL",
                headers=self.get_headers()
            ) as response:
                results["yfinance"] = response.status == 200
                if response.status == 200:
                    logger.info("✅ YFinance endpoint working")
                else:
                    logger.error(f"❌ YFinance endpoint failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ YFinance error: {e}")
            results["yfinance"] = False
        
        # Test Polygon data
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/data/polygon/AAPL",
                headers=self.get_headers()
            ) as response:
                results["polygon"] = response.status == 200
                if response.status == 200:
                    logger.info("✅ Polygon endpoint working")
                else:
                    logger.error(f"❌ Polygon endpoint failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Polygon error: {e}")
            results["polygon"] = False
        
        return results
    
    async def test_ai_endpoints(self) -> Dict[str, bool]:
        """Test AI endpoints."""
        results = {}
        
        # Test market analysis
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/ai/analyze-market/EUR_USD",
                headers=self.get_headers()
            ) as response:
                results["market_analysis"] = response.status == 200
                if response.status == 200:
                    logger.info("✅ Market analysis endpoint working")
                else:
                    logger.error(f"❌ Market analysis endpoint failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Market analysis error: {e}")
            results["market_analysis"] = False
        
        # Test AI knowledge stack
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/ai/knowledge/market-data/AAPL",
                headers=self.get_headers()
            ) as response:
                results["ai_knowledge"] = response.status == 200
                if response.status == 200:
                    logger.info("✅ AI knowledge stack working")
                else:
                    logger.error(f"❌ AI knowledge stack failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ AI knowledge stack error: {e}")
            results["ai_knowledge"] = False
        
        return results
    
    async def test_trading_endpoints(self) -> Dict[str, bool]:
        """Test trading endpoints."""
        results = {}
        
        # Test positions
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/trading/positions",
                headers=self.get_headers()
            ) as response:
                results["positions"] = response.status == 200
                if response.status == 200:
                    logger.info("✅ Positions endpoint working")
                else:
                    logger.error(f"❌ Positions endpoint failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Positions error: {e}")
            results["positions"] = False
        
        # Test orders
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/trading/orders",
                headers=self.get_headers()
            ) as response:
                results["orders"] = response.status == 200
                if response.status == 200:
                    logger.info("✅ Orders endpoint working")
                else:
                    logger.error(f"❌ Orders endpoint failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Orders error: {e}")
            results["orders"] = False
        
        return results
    
    async def test_risk_endpoints(self) -> Dict[str, bool]:
        """Test risk management endpoints."""
        results = {}
        
        # Test risk status
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/risk/status",
                headers=self.get_headers()
            ) as response:
                results["risk_status"] = response.status == 200
                if response.status == 200:
                    logger.info("✅ Risk status endpoint working")
                else:
                    logger.error(f"❌ Risk status endpoint failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Risk status error: {e}")
            results["risk_status"] = False
        
        # Test risk metrics
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/risk/metrics",
                headers=self.get_headers()
            ) as response:
                results["risk_metrics"] = response.status == 200
                if response.status == 200:
                    logger.info("✅ Risk metrics endpoint working")
                else:
                    logger.error(f"❌ Risk metrics endpoint failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Risk metrics error: {e}")
            results["risk_metrics"] = False
        
        return results
    
    async def test_performance(self) -> Dict[str, Any]:
        """Test system performance."""
        results = {}
        
        # Test response times
        endpoints = [
            "/health",
            "/api/v1/data/market-data/EUR_USD",
            "/api/v1/ai/analyze-market/EUR_USD",
            "/api/v1/risk/status"
        ]
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                async with self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.get_headers()
                ) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    
                    results[endpoint] = {
                        "status": response.status,
                        "response_time_ms": response_time,
                        "success": response.status == 200
                    }
                    
                    if response.status == 200:
                        logger.info(f"✅ {endpoint}: {response_time:.2f}ms")
                    else:
                        logger.error(f"❌ {endpoint}: {response.status} ({response_time:.2f}ms)")
                        
            except Exception as e:
                logger.error(f"❌ {endpoint} error: {e}")
                results[endpoint] = {
                    "status": "error",
                    "response_time_ms": 0,
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    async def test_concurrent_requests(self) -> Dict[str, Any]:
        """Test concurrent request handling."""
        results = {}
        
        # Test 10 concurrent requests
        async def make_request(request_id: int) -> Dict[str, Any]:
            try:
                start_time = time.time()
                async with self.session.get(
                    f"{self.base_url}/api/v1/data/market-data/EUR_USD",
                    headers=self.get_headers()
                ) as response:
                    end_time = time.time()
                    return {
                        "request_id": request_id,
                        "status": response.status,
                        "response_time_ms": (end_time - start_time) * 1000,
                        "success": response.status == 200
                    }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "status": "error",
                    "response_time_ms": 0,
                    "success": False,
                    "error": str(e)
                }
        
        # Make 10 concurrent requests
        tasks = [make_request(i) for i in range(10)]
        concurrent_results = await asyncio.gather(*tasks)
        
        # Analyze results
        successful_requests = sum(1 for r in concurrent_results if r["success"])
        avg_response_time = sum(r["response_time_ms"] for r in concurrent_results) / len(concurrent_results)
        max_response_time = max(r["response_time_ms"] for r in concurrent_results)
        min_response_time = min(r["response_time_ms"] for r in concurrent_results)
        
        results = {
            "total_requests": len(concurrent_results),
            "successful_requests": successful_requests,
            "success_rate": successful_requests / len(concurrent_results),
            "avg_response_time_ms": avg_response_time,
            "max_response_time_ms": max_response_time,
            "min_response_time_ms": min_response_time,
            "detailed_results": concurrent_results
        }
        
        logger.info(f"✅ Concurrent test: {successful_requests}/{len(concurrent_results)} successful")
        logger.info(f"   Avg response time: {avg_response_time:.2f}ms")
        
        return results
    
    async def test_error_handling(self) -> Dict[str, bool]:
        """Test error handling."""
        results = {}
        
        # Test invalid endpoint
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/invalid/endpoint",
                headers=self.get_headers()
            ) as response:
                results["invalid_endpoint"] = response.status == 404
                if response.status == 404:
                    logger.info("✅ Invalid endpoint handled correctly")
                else:
                    logger.error(f"❌ Invalid endpoint not handled: {response.status}")
        except Exception as e:
            logger.error(f"❌ Invalid endpoint error: {e}")
            results["invalid_endpoint"] = False
        
        # Test invalid symbol
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/data/market-data/INVALID_SYMBOL",
                headers=self.get_headers()
            ) as response:
                results["invalid_symbol"] = response.status in [400, 404, 422]
                if response.status in [400, 404, 422]:
                    logger.info("✅ Invalid symbol handled correctly")
                else:
                    logger.error(f"❌ Invalid symbol not handled: {response.status}")
        except Exception as e:
            logger.error(f"❌ Invalid symbol error: {e}")
            results["invalid_symbol"] = False
        
        return results
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive system test."""
        logger.info("🚀 Starting comprehensive production system test...")
        
        # Test authentication
        if not await self.authenticate():
            logger.error("❌ Authentication failed - cannot proceed with tests")
            return {"error": "Authentication failed"}
        
        # Run all tests
        test_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "health": await self.test_health_endpoint(),
            "data_endpoints": await self.test_data_endpoints(),
            "ai_endpoints": await self.test_ai_endpoints(),
            "trading_endpoints": await self.test_trading_endpoints(),
            "risk_endpoints": await self.test_risk_endpoints(),
            "performance": await self.test_performance(),
            "concurrent_requests": await self.test_concurrent_requests(),
            "error_handling": await self.test_error_handling()
        }
        
        # Calculate overall success rate
        total_tests = 0
        passed_tests = 0
        
        for category, results in test_results.items():
            if isinstance(results, dict):
                for test_name, result in results.items():
                    if isinstance(result, bool):
                        total_tests += 1
                        if result:
                            passed_tests += 1
                    elif isinstance(result, dict) and "success" in result:
                        total_tests += 1
                        if result["success"]:
                            passed_tests += 1
        
        test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "overall_status": "PASS" if passed_tests / total_tests >= 0.8 else "FAIL"
        }
        
        # Log summary
        logger.info(f"\n📊 Test Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Success Rate: {test_results['summary']['success_rate']:.2%}")
        logger.info(f"   Overall Status: {test_results['summary']['overall_status']}")
        
        return test_results

async def main():
    """Main test function."""
    async with ProductionSystemTester() as tester:
        results = await tester.run_comprehensive_test()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"📄 Test results saved to: {filename}")
        
        # Exit with appropriate code
        if results.get("summary", {}).get("overall_status") == "PASS":
            logger.info("🎉 All tests passed!")
            sys.exit(0)
        else:
            logger.error("❌ Some tests failed!")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
