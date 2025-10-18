from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

from .enums import CEFRLevel

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class LoginSignUpResponseModel(BaseModel):
    status: str = Field(..., description="Login/Signup status message")
    data: str = Field(..., description="User ID for user room")
    message: Optional[str] = Field(None, description="Additional message")
    
# --- Model for Creating a User (Sign Up) ---

class SignUpModel(BaseModel):
    # Authentication
    name: str = Field(..., min_length=2, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    hashed_password: str = Field(..., min_length=6, description="User's hashed password")

    # CEFR Progress Tracking
    current_cefr_level: CEFRLevel = Field(default=CEFRLevel.A0, description="Current CEFR level: A0...C2")

    # Topic Interests (For Future Lobby Matching)
    topic_categories: List[str] = Field(default_factory=list, description="Topic categories of interest")

# --- Model for Reading from DB ---

class UserModel(SignUpModel):
    """Full User model as represented in the database."""
    user_id: str = Field(..., description="User UUID, Primary Key")
    created_at: datetime = Field(..., description="Account creation timestamp")

    class Config:
        from_attributes = True



# --- NEW: Update Models ---
class UserTopicCategoriesModel(BaseModel):
    """Model for updating a user's topic categories and CEFR level."""
    user_id: str = Field(..., description="User UUID, Primary Key")
    topic_categories: Optional[List[str]] = None


class UpdateUserCEFRModel(BaseModel):
    """Model for updating a user's CEFR level."""
    user_id: str = Field(..., description="User UUID, Primary Key")
    current_cefr_level: CEFRLevel = Field(..., description="The user's new CEFR level")

class UpdateUserLastActiveModel(BaseModel):
    """Model for updating a user's last active timestamp."""
    user_id: str = Field(..., description="User UUID, Primary Key")
    last_active: datetime = Field(..., description="Timestamp of last activity")

class UpdateUserPasswordModel(BaseModel):
    """Model for updating a user's password."""
    user_id: str = Field(..., description="User UUID, Primary Key")
    hashed_password: str = Field(..., description="The new hashed password")