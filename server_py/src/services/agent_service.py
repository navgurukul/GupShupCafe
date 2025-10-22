"""
Agent Service
Business logic for AI agent management and interactions with transcripts/feedback
Integrates with actual Strands-based agents for live responses
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import asyncio
import json
import logging

# Import actual agent implementations
from ..agents.english_feedback_agent import EnglishFeedbackAgent
from ..agents.debate_facilitator_agent import DebateFacilitatorAgent
from ..agents.agentcore import AgentCore
from ..llm.strands_model_adapter import StrandsModelAdapter

from ..models import TranscriptModel, UpdateTranscriptModel, UpdateTranscriptResponseModel
from .transcript_service import transcript_service
from .feedback_service import feedback_service

from ..database.database import db
from ..models import (
    CreateAgentModel,
    CreateAgentResponseModel,
    AgentModel,
    AgentReplyModel,
    AgentReplyResponseModel,
    UpdateAgentModel,
    UpdateAgentResponseModel,
    DeleteAgentResponseModel,
    AgentUpdateModel,
    AgentTranscriptProcessingModel,
    AgentFeedbackGenerationModel,
    AgentInteractionStatsModel,
    AgentHealthModel,
    AgentResponseTextModel,
    ListAgentsResponseModel,
    AgentStatus,
    AgentType,
    AgentModelSource
)

logger = logging.getLogger(__name__)


class AgentService:
    """Service class for agent operations and interactions with live Strands agents."""
    
    # Class-level cache for agent instances
    _agent_instances: Dict[str, Any] = {}
    _agent_core: Optional[AgentCore] = None

    @staticmethod
    def _get_or_create_agent_core() -> AgentCore:
        """Get or create the AgentCore instance (singleton pattern)."""
        if AgentService._agent_core is None:
            try:
                AgentService._agent_core = AgentCore(
                    model_provider=None,  # Uses environment default
                    max_tokens=500,
                    enable_mcp_tools=True
                )
                AgentService._agent_core.activate_mcp_tools()
                logger.info("✅ AgentCore initialized and MCP tools activated")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize AgentCore with MCP tools: {e}")
                # Fallback without MCP tools
                AgentService._agent_core = AgentCore(
                    model_provider=None,
                    max_tokens=500,
                    enable_mcp_tools=False
                )
                logger.info("✅ AgentCore initialized without MCP tools")
        
        return AgentService._agent_core
    
    @staticmethod
    def _get_agent_instance(agent_id: str, agent_type: str) -> Optional[Any]:
        """Get cached agent instance or create new one."""
        if agent_id in AgentService._agent_instances:
            return AgentService._agent_instances[agent_id]
        
        try:
            # Create Strands model
            model = StrandsModelAdapter.create_model()
            
            # Create appropriate agent instance
            if agent_type == AgentType.ENGLISH.value:
                agent_instance = EnglishFeedbackAgent(model)
            elif agent_type == AgentType.FACILITATOR.value:
                agent_instance = DebateFacilitatorAgent(model)
            else:
                logger.error(f"Unknown agent type: {agent_type}")
                return None
            
            # Cache the instance
            AgentService._agent_instances[agent_id] = agent_instance
            logger.info(f"✅ Created and cached {agent_type} agent instance: {agent_id}")
            
            return agent_instance
            
        except Exception as e:
            logger.error(f"Failed to create agent instance {agent_id}: {e}")
            return None

    @staticmethod
    async def create_agent(agent_data: CreateAgentModel) -> CreateAgentResponseModel:
        """Create a new agent instance."""
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
            
            # Create the agent model for response
            agent_model = AgentModel(
                agent_id=agent_id,
                room_id=agent_data.room_id,
                agent_model=agent_data.agent_model.value,
                agent_type=agent_data.agent_type.value,
                status=agent_data.status.value if agent_data.status else AgentStatus.ACTIVE.value,
                total_interactions=0,
                created_at=datetime.utcnow()
            )
            
            return CreateAgentResponseModel(
                success=True,
                data=agent_model,
                message="Agent created successfully"
            )
        except Exception as e:
            print(f"Error creating agent: {e}")
            return CreateAgentResponseModel(
                success=False,
                data=None,
                message=f"Failed to create agent: {str(e)}"
            )

    @staticmethod
    async def create_room_agents(room_id: str, room_topic: str = None) -> Dict[str, str]:
        """
        Create both facilitator and English feedback agents for a room.

        Returns dict with agent_ids: {'facilitator': agent_id, 'english': agent_id}
        """

        # Create facilitator agent
        facilitator_data = CreateAgentModel(
            room_id=room_id,
            agent_model=AgentModelSource.GEMINI,
            agent_type=AgentType.FACILITATOR,
        )
        facilitator_response = await AgentService.create_agent(facilitator_data)
        facilitator_id = facilitator_response.data.agent_id if facilitator_response.success else None

        # Create English feedback agent
        english_data = CreateAgentModel(
            room_id=room_id,
            agent_model=AgentModelSource.GEMINI,
            agent_type=AgentType.ENGLISH,
        )
        english_response = await AgentService.create_agent(english_data)
        english_id = english_response.data.agent_id if english_response.success else None

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
        """Get all agents for a specific room."""
        try:
            agents_data = await db.get_agents_by_room(room_id)
            agents = [AgentModel(**agent) for agent in agents_data]
            return agents
        except Exception as e:
            print(f"Error fetching agents for room {room_id}: {e}")
            return []

    @staticmethod
    async def update_agent(agent_id: str, update_data: AgentUpdateModel) -> UpdateAgentResponseModel:
        """Update agent properties."""
        update_dict = {}

        if update_data.status:
            update_dict["status"] = update_data.status.value

        if not update_dict:
            return UpdateAgentResponseModel(
                status="error",
                data=update_data,
                message="No valid fields to update"
            )

        # Use existing database method to update status
        try:
            if "status" in update_dict:
                result = await db.update_agent_status(agent_id, update_dict["status"])
                if result > 0:
                    return UpdateAgentResponseModel(
                        status="success",
                        data=update_data,
                        message="Agent updated successfully"
                    )
                else:
                    return UpdateAgentResponseModel(
                        status="error",
                        data=update_data,
                        message="Agent not found or no changes made"
                    )
        except Exception as e:
            print(f"Error updating agent {agent_id}: {e}")
            return UpdateAgentResponseModel(
                status="error",
                data=update_data,
                message=f"Failed to update agent: {str(e)}"
            )

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
        """Delete an agent."""
        try:
            result = await db.delete_agent(agent_id)
            if result > 0:
                return DeleteAgentResponseModel(
                    status="success",
                    data=agent_id,
                    message="Agent deleted successfully"
                )
            else:
                return DeleteAgentResponseModel(
                    status="error",
                    data=agent_id,
                    message="Agent not found"
                )
        except Exception as e:
            print(f"Error deleting agent {agent_id}: {e}")
            return DeleteAgentResponseModel(
                status="error",
                data=agent_id,
                message=f"Failed to delete agent: {str(e)}"
            )

    @staticmethod
    async def process_transcript_for_feedback(
        agent_id: str,
        transcript_id: str,
        feedback_type: str = "instant"
    ) -> AgentReplyModel:
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

            return AgentReplyModel(
                agent_id=agent_id,
                response_text=feedback_text
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
        """Generate English language feedback using the actual EnglishFeedbackAgent."""
        try:
            # Get the actual agent instance
            agent_instance = AgentService._get_agent_instance(
                agent.agent_id, 
                agent.agent_type
            )
            
            if not agent_instance:
                logger.error(f"Failed to get English agent instance for {agent.agent_id}")
                return "Unable to generate feedback at this time."
            
            # Prepare data for the agent
            transcript_text = transcript_data.get("transcript_text", "")
            room_id = transcript_data.get("room_id", "")
            participant_id = transcript_data.get("participant_id", "")
            
            # Get room context if available
            try:
                from .room_service import room_service
                room_data = await room_service.get_room(room_id)
                topic = room_data.topic if room_data else "general discussion"
            except Exception as e:
                logger.warning(f"Could not get room context: {e}")
                topic = "general discussion"
            
            # Prepare context for the agent
            context = {
                "topic": topic,
                "feedback_type": feedback_type,
                "speaker_info": {
                    "participant_id": participant_id,
                    "word_count": transcript_data.get("word_count", 0),
                    "speech_rate": transcript_data.get("speech_rate", 0)
                }
            }
            
            # Call the actual agent
            analysis_data = {
                "text": transcript_text,
                "context": context
            }
            
            result = await agent_instance.analyze(analysis_data)
            
            # Format the response based on feedback type
            if feedback_type == "instant":
                # Quick feedback format
                cefr_level = result.get("cefr_level", "")
                suggestions = result.get("suggestions", [])
                
                feedback_parts = []
                if cefr_level:
                    feedback_parts.append(f"CEFR Level: {cefr_level}")
                
                if suggestions:
                    # Take first 2 suggestions for instant feedback
                    for suggestion in suggestions[:2]:
                        feedback_parts.append(f"• {suggestion}")
                
                return " | ".join(feedback_parts) if feedback_parts else "Keep practicing!"
            
            else:  # comprehensive feedback
                # Return the full analysis text
                return result.get("analysis", "Comprehensive analysis completed.")
                
        except Exception as e:
            logger.error(f"Error generating English feedback: {e}")
            # Fallback to simple feedback
            transcript_text = transcript_data.get("transcript_text", "")
            word_count = len(transcript_text.split()) if transcript_text else 0
            
            if feedback_type == "instant":
                return f"Good contribution! ({word_count} words) Keep practicing your English skills."
            else:
                return f"Thank you for your participation. Your contribution of {word_count} words shows engagement with the topic. Continue practicing to improve your fluency and vocabulary."

    @staticmethod
    async def _generate_facilitator_response(
        agent: AgentModel,
        transcript_data: Dict[str, Any]
    ) -> str:
        """Generate facilitator response using the actual DebateFacilitatorAgent."""
        try:
            # Get the actual agent instance
            agent_instance = AgentService._get_agent_instance(
                agent.agent_id, 
                agent.agent_type
            )
            
            if not agent_instance:
                logger.error(f"Failed to get Facilitator agent instance for {agent.agent_id}")
                return "Thank you for your contribution to the discussion."
            
            # Prepare context for the facilitator
            transcript_text = transcript_data.get("transcript_text", "")
            room_id = transcript_data.get("room_id", "")
            participant_id = transcript_data.get("participant_id", "")
            
            # Get room and participant context
            try:
                from .room_service import room_service
                from .participant_service import participant_service
                
                room_data = await room_service.get_room(room_id)
                topic = room_data.topic if room_data else "the current topic"
                
                participant_data = await participant_service.get_participant(participant_id)
                speaker_name = participant_data.anonymous_name if participant_data else "Speaker"
                
            except Exception as e:
                logger.warning(f"Could not get room/participant context: {e}")
                topic = "the current topic"
                speaker_name = "Speaker"
            
            # Get recent statements for context
            try:
                recent_transcripts = await db.get_recent_transcripts(room_id, limit=5)
                previous_statements = [
                    t.get("transcript_text", "") 
                    for t in recent_transcripts 
                    if t.get("transcript_text")
                ]
            except Exception as e:
                logger.warning(f"Could not get recent transcripts: {e}")
                previous_statements = []
            
            # Prepare context for the facilitator agent
            context = {
                "topic": topic,
                "current_speaker": {"anonymous_name": speaker_name},
                "turn_number": len(previous_statements) + 1,
                "previous_statements": previous_statements,
                "current_round": 1,  # Could be enhanced to track actual rounds
                "total_rounds": 3
            }
            
            # Generate facilitator response
            response = await agent_instance.facilitate_turn(context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating facilitator response: {e}")
            # Fallback responses based on content analysis
            transcript_text = transcript_data.get("transcript_text", "").lower()
            
            if "agree" in transcript_text:
                return "I appreciate you sharing that perspective. What specific examples support your viewpoint?"
            elif "disagree" in transcript_text:
                return "Thank you for presenting a different angle. Can you help us understand your reasoning?"
            elif "?" in transcript_text:
                return "That's an excellent question. Let's explore this together. What do others think?"
            else:
                return "Interesting point! How do you think this connects to what we discussed earlier?"

    @staticmethod
    async def generate_facilitator_turn_response(
        room_id: str,
        recent_transcripts: List[Dict[str, Any]],
        feedback_summaries: List[Dict[str, Any]]
    ) -> str:
        """
        Generate facilitator's speaking turn response using the actual DebateFacilitatorAgent.
        """
        try:
            # Get the facilitator agent for this room
            agents = await AgentService.get_agents_by_room(room_id)
            facilitator = next(
                (a for a in agents if a.agent_type == AgentType.FACILITATOR.value), None)

            if not facilitator:
                return "Thank you all for your thoughtful contributions to this discussion."

            # Get the actual agent instance
            agent_instance = AgentService._get_agent_instance(
                facilitator.agent_id, 
                facilitator.agent_type
            )
            
            if not agent_instance:
                logger.error(f"Failed to get Facilitator agent instance for {facilitator.agent_id}")
                return "Thank you all for your thoughtful contributions to this discussion."

            # Get room context
            try:
                from .room_service import room_service
                room_data = await room_service.get_room(room_id)
                topic = room_data.topic if room_data else "the current discussion"
            except Exception as e:
                logger.warning(f"Could not get room context: {e}")
                topic = "the current discussion"

            # Extract statements from recent transcripts
            statements = [
                transcript.get("transcript_text", "")
                for transcript in recent_transcripts
                if transcript.get("transcript_text")
            ]

            # Prepare context for the facilitator
            context = {
                "topic": topic,
                "statements": statements,
                "participants": len(set(t.get("participant_id") for t in recent_transcripts if t.get("participant_id"))),
                "feedback_summaries": feedback_summaries
            }

            # Use the facilitator agent to suggest topic direction
            response = await agent_instance.suggest_topic_direction(statements)
            
            # If the response is too short, enhance it with encouragement
            if len(response.split()) < 10:
                encouragement = await agent_instance.generate_speaking_prompt(topic, context)
                response = f"{response} {encouragement}"

            return response

        except Exception as e:
            logger.error(f"Error generating facilitator turn response: {e}")
            
            # Fallback logic
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
    async def get_agent_stats(agent_id: str) -> AgentInteractionStatsModel:
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

        return AgentInteractionStatsModel(
            agent_id=agent_id,
            total_interactions=agent.total_interactions,
            successful_interactions=agent.total_interactions - (instant_feedback_count + comprehensive_feedback_count),
            failed_interactions=instant_feedback_count + comprehensive_feedback_count,
            average_response_time=avg_processing_time or 0.0,
            last_interaction=last_interaction
        )

    @staticmethod
    async def check_agent_health(agent_id: str) -> Optional[Dict[str, Any]]:
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
        is_healthy = health_status == AgentStatus.ACTIVE and uptime_percentage > 95.0

        return AgentHealthModel(
            agent_id=agent_id,
            status=health_status,
            is_healthy=is_healthy,
            last_health_check=datetime.utcnow(),
            error_message=None if is_healthy else f"Uptime: {uptime_percentage:.1f}%, Errors: {error_count}",
            uptime_seconds=int(uptime_percentage * 3600)  # Simplified uptime calculation
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

    @staticmethod
    async def generate_live_agent_response(
        room_id: str,
        agent_type: AgentType,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate live agent response for socket events.
        
        Args:
            room_id: Room ID where the agent operates
            agent_type: Type of agent (ENGLISH or FACILITATOR)
            context: Context data including transcripts, participants, etc.
            
        Returns:
            Generated response text or None if failed
        """
        try:
            # Get the agent for this room and type
            agents = await AgentService.get_agents_by_room(room_id)
            target_agent = next(
                (a for a in agents if a.agent_type == agent_type.value), None)
            
            if not target_agent:
                logger.warning(f"No {agent_type.value} agent found for room {room_id}")
                return None
            
            # Get the actual agent instance
            agent_instance = AgentService._get_agent_instance(
                target_agent.agent_id, 
                target_agent.agent_type
            )
            
            if not agent_instance:
                logger.error(f"Failed to get agent instance for {target_agent.agent_id}")
                return None
            
            # Generate response based on agent type
            if agent_type == AgentType.ENGLISH:
                # For English agent, analyze the latest transcript
                latest_transcript = context.get("latest_transcript", {})
                if not latest_transcript:
                    return None
                
                # Get room topic for context
                try:
                    from .room_service import room_service
                    room_data = await room_service.get_room(room_id)
                    topic = room_data.topic if room_data else "general discussion"
                except Exception:
                    topic = "general discussion"
                
                analysis_data = {
                    "text": latest_transcript.get("transcript_text", ""),
                    "context": {
                        "topic": topic,
                        "feedback_type": "instant",
                        "speaker_info": {
                            "participant_id": latest_transcript.get("participant_id", ""),
                            "word_count": latest_transcript.get("word_count", 0),
                            "speech_rate": latest_transcript.get("speech_rate", 0)
                        }
                    }
                }
                
                result = await agent_instance.analyze(analysis_data)
                
                # Format for instant feedback
                cefr_level = result.get("cefr_level", "")
                suggestions = result.get("suggestions", [])
                
                feedback_parts = []
                if cefr_level:
                    feedback_parts.append(f"CEFR Level: {cefr_level}")
                
                if suggestions:
                    for suggestion in suggestions[:2]:  # Limit to 2 suggestions
                        feedback_parts.append(f"• {suggestion}")
                
                return " | ".join(feedback_parts) if feedback_parts else "Keep practicing!"
            
            elif agent_type == AgentType.FACILITATOR:
                # For Facilitator agent, provide turn guidance or topic direction
                recent_transcripts = context.get("recent_transcripts", [])
                
                if not recent_transcripts:
                    # Generate opening prompt
                    try:
                        from .room_service import room_service
                        room_data = await room_service.get_room(room_id)
                        topic = room_data.topic if room_data else "the current topic"
                    except Exception:
                        topic = "the current topic"
                    
                    return await agent_instance.generate_speaking_prompt(topic)
                
                # Extract statements for topic direction
                statements = [
                    t.get("transcript_text", "")
                    for t in recent_transcripts
                    if t.get("transcript_text")
                ]
                
                return await agent_instance.suggest_topic_direction(statements)
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating live agent response: {e}")
            return None

    @staticmethod
    async def provide_encouragement_to_participant(
        room_id: str,
        participant_id: str
    ) -> Optional[str]:
        """
        Generate encouragement for a specific participant using the facilitator agent.
        
        Args:
            room_id: Room ID
            participant_id: Participant to encourage
            
        Returns:
            Encouragement message or None if failed
        """
        try:
            # Get facilitator agent
            agents = await AgentService.get_agents_by_room(room_id)
            facilitator = next(
                (a for a in agents if a.agent_type == AgentType.FACILITATOR.value), None)
            
            if not facilitator:
                return None
            
            agent_instance = AgentService._get_agent_instance(
                facilitator.agent_id, 
                facilitator.agent_type
            )
            
            if not agent_instance:
                return None
            
            # Get participant and room context
            try:
                from .participant_service import participant_service
                from .room_service import room_service
                
                participant_data = await participant_service.get_participant(participant_id)
                room_data = await room_service.get_room(room_id)
                
                participant_info = {
                    "anonymous_name": participant_data.anonymous_name if participant_data else "participant"
                }
                
                context = {
                    "topic": room_data.topic if room_data else "this topic"
                }
                
                return await agent_instance.provide_encouragement(participant_info, context)
                
            except Exception as e:
                logger.warning(f"Could not get participant/room context: {e}")
                return "Thank you for your participation! Please share your thoughts."
            
        except Exception as e:
            logger.error(f"Error providing encouragement: {e}")
            return None


# Singleton instance
agent_service = AgentService()
