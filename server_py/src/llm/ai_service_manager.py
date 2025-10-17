"""
AI Service Manager
Factory for creating and managing LLM providers
"""

import os
from typing import Optional, Dict, Any
from .llm_interface import LLMInterface
from .gemini_llm import GeminiLLM
from .bedrock_llm import BedrockLLM


class AIServiceManager:
    """Manages AI/LLM service providers (Factory Pattern)"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AI Service Manager
        
        Args:
            config: Configuration dict with provider settings
        """
        self.config = config or {}
        self._llm: Optional[LLMInterface] = None
        self._current_provider = self.config.get("default_provider", "gemini")
        
        # Initialize default provider
        self._initialize_provider(self._current_provider)
    
    def _initialize_provider(self, provider: str) -> None:
        """
        Initialize LLM provider
        
        Args:
            provider: Provider name ('gemini' or 'bedrock')
        """
        provider = provider.lower()
        
        if provider == "gemini":
            api_key = self.config.get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
            self._llm = GeminiLLM(api_key=api_key)
            print(f"✅ Initialized Gemini LLM provider")
            
        elif provider == "bedrock":
            model_id = self.config.get("bedrock_model_id")
            region = self.config.get("aws_region")
            self._llm = BedrockLLM(model_id=model_id, region=region)
            print(f"✅ Initialized Bedrock LLM provider")
            
        else:
            print(f"⚠️ Unknown provider '{provider}', defaulting to Gemini")
            self._llm = GeminiLLM()
        
        self._current_provider = provider
    
    def get_llm(self) -> LLMInterface:
        """
        Get current LLM provider instance
        
        Returns:
            LLM provider instance
        """
        if not self._llm:
            self._initialize_provider(self._current_provider)
        return self._llm
    
    def switch_provider(self, provider: str) -> None:
        """
        Switch to a different LLM provider
        
        Args:
            provider: Provider name ('gemini' or 'bedrock')
        """
        print(f"🔄 Switching LLM provider from {self._current_provider} to {provider}")
        self._initialize_provider(provider)
    
    def get_current_provider(self) -> str:
        """Get name of current provider"""
        return self._current_provider


# Singleton instance
_ai_service_manager = None


def get_ai_service_manager() -> AIServiceManager:
    """Get singleton AI Service Manager instance"""
    global _ai_service_manager
    if _ai_service_manager is None:
        _ai_service_manager = AIServiceManager()
    return _ai_service_manager
