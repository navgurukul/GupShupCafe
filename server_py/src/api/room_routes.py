"""
API Routes
RESTful endpoints for the application
"""
from fastapi import APIRouter, HTTPException
from ..models.room_pydantic_models import (
    CreateRoomModel, RoomResponseModel, UpdateRoomStatusModel,
    UpdateRoomStateModel, UpdateRoomEndModel, RoomStatus
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

@router.get("/waiting", description="List rooms with status 'waiting'")
async def list_waiting_rooms():
    """List only rooms that are currently waiting"""
    resp = service.list_rooms_by_status(RoomStatus.WAITING)
    if resp["status"] == "failure":
        raise HTTPException(status_code=404, detail=resp["message"])
    return resp

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



@router.get("/{room_id}/state")
async def get_room_state(room_id: str):
    """Get current room state including discussion status"""
    try:
        room = room_manager.get_room(room_id)
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Get current speaker
        current_speaker = room.get_current_speaker()
        
        # Serialize only safe discussion fields
        safe_discussion = {
            "active": room.status.value == "in_progress",
            "topic": room.topic,
            "currentSpeakerIndex": room.current_speaker_index,
            "speakingTime": room.speaking_time,
            "timeRemaining": room.time_remaining,
            "round": room.current_round,
            "startedAt": room.started_at,
            "endedAt": room.ended_at
        }
        
        # Get participants
        participants = room_manager.get_room_participants(room_id)
        
        return {
            "participants": participants,
            "discussion": safe_discussion
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[api/room/{room_id}/state] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to get room state")


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

@router.post("/{room_id}/start", description="Start the discussion", response_model=RoomResponseModel)
async def start_discussion(room_id: str, payload: dict):
    """Start the discussion in a room"""
    resp = await service.start_discussion(room_id, payload)
    if resp["status"] == "failure":
        raise HTTPException(status_code=400, detail=resp["message"])
    return resp