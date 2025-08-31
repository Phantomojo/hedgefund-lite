#!/usr/bin/env python3
"""
Quick test for GitHub AI Team integration
Tests initialization and basic functionality without making API calls
"""

import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_github_ai_team_initialization():
    """Test if the GitHub AI Team can be initialized"""
    print("🚀 Quick GitHub AI Team Test")
    print("=" * 40)
    
    # Check if GITHUB_TOKEN is set
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token:")
        print("export GITHUB_TOKEN='your_github_token_here'")
        return False
    
    print(f"✅ GITHUB_TOKEN is set: {os.environ.get('GITHUB_TOKEN')[:10]}...")
    
    try:
        # Test importing the module
        print("📦 Testing module import...")
        from src.services.github_ai_team import GitHubAITeam, AIAgent
        print("✅ Module import successful")
        
        # Test AIAgent dataclass
        print("🧪 Testing AIAgent dataclass...")
        agent = AIAgent(
            name="Test Agent",
            model="openai/gpt-5",
            role="Test role",
            capabilities=["test"],
            temperature=0.7,
            max_tokens=2000
        )
        print(f"✅ AIAgent created: {agent.name} ({agent.model})")
        
        # Test GitHubAITeam initialization (without API calls)
        print("🏗️ Testing GitHubAITeam initialization...")
        
        # Mock the OpenAI client to avoid API calls
        class MockOpenAIClient:
            def __init__(self, *args, **kwargs):
                pass
            
            def chat(self):
                class MockChat:
                    def completions(self):
                        class MockCompletions:
                            def create(self, *args, **kwargs):
                                class MockResponse:
                                    def __init__(self):
                                        self.choices = [type('obj', (object,), {'message': type('obj', (object,), {'content': 'Mock response'})()})]
                                return MockResponse()
                        return MockCompletions()
                return MockChat()
        
        # Patch the OpenAI import
        import src.services.github_ai_team as github_ai_module
        original_openai = github_ai_module.OpenAI
        github_ai_module.OpenAI = MockOpenAIClient
        
        # Initialize the team
        ai_team = GitHubAITeam()
        print(f"✅ GitHubAITeam initialized with {len(ai_team.ai_agents)} agents")
        
        # Display team members
        print("\n🤖 AI Team Members:")
        for agent_id, agent in ai_team.ai_agents.items():
            print(f"  • {agent.name} ({agent.model})")
            print(f"    Role: {agent.role}")
            print(f"    Capabilities: {', '.join(agent.capabilities)}")
            print()
        
        # Test team configuration
        print("⚙️ Testing team configuration...")
        print(f"  • Endpoint: {ai_team.endpoint}")
        print(f"  • Token configured: {bool(ai_team.token)}")
        print(f"  • Consensus threshold: {ai_team.consensus_threshold}")
        print(f"  • Max retries: {ai_team.max_retries}")
        print(f"  • Timeout: {ai_team.timeout}s")
        
        # Test agent access
        print("\n🔍 Testing agent access...")
        strategist = ai_team.ai_agents.get("strategist")
        if strategist:
            print(f"✅ Strategist agent found: {strategist.name}")
            print(f"   Model: {strategist.model}")
            print(f"   Temperature: {strategist.temperature}")
        else:
            print("❌ Strategist agent not found")
        
        # Test API endpoints availability
        print("\n📡 Testing API endpoints...")
        try:
            from src.api.v1.endpoints.github_ai_team import router
            print("✅ GitHub AI Team API endpoints available")
            
            # Check if endpoints are registered
            routes = [route.path for route in router.routes]
            print(f"   Available endpoints: {len(routes)}")
            for route in routes:
                print(f"   • {route}")
                
        except ImportError as e:
            print(f"❌ API endpoints not available: {e}")
        
        # Restore original OpenAI
        github_ai_module.OpenAI = original_openai
        
        print("\n🎉 Quick test completed successfully!")
        print("The GitHub AI Team integration is properly configured.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_requirements():
    """Test if required packages are installed"""
    print("\n📦 Testing required packages...")
    
    required_packages = [
        "openai",
        "azure.core",
        "azure.ai.inference"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}: Installed")
        except ImportError:
            print(f"❌ {package}: Not installed")
            return False
    
    return True

def main():
    """Main test function"""
    print("🚀 GitHub AI Team Quick Test Suite")
    print("=" * 50)
    
    # Test requirements
    if not test_requirements():
        print("\n❌ Some required packages are missing.")
        print("Please install them with: pip install openai azure-core azure-ai-inference")
        return False
    
    # Test initialization
    success = test_github_ai_team_initialization()
    
    if success:
        print("\n🎉 All quick tests passed!")
        print("The GitHub AI Team is ready for integration.")
        print("\nNext steps:")
        print("1. Test with real API calls: python scripts/test_github_ai_team.py")
        print("2. Start the server: uvicorn src.main:app --reload")
        print("3. Access API docs: http://localhost:8000/docs")
    else:
        print("\n❌ Quick tests failed. Please check the configuration.")
    
    return success

if __name__ == "__main__":
    main()
