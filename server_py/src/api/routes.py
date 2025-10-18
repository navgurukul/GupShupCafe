"""
API Routes
RESTful endpoints for the application
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import os

from ..ai.topic_generator import (
    get_all_fallback_topics,
    generate_discussion_topic,
    get_topic_by_category
)
# from ..database import db_connection as db
from ..socket.room_manager import room_manager

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "service": "AI Roundtable API"
    }


@router.get("/topics")
async def get_topics():
    """Get all available fallback topics"""
    try:
        topics = get_all_fallback_topics()
        return {
            "success": True,
            "data": topics,
            "count": len(topics)
        }
    except Exception as e:
        print(f"Error getting topics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve topics")


@router.get("/topics/generate")
async def generate_topic():
    """Generate a new discussion topic"""
    try:
        topic = await generate_discussion_topic()
        return {
            "success": True,
            "data": topic
        }
    except Exception as e:
        print(f"Error generating topic: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate topic")


@router.get("/topics/category/{category}")
async def get_topic_by_cat(category: str):
    """Get topic by category"""
    try:
        topic = get_topic_by_category(category)
        
        if not topic:
            raise HTTPException(
                status_code=404,
                detail="Topic not found for this category"
            )
        
        return {
            "success": True,
            "data": topic
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting topic by category: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve topic")


# @router.get("/analytics/rooms")
# async def get_rooms(limit: int = Query(default=10, ge=1, le=100)):
#     """Get room analytics"""
#     try:
#         rooms = await db.get_room_analytics(limit)
        
#         return {
#             "success": True,
#             "data": rooms,
#             "count": len(rooms)
#         }
#     except Exception as e:
#         print(f"Error getting room analytics: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to retrieve room analytics")


# @router.get("/analytics/topics")
# async def get_topic_analytics():
#     """Get topic usage analytics"""
#     try:
#         topics = await db.get_topic_analytics()
        
#         return {
#             "success": True,
#             "data": topics,
#             "count": len(topics)
#         }
#     except Exception as e:
#         print(f"Error getting topic analytics: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to retrieve topic analytics")


# @router.get("/analytics/stats")
# async def get_stats():
#     """Get server statistics"""
#     try:
#         stats = await db.get_server_stats()
        
#         return {
#             "success": True,
#             "data": stats
#         }
#     except Exception as e:
#         print(f"Error getting server stats: {str(e)}")
#         raise HTTPException(status_code=500, detail="Failed to retrieve server statistics")


@router.post("/feedback")
async def submit_feedback(feedback_data: dict):
    """Submit user feedback"""
    try:
        rating = feedback_data.get("rating")
        comment = feedback_data.get("comment")
        room_id = feedback_data.get("room_id")
        
        # Log feedback (in production, save to database)
        print(f"Feedback received: {{'rating': {rating}, 'comment': {comment[:100] if comment else None}, 'room_id': {room_id}, 'timestamp': {__import__('datetime').datetime.now()}}}")
        
        return {
            "success": True,
            "message": "Feedback received successfully"
        }
    except Exception as e:
        print(f"Error handling feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.get("/config")
async def get_config():
    """Get public configuration"""
    try:
        config = {
            "minParticipants": int(os.getenv("MIN_PARTICIPANTS", "1")),
            "maxParticipants": int(os.getenv("MAX_PARTICIPANTS", "8")),
            "defaultSpeakingTime": int(os.getenv("DEFAULT_SPEAKING_TIME", "60")),
            "features": {
                "aiTopics": bool(
                    os.getenv("HUGGINGFACE_API_KEY") and 
                    os.getenv("HUGGINGFACE_API_KEY") != "your_huggingface_api_key_here"
                ),
                "analytics": True,
                "feedback": True
            }
        }
        
        return {
            "success": True,
            "data": config
        }
    except Exception as e:
        print(f"[api/config] Error getting config: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": "Failed to retrieve configuration",
                "details": str(e)
            }
        )


@router.get("/room/{room_id}/state")
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
