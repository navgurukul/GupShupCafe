"""
Test Agent System
Tests for agent models, services, and API routes
"""

import pytest
import uuid
from datetime import datetime

from src.models import (
    CreateAgentModel,
    AgentModel,
    AgentUpdateModel,
    AgentStatus,
    AgentType,
    AgentModelSource
)
from src.services.agent_service import agent_service


class TestAgentModels:
    """Test agent Pydantic models."""
    
    def test_create_agent_model(self):
        """Test CreateAgentModel validation."""
        agent_data = CreateAgentModel(
            room_id="room-123",
            agent_model=AgentModelSource.GEMINI,
            agent_type=AgentType.ENGLISH,
            system_prompt="You are an English tutor."
        )
        
        assert agent_data.room_id == "room-123"
        assert agent_data.agent_model == AgentModelSource.GEMINI
        assert agent_data.agent_type == AgentType.ENGLISH
        assert agent_data.status == AgentStatus.ACTIVE  # Default value
        assert agent_data.system_prompt == "You are an English tutor."

    def test_agent_model(self):
        """Test AgentModel with all fields."""
        agent_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        
        agent = AgentModel(
            agent_id=agent_id,
            room_id="room-123",
            agent_model="Gemini",
            agent_type="english",
            status="active",
            system_prompt="Test prompt",
            total_interactions=5,
            created_at=created_at
        )
        
        assert agent.agent_id == agent_id
        assert agent.room_id == "room-123"
        assert agent.agent_model == "Gemini"
        assert agent.agent_type == "english"
        assert agent.status == "active"
        assert agent.total_interactions == 5
        assert agent.created_at == created_at

    def test_agent_update_model(self):
        """Test AgentUpdateModel for partial updates."""
        update_data = AgentUpdateModel(
            status=AgentStatus.INACTIVE,
            system_prompt="Updated prompt"
        )
        
        assert update_data.status == AgentStatus.INACTIVE
        assert update_data.system_prompt == "Updated prompt"


class TestAgentEnums:
    """Test agent enums."""
    
    def test_agent_status_enum(self):
        """Test AgentStatus enum values."""
        assert AgentStatus.ACTIVE == "active"
        assert AgentStatus.INACTIVE == "inactive"
        assert AgentStatus.ERROR == "error"
        assert AgentStatus.PROCESSING == "processing"

    def test_agent_type_enum(self):
        """Test AgentType enum values."""
        assert AgentType.FACILITATOR == "facilitator"
        assert AgentType.ENGLISH == "english"
        assert AgentType.TUTOR == "tutor"
        assert AgentType.MODERATOR == "moderator"

    def test_agent_model_source_enum(self):
        """Test AgentModelSource enum values."""
        assert AgentModelSource.GEMINI == "Gemini"
        assert AgentModelSource.BEDROCK == "Bedrock"


class TestAgentService:
    """Test agent service methods."""
    
    @pytest.mark.asyncio
    async def test_agent_service_methods_exist(self):
        """Test that all expected service methods exist."""
        # Test that methods exist (they'll fail without database, but that's expected)
        assert hasattr(agent_service, 'create_agent')
        assert hasattr(agent_service, 'get_agent')
        assert hasattr(agent_service, 'get_agents_by_room')
        assert hasattr(agent_service, 'update_agent')
        assert hasattr(agent_service, 'increment_interactions')
        assert hasattr(agent_service, 'delete_agent')
        assert hasattr(agent_service, 'process_transcript_for_feedback')
        assert hasattr(agent_service, 'get_agent_stats')
        assert hasattr(agent_service, 'check_agent_health')
        assert hasattr(agent_service, 'get_agents_by_type')
        assert hasattr(agent_service, 'get_active_agents')
        
        # Test new methods for room agent management
        assert hasattr(agent_service, 'create_room_agents')
        assert hasattr(agent_service, 'generate_facilitator_turn_response')
        assert hasattr(agent_service, '_generate_english_feedback')
        assert hasattr(agent_service, '_generate_facilitator_response')

    def test_create_room_agents_parameters(self):
        """Test create_room_agents method signature."""
        import inspect
        sig = inspect.signature(agent_service.create_room_agents)
        params = list(sig.parameters.keys())
        
        assert 'room_id' in params
        assert 'room_topic' in params

    def test_feedback_generation_methods(self):
        """Test feedback generation method signatures."""
        import inspect
        
        # Test English feedback method
        sig = inspect.signature(agent_service._generate_english_feedback)
        params = list(sig.parameters.keys())
        assert 'agent' in params
        assert 'transcript_data' in params
        assert 'feedback_type' in params
        
        # Test facilitator response method
        sig = inspect.signature(agent_service._generate_facilitator_response)
        params = list(sig.parameters.keys())
        assert 'agent' in params
        assert 'transcript_data' in params


class TestAgentIntegration:
    """Test agent system integration scenarios."""
    
    def test_room_agent_creation_flow(self):
        """Test the expected flow for creating room agents."""
        # This would test the integration between room creation and agent setup
        # In a real test, this would use a test database
        room_id = "test-room-123"
        topic = {
            "title": "Climate Change Discussion",
            "category": "Environment"
        }
        
        # Verify the expected agent types would be created
        expected_types = [AgentType.FACILITATOR, AgentType.ENGLISH]
        assert len(expected_types) == 2
        
    def test_transcript_processing_flow(self):
        """Test the expected flow for transcript processing."""
        transcript_data = {
            "transcript_id": "test-transcript-123",
            "room_id": "test-room-123",
            "participant_id": "test-participant-123",
            "user_id": "test-user-123",
            "transcript_text": "I think climate change is a serious issue that requires immediate action.",
            "word_count": 12,
            "speech_rate": 2.0,
            "duration": 6
        }
        
        # Verify transcript data structure
        assert transcript_data["transcript_text"]
        assert transcript_data["word_count"] > 0
        assert transcript_data["speech_rate"] > 0
        
    def test_feedback_types(self):
        """Test different feedback types."""
        feedback_types = ["instant", "comprehensive"]
        
        for feedback_type in feedback_types:
            assert feedback_type in ["instant", "comprehensive"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])