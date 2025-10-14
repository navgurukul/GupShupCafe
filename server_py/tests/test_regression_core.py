"""
Regression Tests for Core Backend Features
Tests critical functionality and edge cases to prevent regressions
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import asyncio
from main import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


class TestAnalyticsEndpoints:
    """Test suite for analytics endpoints"""

    @pytest.mark.skip(reason="Analytics endpoints require initialized database - tested separately")
    def test_analytics_sessions_empty_database(self, client):
        """Test session analytics with empty database"""
        response = client.get("/api/analytics/sessions?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert data["count"] >= 0

    @pytest.mark.skip(reason="Analytics endpoints require initialized database - tested separately")
    def test_analytics_sessions_limit_parameter(self, client):
        """Test session analytics respects limit parameter"""
        # Request only 3
        response = client.get("/api/analytics/sessions?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"], list)

    def test_analytics_sessions_invalid_limit(self, client):
        """Test analytics with invalid limit parameter"""
        response = client.get("/api/analytics/sessions?limit=0")
        assert response.status_code == 422  # Validation error
        
        response = client.get("/api/analytics/sessions?limit=101")
        assert response.status_code == 422  # Validation error

    @pytest.mark.skip(reason="Analytics endpoints require initialized database - tested separately")
    def test_analytics_topics_endpoint(self, client):
        """Test topic analytics endpoint"""
        response = client.get("/api/analytics/topics")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert "count" in data

    @pytest.mark.skip(reason="Analytics endpoints require initialized database - tested separately")
    def test_analytics_stats_comprehensive(self, client):
        """Test server stats endpoint returns all required fields"""
        response = client.get("/api/analytics/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        stats = data["data"]
        
        # Check all required stats fields
        assert "totalSessions" in stats
        assert "totalParticipants" in stats
        assert "avgSessionDuration" in stats
        assert "avgParticipantsPerSession" in stats
        assert "topCategories" in stats


class TestSessionLifecycle:
    """Test complete session lifecycle"""

    def test_create_and_retrieve_session(self, test_db):
        """Test creating and retrieving a session"""
        session_data = {
            "id": "lifecycle-session-1",
            "roomId": "test-room-lifecycle",
            "topic": {
                "title": "Test Topic",
                "category": "Technology"
            },
            "participantCount": 3,
            "startedAt": datetime.now().isoformat(),
            "endedAt": None,
            "durationSeconds": None,
            "roundsCompleted": 0
        }
        
        result = asyncio.run(test_db.save_session(session_data))
        assert result is not None
        
        # Retrieve and verify
        sessions = asyncio.run(test_db.get_session_analytics(limit=10))
        saved_session = next((s for s in sessions if s["id"] == session_data["id"]), None)
        assert saved_session is not None
        assert saved_session["id"] == session_data["id"]

    def test_update_session_end_data(self, test_db):
        """Test updating session with end data"""
        # Create session
        session_data = {
            "id": "lifecycle-session-2",
            "roomId": "test-room-end",
            "topic": {"title": "Test", "category": "Test"},
            "participantCount": 2,
            "startedAt": datetime.now().isoformat(),
            "endedAt": None,
            "durationSeconds": None,
            "roundsCompleted": 0
        }
        asyncio.run(test_db.save_session(session_data))
        
        # Update with end data
        end_data = {
            "id": session_data["id"],
            "endedAt": (datetime.now() + timedelta(minutes=10)).isoformat(),
            "durationSeconds": 600,
            "roundsCompleted": 3,
            "participantCount": 2
        }
        
        result = asyncio.run(test_db.update_session_end(end_data))
        assert result == 1  # One row updated

    def test_session_with_multiple_participants(self, test_db):
        """Test session with multiple participants joining"""
        session_id = "multi-participant-session"
        
        # Create session
        session_data = {
            "id": session_id,
            "roomId": "test-room-multi",
            "topic": {"title": "Multi-participant Test", "category": "Education"},
            "participantCount": 0,
            "startedAt": datetime.now().isoformat(),
            "endedAt": None,
            "durationSeconds": None,
            "roundsCompleted": 0
        }
        asyncio.run(test_db.save_session(session_data))
        
        # Add multiple participants
        for i in range(4):
            participant = {
                "id": f"participant-multi-{i}",
                "sessionId": session_id,
                "userId": f"user-multi-{i}",
                "anonymousName": f"User {i}",
                "campus": "Test Campus",
                "location": "Test Location",
                "joinedAt": datetime.now().isoformat(),
                "leftAt": None,
                "speakingTimeSeconds": 0
            }
            asyncio.run(test_db.save_participant(participant))


class TestParticipantManagement:
    """Test participant management functionality"""

    def test_save_participant_with_all_fields(self, test_db):
        """Test saving participant with all required fields"""
        session_data = {
            "id": "participant-test-session",
            "roomId": "test-room",
            "topic": {"title": "Test", "category": "Test"},
            "participantCount": 1,
            "startedAt": datetime.now().isoformat(),
            "endedAt": None,
            "durationSeconds": None,
            "roundsCompleted": 0
        }
        asyncio.run(test_db.save_session(session_data))
        
        participant = {
            "id": "participant-full-fields",
            "sessionId": "participant-test-session",
            "userId": "user-123",
            "anonymousName": "Clever Cat",
            "campus": "NavGurukul Bangalore",
            "location": "Bangalore, India",
            "joinedAt": datetime.now().isoformat(),
            "leftAt": None,
            "speakingTimeSeconds": 0
        }
        
        result = asyncio.run(test_db.save_participant(participant))
        assert result is not None

    def test_participant_speaking_time(self, test_db):
        """Test tracking participant speaking time"""
        session_data = {
            "id": "speaking-time-session",
            "roomId": "test-room",
            "topic": {"title": "Test", "category": "Test"},
            "participantCount": 1,
            "startedAt": datetime.now().isoformat(),
            "endedAt": None,
            "durationSeconds": None,
            "roundsCompleted": 0
        }
        asyncio.run(test_db.save_session(session_data))
        
        participant = {
            "id": "participant-speaking",
            "sessionId": "speaking-time-session",
            "userId": "speaker-user",
            "anonymousName": "Talkative Tiger",
            "campus": "Test Campus",
            "location": "Test Location",
            "joinedAt": datetime.now().isoformat(),
            "leftAt": None,
            "speakingTimeSeconds": 120  # 2 minutes
        }
        
        result = asyncio.run(test_db.save_participant(participant))
        assert result is not None


class TestTopicRecording:
    """Test topic recording and analytics"""

    def test_record_topic_multiple_times(self, test_db):
        """Test recording same topic multiple times increments count"""
        topic = {
            "title": "Repeated Topic",
            "description": "Testing multiple uses",
            "category": "Testing",
            "questions": ["Q1?", "Q2?", "Q3?"]
        }
        
        # Record 5 times
        for _ in range(5):
            asyncio.run(test_db.record_topic_usage(topic))
        
        # Check count
        topics = asyncio.run(test_db.get_topic_analytics())
        recorded = next((t for t in topics if t["title"] == topic["title"]), None)
        assert recorded is not None
        assert recorded["used_count"] == 5

    def test_record_different_topics(self, test_db):
        """Test recording multiple different topics"""
        topics = [
            {"title": "Topic A", "category": "Cat1", "description": "Desc A", "questions": []},
            {"title": "Topic B", "category": "Cat2", "description": "Desc B", "questions": []},
            {"title": "Topic C", "category": "Cat3", "description": "Desc C", "questions": []}
        ]
        
        for topic in topics:
            asyncio.run(test_db.record_topic_usage(topic))
        
        # Verify all recorded
        analytics = asyncio.run(test_db.get_topic_analytics())
        assert len(analytics) >= 3


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_get_room_state_structure(self, client):
        """Test room state endpoint returns expected structure"""
        # Test with a room that may not exist - it returns empty state
        response = client.get("/api/room/test-room-structure/state")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "participants" in data
            assert "discussion" in data

    def test_invalid_category_topic_request(self, client):
        """Test requesting topic with invalid category"""
        response = client.get("/api/topics/category/NonExistentCategory12345")
        assert response.status_code == 404

    def test_feedback_with_missing_fields(self, client):
        """Test submitting feedback with missing fields"""
        # Should still work as fields are optional
        feedback = {"rating": 5}
        response = client.post("/api/feedback", json=feedback)
        assert response.status_code == 200

    def test_feedback_with_empty_comment(self, client):
        """Test submitting feedback with empty comment"""
        feedback = {
            "rating": 4,
            "comment": "",
            "session_id": "test-session"
        }
        response = client.post("/api/feedback", json=feedback)
        assert response.status_code == 200

    def test_config_returns_valid_structure(self, client):
        """Test config endpoint returns expected structure"""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        config = data["data"]
        
        # Verify required fields
        assert "minParticipants" in config
        assert "maxParticipants" in config
        assert "defaultSpeakingTime" in config
        assert "features" in config
        
        # Verify features structure
        features = config["features"]
        assert "aiTopics" in features
        assert "analytics" in features
        assert "feedback" in features
        
        # Verify types
        assert isinstance(config["minParticipants"], int)
        assert isinstance(config["maxParticipants"], int)
        assert isinstance(features["analytics"], bool)


class TestIntegrationWorkflows:
    """Test complete workflows that involve multiple components"""

    def test_complete_discussion_workflow(self, client):
        """Test a complete discussion workflow through API"""
        # 1. Generate a topic
        topic_response = client.get("/api/topics/generate")
        assert topic_response.status_code == 200
        topic_data = topic_response.json()
        assert topic_data["success"] is True
        assert "data" in topic_data
        topic = topic_data["data"]
        assert "title" in topic
        
        # 2. Get topics list
        topics_response = client.get("/api/topics")
        assert topics_response.status_code == 200
        topics_data = topics_response.json()
        assert topics_data["success"] is True
        assert len(topics_data["data"]) > 0
        
        # 3. Get topic by category
        category_response = client.get("/api/topics/category/Education")
        assert category_response.status_code == 200
        
        # 4. Submit feedback
        feedback = {
            "rating": 5,
            "comment": "Great discussion!",
            "session_id": "workflow-session"
        }
        feedback_response = client.post("/api/feedback", json=feedback)
        assert feedback_response.status_code == 200
        
        # Note: Analytics endpoints require DB initialization, tested separately

    def test_concurrent_sessions_workflow(self, test_db):
        """Test handling multiple concurrent sessions"""
        # Create multiple sessions
        sessions = []
        for i in range(5):
            session = {
                "id": f"concurrent-session-{i}",
                "roomId": f"room-{i}",
                "topic": {"title": f"Topic {i}", "category": "Test"},
                "participantCount": 2,
                "startedAt": datetime.now().isoformat(),
                "endedAt": None,
                "durationSeconds": None,
                "roundsCompleted": 0
            }
            asyncio.run(test_db.save_session(session))
            sessions.append(session)
        
        # Verify all sessions exist
        analytics = asyncio.run(test_db.get_session_analytics(limit=10))
        concurrent_sessions = [s for s in analytics if s["id"].startswith("concurrent-")]
        assert len(concurrent_sessions) >= 5


# Import asyncio for async operations in tests


class TestTopicsEndpoints:
    """Test topic generation and retrieval endpoints"""

    def test_get_all_topics(self, client):
        """Test getting all available topics"""
        response = client.get("/api/topics")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) > 0
        assert "count" in data
        
        # Verify topic structure
        topic = data["data"][0]
        assert "title" in topic
        assert "category" in topic
        assert "description" in topic

    def test_generate_discussion_topic(self, client):
        """Test topic generation"""
        response = client.get("/api/topics/generate")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        topic = data["data"]
        assert "title" in topic
        assert "description" in topic
        assert "category" in topic

    def test_get_topic_by_valid_category(self, client):
        """Test getting topic by valid category"""
        categories = ["Education", "Technology", "Health", "Environment"]
        
        for category in categories:
            response = client.get(f"/api/topics/category/{category}")
            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True
                assert data["data"]["category"] == category
                break

    def test_get_topic_by_invalid_category(self, client):
        """Test getting topic by invalid category"""
        response = client.get("/api/topics/category/InvalidCategory123")
        assert response.status_code == 404


class TestConfigEndpoint:
    """Test configuration endpoint"""

    def test_config_structure(self, client):
        """Test configuration returns all required fields"""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        config = data["data"]
        assert isinstance(config["minParticipants"], int)
        assert isinstance(config["maxParticipants"], int)
        assert isinstance(config["defaultSpeakingTime"], int)
        
        # Verify value ranges
        assert 1 <= config["minParticipants"] <= config["maxParticipants"]
        assert config["maxParticipants"] <= 20
        assert config["defaultSpeakingTime"] > 0

    def test_config_features(self, client):
        """Test configuration features field"""
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        
        features = data["data"]["features"]
        assert "aiTopics" in features
        assert "analytics" in features
        assert "feedback" in features
        assert isinstance(features["analytics"], bool)
        assert isinstance(features["feedback"], bool)


class TestFeedbackEndpoint:
    """Test feedback submission"""

    def test_submit_complete_feedback(self, client):
        """Test submitting complete feedback"""
        feedback = {
            "rating": 5,
            "comment": "Excellent discussion platform!",
            "session_id": "test-session-feedback"
        }
        response = client.post("/api/feedback", json=feedback)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data

    def test_submit_feedback_with_only_rating(self, client):
        """Test submitting feedback with only rating"""
        feedback = {"rating": 4}
        response = client.post("/api/feedback", json=feedback)
        assert response.status_code == 200

    def test_submit_feedback_various_ratings(self, client):
        """Test submitting feedback with various ratings"""
        for rating in [1, 2, 3, 4, 5]:
            feedback = {
                "rating": rating,
                "comment": f"Rating {rating}",
                "session_id": f"session-{rating}"
            }
            response = client.post("/api/feedback", json=feedback)
            assert response.status_code == 200


class TestRoomStateEndpoint:
    """Test room state endpoint"""

    def test_room_state_response_structure(self, client):
        """Test room state returns expected structure"""
        response = client.get("/api/room/test-room-123/state")
        
        # Room may not exist, but response should be valid
        if response.status_code == 200:
            data = response.json()
            assert "participants" in data
            assert "discussion" in data
            assert isinstance(data["participants"], list)
            assert isinstance(data["discussion"], dict)

    def test_room_state_discussion_fields(self, client):
        """Test room state discussion fields"""
        response = client.get("/api/room/test-room-456/state")
        
        if response.status_code == 200:
            data = response.json()
            discussion = data["discussion"]
            
            # Check expected discussion fields
            expected_fields = ["active", "topic", "currentSpeakerIndex", 
                             "speakingTime", "timeRemaining", "round", 
                             "startedAt", "endedAt"]
            
            for field in expected_fields:
                assert field in discussion

