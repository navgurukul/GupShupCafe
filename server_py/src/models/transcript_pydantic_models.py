from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CreateTranscriptModel(BaseModel):
    """Transcript record for a participant's speech in a room (MVP fields)."""
    room_id: str = Field(..., description="Room ID")
    participant_id: str = Field(..., description="Participant ID")
    user_id: Optional[str] = Field(None, description="User ID")
    text: str = Field(..., min_length=1, description="Transcript text")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when transcript was created")
    audio_file_url: Optional[str] = Field(None, description="URL to the raw audio file")

class CreateTranscriptModelResponse(BaseModel):
    status: str = Field(..., description="Transcript creation status message")
    data: str = Field(..., description="Transcript ID of the created transcript")
    message: Optional[str] = Field(None, description="Additional message")


class TranscriptOut(BaseModel):
    transcript_id: str
    room_id: str
    participant_id: str
    user_id: Optional[str] = None
    text: str
    created_at: datetime
    audio_file_url: Optional[str] = None
    
