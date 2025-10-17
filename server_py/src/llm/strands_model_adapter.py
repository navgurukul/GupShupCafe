"""
Strands Model Adapter
Provides a unified interface for creating Strands-compatible models from different LLM providers
"""

import os
from typing import Optional, Union
from dotenv import load_dotenv

# Import Strands model providers
from strands.models.gemini import GeminiModel
from strands.models.bedrock import BedrockModel
from strands.models import Model

load_dotenv(".env")


class StrandsModelAdapter:
    """
    Adapter for creating Strands-compatible model instances
    Supports switching between Gemini and Bedrock based on environment configuration
    """
    
    @staticmethod
    def create_model(
        provider: Optional[str] = None,
        temperature: float = 0.7,
				# Removed max_output_tokens from here because Strands gets into error if we pass it down to GeminiModel
        **kwargs
    ) -> Model:
        """
        Create a Strands Model instance based on provider selection
        
        Args:
            provider: Provider name ('gemini' or 'bedrock'). 
                     Defaults to env var LLM_PROVIDER or 'gemini'
            temperature: Sampling temperature (0.0 to 1.0)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Strands Model instance
            
        Raises:
            ValueError: If provider is invalid or required credentials are missing
        """
        provider = provider or os.getenv("LLM_PROVIDER", "gemini")
        provider = provider.lower()
        
        if provider == "gemini":
            return StrandsModelAdapter._create_gemini_model(temperature, **kwargs)
        elif provider == "bedrock":
            return StrandsModelAdapter._create_bedrock_model(temperature, **kwargs)
        else:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                f"Supported providers: 'gemini', 'bedrock'"
            )
    
    @staticmethod
    def _create_gemini_model(
        temperature: float = 0.7,
        
        **kwargs
    ) -> GeminiModel:
        """
        Create a Gemini model for Strands
        
        Args:
            temperature: Sampling temperature
            **kwargs: Additional Gemini-specific parameters
            
        Returns:
            GeminiModel instance
            
        Raises:
            ValueError: If GEMINI_API_KEY is not set
        """
        api_key = kwargs.get("api_key") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Please set it in your environment or pass as api_key parameter."
            )
        
        model_id = kwargs.get("model_id") or "gemini-2.5-flash"
        
        # Build params dict with only valid Gemini parameters
        params = {
            "temperature": temperature,
        }
        
        # to prevent passing invalid parameters to GenerateContentConfig
        additional_params = kwargs.get("params", {})
        for key, value in additional_params.items():
            if key != "max_output_tokens":  # Skip max_output_tokens if accidentally passed
                params[key] = value
        
        model = GeminiModel(
            client_args={"api_key": api_key},
            model_id=model_id,
            params=params
        )
        
        print(f"✅ Created Gemini model (model: {model_id}, temp: {temperature})")
        return model
    
    @staticmethod
    def _create_bedrock_model(
        temperature: float = 0.7,
        
        **kwargs
    ) -> BedrockModel:
        """
        Create a Bedrock model for Strands
        
        Args:
            temperature: Sampling temperature
            max_output_tokens: Maximum output tokens
            **kwargs: Additional Bedrock-specific parameters
            
        Returns:
            BedrockModel instance
        """
        model_id = kwargs.get("model_id") or os.getenv(
            "BEDROCK_MODEL_ID", 
            "us.amazon.nova-pro-v1:0"
        )
        region_name = kwargs.get("region_name") or os.getenv("AWS_REGION", "us-east-1")
        
        model = BedrockModel(
            model_id=model_id,
            region_name=region_name,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        
        print(f"✅ Created Bedrock model (model: {model_id}, region: {region_name}, temp: {temperature})")
        return model
    
    @staticmethod
    def get_current_provider() -> str:
        """
        Get the currently configured LLM provider
        
        Returns:
            Provider name from environment or default 'gemini'
        """
        return os.getenv("LLM_PROVIDER", "gemini").lower()


# Convenience function for quick model creation
def create_model(provider: Optional[str] = None, **kwargs) -> Model:
    """
    Convenience function to create a Strands model
    
    Args:
        provider: Provider name or None to use environment default
        **kwargs: Model configuration parameters
        
    Returns:
        Strands Model instance
    """
    return StrandsModelAdapter.create_model(provider=provider, **kwargs)
