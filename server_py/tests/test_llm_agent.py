"""
Tests for LLM Agent Service
"""

import pytest
import os
from datetime import datetime

from src.ai.llm_agent_service import LLMAgentService, llm_agent_service


class TestLLMAgentService:
    """Test LLM Agent Service functionality"""
    
    def test_service_initialization(self):
        """Test service initializes correctly"""
        service = LLMAgentService()
        assert service.agent_participant_id == "llm-agent"
        assert service.agent_name == "AI Tutor"
        assert isinstance(service.conversation_history, dict)
        assert service.agent_initialized is False
    
    def test_enabled_check_default(self):
        """Test that agent is disabled by default"""
        service = LLMAgentService()
        # Should be disabled unless ENABLE_LLM_AGENT is set
        assert service.is_enabled() is False
    
    def test_enabled_check_with_env(self, monkeypatch):
        """Test that agent can be enabled via environment variable"""
        monkeypatch.setenv("ENABLE_LLM_AGENT", "true")
        service = LLMAgentService()
        assert service.is_enabled() is True
    
    def test_get_agent_participant(self):
        """Test getting agent participant object"""
        service = LLMAgentService()
        participant = service.get_agent_participant()
        
        assert participant["id"] == "llm-agent"
        assert participant["anonymousName"] == "AI Tutor"
        assert participant["role"] == "speaker"
        assert participant["isReady"] is True
        assert participant["isAgent"] is True
        assert "joinedAt" in participant
    
    def test_initialize_room(self, sample_topic):
        """Test room initialization"""
        service = LLMAgentService()
        participants = [
            {"id": "user1", "name": "Alice"},
            {"id": "user2", "name": "Bob"}
        ]
        
        result = service.initialize_room("test-room", sample_topic, participants)
        
        assert result is True
        assert service.agent_initialized is True
        assert "test-room" in service.conversation_history
        assert len(service.conversation_history["test-room"]) == 0
    
    def test_add_statement(self):
        """Test adding statements to conversation history"""
        service = LLMAgentService()
        service.conversation_history["test-room"] = []
        
        service.add_statement("test-room", "Alice", "I think this is interesting")
        
        assert len(service.conversation_history["test-room"]) == 1
        statement = service.conversation_history["test-room"][0]
        assert statement["speaker"] == "Alice"
        assert statement["content"] == "I think this is interesting"
        assert "timestamp" in statement
    
    @pytest.mark.asyncio
    async def test_generate_opening_response(self, sample_topic):
        """Test generating opening statement"""
        service = LLMAgentService()
        service.initialize_room("test-room", sample_topic, [])
        
        response = await service.generate_response("test-room", sample_topic)
        
        assert "speaker" in response
        assert response["speaker"] == "AI Tutor"
        assert "content" in response
        assert len(response["content"]) > 0
        assert "timestamp" in response
        assert response["isAgent"] is True
    
    @pytest.mark.asyncio
    async def test_generate_feedback_response(self, sample_topic):
        """Test generating feedback after statements"""
        service = LLMAgentService()
        service.initialize_room("test-room", sample_topic, [])
        
        # Add some statements
        service.add_statement("test-room", "Alice", "Great topic!")
        service.add_statement("test-room", "Bob", "I agree with Alice")
        
        response = await service.generate_response("test-room", sample_topic)
        
        assert "speaker" in response
        assert response["speaker"] == "AI Tutor"
        assert "content" in response
        # Should contain feedback sections
        assert "Feedback" in response["content"] or "feedback" in response["content"]
        assert response["isAgent"] is True
    
    @pytest.mark.asyncio
    async def test_generate_response_error_handling(self):
        """Test error handling in response generation"""
        service = LLMAgentService()
        
        # Generate response for non-existent room (no conversation history)
        response = await service.generate_response("nonexistent-room", {"title": "Test"})
        
        # Should return an opening statement (since no history exists)
        assert "speaker" in response
        assert "content" in response
        # Opening statement should mention the topic
        assert "Test" in response["content"] or "test" in response["content"].lower()
    
    def test_cleanup_room(self):
        """Test cleaning up room data"""
        service = LLMAgentService()
        service.conversation_history["test-room"] = [
            {"speaker": "Alice", "content": "Test"}
        ]
        
        service.cleanup_room("test-room")
        
        assert "test-room" not in service.conversation_history
    
    def test_cleanup_nonexistent_room(self):
        """Test cleaning up non-existent room doesn't error"""
        service = LLMAgentService()
        # Should not raise an error
        service.cleanup_room("nonexistent-room")
    
    def test_opening_statement_variations(self, sample_topic):
        """Test that opening statements vary based on topic"""
        service = LLMAgentService()
        
        # Test with different topics
        topic1 = {"title": "Short"}
        topic2 = {"title": "This is a much longer topic title"}
        
        statement1 = service._generate_opening_statement(topic1)
        statement2 = service._generate_opening_statement(topic2)
        
        # Both should contain the topic title
        assert "Short" in statement1
        assert "This is a much longer topic title" in statement2
        
        # Statements should be reasonably long
        assert len(statement1) > 20
        assert len(statement2) > 20
    
    def test_feedback_generation(self, sample_topic):
        """Test feedback generation logic"""
        service = LLMAgentService()
        
        statements = [
            {"speaker": "Alice", "content": "Interesting point"},
            {"speaker": "Bob", "content": "I agree"}
        ]
        
        feedback = service._generate_feedback(sample_topic, statements)
        
        # Should contain discussion feedback
        assert "Feedback" in feedback or "feedback" in feedback
        # Should mention the topic
        assert sample_topic["title"] in feedback
        # Should mention speakers
        assert "Alice" in feedback or "Bob" in feedback
    
    def test_conversation_history_persistence(self):
        """Test that conversation history persists across multiple statements"""
        service = LLMAgentService()
        room_id = "test-room"
        
        service.initialize_room(room_id, {"title": "Test"}, [])
        
        # Add multiple statements
        service.add_statement(room_id, "Alice", "Statement 1")
        service.add_statement(room_id, "Bob", "Statement 2")
        service.add_statement(room_id, "Charlie", "Statement 3")
        
        # All should be stored
        assert len(service.conversation_history[room_id]) == 3
        assert service.conversation_history[room_id][0]["speaker"] == "Alice"
        assert service.conversation_history[room_id][1]["speaker"] == "Bob"
        assert service.conversation_history[room_id][2]["speaker"] == "Charlie"
    
    def test_global_service_instance(self):
        """Test that global service instance exists"""
        assert llm_agent_service is not None
        assert isinstance(llm_agent_service, LLMAgentService)
