"""
AWS Strands Orchestrator
Coordinates multiple AI agents for comprehensive feedback
Integrates Strands Agent framework with multi-agent coordination and MCP tools
"""

from typing import Dict, Any, List, Optional
from .english_feedback_agent import EnglishFeedbackAgent
from .debate_facilitator_agent import DebateFacilitatorAgent
from ..llm.strands_model_adapter import StrandsModelAdapter
from .mcp_tools_manager import get_mcp_tools_manager, initialize_mcp_clients
import logging

logger = logging.getLogger(__name__)


class AWSStrandsOrchestrator:
    """
    Orchestrates multiple AI agents using Strands framework
    Provides unified interface for agent coordination with MCP tools
    """
    
    def __init__(
        self,
        model_provider: Optional[str] = None,
        enable_mcp_tools: bool = True,
        mcp_config: Optional[Dict[str, str]] = None
    ):
        """
        Initialize AWS Strands Orchestrator with Strands Agent framework and MCP tools
        
        Args:
            model_provider: LLM provider ('gemini' or 'bedrock'). 
                          Defaults to env var LLM_PROVIDER or 'gemini'
            enable_mcp_tools: Whether to initialize and use MCP tools (default: True)
            mcp_config: Custom MCP client configuration (optional)
        """
        # Create Strands model based on environment configuration
        self.model = StrandsModelAdapter.create_model(provider=model_provider)
        self.model_provider = StrandsModelAdapter.get_current_provider()
        
        # Initialize MCP tools if enabled
        self.mcp_enabled = enable_mcp_tools
        self.mcp_manager = None
        
        if enable_mcp_tools:
            try:
                initialize_mcp_clients(mcp_config)
                self.mcp_manager = get_mcp_tools_manager()
                logger.info("✅ MCP tools manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize MCP tools: {e}. Continuing without MCP tools.")
                self.mcp_enabled = False
        
        # Initialize agents with the shared model (tools added later if MCP enabled)
        self.english_agent = EnglishFeedbackAgent(self.model)
        self.facilitator_agent = DebateFacilitatorAgent(self.model)
        
        logger.info(f"✅ Initialized AWSStrandsOrchestrator with {self.model_provider} model")
        logger.info(f"   ├─ EnglishFeedbackAgent ready")
        logger.info(f"   ├─ DebateFacilitatorAgent ready")
        logger.info(f"   └─ MCP tools: {'enabled' if self.mcp_enabled else 'disabled'}")
    
    def activate_mcp_tools(self):
        """
        Activate MCP tools for agents.
        Must be called before using agents if MCP tools are enabled.
        Uses context managers to maintain MCP client connections.
        """
        if not self.mcp_enabled or not self.mcp_manager:
            logger.warning("MCP tools not enabled or manager not initialized")
            return
        
        # Grammar tools for English agent
        try:
            with self.mcp_manager.use_client('grammar_tools') as client:
                grammar_tools = self.mcp_manager.get_tools('grammar_tools')
                self.english_agent.add_mcp_tools(grammar_tools)
                logger.info(f"✅ Added grammar tools to EnglishFeedbackAgent")
        except Exception as e:
            logger.warning(f"⚠️  Could not add grammar tools: {e}")
        
        # Debate tools for Facilitator agent
        try:
            with self.mcp_manager.use_client('debate_tools') as client:
                debate_tools = self.mcp_manager.get_tools('debate_tools')
                self.facilitator_agent.add_mcp_tools(debate_tools)
                logger.info(f"✅ Added debate tools to DebateFacilitatorAgent")
        except Exception as e:
            logger.warning(f"⚠️  Could not add debate tools: {e}")
    
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
            "cefr_level": analysis.get("cefr_level", "")
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
        cefr = result.get("cefr_level", "")
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
        cefr = result.get("cefr_level", "")
        return f"Great contribution, {speaker}! Keep practicing at your {cefr} level."
