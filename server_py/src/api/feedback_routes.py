"""
API Routes for Feedback
"""
from fastapi import APIRouter
from ..models.feedback_pydantic_models import InstantFeedbackModel, ComprehensiveFeedbackModel
from ..services.feedback_service import FeedbackService

router = APIRouter()
service = FeedbackService()

@router.post("/instant", description="Create instant feedback")
async def create_instant_feedback(payload: InstantFeedbackModel):
    return service.create_instant_feedback(payload)

@router.post("/comprehensive", description="Create comprehensive feedback")
async def create_comprehensive_feedback(payload: ComprehensiveFeedbackModel):
    return service.create_comprehensive_feedback(payload)

@router.get("/participant/{participant_id}", description="List feedback items for participant")
async def list_feedback(participant_id: str):
    return service.list_feedback_for_participant(participant_id)
