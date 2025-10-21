"""
Comprehensive Tests for API Routes using Pydantic Models
Tests all API endpoints that use Pydantic models for request/response validation
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from src.models import (
    LoginModel, SignUpModel, LoginSignUpResponseModel,
    CreateRoomModel, RoomStatus, CEFRLevel,
    CreateParticipantModel, ParticipantLeftModel,
    UpdateUserCEFRModel, UpdateRoomStatusModel
)


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


class TestUserRoutes:
    """Test user management API routes"""
    
    @patch('src.api.user_routes.user_service')
    def test_login_success(self, mock_service, client):
        """Test successful user login"""
        # Mock service response
        mock_service.login_user.return_value = LoginSignUpResponseModel(
            status="success",
            data="user-123",
            message="Login successful"
        )
        
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/users/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"] == "user-123"
        assert data["message"] == "Login successful"
    
    @patch('src.api.user_routes.user_service')
    def test_login_invalid_credentials(self, mock_service, client):
        """Test login with invalid credentials"""
        mock_service.login_user.return_value = LoginSignUpResponseModel(
            status="failure",
            data="",
            message="Invalid email or password"
        )
        
        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/users/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failure"
        assert "Invalid email or password" in data["message"]
    
    def test_login_invalid_email_format(self, client):
        """Test login with invalid email format"""
        login_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/users/login", json=login_data)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    @patch('src.api.user_routes.user_service')
    def test_signup_success(self, mock_service, client):
        """Test successful user signup"""
        mock_service.signup_user.return_value = LoginSignUpResponseModel(
            status="success",
            data="user-456",
            message="Signup successful"
        )
        
        signup_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123",
            "current_cefr_level": "B1",
            "topic_categories": ["Technology", "Education"]
        }
        
        response = client.post("/users/signup", json=signup_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"] == "user-456"
    
    def test_signup_validation_errors(self, client):
        """Test signup with validation errors"""
        # Short name
        signup_data = {
            "name": "J",
            "email": "j@example.com",
            "password": "password123"
        }
        
        response = client.post("/users/signup", json=signup_data)
        assert response.status_code == 422
        
        # Short password
        signup_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "123"
        }
        
        response = client.post("/users/signup", json=signup_data)
        assert response.status_code == 422
    
    @patch('src.api.user_routes.user_service')
    def test_get_user_success(self, mock_service, client):
        """Test successful user retrieval"""
        from src.models.user_pydantic_models import UserModel
        
        mock_user = UserModel(
            user_id="user-123",
            created_at=datetime.now(),
            email="test@example.com",
            name="Test User",
            current_cefr_level=CEFRLevel.B1,
            topic_categories=["Technology"]
        )
        
        mock_service.get_user.return_value = {
            "status": "success",
            "data": mock_user,
            "message": "User found"
        }
        
        response = client.get("/users/user-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["user_id"] == "user-123"
    
    @patch('src.api.user_routes.user_service')
    def test_get_user_not_found(self, mock_service, client):
        """Test user not found"""
        mock_service.get_user.return_value = {
            "status": "failure",
            "data": None,
            "message": "User not found"
        }
        
        response = client.get("/users/nonexistent-user")
        
        assert response.status_code == 404
        data = response.json()
        assert "User not found" in data["detail"]
    
    @patch('src.api.user_routes.user_service')
    def test_update_cefr_level_success(self, mock_service, client):
        """Test successful CEFR level update"""
        mock_service.update_user_cefr_level.return_value = {
            "status": "success",
            "data": {"updated": 1},
            "message": "CEFR level updated"
        }
        
        update_data = {
            "user_id": "user-123",
            "current_cefr_level": "B2"
        }
        
        response = client.patch("/users/cefr-level", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @patch('src.api.user_routes.user_service')
    def test_update_password_success(self, mock_service, client):
        """Test successful password update"""
        mock_service.update_user_password.return_value = {
            "status": "success",
            "data": {"updated": 1},
            "message": "Password updated"
        }
        
        update_data = {
            "user_id": "user-123",
            "old_password": "oldpass123",
            "new_password": "newpass123"
        }
        
        response = client.patch("/users/password", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestRoomRoutes:
    """Test room management API routes"""
    
    @patch('src.api.room_routes.service')
    def test_create_room_success(self, mock_service, client):
        """Test successful room creation"""
        from src.models.room_pydantic_models import RoomResponseModel
        
        mock_service.create_room.return_value = RoomResponseModel(
            status="success",
            data="room-123",
            message="Room created successfully"
        )
        
        room_data = {
            "topic_title": "AI Ethics Discussion",
            "topic_category": "Technology",
            "cefr_level": "B1",
            "status": "waiting",
            "created_by": "user-123"
        }
        
        response = client.post("/rooms/", json=room_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"] == "room-123"
    
    def test_create_room_validation_errors(self, client):
        """Test room creation with validation errors"""
        # Missing required fields
        room_data = {
            "topic_title": "Test Topic"
            # Missing required fields
        }
        
        response = client.post("/rooms/", json=room_data)
        assert response.status_code == 422
    
    @patch('src.api.room_routes.service')
    def test_get_room_success(self, mock_service, client):
        """Test successful room retrieval"""
        mock_service.get_room.return_value = {
            "status": "success",
            "data": {
                "room_id": "room-123",
                "topic_title": "AI Ethics",
                "status": "waiting"
            },
            "message": "Room found"
        }
        
        response = client.get("/rooms/room-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["room_id"] == "room-123"
    
    @patch('src.api.room_routes.service')
    def test_get_room_not_found(self, mock_service, client):
        """Test room not found"""
        mock_service.get_room.return_value = {
            "status": "failure",
            "data": None,
            "message": "Room not found"
        }
        
        response = client.get("/rooms/nonexistent-room")
        
        assert response.status_code == 404
    
    @patch('src.api.room_routes.service')
    def test_list_waiting_rooms(self, mock_service, client):
        """Test listing waiting rooms"""
        mock_service.list_rooms_by_status.return_value = {
            "status": "success",
            "data": [
                {"room_id": "room-1", "status": "waiting"},
                {"room_id": "room-2", "status": "waiting"}
            ],
            "message": "Rooms listed for status='waiting'"
        }
        
        response = client.get("/rooms/waiting")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2
    
    @patch('src.api.room_routes.service')
    def test_update_room_status(self, mock_service, client):
        """Test updating room status"""
        mock_service.update_room_status.return_value = {
            "status": "success",
            "data": {"updated": 1},
            "message": "Room status updated"
        }
        
        update_data = {
            "room_id": "room-123",
            "status": "in_progress",
            "started_at": datetime.now().isoformat()
        }
        
        response = client.patch("/rooms/room-123/status", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @patch('src.api.room_routes.service')
    def test_update_room_state(self, mock_service, client):
        """Test updating room discussion state"""
        mock_service.update_room_state.return_value = {
            "status": "success",
            "data": {"updated": 1},
            "message": "Room state updated"
        }
        
        update_data = {
            "room_id": "room-123",
            "current_round": 2,
            "current_speaker_index": 1,
            "participant_count": 4
        }
        
        response = client.patch("/rooms/room-123/state", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @patch('src.api.room_routes.service')
    def test_end_room(self, mock_service, client):
        """Test ending a room"""
        mock_service.end_room.return_value = {
            "status": "success",
            "data": {"updated": 1},
            "message": "Room ended"
        }
        
        end_data = {
            "room_id": "room-123",
            "status": "completed",
            "ended_at": datetime.now().isoformat(),
            "duration_seconds": 1800
        }
        
        response = client.patch("/rooms/room-123/end", json=end_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestParticipantRoutes:
    """Test participant management API routes"""
    
    @patch('src.api.participant_routes.participant_service')
    def test_create_participant_success(self, mock_service, client):
        """Test successful participant creation"""
        from src.models.participant_pydantic_models import CreateParticipantResponseModel
        
        mock_service.create_participant.return_value = CreateParticipantResponseModel(
            status="success",
            data="participant-123",
            message="Participant created successfully"
        )
        
        participant_data = {
            "room_id": "room-123",
            "user_id": "user-456",
            "anonymous_name": "Blue Panda",
            "role": "speaker",
            "starting_cefr_level": "B1",
            "joined_at": datetime.now().isoformat()
        }
        
        response = client.post("/participants/", json=participant_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"] == "participant-123"
    
    def test_create_participant_validation_errors(self, client):
        """Test participant creation with validation errors"""
        # Missing required fields
        participant_data = {
            "room_id": "room-123"
            # Missing required fields
        }
        
        response = client.post("/participants/", json=participant_data)
        assert response.status_code == 422
    
    @patch('src.api.participant_routes.participant_service')
    def test_get_participant_success(self, mock_service, client):
        """Test successful participant retrieval"""
        mock_service.get_participant.return_value = {
            "status": "success",
            "data": {
                "participant_id": "participant-123",
                "user_id": "user-456",
                "room_id": "room-123",
                "anonymous_name": "Blue Panda",
                "is_ready": True
            },
            "message": "Participant found"
        }
        
        response = client.get("/participants/user-456/room-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["data"]["participant_id"] == "participant-123"
    
    @patch('src.api.participant_routes.participant_service')
    def test_get_participant_not_found(self, mock_service, client):
        """Test participant not found"""
        mock_service.get_participant.return_value = {
            "status": "failure",
            "data": None,
            "message": "Participant not found"
        }
        
        response = client.get("/participants/user-456/room-123")
        
        assert response.status_code == 404
    
    @patch('src.api.participant_routes.participant_service')
    def test_list_participants_for_room(self, mock_service, client):
        """Test listing participants for a room"""
        mock_service.list_participants_for_room.return_value = {
            "status": "success",
            "data": [
                {"participant_id": "participant-1", "anonymous_name": "Blue Panda"},
                {"participant_id": "participant-2", "anonymous_name": "Red Dragon"}
            ],
            "message": "Participants listed"
        }
        
        response = client.get("/participants/room/room-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]) == 2
    
    @patch('src.api.participant_routes.participant_service')
    def test_update_participant_muted(self, mock_service, client):
        """Test updating participant muted status"""
        mock_service.update_participant_muted.return_value = {
            "status": "success",
            "data": {"updated": 1},
            "message": "Participant muted status updated"
        }
        
        update_data = {
            "participant_id": "participant-123",
            "is_muted": True
        }
        
        response = client.patch("/participants/muted", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @patch('src.api.participant_routes.participant_service')
    def test_update_participant_speaking(self, mock_service, client):
        """Test updating participant speaking status"""
        mock_service.update_participant_speaking.return_value = {
            "status": "success",
            "data": {"updated": 1},
            "message": "Participant speaking status updated"
        }
        
        update_data = {
            "participant_id": "participant-123",
            "is_speaking": True
        }
        
        response = client.patch("/participants/speaking", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @patch('src.api.participant_routes.participant_service')
    def test_update_participant_ready(self, mock_service, client):
        """Test updating participant ready status"""
        mock_service.update_participant_ready.return_value = {
            "status": "success",
            "data": {"updated": 1},
            "message": "Participant ready status updated"
        }
        
        update_data = {
            "participant_id": "participant-123",
            "is_ready": True
        }
        
        response = client.patch("/participants/ready", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    @patch('src.api.participant_routes.participant_service')
    def test_update_participant_left(self, mock_service, client):
        """Test updating participant left status"""
        mock_service.update_participant_left.return_value = {
            "status": "success",
            "data": {"updated": 1},
            "message": "Participant left status updated"
        }
        
        update_data = {
            "participant_id": "participant-123",
            "left_at": datetime.now().isoformat(),
            "ending_cefr_level": "B2"
        }
        
        response = client.patch("/participants/left", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"


class TestRouteValidation:
    """Test route validation and error handling"""
    
    def test_invalid_json_format(self, client):
        """Test endpoints with invalid JSON"""
        response = client.post(
            "/users/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test endpoints with missing required fields"""
        # Login without password
        response = client.post("/users/login", json={"email": "test@example.com"})
        assert response.status_code == 422
        
        # Room creation without required fields
        response = client.post("/rooms/", json={"topic_title": "Test"})
        assert response.status_code == 422
    
    def test_invalid_enum_values(self, client):
        """Test endpoints with invalid enum values"""
        room_data = {
            "topic_title": "Test Topic",
            "topic_category": "Technology",
            "cefr_level": "INVALID_LEVEL",  # Invalid CEFR level
            "status": "waiting",
            "created_by": "user-123"
        }
        
        response = client.post("/rooms/", json=room_data)
        assert response.status_code == 422
    
    def test_invalid_datetime_format(self, client):
        """Test endpoints with invalid datetime format"""
        update_data = {
            "user_id": "user-123",
            "last_active": "invalid-datetime"
        }
        
        response = client.patch("/users/last-active", json=update_data)
        assert response.status_code == 422


