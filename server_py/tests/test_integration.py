"""
Integration tests for database operations with socket handlers
"""

import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_room_creation_with_participants(test_db):
    """Test creating a room with participants"""
    # Create a room
    room_data = {
        "room_id": "test-room-integration",
        "room_id": "test-room",
        "room_name": "Test Room",
        "topic": {
            "title": "Integration Test Topic",
            "category": "Technology"
        },
        "participantCount": 2,
        "startedAt": datetime.now().isoformat(),
        "endedAt": None,
        "durationSeconds": None,
        "roundsCompleted": 0,
        "status": "active",
        "cefr_level": 3
    }
    
    room_id = await test_db.save_room(room_data)
    assert room_id is not None
    
    # Add participants to the room
    participants_data = [
        {
            "user_id": "user-1",
            "room_id": "test-room-integration",
            "anonymousName": "Happy Tiger",
            "campus": "Campus A",
            "location": "Location A",
            "joinedAt": datetime.now().isoformat(),
            "leftAt": None,
            "speakingTimeSeconds": 0
        },
        {
            "user_id": "user-2",
            "room_id": "test-room-integration",
            "anonymousName": "Clever Eagle",
            "campus": "Campus B",
            "location": "Location B",
            "joinedAt": datetime.now().isoformat(),
            "leftAt": None,
            "speakingTimeSeconds": 0
        }
    ]
    
    for participant in participants_data:
        result = await test_db.save_participant(participant)
        assert result is not None
    
    # Verify room was saved correctly
    rooms = await test_db.get_room_analytics(limit=10)
    assert len(rooms) > 0
    
    # Find our room
    our_room = next((s for s in rooms if s["room_id"] == "test-room-integration"), None)
    assert our_room is not None
    assert our_room["room_name"] == "Test Room"
    assert our_room["recorded_participants"] == 2


@pytest.mark.asyncio
async def test_cefr_level_mapping(test_db):
    """Test that CEFR levels are correctly stored"""
    cefr_levels = {
        'A1': 1,
        'A2': 2,
        'B1': 3,
        'B2': 4,
        'C1': 5,
        'C2': 6
    }
    
    for cefr_str, cefr_int in cefr_levels.items():
        room_data = {
            "room_id": f"test-room-cefr-{cefr_str}",
            "room_id": f"test-room-{cefr_str}",
            "room_name": f"Test Room {cefr_str}",
            "topic": {
                "title": f"Test Topic {cefr_str}",
                "category": "Education"
            },
            "participantCount": 1,
            "startedAt": datetime.now().isoformat(),
            "status": "active",
            "cefr_level": cefr_int
        }
        
        result = await test_db.save_room(room_data)
        assert result is not None
    
    # Verify all rooms were saved
    rooms = await test_db.get_room_analytics(limit=10)
    assert len(rooms) >= 6


@pytest.mark.asyncio
async def test_room_metadata_handling(test_db):
    """Test that room metadata is correctly stored in rooms"""
    room_data = {
        "room_id": "test-room-metadata",
        "room_id": "education-b1",
        "room_name": "Education Discussion",
        "topic": {
            "title": "Educational Methods",
            "category": "education"
        },
        "participantCount": 4,
        "startedAt": datetime.now().isoformat(),
        "status": "active",
        "cefr_level": 3  # B1
    }
    
    result = await test_db.save_room(room_data)
    assert result is not None
    
    # Retrieve and verify
    rooms = await test_db.get_room_analytics(limit=10)
    our_room = next((s for s in rooms if s["room_id"] == "test-room-metadata"), None)
    
    assert our_room is not None
    assert our_room["room_name"] == "Education Discussion"
    assert our_room["topic_category"] == "education"
