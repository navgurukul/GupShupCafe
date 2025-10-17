"""
AI Service Manager
Factory for creating and managing LLM providers with Strands framework
"""

import os
from typing import Optional, Dict, Any
from .strands_model_adapter import StrandsModelAdapter, create_model
from strands.models import Model


class AIServiceManager:
    """
    Manages AI/LLM service providers using Strands framework (Factory Pattern)
    Provides backward compatibility while using Strands models internally
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AI Service Manager with Strands integration
        
        Args:
            config: Configuration dict with provider settings
        """
        self.config = config or {}
        self._model: Optional[Model] = None
        self._current_provider = self.config.get("default_provider") or os.getenv("LLM_PROVIDER", "gemini")
        
        # Initialize default provider
        self._initialize_provider(self._current_provider)
    
    def _initialize_provider(self, provider: str) -> None:
        """
        Initialize LLM provider using Strands framework
        
        Args:
            provider: Provider name ('gemini' or 'bedrock')
        """
        provider = provider.lower()
        
        try:
            # Use StrandsModelAdapter to create the model
            self._model = create_model(
                provider=provider,
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 1000),
                api_key=self.config.get("gemini_api_key") or os.getenv("GEMINI_API_KEY"),
                model_id=self.config.get("model_id"),
                region_name=self.config.get("aws_region")
            )
            self._current_provider = provider
            print(f"✅ AIServiceManager initialized {provider} provider via Strands")
            
        except Exception as e:
            print(f"⚠️ Failed to initialize {provider}: {e}")
            print(f"   Falling back to Gemini provider")
            
            # Fallback to Gemini
            self._model = create_model(provider="gemini", temperature=0.7)
            self._current_provider = "gemini"
    
    def get_model(self) -> Model:
        """
        Get current Strands Model instance
        
        Returns:
            Strands Model instance
        """
        if not self._model:
            self._initialize_provider(self._current_provider)
        return self._model
    
    def get_llm(self) -> Model:
        """
        Get current LLM provider instance (alias for get_model)
        Maintained for backward compatibility
        
        Returns:
            Strands Model instance
        """
        return self.get_model()
    
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


def get_ai_service_manager(config: Optional[Dict[str, Any]] = None) -> AIServiceManager:
    """
    Get singleton AI Service Manager instance
    
    Args:
        config: Optional configuration dict
        
    Returns:
        AIServiceManager instance
    """
    global _ai_service_manager
    if _ai_service_manager is None:
        _ai_service_manager = AIServiceManager(config)
    return _ai_service_manager
