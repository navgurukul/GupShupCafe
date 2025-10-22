"""
Agent Service
Business logic for AI agent management and interactions with transcripts/feedback
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import asyncio
import json
from strands import Agent, tool
from strands.models import Model

from ..agents.debate_facilitator_agent import DebateFacilitatorAgent
from ..agents.english_feedback_agent import EnglishFeedbackAgent

from ..models import TranscriptModel, UpdateTranscriptModel, UpdateTranscriptResponseModel
from .transcript_service import transcript_service
from .feedback_service import feedback_service

from ..database.database import db
from ..models import (
    CreateAgentModel,
    AgentModel,
    AgentReplyModel,
    AgentReplyResponseModel,
    UpdateAgentModel,
    UpdateAgentResponseModel,
    AgentStatus,
    AgentType,
    AgentModelSource,
    DeleteAgentResponseModel
)


class AgentService:
    """Service class for agent operations and interactions."""

    @staticmethod
    async def create_agent(agent_data: CreateAgentModel) -> str:
        """Create a new agent instance.

        # FLAG: NOT CONVERTIBLE - This function returns str instead of pydantic model
        # TODO: Convert to use CreateAgentResponseModel
        """
        agent_id = str(uuid.uuid4())

        db_data = {
            "agent_id": agent_id,
            "room_id": agent_data.room_id,
            "agent_model": agent_data.agent_model.value,
            "agent_type": agent_data.agent_type.value,
            "status": agent_data.status.value if agent_data.status else AgentStatus.ACTIVE.value,
            "total_interactions": 0
        }

        try:
            await db.create_agent(db_data)
            return agent_id
        except Exception as e:
            print(f"Error creating agent: {e}")
            return None

    @staticmethod
    async def create_room_agents(room_id: str, room_topic: str = None) -> Dict[str, str]:
        """
        Create both facilitator and English feedback agents for a room.

        # FLAG: NOT CONVERTIBLE - This function returns Dict instead of pydantic model
        # TODO: Convert to use appropriate response model

        Returns dict with agent_ids: {'facilitator': agent_id, 'english': agent_id}
        """

        # Create facilitator agent
        facilitator_data = CreateAgentModel(
            room_id=room_id,
            agent_model=AgentModelSource.GEMINI,
            agent_type=AgentType.FACILITATOR,
        )
        facilitator_id = await AgentService.create_agent(facilitator_data)

        # Create English feedback agent
        english_data = CreateAgentModel(
            room_id=room_id,
            agent_model=AgentModelSource.GEMINI,
            agent_type=AgentType.ENGLISH,
        )

        english_id = await AgentService.create_agent(english_data)

        return {
            "facilitator_agent_id": facilitator_id,
            "english_agent_id": english_id
        }

    @staticmethod
    async def get_agent(agent_id: str) -> Optional[AgentModel]:
        """Get agent by ID."""
        try:
            agent_data = await db.get_agent(agent_id)
            if not agent_data:
                return None

            return AgentModel(**agent_data)
        except Exception as e:
            print(f"Error fetching agent {agent_id}: {e}")
            return None

    @staticmethod
    async def get_agents_by_room(room_id: str) -> List[AgentModel]:
        """Get all agents for a specific room.

        # FLAG: NOT CONVERTIBLE - This function returns List instead of pydantic model
        # TODO: Convert to use ListAgentsResponseModel
        """
        try:
            agents_data = await db.get_agents_by_room(room_id)
            return [AgentModel(**agent) for agent in agents_data]
        except Exception as e:
            print(f"Error fetching agents for room {room_id}: {e}")
            return []

    @staticmethod
    async def update_agent(agent_id: str, update_data: UpdateAgentModel) -> bool:
        """Update agent properties.

        # FLAG: NOT CONVERTIBLE - This function returns bool instead of pydantic model
        # TODO: Convert to use UpdateAgentResponseModel
        """
        update_dict = {}

        if update_data.status:
            update_dict["status"] = update_data.status.value

        if not update_dict:
            return False

        # Use existing database method to update status
        try:
            if "status" in update_dict:
                await db.update_agent_status(agent_id, update_dict["status"])
        except Exception as e:
            print(f"Error updating agent {agent_id}: {e}")
            return False

        return True

    @staticmethod
    async def increment_interactions(agent_id: str, count: int = 1) -> bool:
        """Increment agent interaction counter."""
        try:
            result = await db.update_agent_interactions(agent_id, count)
            return result > 0
        except Exception as e:
            print(f"Error incrementing interactions for agent {agent_id}: {e}")
            return False

    @staticmethod
    async def delete_agent(agent_id: str) -> DeleteAgentResponseModel:
        """Delete an agent.

        # FLAG: NOT CONVERTIBLE - This function returns bool instead of pydantic model
        # TODO: Convert to use DeleteAgentResponseModel
        """
        try:
            result = await db.delete_agent(agent_id)
            return result > 0
        except Exception as e:
            print(f"Error deleting agent {agent_id}: {e}")
            return False

    @staticmethod
    async def process_transcript_for_feedback(
        agent_id: str,
        transcript_id: str,
        feedback_type: str = "instant"
    ) -> AgentReplyResponseModel:
        """
        Process a transcript to generate feedback.
        This method coordinates with transcript and feedback services.
        """
        # Get the agent
        agent = await AgentService.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        # Update agent status to processing
        try:
            await db.update_agent_status(agent_id, AgentStatus.PROCESSING.value)
        except Exception as e:
            print(f"Error updating agent {agent_id} status to processing: {e}")

        try:
            processing_start = datetime.utcnow()

            # Get transcript data from database
            transcript_data = await db.get_transcript(transcript_id)
            if not transcript_data:
                raise ValueError(f"Transcript {transcript_id} not found")

            # Generate feedback based on agent type
            if agent.agent_type == AgentType.ENGLISH.value:
                feedback_text = await AgentService._generate_english_feedback(
                    agent, transcript_data, feedback_type
                )
            elif agent.agent_type == AgentType.FACILITATOR.value:
                feedback_text = await AgentService._generate_facilitator_response(
                    agent, transcript_data
                )
            else:
                feedback_text = f"Processed transcript for {agent.agent_type} agent"

            # Store feedback in database
            feedback_id = str(uuid.uuid4())
            feedback_data = {
                "id": feedback_id,
                "room_id": transcript_data["room_id"],
                "participant_id": transcript_data["participant_id"],
                "user_id": transcript_data["user_id"],
                "feedback_type": feedback_type,
                "display_message": feedback_text,
                "agent_id": agent_id,
                "agent_model": agent.agent_model
            }

            try:
                await db.save_feedback(feedback_data)
            except Exception as e:
                print(f"Error saving feedback for agent {agent_id}: {e}")

            processing_end = datetime.utcnow()
            processing_time = (
                processing_end - processing_start).total_seconds()

            # Increment interaction counter
            await AgentService.increment_interactions(agent_id)

            # Update agent status back to active
            try:
                await db.update_agent_status(agent_id, AgentStatus.ACTIVE.value)
            except Exception as e:
                print(f"Error updating agent {agent_id} status to active: {e}")

            return AgentReplyResponseModel(
                status="success",
                data=AgentReplyModel(
                    agent_id=agent_id,
                    response_text=feedback_text
                ),
                message="Feedback processed successfully"
            )

        except Exception as e:
            # Update agent status to error
            try:
                await db.update_agent_status(agent_id, AgentStatus.ERROR.value)
            except Exception as e:
                print(f"Error updating agent {agent_id} status to error: {e}")
            raise e

    @staticmethod
    async def _generate_english_feedback(
        agent: AgentModel,
        transcript_data: Dict[str, Any],
        feedback_type: str
    ) -> str:
        """Generate English language feedback for a transcript."""
        # This is a placeholder - in production, this would call the LLM service
        transcript_text = transcript_data.get("transcript_text", "")
        word_count = transcript_data.get("word_count", 0)
        speech_rate = transcript_data.get("speech_rate", 0)

        if feedback_type == "instant":
            # Generate quick, actionable feedback
            feedback_points = []

            if word_count < 20:
                feedback_points.append("Try to elaborate more on your ideas")
            elif word_count > 100:
                feedback_points.append(
                    "Great detail! Consider being more concise")

            if speech_rate > 3.0:
                feedback_points.append(
                    "Good pace! Your speech is clear and easy to follow")
            elif speech_rate < 1.5:
                feedback_points.append(
                    "Try speaking a bit faster to maintain engagement")

            # Add grammar/vocabulary feedback based on text analysis
            if len(transcript_text.split('.')) > 3:
                feedback_points.append("Nice use of complex sentences!")

            return " | ".join(feedback_points) if feedback_points else "Keep up the good work!"

        else:  # comprehensive feedback
            return f"""Comprehensive Analysis:
            
