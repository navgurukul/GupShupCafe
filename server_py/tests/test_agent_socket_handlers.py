"""
Test Agent-Related Socket.io Event Handlers
Tests for socket handlers that interact with AI agents
"""

import pytest
import socketio
import uuid
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime

from src.socket.socket_handlers import setup_socket_handlers, process_transcript_for_english_feedback
from src.socket.room_manager import room_manager
from src.models import AgentType, AgentStatus
from src.services.agent_service import agent_service


@pytest.fixture
async def mock_sio():
    """Create a mock Socket.io server"""
    sio = MagicMock(spec=socketio.AsyncServer)
    sio.emit = AsyncMock()
    sio.enter_room = AsyncMock()
    sio.leave_room = AsyncMock()
    sio.rooms = MagicMock(return_value=[])
    sio.get_session = AsyncMock(return_value={})
    sio.save_session = AsyncMock()
    return sio


@pytest.fixture
def setup_test_room_with_agents():
    """Setup a test room with participants and mock agents"""
    # Clean up any existing rooms
    room_manager.rooms.clear()
    
    room_id = "test-room-agents"
    socket_id = "test-socket-456"
    user_data = {
        "id": "user-456",
        "socketId": socket_id,
        "anonymousName": "Test Speaker",
        "name": "Test Name",
        "campus": "Test Campus",
        "location": "Test Location",
        "role": "speaker",
        "isReady": True
    }
    
    # Add user to room
    room_manager.add_user_to_room(room_id, user_data)
    
    # Mock agent data
    mock_english_agent = {
        "agent_id": "english-agent-123",
        "room_id": room_id,
        "agent_type": "english",
        "status": "active",
        "agent_model": "gemini"
    }
    
    mock_facilitator_agent = {
        "agent_id": "facilitator-agent-123",
        "room_id": room_id,
        "agent_type": "facilitator",
        "status": "active",
        "agent_model": "gemini"
    }
    
    yield {
        "room_id": room_id,
        "socket_id": socket_id,
        "user_data": user_data,
        "english_agent": mock_english_agent,
        "facilitator_agent": mock_facilitator_agent
    }
    
    # Cleanup
    room_manager.rooms.clear()


@pytest.mark.asyncio
async def test_process_transcript_for_english_feedback():
    """Test the background task for processing transcripts with English feedback agent"""
    room_id = "test-room"
    transcript_id = "transcript-123"
    
    # Mock agent service methods
    mock_english_agent = MagicMock()
    mock_english_agent.agent_id = "english-agent-123"
    mock_english_agent.agent_type = "english"
    
    with patch.object(agent_service, 'get_agents_by_room', new_callable=AsyncMock) as mock_get_agents:
        with patch.object(agent_service, 'process_transcript_for_feedback', new_callable=AsyncMock) as mock_process:
            # Setup mocks
            mock_get_agents.return_value = [mock_english_agent]
            mock_process.return_value = MagicMock()
            
            # Call the function
            await process_transcript_for_english_feedback(room_id, transcript_id)
            
            # Verify agent service was called correctly
            mock_get_agents.assert_called_once_with(room_id)
            mock_process.assert_called_once_with(
                mock_english_agent.agent_id,
                transcript_id,
                "instant"
            )


@pytest.mark.asyncio
async def test_process_transcript_for_english_feedback_no_agent():
    """Test background task when no English agent exists"""
    room_id = "test-room"
    transcript_id = "transcript-123"
    
    with patch.object(agent_service, 'get_agents_by_room', new_callable=AsyncMock) as mock_get_agents:
        # Setup mock to return no English agents
        mock_facilitator_agent = MagicMock()
        mock_facilitator_agent.agent_type = "facilitator"
        mock_get_agents.return_value = [mock_facilitator_agent]
        
        # Call the function - should handle gracefully
        await process_transcript_for_english_feedback(room_id, transcript_id)
        
        # Verify it tried to get agents but didn't crash
        mock_get_agents.assert_called_once_with(room_id)


