from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


from .base_dict_model import BaseDictModel
from .enums import ParticipantRole


class CreateParticipantModel(BaseDictModel):
    """Complete Participant model matching the schema"""
    room_id: str = Field(..., description="Room ID (foreign key)")
    user_id: str = Field(..., description="User ID (foreign key)")

    # Identity
    anonymous_name: str = Field(..., description="Anonymous name like 'Blue Panda', 'Red Dragon'")
    avatar_color: Optional[str] = Field(
        None, description="Hex color code for avatar")

    # Room Config
    role: ParticipantRole = Field(default=ParticipantRole.PARTICIPANT, description="Role: speaker, host, listener")
    is_ready: bool = Field(default=False, description="Ready to start discussion")
    turn_order: int = Field(default=0, description="Order in speaking turns")

    # Real-Time State
    is_speaking: bool = Field(default=False, description="Currently speaking")
    is_muted: bool = Field(default=False, description="Microphone muted")
    socket_id: Optional[str] = Field(
        None, description="Socket.io connection ID")

    # CEFR Level at Room Start (for progress tracking)
    starting_cefr_level: str = Field(...,
                                     description="CEFR level at room start")
    ending_cefr_level: Optional[str] = Field(
        None, description="CEFR level at room end")

    # Connection
    joined_at: datetime = Field(...,
                                description="Timestamp when participant joined")
    left_at: Optional[datetime] = Field(
        None, description="Timestamp when participant left")

    # Optional fields (campus, location from existing models)
    campusOrLocation: Optional[str] = Field(
        None, description="Campus or location of the participant")

    # Optional field for tracking total speaking time
    speaking_time_seconds: int = Field(
        default=0, description="Total speaking time in seconds")


# --- Get Model for retrieving participants ---

class GetParticipantModel(BaseDictModel):
    """Model for getting participant with optional filters"""
    participant_id: str = Field(...,
                                description="Participant UUID, Primary Key")

    # All other fields from CreateParticipantModel as optional
    room_id: Optional[str] = Field(None, description="Room ID (foreign key)")
    user_id: Optional[str] = Field(None, description="User ID (foreign key)")
    anonymous_name: Optional[str] = Field(
        None, description="Anonymous name like 'Blue Panda', 'Red Dragon'")
    avatar_color: Optional[str] = Field(
        None, description="Hex color code for avatar")
    role: Optional[str] = Field(
        None, description="Role: participant, host, listener")
    is_ready: Optional[bool] = Field(
        None, description="Ready to start discussion")
    turn_order: Optional[int] = Field(
        None, description="Order in speaking turns")
    is_speaking: Optional[bool] = Field(None, description="Currently speaking")
    is_muted: Optional[bool] = Field(None, description="Microphone muted")
    socket_id: Optional[str] = Field(
        None, description="Socket.io connection ID")
    starting_cefr_level: Optional[str] = Field(
        None, description="CEFR level at room start")
    ending_cefr_level: Optional[str] = Field(
        None, description="CEFR level at room end")
    joined_at: Optional[datetime] = Field(
        None, description="Timestamp when participant joined")
    left_at: Optional[datetime] = Field(
        None, description="Timestamp when participant left")
    campusOrLocation: Optional[str] = Field(
        None, description="Campus or location of the participant")
    speaking_time_seconds: Optional[int] = Field(
        None, description="Total speaking time in seconds")
    created_at: Optional[datetime] = Field(
        None, description="Timestamp when participant was created")


# --- Model for data read from DB (includes PK and creation time) ---


class ParticipantModel(CreateParticipantModel):
    """Full participant model as represented in the database."""
    participant_id: str = Field(...,
                                description="Participant UUID, Primary Key")
    created_at: datetime = Field(...,
                                 description="Timestamp when participant was created")

    class Config:
        from_attributes = True


class CreateParticipantResponseModel(BaseDictModel):
    status: str = Field(..., description="Participant creation status message")
    data: str = Field(..., description="Participant ID")
    message: Optional[str] = Field(None, description="Additional message")


# --- List Models ---

class ListParticipantsResponseModel(BaseDictModel):
    """Response model for listing participants"""
    status: str = Field(..., description="List operation status")
    data: List[ParticipantModel] = Field(...,
                                         description="List of participants")
    message: Optional[str] = Field(None, description="Additional message")

# --- Update Models ---


class UpdateParticipantModel(BaseDictModel):
    """Model for updating participant details."""
    anonymous_name: Optional[str] = Field(
        None, description="Updated anonymous name")
    avatar_color: Optional[str] = Field(
        None, description="Updated avatar color")
    role: Optional[str] = Field(None, description="Updated role")
    is_ready: Optional[bool] = Field(None, description="Updated ready status")
    turn_order: Optional[int] = Field(None, description="Updated turn order")
    is_speaking: Optional[bool] = Field(
        None, description="Updated speaking status")
    is_muted: Optional[bool] = Field(None, description="Updated muted status")
    socket_id: Optional[str] = Field(None, description="Updated socket ID")
    ending_cefr_level: Optional[str] = Field(
        None, description="Updated CEFR level at room end")
    left_at: Optional[datetime] = Field(
        None, description="Updated left at timestamp")
    speaking_time_seconds: Optional[int] = Field(
        None, description="Updated total speaking time in seconds")
    campusOrLocation: Optional[str] = Field(
        None, description="Updated campus or location")


class UpdateParticipantResponseModel(BaseDictModel):
    """Response model for updating participant"""
    status: str = Field(..., description="Update operation status")
    data: UpdateParticipantModel = Field(...,
                                         description="Updated participant data")
    message: Optional[str] = Field(None, description="Additional message")

# --- Delete Models ---


class DeleteParticipantResponseModel(BaseDictModel):
    """Response model for deleting participant"""
    status: str = Field(..., description="Delete operation status")
    data: str = Field(..., description="Deleted participant ID")
    message: Optional[str] = Field(None, description="Additional message")

# --- Real-time State Models ---

class ParticipantLeftModel(BaseDictModel):
    """Model for participant leaving a room"""
    participant_id: str = Field(..., description="Participant ID")
    room_id: str = Field(..., description="Room ID")
    left_at: datetime = Field(..., description="Timestamp when participant left")

class ParticipantIsMutedModel(BaseDictModel):
    """Model for participant mute status"""
    participant_id: str = Field(..., description="Participant ID")
    room_id: str = Field(..., description="Room ID")
    is_muted: bool = Field(..., description="Mute status")

class ParticipantIsSpeakingModel(BaseDictModel):
    """Model for participant speaking status"""
    participant_id: str = Field(..., description="Participant ID")
    room_id: str = Field(..., description="Room ID")
    is_speaking: bool = Field(..., description="Speaking status")

class ParticipantIsReadyModel(BaseDictModel):
    """Model for participant ready status"""
    participant_id: str = Field(..., description="Participant ID")
    room_id: str = Field(..., description="Room ID")
    is_ready: bool = Field(..., description="Ready status")