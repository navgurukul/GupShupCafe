"""
API Routes for Feedback
"""
from fastapi import APIRouter, HTTPException
from ..models.feedback_pydantic_models import InstantFeedbackModel, ComprehensiveFeedbackModel
from ..services.feedback_service import Feedback_service

router = APIRouter()
service = Feedback_service()

@router.post("/instant", description="Create instant feedback")
async def create_instant_feedback(payload: InstantFeedbackModel):
    return service.create_instant_feedback(payload)

@router.post("/comprehensive", description="Create comprehensive feedback")
async def create_comprehensive_feedback(payload: ComprehensiveFeedbackModel):
    return service.create_comprehensive_feedback(payload)

@router.get("/participant/{participant_id}", description="List feedback items for participant")
async def list_feedback(participant_id: str):
    return service.list_feedback_for_participant(participant_id)

@router.get("/room/{room_id}", description="List feedback for a room")
async def list_feedback_for_room(room_id: str):
    return service.list_feedback_for_room(room_id)

@router.get("/{feedback_id}", description="Get feedback by ID")
async def get_feedback(feedback_id: str):
    resp = service.get_feedback(feedback_id)
    if not resp.get("success"):
        raise HTTPException(status_code=404, detail=resp.get("error", "Not found"))
    return resp

@router.delete("/{feedback_id}", description="Delete feedback")
async def delete_feedback(feedback_id: str):
    return service.delete_feedback(feedback_id)