Fluency: Your speech rate of {speech_rate:.1f} words/second shows good control.
Content: You used {word_count} words effectively to express your ideas.
Suggestions: Continue practicing with varied vocabulary and complex sentence structures.
            
Overall: Strong participation! Focus on expanding your ideas with specific examples."""

    @staticmethod
    async def _generate_facilitator_response(
        agent: AgentModel,
        transcript_data: Dict[str, Any]
    ) -> Agent:
        """Generate facilitator response based on participant input."""
        # This is a placeholder - in production, this would call the LLM service
        transcript_text = transcript_data.get("transcript_text", "")
        response_text = ""
        # Analyze the content and generate appropriate facilitator response
        if "agree" in transcript_text.lower():
            response_text = "I appreciate you sharing that perspective. What specific examples support your viewpoint?"
        elif "disagree" in transcript_text.lower():
            response_text = "Thank you for presenting a different angle. Can you help us understand your reasoning?"
        elif "?" in transcript_text:
            response_text = "That's an excellent question. Let's explore this together. What do others think?"
        else:
            response_text = "Interesting point! How do you think this connects to what we discussed earlier?"
        AgentReplyResponseModel(
            "success",
            AgentReplyModel(
                agent.agent_id,
                response_text
            )
        )

    @staticmethod
    async def generate_facilitator_turn_response(
        room_id: str,
        recent_transcripts: List[Dict[str, Any]],
        feedback_summaries: List[Dict[str, Any]]
    ) -> str:
        """
        Generate facilitator's speaking turn response based on recent conversation and feedback.
        """
        # Get the facilitator agent for this room
        agents = await AgentService.get_agents_by_room(room_id)
        facilitator = next(
            (a for a in agents if a.agent_type == AgentType.FACILITATOR.value), None)

        if not facilitator:
            return "Thank you all for your thoughtful contributions to this discussion."

        # Analyze recent conversation themes
        themes = []
        for transcript in recent_transcripts[-3:]:  # Last 3 transcripts
            text = transcript.get("transcript_text", "").lower()
            if any(word in text for word in ["important", "significant", "key"]):
                themes.append("importance")
            if any(word in text for word in ["different", "various", "multiple"]):
                themes.append("diversity")
            if any(word in text for word in ["example", "instance", "case"]):
                themes.append("examples")

        # Generate response based on themes and feedback
        if "examples" in themes:
            response = "I've noticed several of you are sharing concrete examples, which really enriches our discussion. "
        elif "diversity" in themes:
            response = "It's fascinating to see the different perspectives emerging here. "
        else:
            response = "Thank you all for your thoughtful contributions. "

        # Add feedback-based insights
        if feedback_summaries:
            response += "I can see everyone is working hard to express complex ideas clearly. "

        # Add forward-looking question
        response += "As we continue, I'd like us to consider: How might these different viewpoints actually complement each other?"

        return response

    @staticmethod
    async def get_agent_stats(agent_id: str) -> UpdateAgentResponseModel:
        """Get agent interaction statistics."""
        agent = await AgentService.get_agent(agent_id)
        if not agent:
            return None

        # Get feedback counts from database
        from ..database.database import Database
        db = Database()
        await db.initialize()

        try:
            # Count instant feedback
            instant_feedback_result = await db.db.execute(
                "SELECT COUNT(*) as count FROM feedback WHERE agent_id = ? AND feedback_type = 'instant'",
                (agent_id,)
            )
            instant_feedback_count = (await instant_feedback_result.fetchone())['count']

            # Count comprehensive feedback
            comprehensive_feedback_result = await db.db.execute(
                "SELECT COUNT(*) as count FROM feedback WHERE agent_id = ? AND feedback_type = 'comprehensive'",
                (agent_id,)
            )
            comprehensive_feedback_count = (await comprehensive_feedback_result.fetchone())['count']

            # Calculate average processing time
            processing_time_result = await db.db.execute(
                "SELECT AVG(processing_time) as avg_time FROM feedback WHERE agent_id = ? AND processing_time IS NOT NULL",
                (agent_id,)
            )
            avg_processing_time = (await processing_time_result.fetchone())['avg_time']

            # Get last interaction time
            last_interaction_result = await db.db.execute(
                "SELECT MAX(created_at) as last_interaction FROM feedback WHERE agent_id = ?",
                (agent_id,)
            )
            last_interaction = (await last_interaction_result.fetchone())['last_interaction']

        except Exception as e:
            print(f"Error getting agent stats: {e}")
            instant_feedback_count = 0
            comprehensive_feedback_count = 0
            avg_processing_time = None
            last_interaction = None

        return UpdateAgentResponseModel(
            "success",
            UpdateAgentModel(
                agent_id=agent_id,
                total_interactions=agent.total_interactions,
                instant_feedback_count=instant_feedback_count,
                comprehensive_feedback_count=comprehensive_feedback_count,
                average_processing_time=avg_processing_time,
                last_interaction=last_interaction
            ))

    @staticmethod
    async def check_agent_health(agent_id: str) -> Optional[UpdateAgentResponseModel]:
        """Check agent health status."""
        agent = await AgentService.get_agent(agent_id)
        if not agent:
            return None

        # Get error count from database
        from ..database.database import Database
        db = Database()
        await db.initialize()

        try:
            # Count errors in the last 24 hours
            error_count_result = await db.db.execute(
                "SELECT COUNT(*) as error_count FROM feedback WHERE agent_id = ? AND status = 'error' AND created_at > datetime('now', '-1 day')",
                (agent_id,)
            )
            error_count = (await error_count_result.fetchone())['error_count']

            # Calculate uptime percentage (simplified - in production, track actual uptime)
            total_interactions = agent.total_interactions
            if total_interactions > 0:
                success_count = total_interactions - error_count
                uptime_percentage = (success_count / total_interactions) * 100
            else:
                uptime_percentage = 100.0

        except Exception as e:
            print(f"Error calculating agent health: {e}")
            error_count = 0
            uptime_percentage = 99.5

        # Simple health check - in production, this would ping the LLM service
        health_status = AgentStatus.ACTIVE if agent.status == "active" else AgentStatus.ERROR

        return UpdateAgentResponseModel(
            "sucess",
            UpdateAgentModel(agent_id=agent_id,
                                   status=health_status,
                                   last_health_check=datetime.utcnow(),
                                   error_count=error_count,
                                   uptime_percentage=uptime_percentage
                                   )
        )

    @staticmethod
    async def get_agents_by_type(room_id: str, agent_type: AgentType) -> List[AgentModel]:
        """Get agents by type for a specific room."""
        all_agents = await AgentService.get_agents_by_room(room_id)
        return [agent for agent in all_agents if agent.agent_type == agent_type.value]

    @staticmethod
    async def get_active_agents(room_id: str) -> List[AgentModel]:
        """Get all active agents for a room."""
        all_agents = await AgentService.get_agents_by_room(room_id)
        return [agent for agent in all_agents if agent.status == AgentStatus.ACTIVE.value]


# Singleton instance
agent_service = AgentService()
