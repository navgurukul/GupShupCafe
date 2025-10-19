"""
Tests for API routes
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_api_health_endpoint(client):
    """Test API health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_topics(client):
    """Test getting all topics"""
    response = client.get("/api/topics")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert len(data["data"]) > 0


@pytest.mark.asyncio
async def test_generate_topic(client):
    """Test generating topic"""
    response = client.get("/api/topics/generate")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "title" in data["data"]


def test_get_topic_by_category(client):
    """Test getting topic by category"""
    response = client.get("/api/topics/category/Education")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["category"] == "Education"


def test_get_topic_by_invalid_category(client):
    """Test getting topic by invalid category"""
    response = client.get("/api/topics/category/InvalidCategory")
    assert response.status_code == 404


def test_get_config(client):
    """Test getting configuration"""
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "minParticipants" in data["data"]
    assert "maxParticipants" in data["data"]


def test_submit_feedback(client):
    """Test submitting feedback"""
    feedback = {
        "rating": 5,
        "comment": "Great platform!",
        "room_id": "test-room-123"
    }
    response = client.post("/api/feedback", json=feedback)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_get_room_state(client):
    """Test getting room state"""
    response = client.get("/api/room/test-room/state")
    assert response.status_code == 200
    data = response.json()
    assert "participants" in data
    assert "discussion" in data
