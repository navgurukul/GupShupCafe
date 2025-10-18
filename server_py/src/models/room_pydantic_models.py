from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


# --- Enums Referenced by the Models ---
from .enums import CEFRLevel

class RoomStatus(str, Enum):
    """Room status enumeration"""
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# --- Model for Creating a Room ---

class CreateRoomModel(BaseModel):
    """Complete Room model matching the schema"""
    room_name: Optional[str] = Field(None, description="Human-readable room name")
    
    # Room Configuration
    topic: str = Field(..., description="Discussion topic")
    topic_category: str = Field(..., description="Topic category (Technology, Current Events, etc.)")
    max_participants: int = Field(default=6, description="Maximum number of participants")
    speaking_time_per_turn: int = Field(default=60, description="Speaking time per turn in seconds")
    num_rounds: int = Field(default=3, description="Number of discussion rounds")
    cefr_level: CEFRLevel = Field(..., description="CEFR level for the room")

    # Room State
    status: RoomStatus = Field(..., description="Room status")
    current_round: int = Field(default=0, description="Current round number")
    current_speaker_index: int = Field(default=0, description="Current speaker index")
    
    # Participants
    participant_count: int = Field(default=0, description="Number of participants")
    
    # Timing
    started_at: Optional[datetime] = Field(None, description="Room start time")
    ended_at: Optional[datetime] = Field(None, description="Room end time")
    duration_seconds: int = Field(default=0, description="Room duration in seconds")
    
    # Facilitator Agent
    agent_id: Optional[str] = Field(None, description="AWS Strands agent instance ID")
    
    # Metadata
    created_by: str = Field(..., description="User ID who created the room")

# --- Model for Reading from DB ---

class RoomModel(CreateRoomModel):
    """Full Room model as represented in the database, including PK."""
    room_id: str = Field(..., description="Room UUID, Primary Key")
    created_at: datetime = Field(..., description="Timestamp when room was created")

    class Config:
        from_attributes = True

# --- NEW: Update Models ---

class UpdateRoomStatusModel(BaseModel):
    """Model for updating the room's status."""
    room_id: str = Field(..., description="Room UUID")
    status: RoomStatus = Field(..., description="New room status")
    started_at: Optional[datetime] = Field(None, description="Timestamp when room started (if applicable)")
    
class UpdateRoomStateModel(BaseModel):
    """Model for updating the room's live discussion state."""
    current_round: Optional[int] = Field(None, description="Current round number")
    current_speaker_index: Optional[int] = Field(None, description="Current speaker index")
    participant_count: Optional[int] = Field(None, description="Current number of participants")

class UpdateRoomEndModel(BaseModel):
    """Model for marking a room as finished."""
    status: RoomStatus = Field(..., description="Set to 'finished' or 'cancelled'")
    ended_at: datetime = Field(..., description="Timestamp when room ended")
    duration_seconds: int = Field(..., description="Total room duration in seconds")

class RoomResponseModel(BaseModel):
    status: str = Field(..., description="Room creation status message")
    data: str = Field(..., description="Room ID of the created room")
    message: Optional[str] = Field(None, description="Additional message")

    