@pytest.mark.asyncio
async def test_transcript_received_handler(mock_sio, setup_test_room_with_agents):
    """Test transcript_received socket event handler"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    room_id = setup_test_room_with_agents["room_id"]
    socket_id = setup_test_room_with_agents["socket_id"]
    user_data = setup_test_room_with_agents["user_data"]
    
    # Mock sio.rooms to return the room
    mock_sio.rooms.return_value = [socket_id, room_id]
    
    # Mock database save_transcript
    with patch('src.socket.socket_handlers.db.save_transcript', new_callable=AsyncMock) as mock_save:
        with patch('src.socket.socket_handlers.asyncio.create_task') as mock_create_task:
            # Get the transcript_received handler
            transcript_handler = None
            for call in mock_sio.event.call_args_list:
                if call[0] and hasattr(call[0][0], '__name__'):
                    if call[0][0].__name__ == 'transcript_received':
                        transcript_handler = call[0][0]
                        break
            
            assert transcript_handler is not None, "transcript_received handler not found"
            
            # Test data
            transcript_data = {
                "text": "This is a test transcript for English learning",
                "participantId": user_data["id"],
                "round": 1,
                "turnOrder": 0,
                "confidence": 0.95,
                "startedAt": datetime.now().isoformat(),
                "endedAt": datetime.now().isoformat(),
                "duration": 5.0
            }
            
            # Call the handler
            await transcript_handler(socket_id, transcript_data)
            
            # Verify transcript was saved to database
            mock_save.assert_called_once()
            saved_data = mock_save.call_args[0][0]
            assert saved_data["transcript_text"] == transcript_data["text"]
            assert saved_data["room_id"] == room_id
            assert saved_data["participant_id"] == user_data["id"]
            assert saved_data["word_count"] == len(transcript_data["text"].split())
            
            # Verify background task was created for agent processing
            mock_create_task.assert_called_once()
            
            # Verify transcript-saved event was emitted
            mock_sio.emit.assert_called()
            emit_calls = [call for call in mock_sio.emit.call_args_list 
                         if call[0][0] == "transcript-saved"]
            assert len(emit_calls) > 0


@pytest.mark.asyncio
async def test_request_facilitator_response_handler(mock_sio, setup_test_room_with_agents):
    """Test request_facilitator_response socket event handler"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    room_id = setup_test_room_with_agents["room_id"]
    socket_id = setup_test_room_with_agents["socket_id"]
    
    # Mock sio.rooms to return the room
    mock_sio.rooms.return_value = [socket_id, room_id]
    
    # Mock database methods
    with patch('src.socket.socket_handlers.db.get_recent_transcripts', new_callable=AsyncMock) as mock_get_transcripts:
        with patch('src.socket.socket_handlers.db.get_feedback_by_room', new_callable=AsyncMock) as mock_get_feedback:
            with patch.object(agent_service, 'generate_facilitator_turn_response', new_callable=AsyncMock) as mock_generate:
                # Setup mocks
                mock_get_transcripts.return_value = [
                    {"transcript_text": "I think this is important", "participant_id": "user-1"},
                    {"transcript_text": "I agree with that point", "participant_id": "user-2"}
                ]
                mock_get_feedback.return_value = [
                    {"display_message": "Good use of vocabulary", "participant_id": "user-1"}
                ]
                mock_generate.return_value = "Thank you for those insights. Let's explore this further."
                
                # Get the handler
                facilitator_handler = None
                for call in mock_sio.event.call_args_list:
                    if call[0] and hasattr(call[0][0], '__name__'):
                        if call[0][0].__name__ == 'request_facilitator_response':
                            facilitator_handler = call[0][0]
                            break
                
                assert facilitator_handler is not None, "request_facilitator_response handler not found"
                
                # Call the handler
                await facilitator_handler(socket_id, {})
                
                # Verify database calls
                mock_get_transcripts.assert_called_once_with(room_id, limit=5)
                mock_get_feedback.assert_called_once_with(room_id, "instant")
                
                # Verify agent service was called
                mock_generate.assert_called_once()
                
                # Verify facilitator-speaking event was emitted
                emit_calls = [call for call in mock_sio.emit.call_args_list 
                             if call[0][0] == "facilitator-speaking"]
                assert len(emit_calls) > 0
                emitted_data = emit_calls[0][0][1]
                assert "text" in emitted_data
                assert "timestamp" in emitted_data


