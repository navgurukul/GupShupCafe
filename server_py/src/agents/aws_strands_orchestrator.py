"""
AWS Strands Orchestrator
Coordinates multiple AI agents for comprehensive feedback
"""

from typing import Dict, Any, List, Optional
from .english_feedback_agent import EnglishFeedbackAgent
from .debate_facilitator_agent import DebateFacilitatorAgent
from ..llm.ai_service_manager import AIServiceManager


class AWSStrandsOrchestrator:
    """Orchestrates multiple AI agents using AWS Strands pattern"""
    
    def __init__(self, ai_service_manager: AIServiceManager):
        """
        Initialize AWS Strands Orchestrator
        
        Args:
            ai_service_manager: AI Service Manager instance
        """
        self.ai_service_manager = ai_service_manager
        llm = ai_service_manager.get_llm()
        
        # Initialize agents
        self.english_agent = EnglishFeedbackAgent(llm)
        self.facilitator_agent = DebateFacilitatorAgent(llm)
        
        print("✅ Initialized AWSStrandsOrchestrator with multiple agents")
    
    async def get_english_feedback(
        self,
        statements: List[str],
        instant: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get English language feedback from agents
        
        Args:
            statements: List of statements to analyze
            instant: If True, provide instant feedback; otherwise comprehensive
            context: Additional context (speaker info, topic, etc.)
            
        Returns:
            Feedback results
        """
        context = context or {}
        
        if instant:
            return await self._instant_feedback(statements, context)
        else:
            return await self._comprehensive_feedback(statements, context)
    
    async def _instant_feedback(
        self,
        statements: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide instant feedback (quick analysis)
        
        Args:
            statements: Statements to analyze
            context: Context information
            
        Returns:
            Instant feedback
        """
        # Combine statements
        text = " ".join(statements)
        
        # Quick analysis
        analysis = await self.english_agent.analyze({
            "text": text,
            "context": context
        })
        
        # Format for instant delivery
        message = self._format_feedback_message(analysis)
        
        return {
            "type": "instant",
            "message": message,
            "cefr_level": analysis.get("cefr_level", "B1"),
            "scores": {
                "grammar": analysis.get("grammar_score", 0.0),
                "vocabulary": analysis.get("vocabulary_score", 0.0),
                "fluency": analysis.get("fluency_score", 0.0)
            }
        }
    
    async def _comprehensive_feedback(
        self,
        statements: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide comprehensive feedback (detailed analysis)
        
        Args:
            statements: Statements to analyze
            context: Context information
            
        Returns:
            Comprehensive feedback
        """
        # Combine statements
        text = " ".join(statements)
        
        # Comprehensive analysis
        analysis = await self.english_agent.analyze({
            "text": text,
            "context": context
        })
        
        # Get facilitation suggestions
        facilitation = await self.facilitator_agent.suggest_topic_direction(statements)
        
        return {
            "type": "comprehensive",
            "analysis": analysis,
            "facilitation_suggestion": facilitation,
            "message": self._format_feedback_message(analysis),
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
    
    def _format_feedback_message(self, result: Dict[str, Any]) -> str:
        """
        Format feedback into a user-friendly message
        
        Args:
            result: Analysis result
            
        Returns:
            Formatted message
        """
        cefr = result.get("cefr_level", "B1")
        suggestions = result.get("suggestions", [])
        
        message_parts = [f"Your English level: {cefr}"]
        
        if suggestions:
            message_parts.append("Suggestions:")
            for suggestion in suggestions[:3]:  # Limit to top 3
                message_parts.append(f"• {suggestion}")
        
        return "\n".join(message_parts)
    
    def _format_gentle_mention(self, speaker: str, result: Dict[str, Any]) -> str:
        """
        Format a gentle mention for the speaker
        
        Args:
            speaker: Speaker name
            result: Analysis result
            
        Returns:
            Gentle mention message
        """
        cefr = result.get("cefr_level", "B1")
        return f"Great contribution, {speaker}! Keep practicing at your {cefr} level."
