"""
Debate Facilitator Agent
Manages discussion flow and provides guidance
Uses Strands Agent framework with pluggable LLM models
Integrates MCP tools for topic selection and turn management
"""

from typing import Dict, Any, List, Optional
from strands import Agent, tool
from strands.models import Model
import logging

logger = logging.getLogger(__name__)


class DebateFacilitatorAgent:
    """
    Agent for facilitating roundtable discussions
    Built on Strands Agent framework
    Enhanced with MCP tools for debate room management
    """
    
    def __init__(self, model: Model, mcp_tools: Optional[List[Any]] = None):
        """
        Initialize Debate Facilitator Agent with Strands framework and optional MCP tools
        
        Args:
            model: Strands Model instance (Gemini, Bedrock, etc.)
            mcp_tools: Optional list of MCP tools for debate room management
        """
        self.model = model
        self.mcp_tools = mcp_tools or []
        
        # Define system prompt for facilitation
        system_prompt = """You are an expert discussion facilitator for educational roundtable debates.

Your role is to:
1. Guide participants through constructive discussions
2. Encourage critical thinking and diverse perspectives
3. Provide helpful prompts that deepen the conversation
4. Maintain a supportive, inclusive environment
5. Help participants explore topics thoroughly

Be encouraging, thoughtful, and focus on helping participants develop their ideas and communication skills."""
        
        # Initialize Strands Agent with or without MCP tools
        agent_tools = self.mcp_tools if self.mcp_tools else []
        
        # Initialize Strands Agent
        self.agent = Agent(
            model=self.model,
            system_prompt=system_prompt,
            agent_id="debate_facilitator_agent",
            name="Debate Facilitator Agent",
            description="Facilitates roundtable discussions and guides participants",
            tools=agent_tools  # MCP tools integrated here
        )
        
        logger.info(f"✅ Initialized DebateFacilitatorAgent with Strands framework "
                   f"({len(agent_tools)} MCP tools)")
    
    def add_mcp_tools(self, tools: List[Any]):
        """
        Add MCP tools to the agent dynamically
        
        Args:
            tools: List of MCP tools (from MCPClient.list_tools_sync())
        """
        self.mcp_tools.extend(tools)
        
        # Recreate agent with new tools
        self.agent = Agent(
            model=self.model,
            system_prompt=self.agent._system_prompt,  # Preserve system prompt
            agent_id=self.agent.agent_id,
            name=self.agent.name,
            description=self.agent.description,
            tools=self.mcp_tools
        )
        
        logger.info(f"✅ Added {len(tools)} MCP tools to DebateFacilitatorAgent. "
                   f"Total tools: {len(self.mcp_tools)}")
    
    async def facilitate_turn(self, context: Dict[str, Any]) -> str:
        """
        Provide guidance for current speaking turn
        Can use MCP tools for topic selection and turn management
        
        Args:
            context: Dict with room state, current speaker, topic, etc.
            
        Returns:
            Facilitation message/prompt
        """
        topic = context.get("topic", "the current topic")
        speaker = context.get("current_speaker", {})
        turn_number = context.get("turn_number", 1)
        previous_statements = context.get("previous_statements", [])
        total_rounds = context.get("total_rounds", 3)
        current_round = context.get("current_round", 1)
        
        # Enhanced prompt that hints at MCP tools
        tools_hint = ""
        if self.mcp_tools:
            tool_names = [tool.tool_name for tool in self.mcp_tools]
            tools_hint = f"\n\nYou have access to these tools: {', '.join(tool_names)}. Use them if needed."
        
        # Construct context-aware prompt
        prompt = f"""Generate a brief, engaging speaking prompt for this roundtable discussion:

TOPIC: {topic}
CURRENT SPEAKER: {speaker.get('anonymous_name', 'Speaker')}
TURN: {turn_number} (Round {current_round} of {total_rounds})

PREVIOUS CONTRIBUTIONS:
{self._format_previous_statements(previous_statements)}

Provide a 1-2 sentence prompt that:
- Relates to the topic
- Builds on previous contributions (if any)
- Encourages the speaker to share their perspective
- Is supportive and non-judgmental

Keep it concise and natural.{tools_hint}"""
        
        # Get agent response - agent will use MCP tools automatically if needed
        result = self.agent(prompt)
        response_text = str(result.message.get('content', [{}])[0].get('text', ''))
        
        return response_text.strip()
    
    async def suggest_topic_direction(self, statements: List[str]) -> str:
        """
        Suggest direction for the discussion
        
        Args:
            statements: List of recent statements in the discussion
            
        Returns:
            Suggestion for discussion direction
        """
        if not statements:
            return "Let's explore different perspectives on this topic."
        
        prompt = f"""Based on these discussion points, suggest a direction to deepen the conversation:

RECENT STATEMENTS:
{chr(10).join(f"- {stmt}" for stmt in statements[-5:])}

Provide a brief suggestion (1-2 sentences) for where the discussion could go next to explore the topic more thoroughly."""
        
        result = self.agent(prompt)
        response_text = str(result.message.get('content', [{}])[0].get('text', ''))
        
        return response_text.strip()
    
    async def moderate_discussion(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Monitor and moderate discussion
        
        Args:
            context: Discussion context
            
        Returns:
            Moderation results with any interventions needed
        """
        statements = context.get("statements", [])
        topic = context.get("topic", "")
        
        if not statements:
            return {
                "needs_intervention": False,
                "message": None,
                "reason": None
            }
        
        # Simple moderation logic
        # In a full implementation, this would check for off-topic discussion,
        # inappropriate content, or participants needing encouragement
        
        return {
            "needs_intervention": False,
            "message": None,
            "reason": None
        }
    
    async def generate_speaking_prompt(self, topic: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a speaking prompt for the topic
        
        Args:
            topic: Discussion topic
            context: Optional additional context
            
        Returns:
            Speaking prompt
        """
        context = context or {}
        participant_count = context.get("participant_count", "several")
        
        prompt = f"""Generate an opening prompt for a roundtable discussion:

TOPIC: {topic}
PARTICIPANTS: {participant_count} people

Create a warm, inviting opening prompt (2-3 sentences) that:
- Introduces the topic clearly
- Encourages participants to share their thoughts
- Sets a collaborative, respectful tone

Keep it conversational and engaging."""
        
        result = self.agent(prompt)
        response_text = str(result.message.get('content', [{}])[0].get('text', ''))
        
        return response_text.strip()
    
    async def provide_encouragement(self, participant: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Provide encouragement to a participant
        
        Args:
            participant: Participant info
            context: Discussion context
            
        Returns:
            Encouraging message
        """
        participant_name = participant.get("anonymous_name", "participant")
        topic = context.get("topic", "this topic")
        
        prompt = f"""Generate a brief, supportive message to encourage {participant_name} to share their thoughts on {topic}.

Keep it:
- Warm and genuine
- Encouraging without pressure
- 1-2 sentences maximum

Message:"""
        
        result = self.agent(prompt)
        response_text = str(result.message.get('content', [{}])[0].get('text', ''))
        
        return response_text.strip()
    
    async def summarize_discussion(self, context: Dict[str, Any]) -> str:
        """
        Summarize the discussion
        
        Args:
            context: Discussion context with all statements
            
        Returns:
            Discussion summary
        """
        topic = context.get("topic", "the discussion")
        statements = context.get("statements", [])
        participants = context.get("participants", [])
        
        if not statements:
            return f"The discussion on '{topic}' did not produce any recorded statements."
        
        prompt = f"""Summarize this roundtable discussion:

TOPIC: {topic}
PARTICIPANTS: {len(participants)} people

KEY POINTS DISCUSSED:
{chr(10).join(f"- {stmt}" for stmt in statements)}

Provide a concise summary (3-4 sentences) that:
- Highlights the main perspectives shared
- Notes any interesting insights or agreements
- Acknowledges the collaborative nature of the discussion

Summary:"""
        
        result = self.agent(prompt)
        response_text = str(result.message.get('content', [{}])[0].get('text', ''))
        
        return response_text.strip()
    
    def _format_previous_statements(self, statements: List[str], max_statements: int = 3) -> str:
        """Format previous statements for context"""
        if not statements:
            return "None yet - this is the beginning of the discussion."
        
        recent = statements[-max_statements:]
        formatted = "\n".join(f"- {stmt}" for stmt in recent)
        return formatted if formatted else "None yet - this is the beginning of the discussion."
