from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime, time, timedelta
from enum import Enum

from typing import Optional, List


class RoomStatus(str, Enum):
    """Room status enumeration"""
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CreateRoomModel(BaseModel):
    room_name: str = Field(..., min_length=3, description="Name of the room")
    room_topic: str = Field(..., min_length=5, description="Topic of discussion for the room")
    topic_category: str = Field(..., description="Category of the room topic")
    started_at: datetime = Field(..., description="Room start time in ISO format")    
    ended_at: datetime = Field(..., description="Room end time in ISO format")
    rounds_completed: int = Field(..., description="Number of rounds completed in the room")
    created_at: datetime = Field(..., description="Room creation time in ISO format")
    status: RoomStatus = Field(..., description="Current status of the room")
    cefr_level: int = Field(..., description="CEFR level of the room")

class RoomResponseModel(BaseModel):
    status: str = Field(..., description="Room creation status message")
    data: str = Field(..., description="Room ID of the created room")
    message: Optional[str] = Field(None, description="Additional message")

class RoomModel(BaseModel):
    """Complete Room/Room model matching the schema"""
    id: str = Field(..., description="Room UUID")
    room_name: Optional[str] = Field(None, description="Human-readable room name")
    
    # Room Configuration
    topic: str = Field(..., description="Discussion topic")
    topic_category: str = Field(..., description="Topic category (Technology, Current Events, etc.)")
    max_participants: int = Field(default=6, description="Maximum number of participants")
    speaking_time_per_turn: int = Field(default=60, description="Speaking time per turn in seconds")
    num_rounds: int = Field(default=3, description="Number of discussion rounds")
    
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
    facilitator_agent_id: Optional[str] = Field(None, description="AWS Strands agent instance ID")
    
    # Metadata
    created_at: datetime = Field(..., description="Room creation timestamp")
    created_by: str = Field(..., description="User ID who created the room")

