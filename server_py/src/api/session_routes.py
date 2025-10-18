"""
API Routes
RESTful endpoints for the application
"""
from fastapi import APIRouter
from ..models.room_pydantic_models import CreateRoomModel, RoomResponseModel
from ..services.room_service import Room_service
router = APIRouter()
service = Room_service()

@router.post("/room", description="Create a new room", response_model=RoomResponseModel)
async def create_room(room: CreateRoomModel):
    """Create a new room endpoint"""
    response = service.create_room(room)
    return response