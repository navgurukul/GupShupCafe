from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

from .base_dict_model import BaseDictModel

# --- Enums Referenced by the Models ---
from .enums import CEFRLevel

class RoomStatus(str, Enum):
    """Room status enumeration"""
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# --- Model for Creating a Room ---

class CreateRoomModel(BaseDictModel):
    """Complete Room model matching the schema"""
    room_name: Optional[str] = Field(None, description="Human-readable room name")
    
    # Room Configuration
    topic_title: str = Field(..., description="Discussion topic")
    topic_category: str = Field(..., description="Topic category (Technology, Current Events, etc.)")
    max_participants: int = Field(default=6, description="Maximum number of participants")
    speaking_time_per_turn: int = Field(default=60, description="Speaking time per turn in seconds")
    num_rounds: int = Field(default=3, description="Number of discussion rounds")
    cefr_level: CEFRLevel = Field(..., description="CEFR level for the room")

    # Room State
    status: RoomStatus = Field(default=RoomStatus.WAITING, description="Room status")
    current_round: int = Field(default=0, description="Current round number")
    current_speaker_index: int = Field(default=0, description="Current speaker index")
    rounds_completed: int = Field(default=0, description="Number of rounds completed")
    
    # Participants
    participant_count: int = Field(default=0, description="Number of participants")
    
    # Timing
    started_at: Optional[datetime] = Field(None, description="Room start time")
    ended_at: Optional[datetime] = Field(None, description="Room end time")
    duration_seconds: int = Field(default=0, description="Room duration in seconds")
    
    # Facilitator Agent
    facilitator_agent_id: Optional[str] = Field(None, description="AWS Strands facilitator agent instance ID")
    english_agent_id: Optional[str] = Field(None, description="AWS Strands English agent instance ID")

    # Metadata
    created_by: str = Field(..., description="User ID who created the room")

# --- Get Model for retrieving rooms ---

class GetRoomModel(BaseDictModel):
    """Model for getting room with optional filters"""
    room_id: str = Field(..., description="Room UUID, Primary Key")
    
    # All other fields from CreateRoomModel as optional
    room_name: Optional[str] = Field(None, description="Human-readable room name")
    topic_title: Optional[str] = Field(None, description="Discussion topic")
    topic_category: Optional[str] = Field(None, description="Topic category")
    max_participants: Optional[int] = Field(None, description="Maximum number of participants")
    speaking_time_per_turn: Optional[int] = Field(None, description="Speaking time per turn in seconds")
    num_rounds: Optional[int] = Field(None, description="Number of discussion rounds")
    cefr_level: Optional[CEFRLevel] = Field(None, description="CEFR level for the room")
    status: Optional[RoomStatus] = Field(None, description="Room status")
    current_round: Optional[int] = Field(None, description="Current round number")
    current_speaker_index: Optional[int] = Field(None, description="Current speaker index")
    participant_count: Optional[int] = Field(None, description="Number of participants")
    started_at: Optional[datetime] = Field(None, description="Room start time")
    ended_at: Optional[datetime] = Field(None, description="Room end time")
    duration_seconds: Optional[int] = Field(None, description="Room duration in seconds")
    facilitator_agent_id: Optional[str] = Field(None, description="AWS Strands facilitator agent instance ID")
    english_agent_id: Optional[str] = Field(None, description="AWS Strands English agent instance ID")
    created_by: Optional[str] = Field(None, description="User ID who created the room")
    created_at: Optional[datetime] = Field(None, description="Timestamp when room was created")


# --- Model for data read from DB (includes PK and creation time) ---

class RoomModel(CreateRoomModel):
    """Full Room model as represented in the database, including PK."""
    room_id: str = Field(..., description="Room UUID, Primary Key")
    created_at: datetime = Field(..., description="Timestamp when room was created")

    class Config:
        from_attributes = True

class CreateRoomResponseModel(BaseDictModel):
    """Response model for room creation"""
    status: str = Field(..., description="Room creation status message")
    data: Optional[RoomModel] = Field(None, description="Created room data")
    message: Optional[str] = Field(None, description="Additional message")


# --- List Models ---

class ListRoomsResponseModel(BaseDictModel):
    """Response model for listing rooms"""
    status: str = Field(..., description="List operation status")
    data: List[RoomModel] = Field(..., description="List of rooms")
    message: Optional[str] = Field(None, description="Additional message")

# --- Update Models ---

class UpdateRoomModel(BaseDictModel):
    """Model for updating room details."""
    room_name: Optional[str] = Field(None, description="Updated room name")
    topic_title: Optional[str] = Field(None, description="Updated discussion topic")
    topic_category: Optional[str] = Field(None, description="Updated topic category")
    max_participants: Optional[int] = Field(None, description="Updated maximum participants")
    speaking_time_per_turn: Optional[int] = Field(None, description="Updated speaking time per turn")
    num_rounds: Optional[int] = Field(None, description="Updated number of rounds")
    cefr_level: Optional[CEFRLevel] = Field(None, description="Updated CEFR level")
    status: Optional[RoomStatus] = Field(None, description="Updated room status")
    current_round: Optional[int] = Field(None, description="Updated current round")
    current_speaker_index: Optional[int] = Field(None, description="Updated current speaker index")
    rounds_completed: Optional[int] = Field(None, description="Updated rounds completed")
    participant_count: Optional[int] = Field(None, description="Updated participant count")
    started_at: Optional[datetime] = Field(None, description="Updated start time")
    ended_at: Optional[datetime] = Field(None, description="Updated end time")
    duration_seconds: Optional[int] = Field(None, description="Updated duration")
    facilitator_agent_id: Optional[str] = Field(None, description="Updated facilitator agent ID")
    english_agent_id: Optional[str] = Field(None, description="Updated English agent ID")

class UpdateRoomResponseModel(BaseDictModel):
    """Response model for updating room"""
    status: str = Field(..., description="Update operation status")
    data: UpdateRoomModel = Field(..., description="Updated room data")
    message: Optional[str] = Field(None, description="Additional message")

# --- Delete Models ---

class DeleteRoomResponseModel(BaseDictModel):
    """Response model for deleting room"""
    status: str = Field(..., description="Delete operation status")
    data: str = Field(..., description="Deleted room ID")
    message: Optional[str] = Field(None, description="Additional message")
