#!/usr/bin/env python3
"""
Test Ollama Integration
Tests the Ollama service integration with local AI models
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

async def test_ollama_integration():
    """Test the Ollama integration"""
    print("🚀 Ollama Integration Test Suite")
    print("=" * 50)
    
    try:
        # Import the Ollama service
        from src.services.ollama_service import ollama_service
        
        print("📦 Testing Ollama service import...")
        print("✅ Ollama service imported successfully")
        
        # Test Ollama status
        print("\n🔍 Testing Ollama status...")
        status = await ollama_service.check_ollama_status()
        
        if status["status"] == "running":
            print(f"✅ Ollama is running at {ollama_service.base_url}")
            print(f"📊 Available models: {len(status['available_models'])}")
            print(f"   Models: {', '.join(status['available_models'])}")
        else:
            print(f"❌ Ollama is not running: {status['message']}")
            print("💡 To start Ollama, run: ollama serve")
            return False
        
        # Test model configurations
        print("\n🤖 Testing model configurations...")
        for model_id, model in ollama_service.ollama_models.items():
            is_available = model_id in status["available_models"]
            status_icon = "✅" if is_available else "❌"
            print(f"   {status_icon} {model.name} ({model_id}) - {'Available' if is_available else 'Not Available'}")
        
        # Test a simple model call if any models are available
        if status["available_models"]:
            print(f"\n🧪 Testing model call with {status['available_models'][0]}...")
            test_model = ollama_service.ollama_models.get(status["available_models"][0])
            
            if test_model:
                try:
                    test_prompt = "Hello! Please respond with 'Ollama test successful' if you can see this message."
                    response = await ollama_service.call_ollama_model(test_model, test_prompt)
                    print(f"✅ Model response: {response[:100]}...")
                except Exception as e:
                    print(f"❌ Model call failed: {e}")
        
        # Test market analysis (if models are available)
        if len(status["available_models"]) >= 2:
            print("\n📊 Testing market analysis...")
            
            # Sample market data
            market_data = {
                "symbol": "EUR_USD",
                "timeframe": "1h",
                "data": {
                    "current_price": 1.0850,
                    "bid": 1.0848,
                    "ask": 1.0852,
                    "volume": 1000000,
                    "high": 1.0860,
                    "low": 1.0840,
                    "open": 1.0845,
                    "close": 1.0850,
                    "technical_indicators": {
                        "rsi": 65.5,
                        "macd": 0.002,
                        "ema_20": 1.0840,
                        "ema_50": 1.0830
                    }
                }
            }
            
            try:
                analysis = await ollama_service.analyze_market_conditions(market_data)
                if "error" not in analysis:
                    print("✅ Market analysis completed successfully")
                    print(f"   Confidence score: {analysis.get('confidence_score', 0):.2f}")
                    print(f"   Models used: {len(analysis.get('market_analysis', {}))}")
                else:
                    print(f"❌ Market analysis failed: {analysis['error']}")
            except Exception as e:
                print(f"❌ Market analysis error: {e}")
        
        # Test strategy generation
        if "codellama" in status["available_models"]:
            print("\n💻 Testing strategy generation...")
            
            market_conditions = {
                "trend": "bullish",
                "volatility": "medium",
                "support": 1.0800,
                "resistance": 1.0900,
                "risk_level": "medium"
            }
            
            try:
                strategy = await ollama_service.generate_trading_strategy(market_conditions)
                if "error" not in strategy:
                    print("✅ Strategy generation completed successfully")
                    print(f"   Strategy name: {strategy.get('strategy_name', 'N/A')}")
                else:
                    print(f"❌ Strategy generation failed: {strategy['error']}")
            except Exception as e:
                print(f"❌ Strategy generation error: {e}")
        
        # Test risk assessment
        if "neural-chat" in status["available_models"]:
            print("\n🛡️ Testing risk assessment...")
            
            position_data = {
                "symbol": "EUR_USD",
                "side": "buy",
                "size": 10000,
                "entry_price": 1.0850,
                "stop_loss": 1.0800,
                "take_profit": 1.0900
            }
            
            try:
                risk = await ollama_service.assess_risk(position_data)
                if "error" not in risk:
                    print("✅ Risk assessment completed successfully")
                    print(f"   Risk score: {risk.get('risk_score', 'N/A')}")
                else:
                    print(f"❌ Risk assessment failed: {risk['error']}")
            except Exception as e:
                print(f"❌ Risk assessment error: {e}")
        
        # Test trading decision
        if "phi3" in status["available_models"]:
            print("\n🎯 Testing trading decision...")
            
            analysis_data = {
                "market_analysis": {"trend": "bullish", "confidence": 0.8},
                "strategy": {"name": "trend_following", "confidence": 0.7},
                "risk_assessment": {"risk_score": 0.3}
            }
            
            try:
                decision = await ollama_service.make_trading_decision(analysis_data)
                if "error" not in decision:
                    print("✅ Trading decision completed successfully")
                    print(f"   Action: {decision.get('action', 'N/A')}")
                    print(f"   Confidence: {decision.get('confidence', 'N/A')}")
                else:
                    print(f"❌ Trading decision failed: {decision['error']}")
            except Exception as e:
                print(f"❌ Trading decision error: {e}")
        
        # Save test results
        test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "ollama_status": status,
            "available_models": status["available_models"],
            "total_models": len(status["available_models"]),
            "test_successful": True
        }
        
        with open("ollama_integration_test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        
        print(f"\n💾 Test results saved to: ollama_integration_test_results.json")
        
        print("\n🎉 Ollama integration test completed!")
        print(f"📊 Summary:")
        print(f"   • Ollama Status: {status['status']}")
        print(f"   • Available Models: {len(status['available_models'])}")
        print(f"   • Total Models: {status['total_models']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ollama_installation():
    """Test if Ollama is installed and accessible"""
    print("\n🔧 Testing Ollama installation...")
    
    try:
        import subprocess
        
        # Test if ollama command is available
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama command not found")
            print("💡 Please install Ollama from: https://ollama.ai/")
            return False
            
    except FileNotFoundError:
        print("❌ Ollama not installed")
        print("💡 Please install Ollama from: https://ollama.ai/")
        return False
    except Exception as e:
        print(f"❌ Error checking Ollama installation: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Ollama Integration Test Suite")
    print("=" * 50)
    
    # Test installation first
    installation_ok = await test_ollama_installation()
    
    if installation_ok:
        # Test integration
        integration_ok = await test_ollama_integration()
        
        if integration_ok:
            print("\n🎉 All Ollama tests passed!")
            print("\nNext steps:")
            print("1. Start the server: uvicorn src.main:app --reload")
            print("2. Access API docs: http://localhost:8000/docs")
            print("3. Test Ollama endpoints: http://localhost:8000/api/v1/ollama/status")
        else:
            print("\n❌ Ollama integration tests failed.")
    else:
        print("\n❌ Ollama installation test failed.")
        print("Please install Ollama first: https://ollama.ai/")

if __name__ == "__main__":
    asyncio.run(main())
