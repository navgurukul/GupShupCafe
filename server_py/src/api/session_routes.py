"""
API Routes
RESTful endpoints for the application
"""
from fastapi import APIRouter
from ..models.session_pydantic_models import CreateSessionModel, SessionResponseModel
from ..services.session_service import Session_service
router = APIRouter()
service = Session_service()

@router.post("/session", description="Create a new session", response_model=SessionResponseModel)
async def create_session(session: CreateSessionModel):
    """Create a new session endpoint"""
    response = service.create_session(session)
    return response