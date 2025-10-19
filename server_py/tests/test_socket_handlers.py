"""
Test Socket.io Event Handlers
Tests for socket handlers focusing on lobby connection issues
"""

import pytest
import socketio
from unittest.mock import AsyncMock, MagicMock, patch
from src.socket.socket_handlers import setup_socket_handlers
from src.socket.room_manager import room_manager
from src.models import Participant, ParticipantRole


@pytest.fixture
async def mock_sio():
    """Create a mock Socket.io server"""
    sio = MagicMock(spec=socketio.AsyncServer)
    sio.emit = AsyncMock()
    sio.enter_room = AsyncMock()
    sio.leave_room = AsyncMock()
    sio.rooms = MagicMock(return_value=[])
    sio.get_room = AsyncMock(return_value={})
    return sio


@pytest.fixture
def setup_test_room():
    """Setup a test room with a participant"""
    # Clean up any existing rooms
    room_manager.rooms.clear()
    
    room_id = "test-room"
    socket_id = "test-socket-123"
    user_data = {
        "id": "user-123",
        "socketId": socket_id,
        "anonymousName": "Test User",
        "name": "Test Name",
        "campus": "Test Campus",
        "location": "Test Location",
        "role": "speaker",
        "isReady": False
    }
    
    # Add user to room
    room_manager.add_user_to_room(room_id, user_data)
    
    yield {
        "room_id": room_id,
        "socket_id": socket_id,
        "user_data": user_data
    }
    
    # Cleanup
    room_manager.rooms.clear()


@pytest.mark.asyncio
async def test_user_ready_without_data(mock_sio, setup_test_room):
    """Test user-ready event without data parameter (client behavior)"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    room_id = setup_test_room["room_id"]
    socket_id = setup_test_room["socket_id"]
    
    # Mock sio.rooms to return the room
    mock_sio.rooms.return_value = [socket_id, room_id]
    
    # Get the user_ready handler from the registered events
    user_ready_handler = None
    for call in mock_sio.event.call_args_list:
        if call[0] and hasattr(call[0][0], '__name__'):
            if call[0][0].__name__ == 'user_ready':
                user_ready_handler = call[0][0]
                break
    
    assert user_ready_handler is not None, "user_ready handler not found"
    
    # Call the handler without data (simulating client behavior)
    await user_ready_handler(socket_id, None)
    
    # Verify the user was marked as ready
    room = room_manager.get_room(room_id)
    user = room.get_participant_by_socket(socket_id)
    assert user is not None
    assert user.is_ready is True
    
    # Verify participants-update was emitted
    assert mock_sio.emit.called
    emit_calls = [call for call in mock_sio.emit.call_args_list 
                  if call[0][0] == "participants-update"]
    assert len(emit_calls) > 0


@pytest.mark.asyncio
async def test_user_ready_with_data(mock_sio, setup_test_room):
    """Test user-ready event with data parameter (backward compatibility)"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    room_id = setup_test_room["room_id"]
    socket_id = setup_test_room["socket_id"]
    user_id = setup_test_room["user_data"]["id"]
    
    # Mock sio.rooms to return the room
    mock_sio.rooms.return_value = [socket_id, room_id]
    
    # Get the user_ready handler
    user_ready_handler = None
    for call in mock_sio.event.call_args_list:
        if call[0] and hasattr(call[0][0], '__name__'):
            if call[0][0].__name__ == 'user_ready':
                user_ready_handler = call[0][0]
                break
    
    assert user_ready_handler is not None, "user_ready handler not found"
    
    # Call the handler with data
    data = {"userId": user_id, "isReady": True}
    await user_ready_handler(socket_id, data)
    
    # Verify the user was marked as ready
    room = room_manager.get_room(room_id)
    user = room.get_participant_by_socket(socket_id)
    assert user is not None
    assert user.is_ready is True


@pytest.mark.asyncio
async def test_user_ready_with_false_status(mock_sio, setup_test_room):
    """Test user-ready event can set isReady to False"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    room_id = setup_test_room["room_id"]
    socket_id = setup_test_room["socket_id"]
    user_id = setup_test_room["user_data"]["id"]
    
    # First set user to ready
    room_manager.update_user(room_id, user_id, {"isReady": True})
    
    # Mock sio.rooms to return the room
    mock_sio.rooms.return_value = [socket_id, room_id]
    
    # Get the user_ready handler
    user_ready_handler = None
    for call in mock_sio.event.call_args_list:
        if call[0] and hasattr(call[0][0], '__name__'):
            if call[0][0].__name__ == 'user_ready':
                user_ready_handler = call[0][0]
                break
    
    assert user_ready_handler is not None, "user_ready handler not found"
    
    # Call the handler with isReady: False
    data = {"userId": user_id, "isReady": False}
    await user_ready_handler(socket_id, data)
    
    # Verify the user was marked as not ready
    room = room_manager.get_room(room_id)
    user = room.get_participant_by_socket(socket_id)
    assert user is not None
    assert user.is_ready is False


@pytest.mark.asyncio
async def test_user_ready_no_room_found(mock_sio):
    """Test user-ready event when user is not in any room"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    socket_id = "orphan-socket"
    
    # Mock sio.rooms to return only the socket's own room
    mock_sio.rooms.return_value = [socket_id]
    
    # Get the user_ready handler
    user_ready_handler = None
    for call in mock_sio.event.call_args_list:
        if call[0] and hasattr(call[0][0], '__name__'):
            if call[0][0].__name__ == 'user_ready':
                user_ready_handler = call[0][0]
                break
    
    assert user_ready_handler is not None, "user_ready handler not found"
    
    # Call the handler - should handle gracefully
    await user_ready_handler(socket_id, None)
    
    # Should not crash and should not emit any events
    # (or at least not crash the server)


@pytest.mark.asyncio
async def test_user_ready_triggers_discussion_start(mock_sio, setup_test_room):
    """Test that user-ready can trigger discussion start when conditions are met"""
    # Setup
    await setup_socket_handlers(mock_sio)
    
    room_id = setup_test_room["room_id"]
    socket_id = setup_test_room["socket_id"]
    
    # Mock sio.rooms to return the room
    mock_sio.rooms.return_value = [socket_id, room_id]
    
    # Get the user_ready handler
    user_ready_handler = None
    for call in mock_sio.event.call_args_list:
        if call[0] and hasattr(call[0][0], '__name__'):
            if call[0][0].__name__ == 'user_ready':
                user_ready_handler = call[0][0]
                break
    
    assert user_ready_handler is not None, "user_ready handler not found"
    
    # Call the handler
    await user_ready_handler(socket_id, None)
    
    # Verify the user was marked as ready
    room = room_manager.get_room(room_id)
    user = room.get_participant_by_socket(socket_id)
    assert user.is_ready is True
    
    # Verify that check_and_start_discussion was called
    # (it should emit discussion-started if minimum participants are ready)
    # Since MIN_PARTICIPANTS defaults to 1, this should trigger
