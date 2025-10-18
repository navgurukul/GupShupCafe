"""
API Routes for Transcripts
"""
from fastapi import APIRouter
from ..models.transcript_pydantic_models import CreateTranscriptModel
from ..services.transcript_service import TranscriptService

router = APIRouter()
service = TranscriptService()

@router.post("/", description="Create transcript")
async def create_transcript(payload: CreateTranscriptModel):
    return service.create_transcript(payload)

@router.get("/room/{room_id}", description="List transcripts for a room")
async def list_transcripts(room_id: str):
    return service.list_transcripts_for_room(room_id)
