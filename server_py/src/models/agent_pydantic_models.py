from pydantic import Field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

from .base_dict_model import BaseDictModel



# --- Enums for the Agent Model ---


class AgentStatus(str, Enum):
    """Represents the operational status of an agent instance."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PROCESSING = "processing"


class AgentType(str, Enum):
    """Defines the role of the agent in a room."""
    FACILITATOR = "facilitator"
    ENGLISH = "english"
    TUTOR = "tutor"
    MODERATOR = "moderator"


class AgentModelSource(str, Enum):
    """Specifies the underlying LLM service."""
    GEMINI = "Gemini"
    BEDROCK = "Bedrock"

# --- Core Agent Models ---


class CreateAgentModel(BaseDictModel):
    """Model for creating a new agent instance."""
    room_id: str = Field(...,
                         description="Room ID where the agent will operate")
    agent_model: AgentModelSource = Field(...,
                                          description="LLM service (Gemini or Bedrock)")
    agent_type: AgentType = Field(
        default=AgentType.ENGLISH, description="Agent specialization type")
    status: AgentStatus = Field(
        default=AgentStatus.ACTIVE, description="Initial agent status")


class AgentModel(BaseDictModel):
    """Full agent model as represented in the database."""
    agent_id: str = Field(...,
                          description="Unique identifier for the agent instance")
    room_id: str = Field(..., description="Room ID where the agent operates")
    agent_model: str = Field(...,
                             description="LLM service (Gemini or Bedrock)")
    agent_type: str = Field(..., description="Agent specialization type")
    status: str = Field(..., description="Current agent status")
    total_interactions: int = Field(
        default=0, description="Counter for LLM invocations")
    created_at: datetime = Field(...,
                                 description="Timestamp of agent creation")

    class Config:
        from_attributes = True


class CreateAgentResponseModel(BaseDictModel):
    """Response model for agent creation."""
    success: bool = Field(..., description="Creation success status")
    data: AgentModel = Field(..., description="Created agent data")
    message: Optional[str] = Field(None, description="Additional message")

# --- Agent Interaction Models ---

class AgentResponseModel(BaseDictModel):
    """Model for agent response data."""
    agent_id: str = Field(..., description="Agent that generated the response")
    response_text: str = Field(..., description="Generated response text")
    processing_time: float = Field(...,
                                   description="Time taken to generate response")
    confidence_score: Optional[float] = Field(
        None, description="Confidence in the response")
    tokens_used: Optional[int] = Field(
        None, description="Number of tokens consumed")

# --- List Models ---


class ListAgentsResponseModel(BaseDictModel):
    """Response model for listing agents"""
    status: str = Field(..., description="List operation status")
    data: List[AgentModel] = Field(..., description="List of agents")
    message: Optional[str] = Field(None, description="Additional message")

# --- Update Models ---


class UpdateAgentModel(BaseDictModel):
    """Model for updating agent details."""
    status: Optional[AgentStatus] = Field(
        None, description="Updated agent status")
    agent_type: Optional[AgentType] = Field(
        None, description="Updated agent type")
    total_interactions: Optional[int] = Field(
        None, description="Updated total interactions count")


class UpdateAgentResponseModel(BaseDictModel):
    """Response model for updating agent"""
    status: str = Field(..., description="Update operation status")
    data: UpdateAgentModel = Field(..., description="Updated agent data")
    message: Optional[str] = Field(None, description="Additional message")

# --- Delete Models ---


class DeleteAgentResponseModel(BaseDictModel):
    """Response model for deleting agent"""
    status: str = Field(..., description="Delete operation status")
    data: str = Field(..., description="Deleted agent ID")
    message: Optional[str] = Field(None, description="Additional message")

# --- Additional Agent Models ---

class AgentUpdateModel(BaseDictModel):
    """Model for updating agent details"""
    agent_id: str = Field(..., description="Agent ID")
    status: Optional[AgentStatus] = Field(None, description="Updated agent status")
    total_interactions: Optional[int] = Field(None, description="Updated total interactions count")

class AgentTranscriptProcessingModel(BaseDictModel):
    """Model for agent transcript processing"""
    agent_id: str = Field(..., description="Agent ID")
    transcript_id: str = Field(..., description="Transcript ID")
    processing_status: str = Field(..., description="Processing status")
    processing_result: Optional[str] = Field(None, description="Processing result")

class AgentFeedbackGenerationModel(BaseDictModel):
    """Model for agent feedback generation"""
    agent_id: str = Field(..., description="Agent ID")
    participant_id: str = Field(..., description="Participant ID")
    feedback_type: str = Field(..., description="Type of feedback generated")
    feedback_content: str = Field(..., description="Feedback content")

class AgentInteractionStatsModel(BaseDictModel):
    """Model for agent interaction statistics"""
    agent_id: str = Field(..., description="Agent ID")
    total_interactions: int = Field(..., description="Total interactions count")
    successful_interactions: int = Field(..., description="Successful interactions count")
    failed_interactions: int = Field(..., description="Failed interactions count")
    average_response_time: float = Field(..., description="Average response time in seconds")

class AgentHealthModel(BaseDictModel):
    """Model for agent health status"""
    agent_id: str = Field(..., description="Agent ID")
    status: str = Field(..., description="Agent status")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    health_score: float = Field(..., description="Health score (0.0-1.0)")
    error_count: int = Field(..., description="Error count")
    uptime_seconds: int = Field(..., description="Uptime in seconds")

