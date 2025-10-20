from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# --- Enums Referenced by the Models ---
from .enums import CEFRLevel, ParticipantRole
from .participant_pydantic_models import Participant

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
    topic_title: str = Field(..., description="Discussion topic")
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

    
# --- Domain Model for Room Management ---
class Room(BaseModel):
    """Domain model for room used in room management"""
    room_id: str = Field(..., description="Room identifier")
    room_name: str = Field(default="General", description="Room name")
    topic: Optional[dict] = Field(None, description="Discussion topic")
    max_participants: int = Field(default=6, description="Maximum participants")
    speaking_time: int = Field(default=60, description="Speaking time per turn")
    num_rounds: int = Field(default=3, description="Number of rounds")
    cefr_level: str = Field(default="A1", description="CEFR level")
    status: RoomStatus = Field(default=RoomStatus.WAITING, description="Room status")
    current_round: int = Field(default=0, description="Current round")
    current_speaker_index: int = Field(default=0, description="Current speaker index")
    participants: List[Participant] = Field(default_factory=list, description="List of participants")
    started_at: Optional[str] = Field(None, description="Start timestamp")
    ended_at: Optional[str] = Field(None, description="End timestamp")
    time_remaining: int = Field(default=60, description="Time remaining in current turn")
    created_by: str = Field(default="system", description="Creator user ID")
    metadata: Optional[dict] = Field(None, description="Additional room metadata")
    
    def add_participant(self, participant: Participant):
        """Add participant to room"""
        # Remove existing participant with same socket_id if exists
        self.participants = [p for p in self.participants if p.socket_id != participant.socket_id]
        # Add new participant
        self.participants.append(participant)
    
    def remove_participant(self, socket_id: str):
        """Remove participant by socket_id"""
        self.participants = [p for p in self.participants if p.socket_id != socket_id]
    
    def get_participant_by_socket(self, socket_id: str) -> Optional[Participant]:
        """Get participant by socket_id"""
        for p in self.participants:
            if p.socket_id == socket_id:
                return p
        return None
    
    def get_participant_by_id(self, user_id: str) -> Optional[Participant]:
        """Get participant by user_id"""
        for p in self.participants:
            if p.id == user_id:
                return p
        return None
    
    def get_current_speaker(self) -> Optional[Participant]:
        """Get current speaker based on speaker index"""
        speakers = [p for p in self.participants if p.role == ParticipantRole.PARTICIPANT]
        if speakers and 0 <= self.current_speaker_index < len(speakers):
            return speakers[self.current_speaker_index]
        return None
    
    def advance_turn(self) -> Optional[Participant]:
        """Advance to next speaker and return next speaker"""
        speakers = [p for p in self.participants if p.role == ParticipantRole.PARTICIPANT]
        if not speakers:
            return None
            
        self.current_speaker_index += 1
        
        # Check if round is complete
        if self.current_speaker_index >= len(speakers):
            self.current_speaker_index = 0
            self.current_round += 1
            
            # Check if discussion is complete
            if self.current_round > self.num_rounds:
                self.status = RoomStatus.COMPLETED
                return None
        
        return self.get_current_speaker()
    
    def update_participant(self, user_id: str, updates: dict):
        """Update participant data"""
        for p in self.participants:
            if p.id == user_id:
                for key, value in updates.items():
                    if hasattr(p, key):
                        setattr(p, key, value)
                break

    class Config:
        from_attributes = True