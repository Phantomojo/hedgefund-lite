#!/usr/bin/env python3
"""
Comprehensive Stress Test for Autonomous Trading System
Tests system under load, concurrent requests, and various edge cases.
"""

import asyncio
import aiohttp
import time
import json
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Dict, List, Any
import statistics

class TradingSystemStressTester:
    """Comprehensive stress tester for the trading system."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.auth_token = None
        self.test_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "response_times": [],
            "concurrent_tests": {},
            "load_tests": {},
            "edge_case_tests": {},
            "performance_metrics": {}
        }
        
    def get_auth_token(self):
        """Get authentication token."""
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                data={"username": "admin", "password": "password"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                return True
            return False
        except Exception:
            return False
    
    def get_auth_headers(self):
        """Get authentication headers."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def make_request(self, session, endpoint, method="GET", data=None, description=""):
        """Make a single request and record metrics."""
        start_time = time.time()
        try:
            url = f"{self.base_url}{endpoint}"
            headers = self.get_auth_headers()
            
            if method == "GET":
                async with session.get(url, headers=headers, timeout=30) as response:
                    result = await response.text()
                    status_code = response.status
            elif method == "POST":
                async with session.post(url, json=data, headers=headers, timeout=30) as response:
                    result = await response.text()
                    status_code = response.status
            else:
                return {"success": False, "error": f"Unsupported method: {method}"}
            
            response_time = time.time() - start_time
            success = status_code < 400
            
            return {
                "success": success,
                "status_code": status_code,
                "response_time": response_time,
                "endpoint": endpoint,
                "description": description,
                "response": result[:100] if result else "No response"
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time,
                "endpoint": endpoint,
                "description": description
            }
    
    async def concurrent_load_test(self, num_requests=100, max_concurrent=10):
        """Test system under concurrent load."""
        print(f"🔄 Running concurrent load test: {num_requests} requests, max {max_concurrent} concurrent")
        
        endpoints = [
            ("/health", "GET", None, "Health check"),
            ("/metrics", "GET", None, "Metrics"),
            ("/api/v1/data/market-data/EURUSD", "GET", None, "Market data"),
            ("/api/v1/ai/models", "GET", None, "AI models"),
            ("/api/v1/trading/positions", "GET", None, "Positions"),
            ("/api/v1/risk/metrics", "GET", None, "Risk metrics"),
            ("/api/v1/ai/analyze-market", "POST", {"pair": "EURUSD", "timeframe": "H1", "data": {}}, "AI analysis"),
            ("/api/v1/ai/generate-strategy", "POST", {"market_conditions": {"trend": "up"}, "pair": "EURUSD", "timeframe": "H1"}, "Strategy generation")
        ]
        
        async with aiohttp.ClientSession() as session:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def make_request_with_semaphore(endpoint, method, data, description):
                async with semaphore:
                    return await self.make_request(session, endpoint, method, data, description)
            
            tasks = []
            for _ in range(num_requests):
                endpoint, method, data, description = random.choice(endpoints)
                task = make_request_with_semaphore(endpoint, method, data, description)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            successful = 0
            failed = 0
            response_times = []
            
            for result in results:
                if isinstance(result, dict) and result.get("success"):
                    successful += 1
                    response_times.append(result["response_time"])
                else:
                    failed += 1
            
            success_rate = (successful / num_requests) * 100 if num_requests > 0 else 0
            avg_response_time = statistics.mean(response_times) if response_times else 0
            max_response_time = max(response_times) if response_times else 0
            min_response_time = min(response_times) if response_times else 0
            
            self.test_results["concurrent_tests"][f"load_{num_requests}"] = {
                "total_requests": num_requests,
                "successful": successful,
                "failed": failed,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "min_response_time": min_response_time
            }
            
            print(f"   ✅ Success Rate: {success_rate:.1f}%")
            print(f"   ⏱️  Avg Response Time: {avg_response_time:.3f}s")
            print(f"   📊 Successful: {successful}, Failed: {failed}")
            
            return success_rate >= 95  # 95% success rate threshold
    
    async def rapid_fire_test(self, duration_seconds=60):
        """Test system with rapid-fire requests for extended period."""
        print(f"🔥 Running rapid-fire test for {duration_seconds} seconds")
        
        endpoints = [
            ("/health", "GET", None),
            ("/api/v1/data/market-data/EURUSD", "GET", None),
            ("/api/v1/ai/models", "GET", None),
            ("/api/v1/trading/positions", "GET", None),
            ("/api/v1/risk/metrics", "GET", None)
        ]
        
        start_time = time.time()
        successful = 0
        failed = 0
        response_times = []
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < duration_seconds:
                endpoint, method, data = random.choice(endpoints)
                result = await self.make_request(session, endpoint, method, data)
                
                if result.get("success"):
                    successful += 1
                    response_times.append(result["response_time"])
                else:
                    failed += 1
                
                # Small delay to prevent overwhelming
                await asyncio.sleep(0.1)
        
        total_requests = successful + failed
        success_rate = (successful / total_requests) * 100 if total_requests > 0 else 0
        avg_response_time = statistics.mean(response_times) if response_times else 0
        requests_per_second = total_requests / duration_seconds
        
        self.test_results["load_tests"]["rapid_fire"] = {
            "duration_seconds": duration_seconds,
            "total_requests": total_requests,
            "successful": successful,
            "failed": failed,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "requests_per_second": requests_per_second
        }
        
        print(f"   ✅ Success Rate: {success_rate:.1f}%")
        print(f"   ⏱️  Avg Response Time: {avg_response_time:.3f}s")
        print(f"   🚀 Requests/Second: {requests_per_second:.1f}")
        print(f"   📊 Total Requests: {total_requests}")
        
        return success_rate >= 90  # 90% success rate threshold
    
    async def edge_case_test(self):
        """Test system with edge cases and error conditions."""
        print("🔍 Running edge case tests")
        
        edge_cases = [
            # Invalid authentication
            ("/api/v1/trading/positions", "GET", None, "No auth"),
            # Invalid endpoints
            ("/api/v1/nonexistent", "GET", None, "Invalid endpoint"),
            # Invalid data
            ("/api/v1/ai/analyze-market", "POST", {"invalid": "data"}, "Invalid data"),
            # Empty requests
            ("/api/v1/ai/generate-strategy", "POST", {}, "Empty request"),
            # Large data
            ("/api/v1/ai/analyze-market", "POST", {"pair": "EURUSD", "timeframe": "H1", "data": {"large": "x" * 10000}}, "Large data"),
            # Special characters
            ("/api/v1/data/market-data/EUR/USD", "GET", None, "Special chars in URL"),
            # Very long parameters
            ("/api/v1/data/market-data/" + "A" * 100, "GET", None, "Very long parameter")
        ]
        
        async with aiohttp.ClientSession() as session:
            results = []
            for endpoint, method, data, description in edge_cases:
                if description == "No auth":
                    # Test without authentication
                    headers = {"Content-Type": "application/json"}
                    url = f"{self.base_url}{endpoint}"
                    try:
                        if method == "GET":
                            async with session.get(url, headers=headers, timeout=10) as response:
                                result = {"success": response.status == 401, "status_code": response.status, "description": description}
                        else:
                            async with session.post(url, json=data, headers=headers, timeout=10) as response:
                                result = {"success": response.status == 401, "status_code": response.status, "description": description}
                    except Exception as e:
                        result = {"success": False, "error": str(e), "description": description}
                else:
                    result = await self.make_request(session, endpoint, method, data, description)
                
                results.append(result)
            
            # Analyze results
            expected_failures = 0
            unexpected_successes = 0
            
            for result in results:
                if "No auth" in result.get("description", ""):
                    if result.get("success"):
                        unexpected_successes += 1
                    else:
                        expected_failures += 1
                elif "Invalid" in result.get("description", ""):
                    if result.get("success"):
                        unexpected_successes += 1
                    else:
                        expected_failures += 1
            
            self.test_results["edge_case_tests"] = {
                "total_tests": len(results),
                "expected_failures": expected_failures,
                "unexpected_successes": unexpected_successes,
                "results": results
            }
            
            print(f"   ✅ Expected Failures: {expected_failures}")
            print(f"   ❌ Unexpected Successes: {unexpected_successes}")
            
            return unexpected_successes == 0  # No unexpected successes
    
    async def memory_leak_test(self, iterations=1000):
        """Test for potential memory leaks with repeated requests."""
        print(f"🧠 Running memory leak test: {iterations} iterations")
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            response_times = []
            
            for i in range(iterations):
                result = await self.make_request(session, "/health", "GET", None, f"Iteration {i}")
                if result.get("success"):
                    response_times.append(result["response_time"])
                
                if i % 100 == 0:
                    print(f"   Progress: {i}/{iterations}")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Check for response time degradation
            if len(response_times) > 10:
                first_half = response_times[:len(response_times)//2]
                second_half = response_times[len(response_times)//2:]
                
                first_avg = statistics.mean(first_half)
                second_avg = statistics.mean(second_half)
                degradation = ((second_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
                
                self.test_results["load_tests"]["memory_leak"] = {
                    "iterations": iterations,
                    "total_time": total_time,
                    "avg_response_time": statistics.mean(response_times),
                    "response_time_degradation": degradation,
                    "first_half_avg": first_avg,
                    "second_half_avg": second_avg
                }
                
                print(f"   ⏱️  Avg Response Time: {statistics.mean(response_times):.3f}s")
                print(f"   📉 Response Time Degradation: {degradation:.1f}%")
                print(f"   ⏱️  Total Time: {total_time:.1f}s")
                
                return degradation < 50  # Less than 50% degradation
            else:
                return False
    
    async def data_consistency_test(self):
        """Test data consistency across multiple requests."""
        print("📊 Running data consistency test")
        
        async with aiohttp.ClientSession() as session:
            # Test market data consistency
            market_data_results = []
            for _ in range(10):
                result = await self.make_request(session, "/api/v1/data/market-data/EURUSD", "GET", None)
                if result.get("success"):
                    try:
                        data = json.loads(result.get("response", "{}"))
                        market_data_results.append(data)
                    except:
                        pass
            
            # Test AI models consistency
            models_results = []
            for _ in range(5):
                result = await self.make_request(session, "/api/v1/ai/models", "GET", None)
                if result.get("success"):
                    try:
                        data = json.loads(result.get("response", "{}"))
                        models_results.append(data)
                    except:
                        pass
            
            # Check consistency
            market_data_consistent = len(set(str(r) for r in market_data_results)) <= 2  # Allow some variation
            models_consistent = len(set(str(r) for r in models_results)) <= 2
            
            self.test_results["edge_case_tests"]["data_consistency"] = {
                "market_data_consistent": market_data_consistent,
                "models_consistent": models_consistent,
                "market_data_samples": len(market_data_results),
                "models_samples": len(models_results)
            }
            
            print(f"   📈 Market Data Consistent: {market_data_consistent}")
            print(f"   🤖 Models Consistent: {models_consistent}")
            
            return market_data_consistent and models_consistent
    
    async def run_comprehensive_stress_test(self):
        """Run all stress tests."""
        print("🧪 COMPREHENSIVE STRESS TEST SUITE")
        print("=" * 60)
        print(f"Testing started at: {self.test_results['timestamp']}")
        print()
        
        # Get authentication token
        if not self.get_auth_token():
            print("❌ Failed to get authentication token")
            return False
        
        print("✅ Authentication successful")
        print()
        
        # Run all tests
        test_results = []
        
        # 1. Concurrent load test
        print("1️⃣ CONCURRENT LOAD TEST")
        print("-" * 30)
        result1 = await self.concurrent_load_test(50, 5)
        test_results.append(("Concurrent Load (50 req, 5 concurrent)", result1))
        print()
        
        # 2. Heavy concurrent load test
        print("2️⃣ HEAVY CONCURRENT LOAD TEST")
        print("-" * 30)
        result2 = await self.concurrent_load_test(200, 20)
        test_results.append(("Heavy Concurrent Load (200 req, 20 concurrent)", result2))
        print()
        
        # 3. Rapid fire test
        print("3️⃣ RAPID FIRE TEST")
        print("-" * 30)
        result3 = await self.rapid_fire_test(30)  # 30 seconds
        test_results.append(("Rapid Fire (30 seconds)", result3))
        print()
        
        # 4. Memory leak test
        print("4️⃣ MEMORY LEAK TEST")
        print("-" * 30)
        result4 = await self.memory_leak_test(500)  # 500 iterations
        test_results.append(("Memory Leak (500 iterations)", result4))
        print()
        
        # 5. Edge case test
        print("5️⃣ EDGE CASE TEST")
        print("-" * 30)
        result5 = await self.edge_case_test()
        test_results.append(("Edge Cases", result5))
        print()
        
        # 6. Data consistency test
        print("6️⃣ DATA CONSISTENCY TEST")
        print("-" * 30)
        result6 = await self.data_consistency_test()
        test_results.append(("Data Consistency", result6))
        print()
        
        # Generate comprehensive report
        self.generate_stress_test_report(test_results)
    
    def generate_stress_test_report(self, test_results):
        """Generate comprehensive stress test report."""
        print("📋 COMPREHENSIVE STRESS TEST REPORT")
        print("=" * 60)
        
        passed_tests = sum(1 for _, result in test_results if result)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {total_tests - passed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        print("📊 DETAILED RESULTS:")
        print("-" * 30)
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print()
        print("📈 PERFORMANCE METRICS:")
        print("-" * 30)
        
        # Aggregate performance metrics
        all_response_times = []
        for test_type, data in self.test_results["concurrent_tests"].items():
            if "avg_response_time" in data:
                all_response_times.append(data["avg_response_time"])
        
        for test_type, data in self.test_results["load_tests"].items():
            if "avg_response_time" in data:
                all_response_times.append(data["avg_response_time"])
        
        if all_response_times:
            print(f"Average Response Time: {statistics.mean(all_response_times):.3f}s")
            print(f"Fastest Response: {min(all_response_times):.3f}s")
            print(f"Slowest Response: {max(all_response_times):.3f}s")
        
        print()
        print("🔍 STRESS TEST ASSESSMENT:")
        if success_rate >= 95:
            print("🎉 EXCELLENT: System passed all stress tests!")
            print("   The system is ready for production use.")
        elif success_rate >= 80:
            print("⚠️  GOOD: System passed most stress tests.")
            print("   Minor issues detected but system is functional.")
        elif success_rate >= 60:
            print("⚠️  FAIR: System passed some stress tests.")
            print("   Significant issues detected, needs improvement.")
        else:
            print("❌ POOR: System failed most stress tests.")
            print("   Major issues detected, not ready for production.")
        
        # Save detailed results
        with open('stress_test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print()
        print(f"📄 Detailed results saved to: stress_test_results.json")

async def main():
    """Main stress test runner."""
    tester = TradingSystemStressTester()
    await tester.run_comprehensive_stress_test()

if __name__ == "__main__":
    asyncio.run(main())
