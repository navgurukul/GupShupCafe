"""
Tests for room manager
"""

import pytest
from src.socket.room_manager import RoomManager
from datetime import datetime


@pytest.fixture
def room_manager():
    """Create a fresh room manager for each test"""
    return RoomManager()


@pytest.fixture
def sample_user():
    """Sample user data"""
    return {
        "id": "user-123",
        "socketId": "socket-123",
        "anonymousName": "Friendly Fox",
        "name": "Test User",
        "campus": "Test Campus",
        "location": "Test Location",
        "role": "speaker",
        "isReady": False,
        "joinedAt": datetime.now().isoformat()
    }


def test_get_room(room_manager):
    """Test getting or creating a room"""
    room = room_manager.get_room("test-room")
    
    assert room is not None
    assert room.room_code == "test-room"
    assert hasattr(room, "participants")
    assert hasattr(room, "status")
    assert len(room.participants) == 0


def test_add_user_to_room(room_manager, sample_user):
    """Test adding user to room"""
    room_manager.add_user_to_room("test-room", sample_user)
    
    room = room_manager.get_room("test-room")
    assert len(room.participants) == 1
    assert room.participants[0].id == sample_user["id"]


def test_remove_user_from_room(room_manager, sample_user):
    """Test removing user from room"""
    room_manager.add_user_to_room("test-room", sample_user)
    room_manager.remove_user_from_room("test-room", sample_user["id"])
    
    # Room should be cleaned up when empty - check before calling get_room
    # because get_room will recreate it
    assert "test-room" not in room_manager.rooms


def test_update_user(room_manager, sample_user):
    """Test updating user data"""
    room_manager.add_user_to_room("test-room", sample_user)
    room_manager.update_user("test-room", sample_user["id"], {"isReady": True})
    
    room = room_manager.get_room("test-room")
    assert room.participants[0].is_ready is True


def test_get_room_participants(room_manager, sample_user):
    """Test getting room participants"""
    room_manager.add_user_to_room("test-room", sample_user)
    
    participants = room_manager.get_room_participants("test-room")
    assert len(participants) == 1
    assert participants[0]["id"] == sample_user["id"]
    assert "anonymousName" in participants[0]
    assert "isReady" in participants[0]


def test_change_user_role(room_manager, sample_user):
    """Test changing user role"""
    room_manager.add_user_to_room("test-room", sample_user)
    
    success = room_manager.change_user_role("test-room", sample_user["id"], "listener")
    assert success is True
    
    room = room_manager.get_room("test-room")
    assert room.participants[0].role.value == "listener"


def test_change_invalid_role(room_manager, sample_user):
    """Test changing to invalid role"""
    room_manager.add_user_to_room("test-room", sample_user)
    
    success = room_manager.change_user_role("test-room", sample_user["id"], "invalid")
    assert success is False


def test_get_role_stats(room_manager):
    """Test getting role statistics"""
    # Add speakers
    for i in range(3):
        room_manager.add_user_to_room("test-room", {
            "id": f"speaker-{i}",
            "socketId": f"socket-{i}",
            "anonymousName": f"Speaker {i}",
            "role": "speaker",
            "isReady": False,
            "joinedAt": datetime.now().isoformat()
        })
    
    # Add listeners
    for i in range(2):
        room_manager.add_user_to_room("test-room", {
            "id": f"listener-{i}",
            "socketId": f"socket-l-{i}",
            "anonymousName": f"Listener {i}",
            "role": "listener",
            "isReady": False,
            "joinedAt": datetime.now().isoformat()
        })
    
    stats = room_manager.get_role_stats("test-room")
    assert stats["totalParticipants"] == 5
    assert stats["speakers"] == 3
    assert stats["listeners"] == 2


def test_can_become_speaker(room_manager):
    """Test checking if user can become speaker"""
    # Add 6 speakers (max)
    for i in range(6):
        room_manager.add_user_to_room("test-room", {
            "id": f"speaker-{i}",
            "socketId": f"socket-{i}",
            "anonymousName": f"Speaker {i}",
            "role": "speaker",
            "isReady": False,
            "joinedAt": datetime.now().isoformat()
        })
    
    # Should not be able to add more
    can_add = room_manager.can_become_speaker("test-room", max_speakers=6)
    assert can_add is False
    
    # Remove one
    room_manager.remove_user_from_room("test-room", "speaker-0")
    
    # Should be able to add now
    can_add = room_manager.can_become_speaker("test-room", max_speakers=6)
    assert can_add is True


def test_get_discussion_state(room_manager, sample_user):
    """Test getting discussion state"""
    room_manager.add_user_to_room("test-room", sample_user)
    
    state = room_manager.get_discussion_state("test-room")
    assert "active" in state
    assert "topic" in state
    assert "currentSpeaker" in state
    assert state["participantCount"] == 1


def test_get_all_rooms(room_manager):
    """Test getting all rooms"""
    room_manager.add_user_to_room("room-1", {
        "id": "user-1",
        "socketId": "socket-1",
        "anonymousName": "User 1",
        "isReady": False,
        "joinedAt": datetime.now().isoformat()
    })
    
    room_manager.add_user_to_room("room-2", {
        "id": "user-2",
        "socketId": "socket-2",
        "anonymousName": "User 2",
        "isReady": False,
        "joinedAt": datetime.now().isoformat()
    })
    
    rooms = room_manager.get_all_rooms()
    assert len(rooms) == 2


def test_get_stats(room_manager):
    """Test getting server stats"""
    room_manager.add_user_to_room("room-1", {
        "id": "user-1",
        "socketId": "socket-1",
        "anonymousName": "User 1",
        "isReady": False,
        "joinedAt": datetime.now().isoformat()
    })
    
    stats = room_manager.get_stats()
    assert stats["totalRooms"] == 1
    assert stats["totalParticipants"] == 1
    assert "timestamp" in stats
