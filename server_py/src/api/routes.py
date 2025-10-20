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



@router.get("/config")
async def get_config():
    """Get public configuration"""
    try:
        config = {
            "minParticipants": int(os.getenv("MIN_PARTICIPANTS", "1")),
            "maxParticipants": int(os.getenv("MAX_PARTICIPANTS", "6")),
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

