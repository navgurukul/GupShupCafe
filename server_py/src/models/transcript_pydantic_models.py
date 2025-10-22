from pydantic import Field, UUID4
from datetime import datetime
from typing import Optional, List
import uuid

from .base_dict_model import BaseDictModel



# --- Model for creating a new transcript ---

class CreateTranscriptModel(BaseDictModel):
    """
    Pydantic model for creating a new transcript record.
    Combines and cleans the provided fields.
    """
    room_id: str = Field(..., description="Room ID (foreign key)")
    participant_id: str = Field(..., description="Participant ID (foreign key)")
    user_id: Optional[str] = Field(None, description="User ID (foreign key)")
    
    # Context
    round_number: int = Field(..., description="Round number for the room")
    turn_order: int = Field(..., description="Turn order of the participant")

    # Content
    transcript_text: str = Field(..., min_length=1, description="Transcribed speech text")
    language: str = Field(default="en", description="Language code (e.g., 'en')")
    stt_confidence: float = Field(default=0.0, description="STT confidence (0.0-1.0)")
    
    # Timing
    started_at: datetime = Field(..., description="Timestamp when speech started")
    ended_at: datetime = Field(..., description="Timestamp when speech ended")
    duration_seconds: int = Field(..., description="Duration of speech in seconds")

    # Audio Metadata
    word_count: int = Field(..., description="Word count of the transcript")
    speech_rate: float = Field(..., description="Speech rate in words per minute")
    
    # Processing Status (set at creation)
    is_processed: bool = Field(default=False, description="Has feedback been generated?")
    processed_at: Optional[datetime] = Field(None, description="Feedback's created_at time")

    # Raw Audio Reference
    audio_file_url: Optional[str] = Field(None, description="URL to the raw audio file")

# --- Model for data read from DB (includes PK and creation time) ---

class TranscriptModel(CreateTranscriptModel):
    """Full transcript model as represented in the database."""
    transcript_id: str = Field(..., description="Transcript UUID, Primary Key")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    
    class Config:
        from_attributes = True

class CreateTranscriptModelResponse(BaseDictModel):
    status: str = Field(..., description="Transcript creation status message")
    data: TranscriptModel = Field(..., description="Transcript ID of the created transcript")
    message: Optional[str] = Field(None, description="Additional message")


# --- List Models ---

class ListTranscriptsResponseModel(BaseDictModel):
    """Response model for listing transcripts"""
    status: str = Field(..., description="List operation status")
    data: List[TranscriptModel] = Field(..., description="List of transcripts")
    message: Optional[str] = Field(None, description="Additional message")

# --- Update Models ---

class UpdateTranscriptModel(BaseDictModel):
    """Model for updating transcript details."""
    transcript_text: Optional[str] = Field(None, description="Updated transcript text")
    language: Optional[str] = Field(None, description="Updated language code")
    stt_confidence: Optional[float] = Field(None, description="Updated STT confidence")
    started_at: Optional[datetime] = Field(None, description="Updated start timestamp")
    ended_at: Optional[datetime] = Field(None, description="Updated end timestamp")
    duration_seconds: Optional[int] = Field(None, description="Updated duration")
    word_count: Optional[int] = Field(None, description="Updated word count")
    speech_rate: Optional[float] = Field(None, description="Updated speech rate")
    is_processed: Optional[bool] = Field(None, description="Updated processing status")
    processed_at: Optional[datetime] = Field(None, description="Updated processed timestamp")
    audio_file_url: Optional[str] = Field(None, description="Updated audio file URL")

class UpdateTranscriptResponseModel(BaseDictModel):
    """Response model for updating transcript"""
    status: str = Field(..., description="Update operation status")
    data: UpdateTranscriptModel = Field(..., description="Updated transcript data")
    message: Optional[str] = Field(None, description="Additional message")

# --- Delete Models ---

class DeleteTranscriptResponseModel(BaseDictModel):
    """Response model for deleting transcript"""
    status: str = Field(..., description="Delete operation status")
    data: str = Field(..., description="Deleted transcript ID")
    message: Optional[str] = Field(None, description="Additional message")

# --- Processing Models ---

class UpdateTranscriptProcessingModel(BaseDictModel):
    """Model for updating transcript processing status"""
    transcript_id: str = Field(..., description="Transcript ID")
    is_processed: bool = Field(..., description="Processing status")
    processed_at: Optional[datetime] = Field(None, description="Processing timestamp")

class UpdateTranscriptAudioURLModel(BaseDictModel):
    """Model for updating transcript audio URL"""
    transcript_id: str = Field(..., description="Transcript ID")
    audio_file_url: str = Field(..., description="Audio file URL")

