"""
API Routes
RESTful endpoints for the application
"""
from fastapi import APIRouter
from ..models.room_pydantic_models import CreateRoomModel, RoomResponseModel
router = APIRouter()

@router.post("/rooms", description="Create a new room", response_model=RoomResponseModel)
async def create_room(room: CreateRoomModel):
    """Create a new room endpoint"""
    pass