"""
API Routes
RESTful endpoints for the application
"""
from fastapi import APIRouter, HTTPException
from ..models.room_pydantic_models import (
    CreateRoomModel, RoomResponseModel, UpdateRoomStatusModel,
    UpdateRoomStateModel, UpdateRoomEndModel
)
from ..services.room_service import Room_service
router = APIRouter()
service = Room_service()

@router.post("/", description="Create a new room", response_model=RoomResponseModel)
async def create_room(room: CreateRoomModel):
    """Create a new room endpoint"""
    response = service.create_room(room)
    return response

@router.get("/{room_id}", description="Get room by ID")
async def get_room(room_id: str):
    resp = service.get_room(room_id)
    if resp["status"] == "failure":
        raise HTTPException(status_code=404, detail=resp["message"])
    return resp

@router.get("/", description="List rooms")
async def list_rooms():
    return service.list_rooms()

@router.patch("/{room_id}", description="Update room")
async def update_room(room_id: str, payload: dict):
    resp = service.update_room(room_id, payload)
    if resp["status"] == "failure":
        raise HTTPException(status_code=400, detail=resp["message"])
    return resp

@router.delete("/{room_id}", description="Delete room")
async def delete_room(room_id: str):
    return service.delete_room(room_id)

@router.patch("/{room_id}/status", description="Update room status")
async def update_room_status(room_id: str, payload: UpdateRoomStatusModel):
    resp = service.update_room_status(room_id, payload)
    if resp["status"] == "failure":
        raise HTTPException(status_code=400, detail=resp["message"])
    return resp

@router.patch("/{room_id}/state", description="Update room discussion state")
async def update_room_state(room_id: str, payload: UpdateRoomStateModel):
    resp = service.update_room_state(room_id, payload)
    if resp["status"] == "failure":
        raise HTTPException(status_code=400, detail=resp["message"])
    return resp

@router.patch("/{room_id}/end", description="End room and mark as finished")
async def end_room(room_id: str, payload: UpdateRoomEndModel):
    resp = service.end_room(room_id, payload)
    if resp["status"] == "failure":
        raise HTTPException(status_code=400, detail=resp["message"])
    return resp