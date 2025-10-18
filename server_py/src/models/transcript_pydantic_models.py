from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CreateTranscriptModel(BaseModel):
    """Transcript record for a participant's speech in a room."""
    id: str = Field(..., description="Transcript UUID")
    room_id: str = Field(..., description="Room ID")
    participant_id: str = Field(..., description="Participant ID")
    user_id: str = Field(..., description="User ID")
    text: str = Field(..., min_length=1, description="Transcript text")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when transcript was created")

    # Context
    round_number: int = Field(..., description="Round number out of the total number of rounds for a room")
    turn_order: int = Field(..., description="Turn order of the participant within the round")

    # Content
    transcript_text: str = Field(..., description="Transcribed speech")
    language: str = Field(..., description="Language code (e.g., 'en')")
    stt_confidence: float = Field(..., description="Speech-to-text confidence (0.0-1.0)")

    # Timing
    started_at: datetime = Field(..., description="Timestamp when transcription started")
    ended_at: datetime = Field(..., description="Timestamp when transcription ended")
    duration_seconds: int = Field(..., description="Duration of the transcription in seconds")

    # Audio Metadata
    word_count: int = Field(..., description="Number of words in the transcription")
    speech_rate: float = Field(..., description="Speech rate in words per minute")

    # Processing Status
    is_processed: bool = Field(..., description="Has feedback been generated?")
    processed_at: Optional[datetime] = Field(..., description="Feedback's created_at time stored here")

    # Raw Audio Reference (optional, for future features)
    audio_file_url: Optional[str] = Field(None, description="URL to the raw audio file")

class CreateTranscriptModelResponse(BaseModel):
	 status: str = Field(..., description="Transcript creation status message")
	 data: str = Field(..., description="Transcript ID of the created transcript")
	 message: Optional[str] = Field(None, description="Additional message")
    
