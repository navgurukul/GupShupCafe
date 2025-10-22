from pydantic import EmailStr, Field
from typing import Optional, List
from datetime import datetime

from .base_dict_model import BaseDictModel
from .enums import CEFRLevel

class LoginModel(BaseDictModel):
    email: EmailStr
    password: str


# --- Model for Creating a User (Sign Up) ---

class SignUpModel(BaseDictModel):
    # Authentication
    name: str = Field(..., min_length=2, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")

    # CEFR Progress Tracking
    current_cefr_level: CEFRLevel = Field(default=CEFRLevel.A0, description="Current CEFR level: A0...C2")

    # Topic Interests (For Future Lobby Matching)
    topic_categories: List[str] = Field(default_factory=list, description="Topic categories of interest")

# --- Model for Reading from DB ---

class UserModel(BaseDictModel):
    """Full User model as represented in the database."""
    user_id: str = Field(..., description="User UUID, Primary Key")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_active: Optional[datetime] = Field(None, description="Last active timestamp")

    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=2, description="User's full name")
    # CEFR Progress Tracking
    current_cefr_level: CEFRLevel = Field(..., description="Current CEFR level: A0...C2")

    # Topic Interests (For Future Lobby Matching)
    topic_categories: List[str] = Field(..., description="Topic categories of interest")

    
class LoginSignUpResponseModel(BaseDictModel):
    status: str = Field(..., description="Login/Signup status message")
    data: UserModel = Field(..., description="User for user room")
    message: Optional[str] = Field(None, description="Additional message")
    

# --- List Models ---

class ListUsersResponseModel(BaseDictModel):
    """Response model for listing users"""
    status: str = Field(..., description="List operation status")
    data: List[UserModel] = Field(..., description="List of users")
    message: Optional[str] = Field(None, description="Additional message")

# --- Update Models ---

class UpdateUserModel(BaseDictModel):
    """Model for updating user details."""
    name: Optional[str] = Field(None, description="Updated user name")
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    current_cefr_level: Optional[CEFRLevel] = Field(None, description="Updated CEFR level")
    topic_categories: Optional[List[str]] = Field(None, description="Updated topic categories")
    last_active: Optional[datetime] = Field(None, description="Updated last active timestamp")

class UpdateUserResponseModel(BaseDictModel):
    """Response model for updating user"""
    status: str = Field(..., description="Update operation status")
    data: UpdateUserModel = Field(..., description="Updated user data")
    message: Optional[str] = Field(None, description="Additional message")

# --- Delete Models ---

class DeleteUserResponseModel(BaseDictModel):
    """Response model for deleting user"""
    status: str = Field(..., description="Delete operation status")
    data: str = Field(..., description="Deleted user ID")
    message: Optional[str] = Field(None, description="Additional message")

