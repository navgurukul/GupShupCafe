from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CreateParticipantModel(BaseModel):
    """Complete Participant model matching the schema"""
    room_id: str = Field(..., description="Room ID (foreign key)")
    user_id: str = Field(..., description="User ID (foreign key)")
    
    # Identity
    anonymous_name: str = Field(..., description="Anonymous name like 'Blue Panda', 'Red Dragon'")
    avatar_color: Optional[str] = Field(None, description="Hex color code for avatar")
    
    # Room Config
    role: str = Field(default="participant", description="Role: participant, host, listener")
    is_ready: bool = Field(default=False, description="Ready to start discussion")
    turn_order: int = Field(default=0, description="Order in speaking turns")
    
    # Real-Time State
    is_speaking: bool = Field(default=False, description="Currently speaking")
    is_muted: bool = Field(default=False, description="Microphone muted")
    socket_id: Optional[str] = Field(None, description="Socket.io connection ID")
    
    # CEFR Level at Room Start (for progress tracking)
    starting_cefr_level: str = Field(..., description="CEFR level at room start")
    ending_cefr_level: Optional[str] = Field(None, description="CEFR level at room end")
    
    # Connection
    joined_at: datetime = Field(..., description="Timestamp when participant joined")
    left_at: Optional[datetime] = Field(None, description="Timestamp when participant left")

    # Optional fields (campus, location from existing models)
    campusOrLocation: Optional[str] = Field(None, description="Campus or location of the participant")
    
    # Optional field for tracking total speaking time
    speaking_time_seconds: int = Field(default=0, description="Total speaking time in seconds")

    
class CreateParticipantResponseModel(BaseModel):
    status: str = Field(..., description="Participant creation status message")
    data: str = Field(..., description="Participant user ID")
    message: Optional[str] = Field(None, description="Additional message")

# --- Model for data read from DB (includes PK and creation time) ---
class ParticipantModel(CreateParticipantModel):
    """Full participant model as represented in the database."""
    participant_id: str = Field(..., description="Participant UUID, Primary Key")
    created_at: datetime = Field(..., description="Timestamp when participant was created")

    class Config:
        from_attributes = True

# --- Model for Updating Participant Info ---
class JoinRoomAsParticipantModel(BaseModel):
    room_id: str = Field(..., description="ID of the room to join")
    participant_number: int = Field(..., description="Participant number for joining the room")
    anonymous_name: str = Field(..., min_length=2, description="Anonymous name for the participant")
    campusOrLocation: Optional[str] = Field(None, description="Campus or Location of the participant")



class ParticipantLeftModel(BaseModel):
    participant_id: str = Field(..., description="Participant UUID")
    left_at: Optional[datetime] = Field(None, description="Timestamp when participant left")
    ending_cefr_level: Optional[str] = Field(None, description="CEFR level at room end")

class ParticipantIsMutedModel(BaseModel):
    participant_id: str = Field(..., description="Participant UUID")
    is_muted: Optional[bool] = Field(None, description="Is the participant muted?")

class ParticipantIsSpeakingModel(BaseModel):
    participant_id: str = Field(..., description="Participant UUID")
    is_speaking: Optional[bool] = Field(None, description="Is the participant speaking?")

class ParticipantIsReadyModel(BaseModel):
    participant_id: str = Field(..., description="Participant UUID")
    is_ready: Optional[bool] = Field(None, description="Is the participant ready?")

class UpdateParticipantModel(BaseModel):
    """Model for updating participant details."""
    participant_id: str = Field(..., description="Participant UUID")
    anonymous_name: Optional[str] = Field(None, description="Updated anonymous name")
    avatar_color: Optional[str] = Field(None, description="Updated avatar color")
    role: Optional[str] = Field(None, description="Updated role")
    is_ready: Optional[bool] = Field(None, description="Updated ready status")
    turn_order: Optional[int] = Field(None, description="Updated turn order")
    is_speaking: Optional[bool] = Field(None, description="Updated speaking status")
    is_muted: Optional[bool] = Field(None, description="Updated muted status")
    socket_id: Optional[str] = Field(None, description="Updated socket ID")
    ending_cefr_level: Optional[str] = Field(None, description="Updated CEFR level at room end")
    left_at: Optional[datetime] = Field(None, description="Updated left at timestamp"),
    speaking_time_seconds: Optional[int] = Field(None, description="Updated total speaking time in seconds")