"""
Ollama Service - Local AI Models for Trading
Integrates Ollama models for local AI analysis and trading decisions
"""

import os
import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class OllamaModel:
    """Represents an Ollama model configuration"""
    name: str
    model_id: str
    role: str
    capabilities: List[str]
    temperature: float = 0.7
    max_tokens: int = 2000
    is_active: bool = True


class OllamaService:
    """
    Ollama Service - Local AI models for trading analysis
    
    Models include:
    - llama3.2: General reasoning and strategy generation
    - codellama: Algorithm development and backtesting
    - mistral: Market sentiment analysis
    - phi3: Real-time decision making
    - neural-chat: Risk analysis and compliance
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = None
        
        # Define available Ollama models
        self.ollama_models = self._initialize_ollama_models()
        
        # Service settings
        self.timeout = 30
        self.max_retries = 3
        self.available_models = []
        
        logger.info(f"Ollama service initialized with base URL: {base_url}")
    
    def _initialize_ollama_models(self) -> Dict[str, OllamaModel]:
        """Initialize the available Ollama models"""
        return {
            "llama3.2": OllamaModel(
                name="Llama 3.2 Trading Strategist",
                model_id="llama3.2",
                role="Lead strategy generation and market analysis",
                capabilities=["strategy_generation", "market_analysis", "risk_assessment"],
                temperature=0.8,
                max_tokens=3000
            ),
            
            "codellama": OllamaModel(
                name="CodeLlama Algorithm Developer",
                model_id="codellama",
                role="Algorithm development and backtesting",
                capabilities=["algorithm_development", "backtesting", "optimization"],
                temperature=0.4,
                max_tokens=4000
            ),
            
            "mistral": OllamaModel(
                name="Mistral Sentiment Analyst",
                model_id="mistral",
                role="Market sentiment and news analysis",
                capabilities=["sentiment_analysis", "news_analysis", "social_sentiment"],
                temperature=0.6,
                max_tokens=2000
            ),
            
            "phi3": OllamaModel(
                name="Phi-3 Decision Maker",
                model_id="phi3",
                role="Real-time decision making and execution",
                capabilities=["decision_making", "execution_analysis", "performance_monitoring"],
                temperature=0.2,
                max_tokens=1500
            ),
            
            "neural-chat": OllamaModel(
                name="Neural Chat Risk Analyst",
                model_id="neural-chat",
                role="Risk management and compliance analysis",
                capabilities=["risk_analysis", "compliance_check", "position_sizing"],
                temperature=0.3,
                max_tokens=2000
            ),
            
            "qwen2": OllamaModel(
                name="Qwen2 Market Researcher",
                model_id="qwen2",
                role="Market research and fundamental analysis",
                capabilities=["market_research", "fundamental_analysis", "economic_analysis"],
                temperature=0.7,
                max_tokens=2500
            ),
            
            "gemma2": OllamaModel(
                name="Gemma2 Portfolio Manager",
                model_id="gemma2",
                role="Portfolio optimization and rebalancing",
                capabilities=["portfolio_optimization", "rebalancing", "asset_allocation"],
                temperature=0.5,
                max_tokens=2000
            ),
            
            "llama3.1": OllamaModel(
                name="Llama 3.1 Technical Analyst",
                model_id="llama3.1",
                role="Technical analysis and pattern recognition",
                capabilities=["technical_analysis", "pattern_recognition", "indicator_analysis"],
                temperature=0.5,
                max_tokens=2500
            )
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session
    
    async def check_ollama_status(self) -> Dict[str, Any]:
        """Check if Ollama is running and get available models"""
        try:
            session = await self._get_session()
            
            # Check if Ollama is running
            async with session.get(f"{self.base_url}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    
                    self.available_models = [model["name"] for model in models]
                    
                    return {
                        "status": "running",
                        "available_models": self.available_models,
                        "total_models": len(models),
                        "base_url": self.base_url
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Ollama returned status {response.status}",
                        "available_models": [],
                        "total_models": 0
                    }
                    
        except Exception as e:
            logger.error(f"Error checking Ollama status: {e}")
            return {
                "status": "error",
                "message": str(e),
                "available_models": [],
                "total_models": 0
            }
    
    async def call_ollama_model(self, model: OllamaModel, prompt: str) -> str:
        """Call an Ollama model with a prompt"""
        for attempt in range(self.max_retries):
            try:
                session = await self._get_session()
                
                # Prepare the request
                payload = {
                    "model": model.model_id,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": model.temperature,
                        "num_predict": model.max_tokens
                    }
                }
                
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        error_text = await response.text()
                        logger.warning(f"Attempt {attempt + 1} failed for {model.name}: {error_text}")
                        
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {model.name}: {e}")
                if attempt == self.max_retries - 1:
                    raise e
                await asyncio.sleep(1)
        
        return ""
    
    async def analyze_market_conditions(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market conditions using Ollama models
        """
        logger.info("Starting market analysis with Ollama models")
        
        # Check which models are available
        status = await self.check_ollama_status()
        if status["status"] != "running":
            return {
                "error": "Ollama not available",
                "status": status
            }
        
        # Define analysis tasks for available models
        tasks = {}
        
        if "llama3.2" in self.available_models:
            tasks["llama3.2"] = self._analyze_strategy_opportunities(market_data)
        
        if "llama3.1" in self.available_models:
            tasks["llama3.1"] = self._analyze_technical_indicators(market_data)
        
        if "mistral" in self.available_models:
            tasks["mistral"] = self._analyze_market_sentiment(market_data)
        
        if "qwen2" in self.available_models:
            tasks["qwen2"] = self._analyze_fundamentals(market_data)
        
        if "neural-chat" in self.available_models:
            tasks["neural-chat"] = self._assess_market_risks(market_data)
        
        # Execute all analyses concurrently
        if tasks:
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            # Compile results
            analysis_results = {}
            for agent_name, result in zip(tasks.keys(), results):
                if isinstance(result, Exception):
                    logger.error(f"Error in {agent_name} analysis: {result}")
                    analysis_results[agent_name] = {"error": str(result)}
                else:
                    analysis_results[agent_name] = result
            
            # Generate consensus analysis
            consensus = await self._generate_consensus_analysis(analysis_results)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "market_analysis": analysis_results,
                "consensus": consensus,
                "confidence_score": self._calculate_confidence(analysis_results),
                "ollama_status": status
            }
        else:
            return {
                "error": "No Ollama models available",
                "ollama_status": status
            }
    
    async def generate_trading_strategy(self, market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading strategy using Ollama models
        """
        logger.info("Generating trading strategy with Ollama models")
        
        # Check if codellama is available for strategy generation
        status = await self.check_ollama_status()
        if status["status"] != "running" or "codellama" not in self.available_models:
            return {
                "error": "CodeLlama not available for strategy generation",
                "ollama_status": status
            }
        
        model = self.ollama_models["codellama"]
        
        prompt = f"""
        As an Algorithm Developer, create a trading strategy based on the following market conditions:
        
        Market Conditions: {json.dumps(market_conditions, indent=2)}
        
        Generate a complete trading strategy including:
        1. Entry conditions
        2. Exit conditions
        3. Risk management rules
        4. Position sizing
        5. Python code implementation
        
        Format your response as JSON with the following structure:
        {{
            "strategy_name": "strategy_name",
            "entry_conditions": ["condition1", "condition2"],
            "exit_conditions": ["condition1", "condition2"],
            "risk_management": {{
                "stop_loss_pips": 50,
                "take_profit_pips": 100,
                "max_risk_per_trade": 0.02
            }},
            "position_sizing": {{
                "method": "fixed_risk",
                "risk_per_trade": 0.02
            }},
            "python_code": "def strategy_function(): ...",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = await self.call_ollama_model(model, prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in strategy generation: {e}")
            return {"error": str(e)}
    
    async def assess_risk(self, position_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risk using Ollama models
        """
        logger.info("Assessing risk with Ollama models")
        
        # Check if neural-chat is available for risk assessment
        status = await self.check_ollama_status()
        if status["status"] != "running" or "neural-chat" not in self.available_models:
            return {
                "error": "Neural Chat not available for risk assessment",
                "ollama_status": status
            }
        
        model = self.ollama_models["neural-chat"]
        
        prompt = f"""
        As a Risk Analyst, assess the risk for the following position:
        
        Position Data: {json.dumps(position_data, indent=2)}
        
        Provide a comprehensive risk assessment including:
        1. Position risk level
        2. Portfolio impact
        3. Market risk factors
        4. Liquidity risk
        5. Recommendations
        
        Format your response as JSON with the following structure:
        {{
            "position_risk": "low/medium/high",
            "risk_score": 0.0-1.0,
            "portfolio_impact": "low/medium/high",
            "market_risk_factors": ["factor1", "factor2"],
            "liquidity_risk": "low/medium/high",
            "recommendations": ["rec1", "rec2"],
            "overall_risk_score": 0.0-1.0
        }}
        """
        
        try:
            response = await self.call_ollama_model(model, prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            return {"error": str(e)}
    
    async def make_trading_decision(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make trading decision using Ollama models
        """
        logger.info("Making trading decision with Ollama models")
        
        # Check if phi3 is available for decision making
        status = await self.check_ollama_status()
        if status["status"] != "running" or "phi3" not in self.available_models:
            return {
                "error": "Phi-3 not available for decision making",
                "ollama_status": status
            }
        
        model = self.ollama_models["phi3"]
        
        prompt = f"""
        As a Decision Maker, make a trading decision based on the following analysis:
        
        Analysis Data: {json.dumps(analysis_data, indent=2)}
        
        Make a clear trading decision including:
        1. Action (buy/sell/hold)
        2. Asset/symbol
        3. Entry price
        4. Stop loss
        5. Take profit
        6. Confidence level
        7. Reasoning
        
        Format your response as JSON with the following structure:
        {{
            "action": "buy/sell/hold",
            "symbol": "EUR_USD",
            "entry_price": 1.0850,
            "stop_loss": 1.0800,
            "take_profit": 1.0900,
            "confidence": 0.0-1.0,
            "reasoning": "explanation",
            "execution_priority": "high/medium/low"
        }}
        """
        
        try:
            response = await self.call_ollama_model(model, prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in trading decision: {e}")
            return {"error": str(e)}
    
    async def _analyze_strategy_opportunities(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze strategy opportunities using Llama 3.2"""
        model = self.ollama_models["llama3.2"]
        
        prompt = f"""
        As a Trading Strategist, analyze the following market data and identify trading opportunities:
        
        Market Data: {json.dumps(market_data, indent=2)}
        
        Provide analysis on:
        1. Market trends and momentum
        2. Potential entry/exit points
        3. Risk/reward ratios
        4. Strategy recommendations
        5. Market timing considerations
        
        Format your response as JSON with the following structure:
        {{
            "market_trend": "bullish/bearish/sideways",
            "opportunities": [
                {{
                    "asset": "symbol",
                    "direction": "long/short",
                    "entry_price": "price",
                    "target_price": "price",
                    "stop_loss": "price",
                    "confidence": 0.0-1.0,
                    "rationale": "explanation"
                }}
            ],
            "risk_level": "low/medium/high",
            "recommended_strategies": ["strategy1", "strategy2"]
        }}
        """
        
        try:
            response = await self.call_ollama_model(model, prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in strategy analysis: {e}")
            return {"error": str(e)}
    
    async def _analyze_technical_indicators(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technical indicators using Llama 3.1"""
        model = self.ollama_models["llama3.1"]
        
        prompt = f"""
        As a Technical Analyst, analyze the following market data for technical patterns and indicators:
        
        Market Data: {json.dumps(market_data, indent=2)}
        
        Analyze:
        1. Support and resistance levels
        2. Moving averages and trends
        3. RSI, MACD, Bollinger Bands
        4. Chart patterns (head & shoulders, triangles, etc.)
        5. Volume analysis
        6. Momentum indicators
        
        Return JSON with:
        {{
            "support_levels": [prices],
            "resistance_levels": [prices],
            "trend_direction": "up/down/sideways",
            "technical_signals": [
                {{
                    "indicator": "name",
                    "signal": "buy/sell/neutral",
                    "strength": 0.0-1.0,
                    "value": "current_value"
                }}
            ],
            "patterns": [
                {{
                    "pattern": "name",
                    "reliability": 0.0-1.0,
                    "target": "price",
                    "completion": 0.0-1.0
                }}
            ]
        }}
        """
        
        try:
            response = await self.call_ollama_model(model, prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in technical analysis: {e}")
            return {"error": str(e)}
    
    async def _analyze_market_sentiment(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market sentiment using Mistral"""
        model = self.ollama_models["mistral"]
        
        prompt = f"""
        As a Sentiment Analyst, analyze the market sentiment from the following data:
        
        Market Data: {json.dumps(market_data, indent=2)}
        
        Analyze:
        1. News sentiment impact
        2. Social media sentiment
        3. Market fear/greed indicators
        4. Institutional sentiment
        5. Retail sentiment
        6. Overall market mood
        
        Return JSON with:
        {{
            "overall_sentiment": "bullish/bearish/neutral",
            "sentiment_score": -1.0 to 1.0,
            "news_sentiment": {{
                "score": -1.0 to 1.0,
                "impact": "high/medium/low"
            }},
            "social_sentiment": {{
                "score": -1.0 to 1.0,
                "volume": "high/medium/low"
            }},
            "fear_greed_index": 0-100,
            "sentiment_signals": [
                {{
                    "source": "name",
                    "sentiment": "positive/negative/neutral",
                    "confidence": 0.0-1.0
                }}
            ]
        }}
        """
        
        try:
            response = await self.call_ollama_model(model, prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {"error": str(e)}
    
    async def _analyze_fundamentals(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze fundamentals using Qwen2"""
        model = self.ollama_models["qwen2"]
        
        prompt = f"""
        As a Market Researcher, analyze the fundamental factors affecting the market:
        
        Market Data: {json.dumps(market_data, indent=2)}
        
        Analyze:
        1. Economic indicators
        2. Central bank policies
        3. Political factors
        4. Market fundamentals
        5. Long-term trends
        
        Return JSON with fundamental analysis.
        """
        
        try:
            response = await self.call_ollama_model(model, prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in fundamental analysis: {e}")
            return {"error": str(e)}
    
    async def _assess_market_risks(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market risks using Neural Chat"""
        model = self.ollama_models["neural-chat"]
        
        prompt = f"""
        As a Risk Analyst, assess the market risks:
        
        Market Data: {json.dumps(market_data, indent=2)}
        
        Assess:
        1. Market volatility
        2. Liquidity risks
        3. Systemic risks
        4. Event risks
        5. Correlation risks
        
        Return JSON with risk assessment.
        """
        
        try:
            response = await self.call_ollama_model(model, prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in market risk assessment: {e}")
            return {"error": str(e)}
    
    async def _generate_consensus_analysis(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate consensus analysis from all model results"""
        # Use phi3 for consensus if available
        if "phi3" not in self.available_models:
            return {"error": "Phi-3 not available for consensus"}
        
        model = self.ollama_models["phi3"]
        
        prompt = f"""
        As the Decision Maker, synthesize the following analysis results from the AI team:
        
        Analysis Results: {json.dumps(analysis_results, indent=2)}
        
        Generate a consensus analysis that:
        1. Identifies areas of agreement/disagreement
        2. Provides overall market assessment
        3. Highlights key insights
        4. Recommends next steps
        
        Return JSON with:
        {{
            "consensus_assessment": "bullish/bearish/neutral",
            "confidence_level": 0.0-1.0,
            "key_insights": ["insight1", "insight2"],
            "areas_of_agreement": ["area1", "area2"],
            "areas_of_disagreement": ["area1", "area2"],
            "recommended_actions": ["action1", "action2"],
            "risk_level": "low/medium/high"
        }}
        """
        
        try:
            response = await self.call_ollama_model(model, prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error in consensus generation: {e}")
            return {"error": str(e)}
    
    def _calculate_confidence(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate overall confidence score from analysis results"""
        valid_results = [r for r in analysis_results.values() if "error" not in r]
        if not valid_results:
            return 0.0
        
        # Simple confidence calculation based on number of successful analyses
        return len(valid_results) / len(analysis_results)
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()


# Global Ollama service instance
ollama_service = OllamaService()
