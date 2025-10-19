"""
API Routes for Transcripts
"""
from fastapi import APIRouter, HTTPException
from ..models.transcript_pydantic_models import (
    CreateTranscriptModel, UpdateTranscriptProcessingModel, UpdateTranscriptAudioURLModel
)
from ..services.transcript_service import TranscriptService

router = APIRouter()
service = TranscriptService()

@router.post("/", description="Create transcript")
async def create_transcript(payload: CreateTranscriptModel):
    return service.create_transcript(payload)

@router.get("/room/{room_id}", description="List transcripts for a room")
async def list_transcripts(room_id: str):
    return service.list_transcripts_for_room(room_id)

@router.get("/{transcript_id}", description="Get transcript by ID")
async def get_transcript(transcript_id: str):
    resp = service.get_transcript(transcript_id)
    if not resp.get("success"):
        raise HTTPException(status_code=404, detail=resp.get("error", "Not found"))
    return resp

@router.delete("/{transcript_id}", description="Delete transcript")
async def delete_transcript(transcript_id: str):
    return service.delete_transcript(transcript_id)

@router.patch("/processing", description="Update transcript processing status")
async def update_transcript_processing(payload: UpdateTranscriptProcessingModel):
    resp = service.update_transcript_processing(payload)
    if not resp.get("success"):
        raise HTTPException(status_code=400, detail=resp.get("error", "Failed to update"))
    return resp

@router.patch("/audio-url", description="Update transcript audio file URL")
async def update_transcript_audio_url(payload: UpdateTranscriptAudioURLModel):
    resp = service.update_transcript_audio_url(payload)
    if not resp.get("success"):
        raise HTTPException(status_code=400, detail=resp.get("error", "Failed to update"))
    return resp
