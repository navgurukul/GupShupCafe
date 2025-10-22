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


# --- Get Model for retrieving agents ---

class GetAgentModel(BaseDictModel):
    """Model for getting agent with optional filters"""
    agent_id: str = Field(..., description="Unique identifier for the agent instance")
    
    # All other fields from CreateAgentModel as optional
    room_id: Optional[str] = Field(None, description="Room ID where the agent operates")
    agent_model: Optional[str] = Field(None, description="LLM service (Gemini or Bedrock)")
    agent_type: Optional[str] = Field(None, description="Agent specialization type")
    status: Optional[str] = Field(None, description="Current agent status")
    total_interactions: Optional[int] = Field(None, description="Counter for LLM invocations")
    created_at: Optional[datetime] = Field(None, description="Timestamp of agent creation")


class CreateAgentResponseModel(BaseDictModel):
    """Response model for agent creation."""
    success: bool = Field(..., description="Creation success status")
    data: AgentModel = Field(..., description="Created agent data")
    message: Optional[str] = Field(None, description="Additional message")

# --- Agent Interaction Models ---


class AgentReplyModel(BaseDictModel):
    """Model for agent response data."""
    agent_id: str = Field(..., description="Agent that generated the response")
    response_text: str = Field(..., description="Generated response text")


class AgentReplyResponseModel(BaseDictModel):
    """Response model for agent replies"""
    status: str = Field(..., description="Reply operation status")
    data: AgentReplyModel = Field(..., description="Agent reply data")
    message: Optional[str] = Field(None, description="Additional message")

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
