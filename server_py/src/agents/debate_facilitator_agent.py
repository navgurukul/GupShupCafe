"""
Debate Facilitator Agent
Manages discussion flow and provides guidance
"""

from typing import Dict, Any, List, Optional
from ..llm.llm_interface import LLMInterface


class DebateFacilitatorAgent:
    """Agent for facilitating roundtable discussions"""
    
    def __init__(self, llm_provider: LLMInterface):
        """
        Initialize Debate Facilitator Agent
        
        Args:
            llm_provider: LLM provider instance
        """
        self.llm_provider = llm_provider
        print("✅ Initialized DebateFacilitatorAgent")
    
    async def facilitate_turn(self, context: Dict[str, Any]) -> str:
        """
        Provide guidance for current speaking turn
        
        Args:
            context: Dict with room state, current speaker, topic, etc.
            
        Returns:
            Facilitation message
        """
        topic = context.get("topic", "the current topic")
        speaker = context.get("current_speaker", {})
        turn_number = context.get("turn_number", 1)
        
        # Generate contextual prompt
        messages = [
            {
                "role": "system",
                "content": "You are a helpful discussion facilitator"
            },
            {
                "role": "user",
                "content": f"Generate a brief prompt for speaker {speaker.get('name', 'the speaker')} on turn {turn_number} about {topic}"
            }
        ]
        
        response = await self.llm_provider.chat(messages, temperature=0.8)
        return response.get("content", "Please share your thoughts on this topic.")
    
    async def suggest_topic_direction(self, statements: List[str]) -> str:
        """
        Suggest direction for the discussion
        
        Args:
            statements: List of recent statements in the discussion
            
        Returns:
            Suggestion for discussion direction
        """
        # Analyze discussion flow
        if not statements:
            return "Let's explore different perspectives on this topic."
        
        # Placeholder logic
        return "Consider exploring the counterarguments to what was just said."
    
    async def moderate_discussion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor and moderate discussion
        
        Args:
            context: Discussion context
            
        Returns:
            Moderation results with any interventions needed
        """
        return {
            "needs_intervention": False,
            "message": None,
            "reason": None
        }
    
    async def generate_speaking_prompt(self, topic: str) -> str:
        """
        Generate a speaking prompt for the topic
        
        Args:
            topic: Discussion topic
            
        Returns:
            Speaking prompt
        """
        messages = [
            {
                "role": "system",
                "content": "You are a helpful discussion facilitator. Generate brief, engaging speaking prompts."
            },
            {
                "role": "user",
                "content": f"Generate a thought-provoking prompt about: {topic}"
            }
        ]
        
        response = await self.llm_provider.chat(messages, temperature=0.9, max_tokens=100)
        return response.get("content", f"What are your thoughts on {topic}?")
