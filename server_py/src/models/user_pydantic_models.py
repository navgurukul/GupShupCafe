from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class LoginResponseModel(BaseModel):
    status: str = Field(..., description="Login status message")
    data: str = Field(..., description="User ID for user session")
    message: Optional[str] = Field(None, description="Additional message")
    
class SignUpModel(BaseModel):
    # user_id: str = Field(..., description="Unique identifier for the user")
    name: str = Field(..., min_length=2, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")
    category: list[str] = Field(..., description="Categories of interest for the user")
    # crf_level: Optional[int] = Field(default=0, description="CRF level for the user")

class CreateRoomModel(BaseModel):
    room_id: str = Field(..., description="Unique identifier for the room")
    room_name: str = Field(..., min_length=3, description="Name of the room")
    room_topic: str = Field(..., min_length=5, description="Topic of discussion for the room")
    participants: int = Field(..., ge=2, le=6, description="Number of participants expected in the room (2-6)")

class JoinRoomModel(BaseModel):
    room_id: str = Field(..., description="ID of the room to join")
    participant_number: int = Field(..., description="Participant number for joining the room")