"""
LLM Interface
Abstract base class for LLM providers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class LLMInterface(ABC):
    """Abstract interface for Language Model providers"""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Send chat messages to LLM and get response
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict with 'content' and other response metadata
        """
        pass
    
    @abstractmethod
    async def analyze_english(
        self,
        transcript: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze English language proficiency
        
        Args:
            transcript: Text to analyze
            context: Additional context (speaker info, topic, etc.)
            
        Returns:
            Dict with analysis results (grammar, vocabulary, fluency, CEFR level)
        """
        pass
