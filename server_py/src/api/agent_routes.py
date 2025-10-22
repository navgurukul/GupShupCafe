"""
Agent API Routes
RESTful endpoints for AI agent management and interactions
"""

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from ..models import (
    CreateAgentModel,
    CreateAgentResponseModel,
    AgentModel,
    AgentUpdateModel,
    AgentModelSource,
    AgentReplyModel,
    AgentReplyResponseModel,
    AgentStatus,
    AgentType,
    ListAgentsResponseModel
    
)
from ..services.agent_service import agent_service

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=CreateAgentResponseModel)
async def create_agent(agent_data: CreateAgentModel):
    """Create a new AI agent instance."""
    try:
        agent_id = await agent_service.create_agent(agent_data)
        return CreateAgentResponseModel(
            success=True,
            data=agent_id,
            message="Agent created successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("/{agent_id}", response_model=CreateAgentResponseModel)
async def get_agent(agent_id: str):
    """Get agent by ID."""
    agent = await agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return CreateAgentResponseModel("success", agent, "Agent retrieved successfully")


@router.get("/room/{room_id}", response_model=ListAgentsResponseModel)
async def get_agents_by_room(room_id: str):
    """Get all agents for a specific room."""
    agents = await agent_service.get_agents_by_room(room_id)
    return ListAgentsResponseModel("success", agents, "Agents retrieved successfully")


@router.get("/room/{room_id}/type/{agent_type}", response_model=ListAgentsResponseModel)
async def get_agents_by_type(room_id: str, agent_type: AgentType):
    """Get agents by type for a specific room."""
    agents = await agent_service.get_agents_by_type(room_id, agent_type)
    return ListAgentsResponseModel("success", agents, "Agents retrieved successfully")


@router.get("/room/{room_id}/active", response_model=ListAgentsResponseModel)
async def get_active_agents(room_id: str):
    """Get all active agents for a room."""
    agents = await agent_service.get_active_agents(room_id)
    return ListAgentsResponseModel("success", agents, "Active agents retrieved successfully")


@router.patch("/{agent_id}", response_model=UpdateAgentResponseModel)
async def update_agent(agent_id: str, update_data: UpdateAgentModel):
    """Update agent properties."""
    success = await agent_service.update_agent(agent_id, update_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found or no changes made"
        )
    return 


@router.delete("/{agent_id}", response_model=dict)
async def delete_agent(agent_id: str):
    """Delete an agent."""
    success = await agent_service.delete_agent(agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return {"success": True, "message": "Agent deleted successfully"}


@router.post("/{agent_id}/process-transcript", response_model=AgentResponseTextModel)
async def process_transcript(
    agent_id: str, 
    processing_data: AgentTranscriptProcessingModel
):
    """Process a transcript to generate feedback."""
    try:
        if processing_data.agent_id != agent_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agent ID mismatch"
            )
        
        response = await agent_service.process_transcript_for_feedback(
            agent_id=agent_id,
            transcript_id=processing_data.transcript_id,
            feedback_type=processing_data.processing_type
        )
        return response
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process transcript: {str(e)}"
        )


@router.get("/{agent_id}/stats", response_model=AgentInteractionStatsModel)
async def get_agent_stats(agent_id: str):
    """Get agent interaction statistics."""
    stats = await agent_service.get_agent_stats(agent_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return stats


@router.get("/{agent_id}/health", response_model=AgentHealthModel)
async def check_agent_health(agent_id: str):
    """Check agent health status."""
    health = await agent_service.check_agent_health(agent_id)
    if not health:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return health


@router.post("/{agent_id}/interactions/increment", response_model=dict)
async def increment_interactions(agent_id: str, count: int = 1):
    """Increment agent interaction counter."""
    success = await agent_service.increment_interactions(agent_id, count)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return {
        "success": True, 
        "message": f"Incremented interactions by {count}",
        "agent_id": agent_id
    }


@router.post("/room/{room_id}/create-agents", response_model=dict)
async def create_room_agents(room_id: str, topic_data: dict = None):
    """Create facilitator and English feedback agents for a room."""
    try:
        agent_ids = await agent_service.create_room_agents(room_id, topic_data)
        return {
            "success": True,
            "data": agent_ids,
            "message": "Room agents created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create room agents: {str(e)}"
        )


@router.post("/{agent_id}/generate-facilitator-response", response_model=dict)
async def generate_facilitator_response(
    agent_id: str, 
    context_data: dict
):
    """Generate facilitator response for TTS."""
    try:
        room_id = context_data.get("roomId")
        if not room_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Room ID is required"
            )
        
        # Get recent transcripts and feedback
        from ..database.database import db
        recent_transcripts = await db.get_recent_transcripts(room_id, limit=5)
        feedback_summaries = await db.get_feedback_by_room(room_id, "instant")
        
        # Generate response
        response_text = await agent_service.generate_facilitator_turn_response(
            room_id, recent_transcripts, feedback_summaries
        )
        
        return {
            "success": True,
            "data": {
                "responseText": response_text,
                "agentId": agent_id,
                "timestamp": __import__("datetime").datetime.now().isoformat()
            },
            "message": "Facilitator response generated"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate facilitator response: {str(e)}"
        )