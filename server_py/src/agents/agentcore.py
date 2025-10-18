"""
AgentCore: Production-Ready Multi-Agent Orchestrator for GupShup Café
Coordinates EnglishFeedbackAgent and DebateFacilitatorAgent using Strands framework
Integrates with Bedrock AgentCore patterns for production deployment
Supports MCP tools for enhanced capabilities
"""

from typing import Dict, Any, List, Optional
from .english_feedback_agent import EnglishFeedbackAgent
from .debate_facilitator_agent import DebateFacilitatorAgent
from .mcp_tools_manager import get_mcp_tools_manager, initialize_mcp_clients
from ..llm.strands_model_adapter import StrandsModelAdapter
import logging

logger = logging.getLogger(__name__)


class AgentCore:
    """
    Production-ready orchestrator for multi-agent coordination
    Handles room, memory, and unified feedback using Strands and Bedrock AgentCore patterns
    Enhanced with MCP tools integration
    """
    
    def __init__(
        self,
        model_provider: Optional[str] = None,
        max_tokens: int = 500,
        enable_mcp_tools: bool = True,
        mcp_config: Optional[Dict[str, str]] = None
    ):
        """
        Initialize AgentCore with Strands model, agents, and MCP tools
        
        Args:
            model_provider: LLM provider ('gemini', 'bedrock', etc.)
            max_tokens: Maximum tokens for all LLM calls (default: 500)
            enable_mcp_tools: Whether to initialize and use MCP tools (default: True)
            mcp_config: Custom MCP client configuration (optional)
        """
        self.model = StrandsModelAdapter.create_model(provider=model_provider, max_tokens=max_tokens)
        self.model_provider = StrandsModelAdapter.get_current_provider()
        self.max_tokens = max_tokens
        
        # Initialize MCP tools if enabled
        self.mcp_enabled = enable_mcp_tools
        self.mcp_manager = None
        
        if enable_mcp_tools:
            try:
                initialize_mcp_clients(mcp_config)
                self.mcp_manager = get_mcp_tools_manager()
                logger.info("✅ MCP tools manager initialized in AgentCore")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize MCP tools: {e}. Continuing without MCP tools.")
                self.mcp_enabled = False
        
        # Initialize agents
        self.english_agent = EnglishFeedbackAgent(self.model)
        self.facilitator_agent = DebateFacilitatorAgent(self.model)
        
        logger.info(f"✅ AgentCore initialized with {self.model_provider} model (max_tokens={max_tokens})")
        logger.info(f"   ├─ EnglishFeedbackAgent ready")
        logger.info(f"   ├─ DebateFacilitatorAgent ready")
        logger.info(f"   └─ MCP tools: {'enabled' if self.mcp_enabled else 'disabled'}")
    
    def activate_mcp_tools(self):
        """
        Activate MCP tools for agents (following Bedrock AgentCore patterns).
        Should be called before using agents in production.
        """
        if not self.mcp_enabled or not self.mcp_manager:
            logger.warning("MCP tools not enabled or manager not initialized")
            return
        
        # Grammar tools for English agent
        try:
            with self.mcp_manager.use_client('grammar_tools') as client:
                grammar_tools = self.mcp_manager.get_tools('grammar_tools')
                self.english_agent.add_mcp_tools(grammar_tools)
                logger.info(f"✅ Activated grammar tools for EnglishFeedbackAgent")
        except Exception as e:
            logger.warning(f"⚠️  Could not activate grammar tools: {e}")
        
        # Debate tools for Facilitator agent
        try:
            with self.mcp_manager.use_client('debate_tools') as client:
                debate_tools = self.mcp_manager.get_tools('debate_tools')
                self.facilitator_agent.add_mcp_tools(debate_tools)
                logger.info(f"✅ Activated debate tools for DebateFacilitatorAgent")
        except Exception as e:
            logger.warning(f"⚠️  Could not activate debate tools: {e}")

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
