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
    campus: Optional[str] = Field(None, description="Campus of the participant")
    location: Optional[str] = Field(None, description="Location of the participant")



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

# --- Comprehensive Update Model for Participant ---
class ParticipantUpdateModel(BaseModel):
    """Model for updating participant fields."""
    left_at: Optional[datetime] = Field(None, description="Timestamp when participant left")
    speaking_time_seconds: Optional[int] = Field(None, description="Total speaking time in seconds")
    ending_cefr_level: Optional[str] = Field(None, description="CEFR level at room end")
    is_muted: Optional[bool] = Field(None, description="Is the participant muted?")
    is_speaking: Optional[bool] = Field(None, description="Is the participant speaking?")
    is_ready: Optional[bool] = Field(None, description="Is the participant ready?")


# --- Domain Model for Room Management ---
class Participant(BaseModel):
    """Domain model for participant used in room management"""
    id: str = Field(..., description="User ID")
    socket_id: str = Field(..., description="Socket.io connection ID")
    anonymous_name: str = Field(..., description="Anonymous display name")
    name: Optional[str] = Field(None, description="Real name")
    campus: Optional[str] = Field(None, description="Campus")
    location: Optional[str] = Field(None, description="Location")
    role: str = Field(default="listener", description="Role: speaker, listener, host")
    is_ready: bool = Field(default=False, description="Ready to start discussion")
    joined_at: str = Field(..., description="ISO timestamp when joined")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "socketId": self.socket_id,
            "anonymousName": self.anonymous_name,
            "name": self.name,
            "campus": self.campus,
            "location": self.location,
            "role": self.role,
            "isReady": self.is_ready,
            "joinedAt": self.joined_at
        }
    
    def update_ready_status(self, is_ready: bool):
        """Update ready status"""
        self.is_ready = is_ready
    
    def change_role(self, new_role: str):
        """Change participant role"""
        self.role = new_role

    class Config:
        from_attributes = True