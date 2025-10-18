"""
API Routes for Participants
RESTful endpoints for participant management
"""
from fastapi import APIRouter, HTTPException
from ..models.participant_pydantic_models import CreateParticipantModel, ParticipantResponseModel, ParticipantUpdateModel
from ..services.participant_service import Participant_service

router = APIRouter()
participant_service = Participant_service()

@router.post("/", description="Create a new participant", response_model=ParticipantResponseModel)
async def create_participant(participant: CreateParticipantModel):
    """Create a new participant endpoint"""
    response = participant_service.create_participant(participant)
    return response

@router.get("/{user_id}/{room_id}", description="Get participant details")
async def get_participant(user_id: str, room_id: str):
    """Get participant details endpoint"""
    response = participant_service.get_participant(user_id, room_id)
    if response["status"] == "failure":
        raise HTTPException(status_code=404, detail=response["message"])
    return response

@router.get("/room/{room_id}", description="List participants for a room")
async def list_participants(room_id: str):
    return participant_service.list_participants_for_room(room_id)

@router.patch("/{participant_id}", description="Update participant")
async def update_participant(participant_id: str, payload: ParticipantUpdateModel):
    resp = participant_service.update_participant(participant_id, payload)
    if resp["status"] == "failure":
        raise HTTPException(status_code=400, detail=resp["message"])
    return resp

@router.delete("/{participant_id}", description="Delete participant")
async def delete_participant(participant_id: str):
    return participant_service.delete_participant(participant_id)
