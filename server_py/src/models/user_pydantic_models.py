from pydantic import EmailStr, Field
from typing import Optional, List
from datetime import datetime

from .base_dict_model import BaseDictModel
from .enums import CEFRLevel

# --- Base Name Models ---

class BaseUserModel(BaseDictModel):
    """Base model with name field for any model type"""
    name: str = Field(..., min_length=1, description="Model name (e.g., Transcript, User, etc.)")

class UserResponseModel(BaseUserModel):
    """Generic response model with model data"""
    status: str = Field(..., description="Status message")
    data: BaseUserModel = Field(..., description="Model data with name")
    message: Optional[str] = Field(None, description="Additional message")

class UserIDResponseModel(BaseUserModel):
    """Generic response model with model ID"""
    status: str = Field(..., description="Status message")
    data: str = Field(..., description="Model ID")
    message: Optional[str] = Field(None, description="Additional message")

class LoginModel(BaseUserModel):
    email: EmailStr
    password: str

class LoginSignUpResponseModel(BaseUserModel):
    status: str = Field(..., description="Login/Signup status message")
    data: str = Field(..., description="User ID for user room")
    message: Optional[str] = Field(None, description="Additional message")
    
# --- Model for Creating a User (Sign Up) ---

class SignUpModel(BaseUserModel):
    # Authentication
    name: str = Field(..., min_length=2, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")

    # CEFR Progress Tracking
    current_cefr_level: CEFRLevel = Field(default=CEFRLevel.A0, description="Current CEFR level: A0...C2")

    # Topic Interests (For Future Lobby Matching)
    topic_categories: List[str] = Field(default_factory=list, description="Topic categories of interest")

# --- Model for Reading from DB ---

class UserModel(BaseUserModel):
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

    



# --- NEW: Update Models ---
class UpdateUserTopicCategoriesModel(BaseUserModel):
    """Model for updating a user's topic categories and CEFR level."""
    user_id: str = Field(..., description="User UUID, Primary Key")
    topic_categories: Optional[List[str]] = None


class UpdateUserCEFRModel(BaseUserModel):
    """Model for updating a user's CEFR level."""
    user_id: str = Field(..., description="User UUID, Primary Key")
    current_cefr_level: CEFRLevel = Field(..., description="The user's new CEFR level")

class UpdateUserLastActiveModel(BaseUserModel):
    """Model for updating a user's last active timestamp."""
    user_id: str = Field(..., description="User UUID, Primary Key")
    last_active: datetime = Field(..., description="Timestamp of last activity")

class UpdateUserPasswordModel(BaseUserModel):
    """Model for updating a user's password."""
    user_id: str = Field(..., description="User UUID, Primary Key")
    old_password: str = Field(..., description="The current password")
    new_password: str = Field(..., description="The new password")

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

# --- Get Models ---

class GetUserResponseModel(BaseDictModel):
    """Response model for getting a single user"""
    status: str = Field(..., description="Get operation status")
    data: UserModel = Field(..., description="User data")
    message: Optional[str] = Field(None, description="Additional message")
