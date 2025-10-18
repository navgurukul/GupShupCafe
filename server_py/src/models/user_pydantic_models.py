from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class LoginSignUpResponseModel(BaseModel):
    status: str = Field(..., description="Login/Signup status message")
    data: str = Field(..., description="User ID for user room")
    message: Optional[str] = Field(None, description="Additional message")
    
class SignUpModel(BaseModel):
    # user_id: str = Field(..., description="Unique identifier for the user")
    # Authentication
    name: str = Field(..., min_length=2, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")

    # CEFR Progress Tracking 
    current_cefr_level: str = Field(default="A0", description="Current CEFR level: A0, A1, A2, B1, B2, C1, C2")
    
    # Topic Interests (For Future Lobby Matching)
    topic_categories: list[str] = Field(default_factory=list, description="Topic categories of interest")
    
    # Metadata
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_active: Optional[datetime] = Field(None, description="Last activity timestamp")
