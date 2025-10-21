from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

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

class CreateAgentModel(BaseModel):
    """Model for creating a new agent instance."""
    room_id: str = Field(..., description="Room ID where the agent will operate")
    agent_model: AgentModelSource = Field(..., description="LLM service (Gemini or Bedrock)")
    agent_type: AgentType = Field(default=AgentType.ENGLISH, description="Agent specialization type")
    status: AgentStatus = Field(default=AgentStatus.ACTIVE, description="Initial agent status")

class CreateAgentResponseModel(BaseModel):
    """Response model for agent creation."""
    success: bool = Field(..., description="Creation success status")
    data: str = Field(..., description="Created agent ID")
    message: Optional[str] = Field(None, description="Additional message")

class AgentModel(BaseModel):
    """Full agent model as represented in the database."""
    agent_id: str = Field(..., description="Unique identifier for the agent instance")
    room_id: str = Field(..., description="Room ID where the agent operates")
    agent_model: str = Field(..., description="LLM service (Gemini or Bedrock)")
    agent_type: str = Field(..., description="Agent specialization type")
    status: str = Field(..., description="Current agent status")
    total_interactions: int = Field(default=0, description="Counter for LLM invocations")
    created_at: datetime = Field(..., description="Timestamp of agent creation")
    
    class Config:
        from_attributes = True

class AgentUpdateModel(BaseModel):
    """Model for updating an agent's properties."""
    status: Optional[AgentStatus] = Field(None, description="Update the agent's status")
    agent_type: Optional[AgentType] = Field(None, description="Update the agent's type")

# --- Agent Interaction Models ---

class AgentTranscriptProcessingModel(BaseModel):
    """Model for agent processing transcript data."""
    agent_id: str = Field(..., description="Agent processing the transcript")
    transcript_id: str = Field(..., description="Transcript being processed")
    processing_type: str = Field(..., description="Type of processing (instant_feedback, comprehensive_feedback)")

class AgentFeedbackGenerationModel(BaseModel):
    """Model for agent generating feedback."""
    agent_id: str = Field(..., description="Agent generating feedback")
    transcript_id: str = Field(..., description="Source transcript")
    participant_id: str = Field(..., description="Target participant")
    feedback_type: str = Field(..., description="Type of feedback (instant or comprehensive)")

class AgentResponseModel(BaseModel):
    """Model for agent response data."""
    agent_id: str = Field(..., description="Agent that generated the response")
    response_text: str = Field(..., description="Generated response text")
    processing_time: float = Field(..., description="Time taken to generate response")
    confidence_score: Optional[float] = Field(None, description="Confidence in the response")
    tokens_used: Optional[int] = Field(None, description="Number of tokens consumed")

# --- Agent Analytics Models ---

class AgentInteractionStatsModel(BaseModel):
    """Model for agent interaction statistics."""
    agent_id: str = Field(..., description="Agent identifier")
    total_interactions: int = Field(..., description="Total interactions count")
    instant_feedback_count: int = Field(default=0, description="Number of instant feedback generated")
    comprehensive_feedback_count: int = Field(default=0, description="Number of comprehensive feedback generated")
    average_processing_time: Optional[float] = Field(None, description="Average processing time in seconds")
    last_interaction: Optional[datetime] = Field(None, description="Timestamp of last interaction")

class AgentHealthModel(BaseModel):
    """Model for agent health status."""
    agent_id: str = Field(..., description="Agent identifier")
    status: AgentStatus = Field(..., description="Current health status")
    last_health_check: datetime = Field(..., description="Last health check timestamp")
    error_count: int = Field(default=0, description="Number of errors in last 24 hours")
    uptime_percentage: Optional[float] = Field(None, description="Uptime percentage")