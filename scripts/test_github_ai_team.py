#!/usr/bin/env python3
"""
Test script for GitHub AI Team integration
Verifies that the multi-model AI ensemble is working correctly
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.github_ai_team import GitHubAITeam


async def test_github_ai_team():
    """Test the GitHub AI Team integration"""
    print("🚀 Testing GitHub AI Team Integration")
    print("=" * 50)
    
    # Check if GITHUB_TOKEN is set
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token:")
        print("export GITHUB_TOKEN='your_github_token_here'")
        return False
    
    try:
        # Initialize the AI team
        print("📋 Initializing GitHub AI Team...")
        ai_team = GitHubAITeam()
        print(f"✅ AI Team initialized with {len(ai_team.ai_agents)} agents")
        
        # Display team members
        print("\n🤖 AI Team Members:")
        for agent_id, agent in ai_team.ai_agents.items():
            print(f"  • {agent.name} ({agent.model})")
            print(f"    Role: {agent.role}")
            print(f"    Capabilities: {', '.join(agent.capabilities)}")
            print()
        
        # Test market analysis
        print("📊 Testing Market Analysis...")
        market_data = {
            "symbol": "EUR_USD",
            "timeframe": "1h",
            "price_data": {
                "current_price": 1.0850,
                "open": 1.0845,
                "high": 1.0860,
                "low": 1.0840,
                "volume": 1000000,
                "change": 0.0005,
                "change_percent": 0.046
            },
            "technical_indicators": {
                "rsi": 65.5,
                "macd": 0.002,
                "bollinger_bands": {
                    "upper": 1.0870,
                    "middle": 1.0850,
                    "lower": 1.0830
                }
            },
            "news_sentiment": {
                "overall": "positive",
                "score": 0.7,
                "recent_news": [
                    "ECB maintains interest rates",
                    "US economic data shows strength"
                ]
            }
        }
        
        analysis_result = await ai_team.analyze_market_conditions(market_data)
        print("✅ Market analysis completed")
        print(f"   Confidence Score: {analysis_result.get('confidence_score', 0):.2f}")
        
        # Test strategy generation
        print("\n🎯 Testing Strategy Generation...")
        strategy_result = await ai_team.generate_trading_strategy(market_data)
        print("✅ Strategy generation completed")
        
        # Test risk assessment
        print("\n⚠️ Testing Risk Assessment...")
        position_data = {
            "symbol": "EUR_USD",
            "position_size": 10000,
            "entry_price": 1.0850,
            "current_price": 1.0855,
            "unrealized_pnl": 50
        }
        risk_result = await ai_team.assess_risk(position_data)
        print("✅ Risk assessment completed")
        print(f"   Overall Risk Score: {risk_result.get('overall_risk_score', 0):.2f}")
        
        # Test trading decision
        print("\n🎲 Testing Trading Decision...")
        decision_result = await ai_team.make_trading_decision(analysis_result)
        print("✅ Trading decision completed")
        print(f"   Confidence: {decision_result.get('confidence', 0):.2f}")
        print(f"   Execution Priority: {decision_result.get('execution_priority', 'unknown')}")
        
        # Test individual agent
        print("\n🧪 Testing Individual Agent...")
        agent = ai_team.ai_agents["strategist"]
        test_prompt = "What is the current market sentiment for EUR/USD?"
        response = await ai_team._call_ai_model(agent, test_prompt)
        print("✅ Individual agent test completed")
        print(f"   Response length: {len(response)} characters")
        
        # Save test results
        test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_status": "success",
            "ai_team_agents": len(ai_team.ai_agents),
            "market_analysis": {
                "confidence_score": analysis_result.get('confidence_score', 0),
                "has_consensus": 'consensus' in analysis_result
            },
            "strategy_generation": {
                "status": "completed",
                "has_strategy": bool(strategy_result)
            },
            "risk_assessment": {
                "overall_risk_score": risk_result.get('overall_risk_score', 0),
                "has_risk_data": bool(risk_result)
            },
            "trading_decision": {
                "confidence": decision_result.get('confidence', 0),
                "execution_priority": decision_result.get('execution_priority', 'unknown')
            },
            "individual_agent": {
                "response_length": len(response),
                "agent_name": agent.name,
                "model": agent.model
            }
        }
        
        with open("github_ai_team_test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        
        print("\n📄 Test results saved to github_ai_team_test_results.json")
        
        # Summary
        print("\n🎉 GitHub AI Team Integration Test Summary:")
        print("=" * 50)
        print(f"✅ AI Team Initialization: SUCCESS ({len(ai_team.ai_agents)} agents)")
        print(f"✅ Market Analysis: SUCCESS (confidence: {analysis_result.get('confidence_score', 0):.2f})")
        print(f"✅ Strategy Generation: SUCCESS")
        print(f"✅ Risk Assessment: SUCCESS (risk score: {risk_result.get('overall_risk_score', 0):.2f})")
        print(f"✅ Trading Decision: SUCCESS (confidence: {decision_result.get('confidence', 0):.2f})")
        print(f"✅ Individual Agent Test: SUCCESS")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_ai_models_availability():
    """Test which AI models are available"""
    print("\n🔍 Testing AI Models Availability")
    print("=" * 50)
    
    models_to_test = [
        "openai/gpt-5",
        "anthropic/claude-3.5-sonnet",
        "meta-llama/llama-3.1-8b",
        "mistralai/mistral-7b-instruct",
        "codellama/codellama-70b-instruct",
        "microsoft/phi-3.5",
        "openai/gpt-4o-mini",
        "anthropic/claude-3-haiku"
    ]
    
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ GITHUB_TOKEN not set, skipping model availability test")
        return
    
    try:
        ai_team = GitHubAITeam()
        
        for model in models_to_test:
            try:
                # Test with a simple prompt
                test_prompt = "Hello, this is a test message."
                
                # Create a temporary agent for testing
                from src.services.github_ai_team import AIAgent
                temp_agent = AIAgent(
                    name="Test Agent",
                    model=model,
                    role="Testing model availability",
                    capabilities=["test"],
                    temperature=0.1,
                    max_tokens=50
                )
                
                response = await ai_team._call_ai_model(temp_agent, test_prompt)
                print(f"✅ {model}: Available (response: {len(response)} chars)")
                
            except Exception as e:
                print(f"❌ {model}: Not available ({str(e)[:50]}...)")
                
    except Exception as e:
        print(f"❌ Error testing model availability: {e}")


async def main():
    """Main test function"""
    print("🚀 GitHub AI Team Integration Test Suite")
    print("=" * 60)
    
    # Test basic functionality
    success = await test_github_ai_team()
    
    # Test model availability
    await test_ai_models_availability()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("The GitHub AI Team is ready for trading analysis!")
    else:
        print("\n❌ Some tests failed. Please check the configuration.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
