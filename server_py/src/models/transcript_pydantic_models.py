from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional
import uuid

# --- Model for creating a new transcript ---

class CreateTranscriptModel(BaseModel):
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


class CreateTranscriptModelResponse(BaseModel):
    status: str = Field(..., description="Transcript creation status message")
    data: str = Field(..., description="Transcript ID of the created transcript")
    message: Optional[str] = Field(None, description="Additional message")

# --- Model for data read from DB (includes PK and creation time) ---

class TranscriptModel(CreateTranscriptModel):
    """Full transcript model as represented in the database."""
    transcript_id: str = Field(..., description="Transcript UUID, Primary Key")
    created_at: datetime = Field(..., description="Timestamp when record was created")
    
    class Config:
        from_attributes = True

# --- NEW: Update Models ---

class UpdateTranscriptProcessingModel(BaseModel):
    """Model for updating the processing status of a transcript."""
    transcript_id: str = Field(..., description="Transcript ID")
    is_processed: bool = Field(..., description="Set to True when feedback is generated")
    processed_at: datetime = Field(..., description="Timestamp of feedback creation")

class UpdateTranscriptAudioURLModel(BaseModel):
		"""Model for updating the audio file URL after async upload."""
		transcript_id: str = Field(..., description="Transcript ID")
		audio_file_url: str = Field(..., description="URL to the raw audio file")


class TranscriptIsProcessedModel(BaseModel):
		transcript_id: str = Field(..., description="Transcript ID")
		is_processed: bool = Field(..., description="Has the transcript been processed?")



class TranscriptOut(BaseModel):
    transcript_id: str
    room_id: str
    participant_id: str
    user_id: Optional[str] = None
    text: str
    created_at: datetime
    audio_file_url: Optional[str] = None