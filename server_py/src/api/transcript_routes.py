"""
API Routes for Transcripts
"""
from fastapi import APIRouter, HTTPException
from ..models.transcript_pydantic_models import (
    CreateTranscriptModel, UpdateTranscriptModel, UpdateTranscriptResponseModel, ListTranscriptsResponseModel, DeleteTranscriptResponseModel
)
from ..services.transcript_service import Transcript_service

router = APIRouter()
service = Transcript_service()

@router.post("/", description="Create transcript")
async def create_transcript(payload: CreateTranscriptModel):
    return service.create_transcript(payload)

@router.get("/room/{room_id}", description="List transcripts for a room", response_model=ListTranscriptsResponseModel)
async def list_transcripts(room_id: str):
    return service.list_transcripts_for_room(room_id)

@router.get("/{transcript_id}", description="Get transcript by ID", response_model=CreateTranscriptModel)
async def get_transcript(transcript_id: str):
    resp = service.get_transcript(transcript_id)
    if not resp.get("success"):
        raise HTTPException(status_code=404, detail=resp.get("error", "Not found"))
    return resp

@router.delete("/{transcript_id}", description="Delete transcript", response_model=DeleteTranscriptResponseModel)
async def delete_transcript(transcript_id: str):
    return service.delete_transcript(transcript_id)

@router.patch("/processing", description="Update transcript processing status", response_model=UpdateTranscriptResponseModel)
async def update_transcript_processing(payload: UpdateTranscriptModel):
    resp = service.update_transcript_processing(payload)
    if not resp.get("success"):
        raise HTTPException(status_code=400, detail=resp.get("error", "Failed to update"))
    return resp

@router.patch("/audio-url", description="Update transcript audio file URL", response_model=UpdateTranscriptResponseModel)
async def update_transcript_audio_url(payload: UpdateTranscriptModel):
    resp = service.update_transcript_audio_url(payload)
    if not resp.get("success"):
        raise HTTPException(status_code=400, detail=resp.get("error", "Failed to update"))
    return resp