@pytest.mark.asyncio
async def test_get_instant_feedback_handler(mock_sio, setup_test_room_with_agents):
    """Test get_instant_feedback socket event handler"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    room_id = setup_test_room_with_agents["room_id"]
    socket_id = setup_test_room_with_agents["socket_id"]
    participant_id = setup_test_room_with_agents["user_data"]["id"]
    
    # Mock sio.rooms to return the room
    mock_sio.rooms.return_value = [socket_id, room_id]
    
    # Mock database get_feedback_by_room
    with patch('src.socket.socket_handlers.db.get_feedback_by_room', new_callable=AsyncMock) as mock_get_feedback:
        # Setup mock to return feedback for the participant
        mock_get_feedback.return_value = [
            {
                "participant_id": participant_id,
                "display_message": "Great use of complex sentences!",
                "created_at": datetime.now().isoformat()
            },
            {
                "participant_id": "other-user",
                "display_message": "Other feedback",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        # Get the handler
        feedback_handler = None
        for call in mock_sio.event.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__'):
                if call[0][0].__name__ == 'get_instant_feedback':
                    feedback_handler = call[0][0]
                    break
        
        assert feedback_handler is not None, "get_instant_feedback handler not found"
        
        # Call the handler
        request_data = {"participantId": participant_id}
        await feedback_handler(socket_id, request_data)
        
        # Verify database was queried
        mock_get_feedback.assert_called_once_with(room_id, "instant")
        
        # Verify instant-feedback event was emitted with correct participant's feedback
        emit_calls = [call for call in mock_sio.emit.call_args_list 
                     if call[0][0] == "instant-feedback"]
        assert len(emit_calls) > 0
        emitted_data = emit_calls[0][0][1]
        assert emitted_data["participantId"] == participant_id
        assert emitted_data["feedback"] == "Great use of complex sentences!"
        assert "timestamp" in emitted_data


@pytest.mark.asyncio
async def test_get_instant_feedback_no_feedback_available(mock_sio, setup_test_room_with_agents):
    """Test get_instant_feedback when no feedback is available"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    room_id = setup_test_room_with_agents["room_id"]
    socket_id = setup_test_room_with_agents["socket_id"]
    participant_id = setup_test_room_with_agents["user_data"]["id"]
    
    # Mock sio.rooms to return the room
    mock_sio.rooms.return_value = [socket_id, room_id]
    
    # Mock database to return no feedback
    with patch('src.socket.socket_handlers.db.get_feedback_by_room', new_callable=AsyncMock) as mock_get_feedback:
        mock_get_feedback.return_value = []
        
        # Get the handler
        feedback_handler = None
        for call in mock_sio.event.call_args_list:
            if call[0] and hasattr(call[0][0], '__name__'):
                if call[0][0].__name__ == 'get_instant_feedback':
                    feedback_handler = call[0][0]
                    break
        
        assert feedback_handler is not None, "get_instant_feedback handler not found"
        
        # Call the handler
        request_data = {"participantId": participant_id}
        await feedback_handler(socket_id, request_data)
        
        # Verify fallback feedback was provided
        emit_calls = [call for call in mock_sio.emit.call_args_list 
                     if call[0][0] == "instant-feedback"]
        assert len(emit_calls) > 0
        emitted_data = emit_calls[0][0][1]
        assert emitted_data["participantId"] == participant_id
        assert emitted_data["feedback"] == "Keep up the great work!"


@pytest.mark.asyncio
async def test_agent_creation_in_discussion_start():
    """Test that agents are created when discussion starts"""
    room_id = "test-room-discussion"
    active_rooms = {}
    
    # Mock socket.io server
    mock_sio = MagicMock()
    mock_sio.emit = AsyncMock()
    
    # Setup room with ready participants
    room_manager.rooms.clear()
    user_data = {
        "id": "user-789",
        "socketId": "socket-789",
        "anonymousName": "Ready User",
        "role": "speaker",
        "isReady": True,
        "joinedAt": datetime.now().isoformat()
    }
    room_manager.add_user_to_room(room_id, user_data)
    
    # Mock all the required functions
    with patch('src.socket.socket_handlers.generate_discussion_topic', new_callable=AsyncMock) as mock_topic:
        with patch('src.socket.socket_handlers.db.save_room', new_callable=AsyncMock) as mock_save_room:
            with patch('src.socket.socket_handlers.db.save_participant', new_callable=AsyncMock) as mock_save_participant:
                with patch('src.socket.socket_handlers.db.record_topic_usage', new_callable=AsyncMock) as mock_record_topic:
                    with patch('src.socket.socket_handlers.db.update_room', new_callable=AsyncMock) as mock_update_room:
                        with patch.object(agent_service, 'create_room_agents', new_callable=AsyncMock) as mock_create_agents:
                            with patch('src.socket.socket_handlers.start_turn_timer', new_callable=AsyncMock) as mock_timer:
                                # Setup mocks
                                mock_topic.return_value = {"title": "Test Topic", "description": "Test Description"}
                                mock_create_agents.return_value = {
                                    "facilitator": "facilitator-agent-456",
                                    "english": "english-agent-456"
                                }
                                
                                # Import and call the function
                                from src.socket.socket_handlers import check_and_start_discussion
                                await check_and_start_discussion(mock_sio, room_id, active_rooms)
                                
                                # Verify agents were created
                                mock_create_agents.assert_called_once_with(room_id, {"title": "Test Topic", "description": "Test Description"})
                                
                                # Verify room was updated with facilitator agent ID
                                mock_update_room.assert_called()
                                update_calls = mock_update_room.call_args_list
                                agent_update_call = next((call for call in update_calls 
                                                        if "agent_id" in call[0][1]), None)
                                assert agent_update_call is not None
                                assert agent_update_call[0][1]["agent_id"] == "facilitator-agent-456"


