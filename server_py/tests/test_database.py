"""
Tests for database operations
"""

import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_database_initialization(test_db):
    """Test database initialization"""
    assert test_db.db is not None


@pytest.mark.asyncio
async def test_save_room(test_db, sample_room):
    """Test saving a room"""
    result = await test_db.save_room(sample_room)
    assert result is not None


@pytest.mark.asyncio
async def test_save_participant(test_db, sample_participant):
    """Test saving a participant"""
    # First save the room
    room_data = {
        "id": sample_participant["roomId"],
        "roomId": "test-room",
        "topic": {"title": "Test", "category": "Test"},
        "participantCount": 1,
        "startedAt": datetime.now().isoformat(),
        "endedAt": None,
        "durationSeconds": None,
        "roundsCompleted": 0
    }
    await test_db.save_room(room_data)
    
    # Now save participant
    result = await test_db.save_participant(sample_participant)
    assert result is not None


@pytest.mark.asyncio
async def test_record_topic_usage(test_db, sample_topic):
    """Test recording topic usage"""
    # First use
    await test_db.record_topic_usage(sample_topic)
    
    # Get topics
    topics = await test_db.get_topic_analytics()
    assert len(topics) > 0
    assert topics[0]["title"] == sample_topic["title"]
    assert topics[0]["used_count"] == 1
    
    # Second use - should increment
    await test_db.record_topic_usage(sample_topic)
    topics = await test_db.get_topic_analytics()
    assert topics[0]["used_count"] == 2


@pytest.mark.asyncio
async def test_get_room_analytics(test_db, sample_room):
    """Test getting room analytics"""
    # Save a room first
    await test_db.save_room(sample_room)
    
    # Get analytics
    rooms = await test_db.get_room_analytics(limit=10)
    assert len(rooms) > 0
    assert rooms[0]["room_id"] == sample_room["id"]


@pytest.mark.asyncio
async def test_get_server_stats(test_db):
    """Test getting server statistics"""
    stats = await test_db.get_server_stats()
    
    assert "totalRooms" in stats
    assert "totalParticipants" in stats
    assert "avgRoomDuration" in stats
    assert "avgParticipantsPerRoom" in stats
    assert "topCategories" in stats


@pytest.mark.asyncio
async def test_update_room_end(test_db, sample_room):
    """Test updating room end data"""
    # Save a room first
    await test_db.save_room(sample_room)
    
    # Update end data
    update_data = {
        "id": sample_room["id"],
        "endedAt": datetime.now().isoformat(),
        "durationSeconds": 120,
        "roundsCompleted": 2,
        "participantCount": 3
    }
    
    result = await test_db.update_room_end(update_data)
    assert result == 1  # One row updated
