#!/usr/bin/env python3
"""
AI Model Manager
Downloads and manages AI models from Hugging Face for trading analysis
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path
import requests
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    AutoModelForCausalLM,
    pipeline
)
import torch
from huggingface_hub import hf_hub_download, snapshot_download

logger = logging.getLogger(__name__)

class AIModelManager:
    """Manages AI models for trading analysis."""
    
    def __init__(self, models_dir: str = "./models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.models: Dict[str, Any] = {}
        self.model_configs = self._load_model_configs()
        
    def _load_model_configs(self) -> Dict[str, Dict]:
        """Load model configurations."""
        return {
            # Sentiment Analysis Models
            "finbert": {
                "model_id": "ProsusAI/finbert",
                "type": "sentiment",
                "size_gb": 0.4,
                "description": "Financial sentiment analysis",
                "priority": 1
            },
            "twitter_sentiment": {
                "model_id": "cardiffnlp/twitter-roberta-base-sentiment-latest",
                "type": "sentiment", 
                "size_gb": 1.3,
                "description": "Twitter sentiment analysis",
                "priority": 2
            },
            "multilingual_sentiment": {
                "model_id": "nlptown/bert-base-multilingual-uncased-sentiment",
                "type": "sentiment",
                "size_gb": 1.1,
                "description": "Multilingual sentiment analysis",
                "priority": 3
            },
            
            # Text Generation Models
            "tinyllama": {
                "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                "type": "text_generation",
                "size_gb": 1.0,
                "description": "Fast text generation for strategies",
                "priority": 1
            },
            "phi3_mini": {
                "model_id": "microsoft/Phi-3-mini-4k-instruct",
                "type": "text_generation",
                "size_gb": 2.1,
                "description": "Efficient reasoning model",
                "priority": 2
            },
            "mistral_7b": {
                "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
                "type": "text_generation",
                "size_gb": 4.0,
                "description": "High-quality text generation",
                "priority": 3
            },
            
            # Text Classification Models
            "news_classifier": {
                "model_id": "distilbert-base-uncased",
                "type": "classification",
                "size_gb": 0.3,
                "description": "News classification",
                "priority": 1
            },
            
            # Named Entity Recognition
            "ner_model": {
                "model_id": "dslim/bert-base-NER",
                "type": "ner",
                "size_gb": 0.4,
                "description": "Named entity recognition",
                "priority": 2
            }
        }
    
    async def download_model(self, model_name: str) -> bool:
        """Download a model from Hugging Face."""
        if model_name not in self.model_configs:
            logger.error(f"Model {model_name} not found in configurations")
            return False
        
        config = self.model_configs[model_name]
        model_path = self.models_dir / model_name
        
        try:
            logger.info(f"Downloading {model_name} ({config['size_gb']}GB)...")
            
            # Download model files
            snapshot_download(
                repo_id=config["model_id"],
                local_dir=model_path,
                local_dir_use_symlinks=False
            )
            
            # Load model based on type
            if config["type"] == "sentiment":
                self.models[model_name] = pipeline(
                    "sentiment-analysis",
                    model=str(model_path),
                    device=0 if torch.cuda.is_available() else -1
                )
            elif config["type"] == "text_generation":
                tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                model = AutoModelForCausalLM.from_pretrained(
                    str(model_path),
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                self.models[model_name] = {
                    "tokenizer": tokenizer,
                    "model": model
                }
            elif config["type"] == "classification":
                self.models[model_name] = pipeline(
                    "text-classification",
                    model=str(model_path),
                    device=0 if torch.cuda.is_available() else -1
                )
            elif config["type"] == "ner":
                self.models[model_name] = pipeline(
                    "ner",
                    model=str(model_path),
                    device=0 if torch.cuda.is_available() else -1
                )
            
            logger.info(f"✅ Model {model_name} downloaded and loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to download {model_name}: {e}")
            return False
    
    async def download_priority_models(self) -> Dict[str, bool]:
        """Download priority models for trading."""
        results = {}
        
        # Download priority 1 models first
        priority_models = [
            name for name, config in self.model_configs.items() 
            if config["priority"] == 1
        ]
        
        for model_name in priority_models:
            results[model_name] = await self.download_model(model_name)
            await asyncio.sleep(1)  # Rate limiting
        
        return results
    
    def get_model(self, model_name: str) -> Optional[Any]:
        """Get a loaded model."""
        return self.models.get(model_name)
    
    def analyze_sentiment(self, text: str, model_name: str = "finbert") -> Dict[str, Any]:
        """Analyze sentiment using specified model."""
        model = self.get_model(model_name)
        if not model:
            return {"error": f"Model {model_name} not loaded"}
        
        try:
            result = model(text)
            return {
                "text": text,
                "sentiment": result[0]["label"],
                "score": result[0]["score"],
                "model": model_name
            }
        except Exception as e:
            return {"error": f"Sentiment analysis failed: {e}"}
    
    def generate_text(self, prompt: str, model_name: str = "tinyllama", 
                     max_length: int = 200) -> Dict[str, Any]:
        """Generate text using specified model."""
        model_data = self.get_model(model_name)
        if not model_data:
            return {"error": f"Model {model_name} not loaded"}
        
        try:
            tokenizer = model_data["tokenizer"]
            model = model_data["model"]
            
            # Add special tokens for chat models
            if "chat" in model_name.lower():
                prompt = f"<|system|>You are a trading expert. Provide concise, actionable advice.</s><|user|>{prompt}</s><|assistant|>"
            
            inputs = tokenizer(prompt, return_tensors="pt")
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=max_length,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            return {
                "prompt": prompt,
                "generated_text": generated_text,
                "model": model_name
            }
        except Exception as e:
            return {"error": f"Text generation failed: {e}"}
    
    def classify_text(self, text: str, model_name: str = "news_classifier") -> Dict[str, Any]:
        """Classify text using specified model."""
        model = self.get_model(model_name)
        if not model:
            return {"error": f"Model {model_name} not loaded"}
        
        try:
            result = model(text)
            return {
                "text": text,
                "classification": result[0]["label"],
                "score": result[0]["score"],
                "model": model_name
            }
        except Exception as e:
            return {"error": f"Text classification failed: {e}"}
    
    def extract_entities(self, text: str, model_name: str = "ner_model") -> Dict[str, Any]:
        """Extract named entities from text."""
        model = self.get_model(model_name)
        if not model:
            return {"error": f"Model {model_name} not loaded"}
        
        try:
            result = model(text)
            return {
                "text": text,
                "entities": result,
                "model": model_name
            }
        except Exception as e:
            return {"error": f"Entity extraction failed: {e}"}
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Get list of available models."""
        available = {}
        for name, config in self.model_configs.items():
            available[name] = {
                **config,
                "loaded": name in self.models,
                "path": str(self.models_dir / name) if (self.models_dir / name).exists() else None
            }
        return available
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get overall model status."""
        available = self.get_available_models()
        loaded_count = sum(1 for model in available.values() if model["loaded"])
        total_size = sum(model["size_gb"] for model in available.values() if model["loaded"])
        
        return {
            "total_models": len(available),
            "loaded_models": loaded_count,
            "total_size_gb": total_size,
            "models": available
        }

# Global instance
ai_model_manager = AIModelManager()
