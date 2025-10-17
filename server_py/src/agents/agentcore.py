"""
AgentCore: Production-Ready Multi-Agent Orchestrator for GupShup Café
Coordinates EnglishFeedbackAgent and DebateFacilitatorAgent using Strands framework
Integrates with Bedrock AgentCore for session and memory management
"""

from typing import Dict, Any, List, Optional
from .english_feedback_agent import EnglishFeedbackAgent
from .debate_facilitator_agent import DebateFacilitatorAgent
from ..llm.strands_model_adapter import StrandsModelAdapter

class AgentCore:
    """
    Production-ready orchestrator for multi-agent coordination
    Handles session, memory, and unified feedback using Strands and Bedrock AgentCore
    """
    def __init__(self, model_provider: Optional[str] = None, max_tokens: int = 500):
        """
        Initialize AgentCore with Strands model and agents
        Args:
            model_provider: LLM provider ('gemini', 'bedrock', etc.)
            max_tokens: Maximum tokens for all LLM calls (default: 500)
        """
        self.model = StrandsModelAdapter.create_model(provider=model_provider, max_tokens=max_tokens)
        self.english_agent = EnglishFeedbackAgent(self.model)
        self.facilitator_agent = DebateFacilitatorAgent(self.model)
        self.model_provider = StrandsModelAdapter.get_current_provider()
        self.max_tokens = max_tokens
        print(f"✅ AgentCore initialized with {self.model_provider} model (max_tokens={max_tokens})")

    async def analyze_and_facilitate(
        self,
        statements: List[str],
        context: Optional[Dict[str, Any]] = None,
        instant: bool = False,
        speaker: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run both English feedback and facilitation in a single call
        Args:
            statements: List of utterances/statements
            context: Additional context (room, topic, etc.)
            instant: If True, provide instant feedback; else comprehensive
            speaker: Optional speaker name for gentle mention
        Returns:
            Dict with feedback, facilitation, and formatted messages
        """
        context = context or {}
        # English feedback (instant or comprehensive)
        if instant:
            analysis = await self.english_agent.analyze({
                "text": " ".join(statements),
                "context": context
            })
            feedback_message = self._format_feedback_message(analysis)
        else:
            analysis = await self.english_agent.analyze({
                "text": " ".join(statements),
                "context": context
            })
            feedback_message = self._format_feedback_message(analysis)
        # Facilitation suggestion
        facilitation = await self.facilitator_agent.suggest_topic_direction(statements)
        # Gentle mention (optional)
        gentle_mention = self._format_gentle_mention(speaker, analysis) if speaker else None
        return {
            "analysis": analysis,
            "facilitation_suggestion": facilitation,
            "feedback_message": feedback_message,
            "gentle_mention": gentle_mention,
            "max_tokens": self.max_tokens,
            "model_provider": self.model_provider
        }

    def _format_feedback_message(self, result: Dict[str, Any]) -> str:
        cefr = result.get("cefr_level", "")
        suggestions = result.get("suggestions", [])
        message_parts = [f"Your English level: {cefr}"]
        if suggestions:
            message_parts.append("Suggestions:")
            for suggestion in suggestions[:3]:
                message_parts.append(f"• {suggestion}")
        return "\n".join(message_parts)

    def _format_gentle_mention(self, speaker: Optional[str], result: Dict[str, Any]) -> str:
        cefr = result.get("cefr_level", "")
        if not speaker:
            return ""
        return f"Great contribution, {speaker}! Keep practicing at your {cefr} level."
