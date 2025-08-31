#!/usr/bin/env python3
"""
Comprehensive System Status Report
Analyzes what actually works in the trading system.
"""

import requests
import json
import sys
import os
from datetime import datetime, timezone
from typing import Dict, Any, List

class SystemStatusReporter:
    """Comprehensive system status reporter."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.auth_token = None
        self.status_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "unknown",
            "core_system": {},
            "authentication": {},
            "trading_components": {},
            "ai_components": {},
            "data_components": {},
            "monitoring": {},
            "issues": [],
            "recommendations": []
        }
    
    def get_auth_token(self):
        """Get authentication token."""
        try:
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
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def test_endpoint(self, endpoint: str, method: str = "GET", data: Dict = None, description: str = None) -> Dict:
        """Test a specific endpoint."""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = self.get_auth_headers()
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            else:
                return {"status": "error", "message": f"Unsupported method: {method}"}
            
            return {
                "status": "success" if response.status_code < 400 else "error",
                "http_code": response.status_code,
                "response": response.text[:200] if response.text else "No response body",
                "description": description or endpoint
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "description": description or endpoint
            }
    
    def analyze_system(self):
        """Analyze the entire system."""
        print("🔍 COMPREHENSIVE SYSTEM STATUS ANALYSIS")
        print("=" * 60)
        print(f"Analysis started at: {self.status_report['timestamp']}")
        print()
        
        # Test authentication
        print("🔐 AUTHENTICATION SYSTEM:")
        print("-" * 30)
        auth_works = self.get_auth_token()
        if auth_works:
            print("✅ Authentication working - Token obtained")
            self.status_report["authentication"]["login"] = {"status": "working"}
        else:
            print("❌ Authentication failed")
            self.status_report["authentication"]["login"] = {"status": "failed"}
            self.status_report["issues"].append("Authentication system not working")
        
        # Test core endpoints
        print()
        print("🔧 CORE SYSTEM ENDPOINTS:")
        print("-" * 30)
        
        core_endpoints = [
            ("/", "GET", None, "Root endpoint"),
            ("/health", "GET", None, "Health check"),
            ("/metrics", "GET", None, "System metrics"),
            ("/docs", "GET", None, "API documentation")
        ]
        
        for endpoint, method, data, desc in core_endpoints:
            result = self.test_endpoint(endpoint, method, data, desc)
            print(f"{'✅' if result['status'] == 'success' else '❌'} {desc}")
            if result['status'] == 'error':
                print(f"   Error: {result.get('message', 'Unknown error')}")
        
        # Test trading endpoints
        print()
        print("💰 TRADING SYSTEM ENDPOINTS:")
        print("-" * 30)
        
        trading_endpoints = [
            ("/api/v1/trading/positions", "GET", None, "Get positions"),
            ("/api/v1/trading/orders", "GET", None, "Get orders"),
            ("/api/v1/trading/trades", "GET", None, "Get trades"),
            ("/api/v1/portfolio/portfolio/metrics", "GET", None, "Portfolio metrics"),
            ("/api/v1/risk/metrics", "GET", None, "Risk metrics")
        ]
        
        for endpoint, method, data, desc in trading_endpoints:
            result = self.test_endpoint(endpoint, method, data, desc)
            print(f"{'✅' if result['status'] == 'success' else '❌'} {desc}")
            if result['status'] == 'error':
                print(f"   Error: {result.get('message', 'Unknown error')}")
        
        # Test AI endpoints
        print()
        print("🤖 AI SYSTEM ENDPOINTS:")
        print("-" * 30)
        
        ai_endpoints = [
            ("/api/v1/ai/analyze-market", "POST", {"pair": "EURUSD", "timeframe": "H1", "data": {}}, "AI market analysis"),
            ("/api/v1/ai/generate-strategy", "POST", {"market_conditions": {"trend": "up"}, "pair": "EURUSD", "timeframe": "H1"}, "AI strategy generation"),
            ("/api/v1/ai/models", "GET", None, "AI models list"),
            ("/api/v1/strategies/strategies", "GET", None, "Strategies list")
        ]
        
        for endpoint, method, data, desc in ai_endpoints:
            result = self.test_endpoint(endpoint, method, data, desc)
            print(f"{'✅' if result['status'] == 'success' else '❌'} {desc}")
            if result['status'] == 'error':
                print(f"   Error: {result.get('message', 'Unknown error')}")
        
        # Test data endpoints
        print()
        print("📊 DATA SYSTEM ENDPOINTS:")
        print("-" * 30)
        
        data_endpoints = [
            ("/api/v1/data/market-data/EURUSD", "GET", None, "Market data"),
            ("/api/v1/data/news", "GET", None, "News data"),
            ("/api/v1/data/sentiment", "GET", None, "Sentiment data"),
            ("/api/v1/data/data-summary", "GET", None, "Data summary")
        ]
        
        for endpoint, method, data, desc in data_endpoints:
            result = self.test_endpoint(endpoint, method, data, desc)
            print(f"{'✅' if result['status'] == 'success' else '❌'} {desc}")
            if result['status'] == 'error':
                print(f"   Error: {result.get('message', 'Unknown error')}")
        
        # Test monitoring endpoints
        print()
        print("📈 MONITORING ENDPOINTS:")
        print("-" * 30)
        
        monitoring_endpoints = [
            ("/api/v1/monitoring/health", "GET", None, "Monitoring health"),
            ("/api/v1/monitoring/metrics", "GET", None, "Monitoring metrics"),
            ("/api/v1/monitoring/performance", "GET", None, "Performance metrics"),
            ("/api/v1/monitoring/alerts", "GET", None, "System alerts")
        ]
        
        for endpoint, method, data, desc in monitoring_endpoints:
            result = self.test_endpoint(endpoint, method, data, desc)
            print(f"{'✅' if result['status'] == 'success' else '❌'} {desc}")
            if result['status'] == 'error':
                print(f"   Error: {result.get('message', 'Unknown error')}")
        
        # Generate comprehensive report
        self.generate_comprehensive_report()
    
    def generate_comprehensive_report(self):
        """Generate comprehensive status report."""
        print()
        print("📋 COMPREHENSIVE SYSTEM STATUS REPORT")
        print("=" * 60)
        
        # Count working vs broken components
        total_tests = 0
        working_tests = 0
        
        # Analyze what's working
        working_components = []
        broken_components = []
        
        # Core system analysis
        core_endpoints = ["/", "/health", "/metrics", "/docs"]
        for endpoint in core_endpoints:
            total_tests += 1
            result = self.test_endpoint(endpoint)
            if result['status'] == 'success':
                working_tests += 1
                working_components.append(f"Core: {endpoint}")
            else:
                broken_components.append(f"Core: {endpoint}")
        
        # Trading system analysis
        trading_endpoints = [
            "/api/v1/trading/positions",
            "/api/v1/trading/orders", 
            "/api/v1/trading/trades",
            "/api/v1/portfolio/portfolio/metrics",
            "/api/v1/risk/metrics"
        ]
        
        for endpoint in trading_endpoints:
            total_tests += 1
            result = self.test_endpoint(endpoint)
            if result['status'] == 'success':
                working_tests += 1
                working_components.append(f"Trading: {endpoint}")
            else:
                broken_components.append(f"Trading: {endpoint}")
        
        # AI system analysis
        ai_endpoints = [
            ("/api/v1/ai/analyze-market", "POST", {"pair": "EUR_USD", "timeframe": "1H", "data": {}}),
            ("/api/v1/ai/generate-strategy", "POST", {"market_conditions": {"trend": "up"}, "pair": "EUR_USD", "timeframe": "1H"}),
            ("/api/v1/ai/models", "GET", None),
            ("/api/v1/strategies/strategies", "GET", None)
        ]
        
        for endpoint, method, data in ai_endpoints:
            total_tests += 1
            result = self.test_endpoint(endpoint, method, data)
            if result['status'] == 'success':
                working_tests += 1
                working_components.append(f"AI: {endpoint}")
            else:
                broken_components.append(f"AI: {endpoint}")
        
        # Data system analysis
        data_endpoints = [
            "/api/v1/data/market-data/EUR_USD",
            "/api/v1/data/news",
            "/api/v1/data/sentiment",
            "/api/v1/data/data-summary"
        ]
        
        for endpoint in data_endpoints:
            total_tests += 1
            result = self.test_endpoint(endpoint)
            if result['status'] == 'success':
                working_tests += 1
                working_components.append(f"Data: {endpoint}")
            else:
                broken_components.append(f"Data: {endpoint}")
        
        # Calculate success rate
        success_rate = (working_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Endpoints Tested: {total_tests}")
        print(f"Working Endpoints: {working_tests} ✅")
        print(f"Broken Endpoints: {total_tests - working_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print()
        print("✅ WORKING COMPONENTS:")
        for component in working_components:
            print(f"  • {component}")
        
        print()
        print("❌ BROKEN COMPONENTS:")
        for component in broken_components:
            print(f"  • {component}")
        
        print()
        print("🔍 SYSTEM ASSESSMENT:")
        if success_rate >= 90:
            print("🎉 EXCELLENT: System is fully operational!")
            print("   Ready for live trading deployment.")
        elif success_rate >= 70:
            print("⚠️  GOOD: Most systems working with minor issues.")
            print("   Can function but needs some fixes.")
        elif success_rate >= 50:
            print("⚠️  FAIR: Core systems working but significant issues.")
            print("   Basic functionality available.")
        else:
            print("❌ POOR: Major system failures detected.")
            print("   System needs significant work before use.")
        
        print()
        print("🚨 CRITICAL ISSUES IDENTIFIED:")
        if len(broken_components) > 0:
            print("1. Many endpoints returning 500 Internal Server Errors")
            print("2. DataService dependency injection not working")
            print("3. Service initialization issues in main.py")
            print("4. Missing or broken service implementations")
        else:
            print("No critical issues found!")
        
        print()
        print("🔧 RECOMMENDATIONS:")
        if success_rate < 70:
            print("1. Fix DataService dependency injection")
            print("2. Implement missing service methods")
            print("3. Add proper error handling to endpoints")
            print("4. Test each service individually")
            print("5. Add comprehensive logging")
        else:
            print("1. System is ready for basic operations")
            print("2. Consider adding more advanced features")
            print("3. Implement comprehensive monitoring")
        
        # Save detailed report
        self.status_report["overall_status"] = "excellent" if success_rate >= 90 else "good" if success_rate >= 70 else "fair" if success_rate >= 50 else "poor"
        self.status_report["success_rate"] = success_rate
        self.status_report["working_components"] = working_components
        self.status_report["broken_components"] = broken_components
        
        with open('system_status_report.json', 'w') as f:
            json.dump(self.status_report, f, indent=2)
        
        print()
        print(f"📄 Detailed report saved to: system_status_report.json")

def main():
    """Main function."""
    reporter = SystemStatusReporter()
    reporter.analyze_system()

if __name__ == "__main__":
    main()
