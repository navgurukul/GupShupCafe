from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime, time, timedelta

from typing import Optional

class CreateSessionModel(BaseModel):
    room_name: str = Field(..., min_length=3, description="Name of the session")
    room_topic: str = Field(..., min_length=5, description="Topic of discussion for the session")
    topic_category: str = Field(..., description="Category of the session topic")
    started_at: datetime = Field(..., description="Session start time in ISO format")    
    ended_at: datetime = Field(..., description="Session end time in ISO format")
    rounds_completed: int = Field(..., description="Number of rounds completed in the session")
    created_at: datetime = Field(..., description="Session creation time in ISO format")
    # status: str = Field(..., description="Current status of the session")
    crf_level: int = Field(..., description="CRF level of the session")

class SessionResponseModel(BaseModel):
    status: str = Field(..., description="Session creation status message")
    data: str = Field(..., description="Session ID of the created session")
    message: Optional[str] = Field(None, description="Additional message")