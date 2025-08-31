#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Autonomous Trading System
Tests all components to ensure they work as expected.
"""

import asyncio
import requests
import json
import time
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

class TradingSystemTester:
    """Comprehensive testing suite for the trading system."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.failed_tests = []
        self.auth_token = None
    
    def get_auth_headers(self):
        """Get authentication headers if token is available."""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        if not success:
            self.failed_tests.append(test_name)
    
    def test_server_health(self) -> bool:
        """Test if the server is running and healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Server Health Check", True, f"Status: {data.get('status')}")
                return True
            else:
                self.log_test("Server Health Check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Server Health Check", False, f"Error: {str(e)}")
            return False
    
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Root Endpoint", True, f"Message: {data.get('message')}")
                return True
            else:
                self.log_test("Root Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_metrics_endpoint(self) -> bool:
        """Test the metrics endpoint."""
        try:
            response = requests.get(f"{self.base_url}/metrics", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Metrics Endpoint", True, "Metrics retrieved successfully")
                return True
            else:
                self.log_test("Metrics Endpoint", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Metrics Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_authentication(self) -> bool:
        """Test authentication system."""
        try:
            # Test login with correct credentials (admin/password)
            login_data = {
                "username": "admin",
                "password": "password"
            }
            response = requests.post(f"{self.base_url}/api/v1/auth/login", data=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.log_test("Authentication System", True, "Login successful with admin/password")
                return True
            else:
                self.log_test("Authentication System", False, f"Login failed: HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Authentication System", False, f"Error: {str(e)}")
            return False
    
    def test_market_data(self) -> bool:
        """Test market data retrieval."""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            response = requests.get(f"{self.base_url}/api/v1/data/market-data/EURUSD", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Market Data (EURUSD)", True, "Market data retrieved successfully")
                return True
            else:
                self.log_test("Market Data (EURUSD)", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Market Data (EURUSD)", False, f"Error: {str(e)}")
            return False
    
    def test_ai_analysis(self) -> bool:
        """Test AI market analysis."""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            response = requests.post(
                f"{self.base_url}/api/v1/ai/analyze-market",
                json={"pair": "EURUSD", "timeframe": "H1"},
                headers=headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.log_test("AI Market Analysis", True, "AI analysis completed successfully")
                return True
            else:
                self.log_test("AI Market Analysis", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("AI Market Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_strategy_generation(self) -> bool:
        """Test AI strategy generation."""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/ai/generate-strategy",
                json={"pair": "EURUSD", "market_condition": "trending"},
                headers=self.get_auth_headers(),
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.log_test("AI Strategy Generation", True, "Strategy generation completed successfully")
                return True
            else:
                self.log_test("AI Strategy Generation", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("AI Strategy Generation", False, f"Error: {str(e)}")
            return False
    
    def test_trading_execution(self) -> bool:
        """Test trading execution."""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/trading/execute-signal",
                json={
                    "pair": "EURUSD",
                    "side": "BUY",
                    "amount": 1000,
                    "strategy": "test_strategy"
                },
                headers=self.get_auth_headers(),
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.log_test("Trading Execution", True, "Trading execution completed successfully")
                return True
            else:
                self.log_test("Trading Execution", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Trading Execution", False, f"Error: {str(e)}")
            return False
    
    def test_portfolio_metrics(self) -> bool:
        """Test portfolio metrics."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/portfolio/portfolio/metrics", headers=self.get_auth_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Portfolio Metrics", True, "Portfolio metrics retrieved successfully")
                return True
            else:
                self.log_test("Portfolio Metrics", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Portfolio Metrics", False, f"Error: {str(e)}")
            return False
    
    def test_risk_metrics(self) -> bool:
        """Test risk metrics."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/risk/metrics", headers=self.get_auth_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Risk Metrics", True, "Risk metrics retrieved successfully")
                return True
            else:
                self.log_test("Risk Metrics", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Risk Metrics", False, f"Error: {str(e)}")
            return False
    
    def test_strategies_list(self) -> bool:
        """Test strategies listing."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/strategies/strategies", headers=self.get_auth_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Strategies List", True, "Strategies list retrieved successfully")
                return True
            else:
                self.log_test("Strategies List", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Strategies List", False, f"Error: {str(e)}")
            return False
    
    def test_monitoring_health(self) -> bool:
        """Test monitoring health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/monitoring/health", headers=self.get_auth_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Monitoring Health", True, "Monitoring health check successful")
                return True
            else:
                self.log_test("Monitoring Health", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Monitoring Health", False, f"Error: {str(e)}")
            return False
    
    def test_news_data(self) -> bool:
        """Test news data endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/data/news", headers=self.get_auth_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("News Data", True, "News data retrieved successfully")
                return True
            else:
                self.log_test("News Data", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("News Data", False, f"Error: {str(e)}")
            return False
    
    def test_api_documentation(self) -> bool:
        """Test API documentation accessibility."""
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            if response.status_code == 200:
                self.log_test("API Documentation", True, "Swagger docs accessible")
                return True
            else:
                self.log_test("API Documentation", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Documentation", False, f"Error: {str(e)}")
            return False
    
    def test_emergency_endpoints(self) -> bool:
        """Test emergency endpoints."""
        try:
            # Test emergency pause (should fail without auth, but endpoint should exist)
            response = requests.post(f"{self.base_url}/emergency/pause", timeout=10)
            if response.status_code in [401, 403]:  # Unauthorized/Forbidden is expected
                self.log_test("Emergency Endpoints", True, "Emergency endpoints accessible (auth required)")
                return True
            else:
                self.log_test("Emergency Endpoints", False, f"Unexpected response: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Emergency Endpoints", False, f"Error: {str(e)}")
            return False
    
    def run_comprehensive_test(self):
        """Run all tests and provide comprehensive report."""
        print("🧪 COMPREHENSIVE TRADING SYSTEM TEST SUITE")
        print("=" * 60)
        print(f"Testing started at: {datetime.now(timezone.utc).isoformat()}")
        print()
        
        # Core system tests
        print("🔧 CORE SYSTEM TESTS:")
        print("-" * 30)
        self.test_server_health()
        self.test_root_endpoint()
        self.test_metrics_endpoint()
        self.test_api_documentation()
        
        print()
        print("🔐 AUTHENTICATION TESTS:")
        print("-" * 30)
        self.test_authentication()
        
        print()
        print("💰 TRADING INTEGRATION TESTS:")
        print("-" * 30)
        self.test_market_data()
        
        print()
        print("🤖 AI & STRATEGY TESTS:")
        print("-" * 30)
        self.test_ai_analysis()
        self.test_strategy_generation()
        self.test_strategies_list()
        
        print()
        print("📊 TRADING EXECUTION TESTS:")
        print("-" * 30)
        self.test_trading_execution()
        self.test_portfolio_metrics()
        
        print()
        print("⚠️  RISK & MONITORING TESTS:")
        print("-" * 30)
        self.test_risk_metrics()
        self.test_monitoring_health()
        self.test_emergency_endpoints()
        
        print()
        print("📰 NEWS & DATA TESTS:")
        print("-" * 30)
        self.test_news_data()
        
        # Generate comprehensive report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report."""
        print()
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print()
            print("❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"  • {test}")
        
        print()
        print("🔍 SYSTEM STATUS ASSESSMENT:")
        if passed_tests == total_tests:
            print("🎉 EXCELLENT: All systems operational!")
            print("   The autonomous trading system is ready for live trading.")
        elif passed_tests >= total_tests * 0.8:
            print("⚠️  GOOD: Most systems operational with minor issues.")
            print("   The system can function but some features may be limited.")
        elif passed_tests >= total_tests * 0.6:
            print("⚠️  FAIR: Core systems working but significant issues exist.")
            print("   Basic functionality available but advanced features may fail.")
        else:
            print("❌ POOR: Major system issues detected.")
            print("   The system needs significant fixes before use.")
        
        # Save detailed results
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print()
        print(f"📄 Detailed results saved to: test_results.json")

def main():
    """Main test runner."""
    tester = TradingSystemTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
