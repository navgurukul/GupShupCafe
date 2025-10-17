from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class CreateRoomModel(BaseModel):
    room_id: str = Field(..., description="Unique identifier for the room")
    room_name: str = Field(..., min_length=3, description="Name of the room")
    room_topic: str = Field(..., min_length=5, description="Topic of discussion for the room")
   
class RoomResponseModel(BaseModel):
    status: str = Field(..., description="Room creation status message")
    data: str = Field(..., description="Room ID of the created room")
    message: Optional[str] = Field(None, description="Additional message")