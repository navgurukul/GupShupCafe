"""
Tests for API routes - Updated for current repository status
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
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
    assert data["name"] == "AI Roundtable API"


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "AI Roundtable API"


def test_api_health_endpoint(client):
    """Test API health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "AI Roundtable API"


def test_get_topics(client):
    """Test getting all fallback topics"""
    response = client.get("/api/topics")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "count" in data
    assert len(data["data"]) > 0
    # Verify topic structure
    topic = data["data"][0]
    assert "title" in topic
    assert "category" in topic


@pytest.mark.asyncio
async def test_generate_topic(client):
    """Test generating new discussion topic"""
    response = client.get("/api/topics/generate")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "title" in data["data"]
    assert "category" in data["data"]


def test_get_topic_by_category_valid(client):
    """Test getting topic by valid category"""
    response = client.get("/api/topics/category/Education")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["category"] == "Education"


def test_get_topic_by_category_technology(client):
    """Test getting topic by Technology category"""
    response = client.get("/api/topics/category/Technology")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["category"] == "Technology"


def test_get_topic_by_invalid_category(client):
    """Test getting topic by invalid category returns 404"""
    response = client.get("/api/topics/category/NonExistentCategory")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Topic not found" in data["detail"]


def test_get_config(client):
    """Test getting public configuration"""
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    
    config = data["data"]
    assert "minParticipants" in config
    assert "maxParticipants" in config
    assert "defaultSpeakingTime" in config
    assert "features" in config
    
    features = config["features"]
    assert "aiTopics" in features
    assert "analytics" in features
    assert "feedback" in features
    
    # Verify default values
    assert config["minParticipants"] == 1
    assert config["maxParticipants"] == 6
    assert config["defaultSpeakingTime"] == 60


@patch.dict(os.environ, {"HUGGINGFACE_API_KEY": "test_key"})
def test_get_config_with_ai_features(client):
    """Test config with AI features enabled"""
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    config = data["data"]
    assert config["features"]["aiTopics"] is True


@patch.dict(os.environ, {"MIN_PARTICIPANTS": "2", "MAX_PARTICIPANTS": "8", "DEFAULT_SPEAKING_TIME": "90"})
def test_get_config_custom_values(client):
    """Test config with custom environment values"""
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    config = data["data"]
    assert config["minParticipants"] == 2
    assert config["maxParticipants"] == 8
    assert config["defaultSpeakingTime"] == 90


def test_get_config_error_handling(client):
    """Test config endpoint error handling"""
    with patch('src.api.routes.os.getenv', side_effect=Exception("Environment error")):
        response = client.get("/api/config")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert data["detail"]["success"] is False


def test_topics_endpoint_error_handling(client):
    """Test topics endpoint error handling"""
    with patch('src.api.routes.get_all_fallback_topics', side_effect=Exception("Database error")):
        response = client.get("/api/topics")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to retrieve topics" in data["detail"]


def test_generate_topic_error_handling(client):
    """Test generate topic endpoint error handling"""
    with patch('src.api.routes.generate_discussion_topic', side_effect=Exception("AI service error")):
        response = client.get("/api/topics/generate")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to generate topic" in data["detail"]


def test_topic_by_category_error_handling(client):
    """Test topic by category endpoint error handling"""
    with patch('src.api.routes.get_topic_by_category', side_effect=Exception("Database error")):
        response = client.get("/api/topics/category/Education")
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to retrieve topic" in data["detail"]


def test_topic_by_category_not_found(client):
    """Test topic by category when topic is None"""
    with patch('src.api.routes.get_topic_by_category', return_value=None):
        response = client.get("/api/topics/category/Education")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Topic not found for this category" in data["detail"]


# Test for endpoints that might be added in the future
def test_nonexistent_endpoint(client):
    """Test accessing non-existent endpoint"""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


def test_invalid_method(client):
    """Test using invalid HTTP method"""
    response = client.post("/api/topics")
    assert response.status_code == 405  # Method Not Allowed