class TestRouteErrorHandling:
    """Test route error handling"""
    
    @patch('src.api.user_routes.user_service')
    def test_service_error_handling(self, mock_service, client):
        """Test handling of service errors"""
        # Mock service to raise exception
        mock_service.login_user.side_effect = Exception("Database connection error")
        
        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = client.post("/users/login", json=login_data)
        assert response.status_code == 500
    
    @patch('src.api.room_routes.service')
    def test_room_service_failure_response(self, mock_service, client):
        """Test room service failure response handling"""
        mock_service.get_room.return_value = {
            "status": "failure",
            "data": None,
            "message": "Database error"
        }
        
        response = client.get("/rooms/room-123")
        assert response.status_code == 404
        data = response.json()
        assert "Database error" in data["detail"]


class TestRouteIntegration:
    """Test route integration scenarios"""
    
    @patch('src.api.user_routes.user_service')
    @patch('src.api.room_routes.service')
    @patch('src.api.participant_routes.participant_service')
    def test_complete_user_flow(self, mock_participant_service, mock_room_service, mock_user_service, client):
        """Test complete user flow: signup -> create room -> join as participant"""
        # Mock successful signup
        mock_user_service.signup_user.return_value = LoginSignUpResponseModel(
            status="success", data="user-123", message="Signup successful"
        )
        
        # Mock successful room creation
        from src.models.room_pydantic_models import RoomResponseModel
        mock_room_service.create_room.return_value = RoomResponseModel(
            status="success", data="room-456", message="Room created successfully"
        )
        
        # Mock successful participant creation
        from src.models.participant_pydantic_models import CreateParticipantResponseModel
        mock_participant_service.create_participant.return_value = CreateParticipantResponseModel(
            status="success", data="participant-789", message="Participant created successfully"
        )
        
        # Test signup
        signup_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "password123"
        }
        signup_response = client.post("/users/signup", json=signup_data)
        assert signup_response.status_code == 200
        
        # Test room creation
        room_data = {
            "topic_title": "AI Ethics",
            "topic_category": "Technology",
            "cefr_level": "B1",
            "status": "waiting",
            "created_by": "user-123"
        }
        room_response = client.post("/rooms/", json=room_data)
        assert room_response.status_code == 200
        
        # Test participant creation
        participant_data = {
            "room_id": "room-456",
            "user_id": "user-123",
            "anonymous_name": "Blue Panda",
            "starting_cefr_level": "B1",
            "joined_at": datetime.now().isoformat()
        }
        participant_response = client.post("/participants/", json=participant_data)
        assert participant_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])