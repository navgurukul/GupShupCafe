"""
Get Models Usage Examples
Demonstrates how to use the new Get<Name>Model classes in API routes and services
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from src.models import (
    GetParticipantModel,
    GetAgentModel,
    GetRoomModel,
    GetUserModel,
    GetTranscriptModel,
    GetInstantFeedbackModel,
    GetComprehensiveFeedbackModel
)

router = APIRouter()

# Example 1: Basic participant query with optional filters
@router.get("/participants/{participant_id}")
async def get_participant_with_filters(
    participant_id: str,
    room_id: Optional[str] = Query(None),
    is_ready: Optional[bool] = Query(None),
    role: Optional[str] = Query(None)
):
    """Get participant with optional filters"""
    filters = GetParticipantModel(
        participant_id=participant_id,
        room_id=room_id,
        is_ready=is_ready,
        role=role
    )
    # Use filters in service call
    return await participant_service.get_participant_with_filters(filters)

# Example 2: Room search with multiple optional parameters
@router.get("/rooms/{room_id}")
async def get_room_details(
    room_id: str,
    status: Optional[str] = Query(None),
    cefr_level: Optional[str] = Query(None),
    max_participants: Optional[int] = Query(None),
    topic_category: Optional[str] = Query(None)
):
    """Get room with optional search criteria"""
    search_criteria = GetRoomModel(
        room_id=room_id,
        status=status,
        cefr_level=cefr_level,
        max_participants=max_participants,
        topic_category=topic_category
    )
    return await room_service.get_room_with_criteria(search_criteria)

# Example 3: Agent query with type and status filters
@router.get("/agents/{agent_id}")
async def get_agent_info(
    agent_id: str,
    agent_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    room_id: Optional[str] = Query(None)
):
    """Get agent with optional filters"""
    agent_query = GetAgentModel(
        agent_id=agent_id,
        agent_type=agent_type,
        status=status,
        room_id=room_id
    )
    return await agent_service.get_agent_with_filters(agent_query)

# Example 4: User profile with optional data fields
@router.get("/users/{user_id}")
async def get_user_profile(
    user_id: str,
    include_email: Optional[bool] = Query(False),
    include_topics: Optional[bool] = Query(False)
):
    """Get user profile with selective field inclusion"""
    user_query = GetUserModel(user_id=user_id)
    
    # Conditionally include fields based on parameters
    if include_email:
        user_query.email = None  # Will be populated by service
    if include_topics:
        user_query.topic_categories = None  # Will be populated by service
    
    return await user_service.get_user_profile(user_query)

# Example 5: Transcript search with time range and content filters
@router.get("/transcripts/{transcript_id}")
async def get_transcript_details(
    transcript_id: str,
    room_id: Optional[str] = Query(None),
    participant_id: Optional[str] = Query(None),
    min_duration: Optional[int] = Query(None),
    language: Optional[str] = Query(None)
):
    """Get transcript with optional search filters"""
    transcript_query = GetTranscriptModel(
        transcript_id=transcript_id,
        room_id=room_id,
        participant_id=participant_id,
        language=language
    )
    
    # Additional filtering can be handled in service layer
    return await transcript_service.get_transcript_with_filters(
        transcript_query, 
        min_duration=min_duration
    )

# Example 6: Feedback query with type-specific filtering
@router.get("/feedback/instant/{feedback_id}")
async def get_instant_feedback(
    feedback_id: str,
    participant_id: Optional[str] = Query(None),
    room_id: Optional[str] = Query(None),
    agent_model: Optional[str] = Query(None)
):
    """Get instant feedback with optional filters"""
    feedback_query = GetInstantFeedbackModel(
        feedback_id=feedback_id,
        participant_id=participant_id,
        room_id=room_id,
        agent_model=agent_model
    )
    return await feedback_service.get_instant_feedback_with_filters(feedback_query)

@router.get("/feedback/comprehensive/{feedback_id}")
async def get_comprehensive_feedback(
    feedback_id: str,
    participant_id: Optional[str] = Query(None),
    room_id: Optional[str] = Query(None),
    cefr_speaking: Optional[str] = Query(None),
    target_cefr_level: Optional[str] = Query(None)
):
    """Get comprehensive feedback with optional filters"""
    feedback_query = GetComprehensiveFeedbackModel(
        feedback_id=feedback_id,
        participant_id=participant_id,
        room_id=room_id,
        cefr_speaking=cefr_speaking,
        target_cefr_level=target_cefr_level
    )
    return await feedback_service.get_comprehensive_feedback_with_filters(feedback_query)

# Example 7: Service layer usage
class ParticipantService:
    async def get_participant_with_filters(self, filters: GetParticipantModel):
        """Service method using Get model for database queries"""
        query = "SELECT * FROM participants WHERE participant_id = ?"
        params = [filters.participant_id]
        
        # Add optional WHERE clauses based on provided filters
        if filters.room_id:
            query += " AND room_id = ?"
            params.append(filters.room_id)
        
        if filters.is_ready is not None:
            query += " AND is_ready = ?"
            params.append(filters.is_ready)
        
        if filters.role:
            query += " AND role = ?"
            params.append(filters.role)
        
        # Execute query and return results
        return await self.db.execute(query, params)

# Example 8: Complex search with multiple models
@router.get("/search/participants")
async def search_participants(
    room_id: Optional[str] = Query(None),
    is_ready: Optional[bool] = Query(None),
    role: Optional[str] = Query(None),
    cefr_level: Optional[str] = Query(None),
    limit: int = Query(10, le=100)
):
    """Search participants across rooms with complex filters"""
    # This would use multiple Get models for complex queries
    search_params = {
        "room_id": room_id,
        "is_ready": is_ready,
        "role": role,
        "cefr_level": cefr_level,
        "limit": limit
    }
    
    return await participant_service.search_participants(search_params)

# Example 9: Validation and error handling
@router.get("/participants/{participant_id}/validate")
async def validate_participant_query(participant_id: str):
    """Example of validation using Get models"""
    try:
        # This will validate the participant_id format
        query = GetParticipantModel(participant_id=participant_id)
        return {"valid": True, "participant_id": query.participant_id}
    except ValueError as e:
        return {"valid": False, "error": str(e)}

# Example 10: Batch operations with Get models
@router.post("/participants/batch-get")
async def batch_get_participants(participant_queries: list[GetParticipantModel]):
    """Batch get participants using multiple Get models"""
    results = []
    for query in participant_queries:
        result = await participant_service.get_participant_with_filters(query)
        results.append(result)
    return results