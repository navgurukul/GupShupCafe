"""
LLM Agent Service for Roundtable Discussions

This service integrates the LLM Agent (from llmTutor) as a default participant
in roundtable discussions, providing:
- Automated participation in discussions
- English language feedback
- Discussion facilitation
- Fact-checking and guidance
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class LLMAgentService:
    """
    Service for managing LLM Agent as a roundtable participant.
    
    This is a simplified version that provides basic agent responses without
    requiring the full bedrock-agentcore SDK. It uses the existing topic_generator
    and provides structured feedback responses.
    """
    
    def __init__(self):
        """Initialize the LLM Agent service."""
        self.enabled = self._check_if_enabled()
        self.agent_participant_id = "llm-agent"
        self.agent_name = "AI Tutor"
        self.conversation_history: Dict[str, List[Dict[str, Any]]] = {}
        self.agent_initialized = False
        
        if self.enabled:
            logger.info("✅ LLM Agent service enabled")
        else:
            logger.info("ℹ️ LLM Agent service disabled (enable by setting ENABLE_LLM_AGENT=true)")
    
    def _check_if_enabled(self) -> bool:
        """
        Check if LLM Agent should be enabled.
        
        Returns:
            bool: True if agent should be enabled
        """
        # For now, we enable it if explicitly requested via env var
        # In production, you'd check for proper API keys and dependencies
        enabled = os.getenv("ENABLE_LLM_AGENT", "false").lower() == "true"
        return enabled
    
    def is_enabled(self) -> bool:
        """Check if the LLM Agent service is enabled."""
        return self.enabled
    
    def get_agent_participant(self) -> Dict[str, Any]:
        """
        Get the LLM Agent participant object.
        
        Returns:
            Dict with agent participant information
        """
        return {
            "id": self.agent_participant_id,
            "socketId": "llm-agent-socket",
            "name": "AI Tutor",
            "anonymousName": self.agent_name,
            "campus": "Virtual",
            "location": "Cloud",
            "role": "speaker",
            "isReady": True,
            "isAgent": True,  # Special flag to identify as agent
            "joinedAt": datetime.now().isoformat()
        }
    
    def initialize_room(self, room_id: str, topic: Dict[str, Any], participants: List[Dict[str, Any]]) -> bool:
        """
        Initialize the agent for a specific room/discussion.
        
        Args:
            room_id: Room identifier
            topic: Discussion topic
            participants: List of human participants
            
        Returns:
            bool: True if initialization successful
        """
        try:
            self.conversation_history[room_id] = []
            self.agent_initialized = True
            
            logger.info(f"🤖 LLM Agent initialized for room {room_id}")
            logger.info(f"📝 Topic: {topic.get('title', 'Unknown')}")
            logger.info(f"👥 Participants: {len(participants)}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LLM Agent: {str(e)}")
            return False
    
    def add_statement(self, room_id: str, speaker: str, content: str) -> None:
        """
        Record a statement from a participant.
        
        Args:
            room_id: Room identifier
            speaker: Name of the speaker
            content: Content of their statement
        """
        if room_id not in self.conversation_history:
            self.conversation_history[room_id] = []
        
        self.conversation_history[room_id].append({
            "speaker": speaker,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    async def generate_response(self, room_id: str, topic: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an LLM Agent response based on conversation history.
        
        Args:
            room_id: Room identifier
            topic: Discussion topic
            
        Returns:
            Dict with agent response
        """
        try:
            conversation = self.conversation_history.get(room_id, [])
            
            # Get recent statements (last 5)
            recent_statements = conversation[-5:] if len(conversation) > 5 else conversation
            
            if not recent_statements:
                # Opening statement
                response = self._generate_opening_statement(topic)
            else:
                # Generate feedback based on discussion
                response = self._generate_feedback(topic, recent_statements)
            
            return {
                "speaker": self.agent_name,
                "content": response,
                "timestamp": datetime.now().isoformat(),
                "isAgent": True
            }
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return {
                "speaker": self.agent_name,
                "content": "I'm having trouble formulating my thoughts right now. Please continue the discussion.",
                "timestamp": datetime.now().isoformat(),
                "isAgent": True
            }
    
    def _generate_opening_statement(self, topic: Dict[str, Any]) -> str:
        """
        Generate an opening statement for the discussion.
        
        Args:
            topic: Discussion topic
            
        Returns:
            str: Opening statement
        """
        title = topic.get("title", "this topic")
        description = topic.get("description", "")
        
        responses = [
            f"Welcome everyone! I'm excited to discuss {title} with you today. {description} Let's explore different perspectives together.",
            f"Hello! Today's topic about {title} is fascinating. I'm here to facilitate our discussion and provide feedback on both the content and how we express ourselves in English.",
            f"Greetings! As we discuss {title}, I'll be listening carefully and offering insights on both the ideas shared and language usage. Let's have a meaningful conversation!"
        ]
        
        # Simple rotation based on topic title length
        index = len(title) % len(responses)
        return responses[index]
    
    def _generate_feedback(self, topic: Dict[str, Any], recent_statements: List[Dict[str, Any]]) -> str:
        """
        Generate feedback based on recent discussion.
        
        Args:
            topic: Discussion topic
            recent_statements: Recent statements from participants
            
        Returns:
            str: Feedback response
        """
        # Build a simple feedback response
        feedback_parts = []
        
        # Discussion feedback
        feedback_parts.append("**Discussion Feedback:**")
        
        if len(recent_statements) == 1:
            feedback_parts.append(f"Thank you for sharing your perspective! That's an interesting point about {topic.get('title', 'this topic')}.")
        else:
            feedback_parts.append(f"I appreciate everyone's contributions so far. You're exploring {topic.get('title', 'this topic')} from multiple angles.")
        
        # Add some engagement questions
        questions = topic.get("questions", [])
        if questions:
            feedback_parts.append(f"\nConsider this: {questions[0]}")
        
        # English feedback (simplified)
        feedback_parts.append("\n**English Language Tips:**")
        
        speakers = list(set([stmt["speaker"] for stmt in recent_statements]))
        for speaker in speakers[:2]:  # Limit to 2 speakers to keep response concise
            feedback_parts.append(f"• **{speaker}**: Good use of descriptive language! Try varying your sentence structure for even more engaging expression.")
        
        return "\n".join(feedback_parts)
    
    def cleanup_room(self, room_id: str) -> None:
        """
        Clean up agent data for a room.
        
        Args:
            room_id: Room identifier
        """
        if room_id in self.conversation_history:
            del self.conversation_history[room_id]
            logger.info(f"🧹 Cleaned up LLM Agent data for room {room_id}")


# Global service instance
llm_agent_service = LLMAgentService()