@pytest.mark.asyncio
async def test_agent_creation_failure_handling():
    """Test that discussion continues even if agent creation fails"""
    room_id = "test-room-agent-fail"
    active_rooms = {}
    
    # Mock socket.io server
    mock_sio = MagicMock()
    mock_sio.emit = AsyncMock()
    
    # Setup room with ready participants
    room_manager.rooms.clear()
    user_data = {
        "id": "user-999",
        "socketId": "socket-999",
        "anonymousName": "Ready User",
        "role": "speaker",
        "isReady": True,
        "joinedAt": datetime.now().isoformat()
    }
    room_manager.add_user_to_room(room_id, user_data)
    
    # Mock all the required functions
    with patch('src.socket.socket_handlers.generate_discussion_topic', new_callable=AsyncMock) as mock_topic:
        with patch('src.socket.socket_handlers.db.save_room', new_callable=AsyncMock) as mock_save_room:
            with patch('src.socket.socket_handlers.db.save_participant', new_callable=AsyncMock) as mock_save_participant:
                with patch('src.socket.socket_handlers.db.record_topic_usage', new_callable=AsyncMock) as mock_record_topic:
                    with patch('src.socket.socket_handlers.db.update_room', new_callable=AsyncMock) as mock_update_room:
                        with patch.object(agent_service, 'create_room_agents', new_callable=AsyncMock) as mock_create_agents:
                            with patch('src.socket.socket_handlers.start_turn_timer', new_callable=AsyncMock) as mock_timer:
                                # Setup mocks - agent creation fails
                                mock_topic.return_value = {"title": "Test Topic", "description": "Test Description"}
                                mock_create_agents.side_effect = Exception("Agent creation failed")
                                
                                # Import and call the function - should not crash
                                from src.socket.socket_handlers import check_and_start_discussion
                                await check_and_start_discussion(mock_sio, room_id, active_rooms)
                                
                                # Verify discussion still started despite agent failure
                                mock_sio.emit.assert_called()
                                discussion_started_calls = [call for call in mock_sio.emit.call_args_list 
                                                          if call[0][0] == "discussion-started"]
                                assert len(discussion_started_calls) > 0


@pytest.mark.asyncio
async def test_transcript_received_error_handling(mock_sio):
    """Test transcript_received handler error handling"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    socket_id = "error-socket"
    
    # Mock sio.rooms to return no room (error condition)
    mock_sio.rooms.return_value = [socket_id]  # Only socket's own room
    
    # Get the handler
    transcript_handler = None
    for call in mock_sio.event.call_args_list:
        if call[0] and hasattr(call[0][0], '__name__'):
            if call[0][0].__name__ == 'transcript_received':
                transcript_handler = call[0][0]
                break
    
    assert transcript_handler is not None, "transcript_received handler not found"
    
    # Call the handler with invalid data - should handle gracefully
    await transcript_handler(socket_id, {"text": "test"})
    
    # Should not crash and should not emit any events
    # (or at least handle the error gracefully)


@pytest.mark.asyncio
async def test_facilitator_response_error_handling(mock_sio):
    """Test request_facilitator_response handler error handling"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    socket_id = "error-socket"
    
    # Mock sio.rooms to return no room (error condition)
    mock_sio.rooms.return_value = [socket_id]  # Only socket's own room
    
    # Get the handler
    facilitator_handler = None
    for call in mock_sio.event.call_args_list:
        if call[0] and hasattr(call[0][0], '__name__'):
            if call[0][0].__name__ == 'request_facilitator_response':
                facilitator_handler = call[0][0]
                break
    
    assert facilitator_handler is not None, "request_facilitator_response handler not found"
    
    # Call the handler with no room - should handle gracefully
    await facilitator_handler(socket_id, {})
    
    # Should not crash


@pytest.mark.asyncio
async def test_get_instant_feedback_error_handling(mock_sio):
    """Test get_instant_feedback handler error handling"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    socket_id = "error-socket"
    
    # Mock sio.rooms to return no room (error condition)
    mock_sio.rooms.return_value = [socket_id]  # Only socket's own room
    
    # Get the handler
    feedback_handler = None
    for call in mock_sio.event.call_args_list:
        if call[0] and hasattr(call[0][0], '__name__'):
            if call[0][0].__name__ == 'get_instant_feedback':
                feedback_handler = call[0][0]
                break
    
    assert feedback_handler is not None, "get_instant_feedback handler not found"
    
    # Call the handler with no room - should handle gracefully
    await feedback_handler(socket_id, {"participantId": "test-user"})
    
    # Should not crash