"""
Integration tests for database operations with socket handlers
"""

import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_session_creation_with_participants(test_db):
    """Test creating a session with participants"""
    # Create a session
    session_data = {
        "session_id": "test-session-integration",
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
        "crf_level": 3
    }
    
    session_id = await test_db.save_session(session_data)
    assert session_id is not None
    
    # Add participants to the session
    participants_data = [
        {
            "user_id": "user-1",
            "session_id": "test-session-integration",
            "anonymousName": "Happy Tiger",
            "campus": "Campus A",
            "location": "Location A",
            "joinedAt": datetime.now().isoformat(),
            "leftAt": None,
            "speakingTimeSeconds": 0
        },
        {
            "user_id": "user-2",
            "session_id": "test-session-integration",
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
    
    # Verify session was saved correctly
    sessions = await test_db.get_session_analytics(limit=10)
    assert len(sessions) > 0
    
    # Find our session
    our_session = next((s for s in sessions if s["session_id"] == "test-session-integration"), None)
    assert our_session is not None
    assert our_session["room_name"] == "Test Room"
    assert our_session["recorded_participants"] == 2


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
        session_data = {
            "session_id": f"test-session-cefr-{cefr_str}",
            "room_id": f"test-room-{cefr_str}",
            "room_name": f"Test Room {cefr_str}",
            "topic": {
                "title": f"Test Topic {cefr_str}",
                "category": "Education"
            },
            "participantCount": 1,
            "startedAt": datetime.now().isoformat(),
            "status": "active",
            "crf_level": cefr_int
        }
        
        result = await test_db.save_session(session_data)
        assert result is not None
    
    # Verify all sessions were saved
    sessions = await test_db.get_session_analytics(limit=10)
    assert len(sessions) >= 6


@pytest.mark.asyncio
async def test_room_metadata_handling(test_db):
    """Test that room metadata is correctly stored in sessions"""
    session_data = {
        "session_id": "test-session-metadata",
        "room_id": "education-b1",
        "room_name": "Education Discussion",
        "topic": {
            "title": "Educational Methods",
            "category": "education"
        },
        "participantCount": 4,
        "startedAt": datetime.now().isoformat(),
        "status": "active",
        "crf_level": 3  # B1
    }
    
    result = await test_db.save_session(session_data)
    assert result is not None
    
    # Retrieve and verify
    sessions = await test_db.get_session_analytics(limit=10)
    our_session = next((s for s in sessions if s["session_id"] == "test-session-metadata"), None)
    
    assert our_session is not None
    assert our_session["room_name"] == "Education Discussion"
    assert our_session["topic_category"] == "education"
