#!/usr/bin/env python3
"""
AI Model Download Script
Downloads priority AI models for the trading system
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.ai_model_manager import ai_model_manager

async def download_priority_models():
    """Download priority AI models."""
    print("🚀 Starting AI model downloads...")
    print("📊 Priority models to download:")
    
    # Get priority models
    priority_models = [
        name for name, config in ai_model_manager.model_configs.items() 
        if config["priority"] == 1
    ]
    
    for model_name in priority_models:
        config = ai_model_manager.model_configs[model_name]
        print(f"  - {model_name}: {config['description']} ({config['size_gb']}GB)")
    
    print("\n⏳ Downloading models (this may take a while)...")
    
    # Download models
    results = await ai_model_manager.download_priority_models()
    
    print("\n📋 Download Results:")
    for model_name, success in results.items():
        status = "✅ Success" if success else "❌ Failed"
        print(f"  {model_name}: {status}")
    
    # Show final status
    status = ai_model_manager.get_model_status()
    print(f"\n🎯 Final Status:")
    print(f"  Total models: {status['total_models']}")
    print(f"  Loaded models: {status['loaded_models']}")
    print(f"  Total size: {status['total_size_gb']:.1f}GB")
    
    return results

async def download_specific_model(model_name: str):
    """Download a specific model."""
    print(f"🚀 Downloading {model_name}...")
    
    if model_name not in ai_model_manager.model_configs:
        print(f"❌ Model {model_name} not found in configurations")
        return False
    
    config = ai_model_manager.model_configs[model_name]
    print(f"📊 Model: {config['description']} ({config['size_gb']}GB)")
    
    success = await ai_model_manager.download_model(model_name)
    
    if success:
        print(f"✅ {model_name} downloaded successfully")
    else:
        print(f"❌ Failed to download {model_name}")
    
    return success

def list_available_models():
    """List all available models."""
    print("📋 Available AI Models:")
    print()
    
    for name, config in ai_model_manager.model_configs.items():
        status = "✅ Loaded" if name in ai_model_manager.models else "⏳ Not loaded"
        print(f"  {name}:")
        print(f"    Description: {config['description']}")
        print(f"    Type: {config['type']}")
        print(f"    Size: {config['size_gb']}GB")
        print(f"    Priority: {config['priority']}")
        print(f"    Status: {status}")
        print()

async def main():
    """Main function."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_available_models()
        elif command == "download":
            if len(sys.argv) > 2:
                model_name = sys.argv[2]
                await download_specific_model(model_name)
            else:
                await download_priority_models()
        else:
            print("Usage:")
            print("  python download_ai_models.py list")
            print("  python download_ai_models.py download [model_name]")
    else:
        # Default: download priority models
        await download_priority_models()

if __name__ == "__main__":
    asyncio.run(main())
