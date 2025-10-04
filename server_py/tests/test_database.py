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
async def test_save_session(test_db, sample_session):
    """Test saving a session"""
    result = await test_db.save_session(sample_session)
    assert result is not None


@pytest.mark.asyncio
async def test_save_participant(test_db, sample_participant):
    """Test saving a participant"""
    # First save the session
    session_data = {
        "id": sample_participant["sessionId"],
        "roomId": "test-room",
        "topic": {"title": "Test", "category": "Test"},
        "participantCount": 1,
        "startedAt": datetime.now().isoformat(),
        "endedAt": None,
        "durationSeconds": None,
        "roundsCompleted": 0
    }
    await test_db.save_session(session_data)
    
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
async def test_get_session_analytics(test_db, sample_session):
    """Test getting session analytics"""
    # Save a session first
    await test_db.save_session(sample_session)
    
    # Get analytics
    sessions = await test_db.get_session_analytics(limit=10)
    assert len(sessions) > 0
    assert sessions[0]["id"] == sample_session["id"]


@pytest.mark.asyncio
async def test_get_server_stats(test_db):
    """Test getting server statistics"""
    stats = await test_db.get_server_stats()
    
    assert "totalSessions" in stats
    assert "totalParticipants" in stats
    assert "avgSessionDuration" in stats
    assert "avgParticipantsPerSession" in stats
    assert "topCategories" in stats


@pytest.mark.asyncio
async def test_update_session_end(test_db, sample_session):
    """Test updating session end data"""
    # Save a session first
    await test_db.save_session(sample_session)
    
    # Update end data
    update_data = {
        "id": sample_session["id"],
        "endedAt": datetime.now().isoformat(),
        "durationSeconds": 120,
        "roundsCompleted": 2,
        "participantCount": 3
    }
    
    result = await test_db.update_session_end(update_data)
    assert result == 1  # One row updated
