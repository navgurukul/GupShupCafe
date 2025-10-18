from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CreateParticipantModel(BaseModel):
    user_id: str = Field(..., description="User ID of the participant")
    room_id: str = Field(..., description="Room ID the participant is joining")
    anonymous_name: str = Field(..., min_length=2, description="Anonymous name for the participant")
    campus: Optional[str] = Field(None, description="Campus of the participant")
    location: Optional[str] = Field(None, description="Location of the participant")
    joined_at: datetime = Field(..., description="Timestamp when participant joined")
    
class ParticipantResponseModel(BaseModel):
    status: str = Field(..., description="Participant creation status message")
    data: str = Field(..., description="Participant user ID")
    message: Optional[str] = Field(None, description="Additional message")


class JoinRoomAsParticipantModel(BaseModel):
    room_id: str = Field(..., description="ID of the room to join")
    participant_number: int = Field(..., description="Participant number for joining the room")
    anonymous_name: str = Field(..., min_length=2, description="Anonymous name for the participant")
    campus: Optional[str] = Field(None, description="Campus of the participant")
    location: Optional[str] = Field(None, description="Location of the participant")

class ParticipantModel(BaseModel):
    """Complete Participant model matching the schema"""
    id: str = Field(..., description="Participant UUID")
    session_id: str = Field(..., description="Session ID (foreign key)")
    user_id: str = Field(..., description="User ID (foreign key)")
    
    # Identity
    anonymous_name: str = Field(..., description="Anonymous name like 'Blue Panda', 'Red Dragon'")
    avatar_color: Optional[str] = Field(None, description="Hex color code for avatar")
    
    # Session Role
    role: str = Field(default="participant", description="Role: participant, host, listener")
    is_ready: bool = Field(default=False, description="Ready to start discussion")
    
    # Real-Time State
    is_speaking: bool = Field(default=False, description="Currently speaking")
    is_muted: bool = Field(default=False, description="Microphone muted")
    socket_id: Optional[str] = Field(None, description="Socket.io connection ID")
    
    # CEFR Level at Session Start (for progress tracking)
    starting_cefr_level: str = Field(..., description="CEFR level at session start")
    ending_cefr_level: Optional[str] = Field(None, description="CEFR level at session end")
    
    # Connection
    joined_at: datetime = Field(..., description="Timestamp when participant joined")
    left_at: Optional[datetime] = Field(None, description="Timestamp when participant left")
    
    # Optional fields (campus, location from existing models)
    campus: Optional[str] = Field(None, description="Campus of the participant")
    location: Optional[str] = Field(None, description="Location of the participant")
