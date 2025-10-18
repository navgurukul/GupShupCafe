"""
Test configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator
import os
import tempfile

# Set test environment
os.environ["PYTHON_ENV"] = "testing"
os.environ["DATABASE_URL"] = ":memory:"


@pytest.fixture(scope="room")
def event_loop():
    """Create an instance of the default event loop for the test room."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db():
    """Create a test database"""
    from src.database.database import Database
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
        db_path = tmp_file.name
    
    db = Database()
    await db.initialize(db_path)
    
    yield db
    
    await db.close()
    # Clean up
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def sample_topic():
    """Sample topic for testing"""
    return {
        "title": "Test Topic",
        "description": "This is a test topic",
        "category": "Technology",
        "questions": [
            "Question 1?",
            "Question 2?",
            "Question 3?"
        ]
    }


@pytest.fixture
def sample_room():
    """Sample room data for testing"""
    return {
        "id": "test-room-123",
        "roomId": "test-room",
        "topic": {
            "title": "Test Topic",
            "category": "Technology"
        },
        "participantCount": 2,
        "startedAt": "2024-01-01T00:00:00",
        "endedAt": None,
        "durationSeconds": None,
        "roundsCompleted": 0
    }


@pytest.fixture
def sample_participant():
    """Sample participant data for testing"""
    return {
        "id": "participant-123",
        "roomId": "test-room-123",
        "userId": "user-123",
        "anonymousName": "Friendly Fox",
        "campus": "Test Campus",
        "location": "Test Location",
        "joinedAt": "2024-01-01T00:00:00",
        "leftAt": None,
        "speakingTimeSeconds": 0
    }
