"""
Gemini LLM
Google Gemini language model implementation using Strands framework
"""

import os
import re
from typing import List, Dict, Any, Optional
from .llm_interface import LLMInterface
from strands import Agent
from strands.models.gemini import GeminiModel
from dotenv import load_dotenv


class GeminiLLM(LLMInterface):
    """Google Gemini LLM implementation using Strands Agent framework"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini LLM with Strands framework
        
        Args:
            api_key: Google API key (defaults to env var GEMINI_API_KEY)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-2.5-flash"
        
        if not self.api_key:
            raise ValueError("⚠️ GEMINI_API_KEY not set. Please set it in your environment.")
        
        # Initialize Gemini Model for Strands
        self.gemini_model = GeminiModel(
            model_id=self.model_name,
            params={
                "temperature": 0.7,
            }
        )
        
        print(f"✅ Initialized GeminiLLM with Strands (model: {self.model_name})")
    
    def _create_agent(self, system_prompt: str, temperature: float = 0.7) -> Agent:
        """
        Create a Strands Agent with custom configuration
        
        Args:
            system_prompt: System prompt for the agent
            temperature: Sampling temperature
            
        Returns:
            Configured Strands Agent
        """
        model = GeminiModel(
            model_id=self.model_name,
            params={"temperature": temperature}
        )
        return Agent(model=model, system_prompt=system_prompt)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        Send chat messages to Gemini using Strands Agent
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict with response content
        """
        # Extract system message if present
        system_prompt = "You are a helpful AI assistant."
        user_messages = []
        
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", system_prompt)
            else:
                user_messages.append(msg)
        
        # Create agent with system prompt
        agent = self._create_agent(system_prompt, temperature)
        
        # Combine user messages into a single prompt
        prompt = "\n\n".join([
            f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}"
            for msg in user_messages
        ])
        
        # Get response from agent
        try:
            response_text = agent(prompt)
            
            return {
                "content": response_text,
                "model": self.model_name,
                "usage": {
                    "prompt_tokens": len(prompt.split()),  # Approximate
                    "completion_tokens": len(response_text.split()),
                    "total_tokens": len(prompt.split()) + len(response_text.split())
                }
            }
        except Exception as e:
            print(f"❌ Error in Gemini chat: {str(e)}")
            return {
                "content": f"Error: {str(e)}",
                "model": self.model_name,
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
    
    async def analyze_english(
        self,
        transcript: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze English proficiency using Gemini via Strands
        
        Args:
            transcript: Text to analyze
            context: Additional context
            
        Returns:
            Analysis results with CEFR level and suggestions
        """
        context = context or {}
        speaker = context.get("speaker", "the participant")
        
        system_prompt = """
You are an expert English language coach specializing in CEFR-based assessment.
Analyze the provided text and return a JSON-formatted response with:
- grammar_score: float (0.0 to 1.0)
- vocabulary_score: float (0.0 to 1.0)
- fluency_score: float (0.0 to 1.0)
- cefr_level: string (A1, A2, B1, B2, C1, or C2)
- suggestions: array of strings (max 3 specific suggestions)

Be constructive and encouraging in your feedback.
"""
        
        agent = self._create_agent(system_prompt, temperature=0.3)
        
        prompt = f"""
Analyze this English text from {speaker}:

"{transcript}"

Provide a comprehensive assessment in JSON format.
"""
        
        try:
            response_text = agent(prompt)
            
            # Parse response (basic parsing - can be enhanced)
            # For now, we'll extract information or return structured data
            import re
            
            # Try to extract scores
            grammar_match = re.search(r'grammar[_\s]*score["\s:]*([0-9.]+)', response_text, re.IGNORECASE)
            vocab_match = re.search(r'vocabulary[_\s]*score["\s:]*([0-9.]+)', response_text, re.IGNORECASE)
            fluency_match = re.search(r'fluency[_\s]*score["\s:]*([0-9.]+)', response_text, re.IGNORECASE)
            cefr_match = re.search(r'cefr[_\s]*level["\s:]*([ABC][12])', response_text, re.IGNORECASE)
            
            return {
                "grammar_score": float(grammar_match.group(1)) if grammar_match else 0.7,
                "vocabulary_score": float(vocab_match.group(1)) if vocab_match else 0.7,
                "fluency_score": float(fluency_match.group(1)) if fluency_match else 0.7,
                "cefr_level": cefr_match.group(1).upper() if cefr_match else "B1",
                "suggestions": self._extract_suggestions(response_text),
                "analyzed_text": transcript,
                "raw_analysis": response_text
            }
        except Exception as e:
            print(f"❌ Error in English analysis: {str(e)}")
            return {
                "grammar_score": 0.7,
                "vocabulary_score": 0.7,
                "fluency_score": 0.7,
                "cefr_level": "B1",
                "suggestions": ["Unable to analyze at this time"],
                "analyzed_text": transcript,
                "error": str(e)
            }
    
    def _extract_suggestions(self, response_text: str) -> List[str]:
        """Extract suggestions from response text"""
        suggestions = []
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and ('suggest' in line.lower() or '•' in line or '-' in line[:2]):
                # Clean up bullet points and markers
                clean_line = re.sub(r'^[•\-*]\s*', '', line)
                if len(clean_line) > 10 and len(suggestions) < 3:
                    suggestions.append(clean_line)
        
        if not suggestions:
            suggestions = ["Keep practicing! Your English is developing well."]
        
        return suggestions[:3]
