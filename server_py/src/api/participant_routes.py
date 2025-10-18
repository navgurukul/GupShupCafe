"""
API Routes for Participants
RESTful endpoints for participant management
"""
from fastapi import APIRouter, HTTPException
from ..models.participant_pydantic_models import CreateParticipantModel, ParticipantResponseModel
from ..services.participant_service import Participant_service

router = APIRouter()
participant_service = Participant_service()

@router.post("/participant", description="Create a new participant", response_model=ParticipantResponseModel)
async def create_participant(participant: CreateParticipantModel):
    """Create a new participant endpoint"""
    response = participant_service.create_participant(participant)
    return response

@router.get("/participant/{user_id}/{room_id}", description="Get participant details")
async def get_participant(user_id: str, room_id: str):
    """Get participant details endpoint"""
    response = participant_service.get_participant(user_id, room_id)
    if response["status"] == "failure":
        raise HTTPException(status_code=404, detail=response["message"])
    return response
