from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class CreateParticipantModel(BaseModel):
    user_id: str = Field(..., description="User ID of the participant")
    session_id: str = Field(..., description="Session ID the participant is joining")
    anonymous_name: str = Field(..., min_length=2, description="Anonymous name for the participant")
    campus: Optional[str] = Field(None, description="Campus of the participant")
    location: Optional[str] = Field(None, description="Location of the participant")
    joined_at: datetime = Field(..., description="Timestamp when participant joined")
    
class ParticipantResponseModel(BaseModel):
    status: str = Field(..., description="Participant creation status message")
    data: str = Field(..., description="Participant user ID")
    message: Optional[str] = Field(None, description="Additional message")
