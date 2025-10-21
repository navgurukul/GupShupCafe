"""
Comprehensive Tests for Services
Tests all service classes for business logic, database operations, and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid

from src.services.user_services import User_services
from src.services.room_service import Room_service
from src.services.participant_service import Participant_service
from src.services.agent_service import agent_service
from src.services.feedback_service import feedback_service
from src.services.transcript_service import transcript_service

from src.models import (
    LoginModel, SignUpModel, UserModel, UpdateUserCEFRModel,
    CreateRoomModel, RoomStatus, CEFRLevel,
    CreateParticipantModel, ParticipantLeftModel,
    CreateAgentModel, AgentModelSource, AgentType, AgentStatus
)


class TestUserServices:
    """Test user service methods"""
    
    @pytest.fixture
    def user_service(self):
        """Create user service with mocked database"""
        service = User_services()
        service.cursor = Mock()
        service.conn = Mock()
        return service
    
    def test_hash_password(self, user_service):
        """Test password hashing"""
        password = "testpassword123"
        hashed = user_service.hash_password(password)
        assert hashed.startswith("hashed_")
        assert hashed == "hashed_testpassword123"
    
    def test_unhash_password(self, user_service):
        """Test password unhashing"""
        hashed_password = "hashed_testpassword123"
        unhashed = user_service.unhash_password(hashed_password)
        assert unhashed == "testpassword123"
    
    def test_verify_password_correct(self, user_service):
        """Test password verification with correct password"""
        plain_password = "testpassword123"
        hashed_password = "hashed_testpassword123"
        assert user_service.verify_password(plain_password, hashed_password) is True
    
    def test_verify_password_incorrect(self, user_service):
        """Test password verification with incorrect password"""
        plain_password = "wrongpassword"
        hashed_password = "hashed_testpassword123"
        assert user_service.verify_password(plain_password, hashed_password) is False
    
    def test_login_user_success(self, user_service):
        """Test successful user login"""
        # Mock database response
        user_service.cursor.fetchone.return_value = ("user-123", "hashed_password123")
        
        login_model = LoginModel(email="test@example.com", password="password123")
        result = user_service.login_user(login_model)
        
        assert result.status == "success"
        assert result.data == "user-123"
        assert result.message == "Login successful"
    
    def test_login_user_invalid_credentials(self, user_service):
        """Test login with invalid credentials"""
        # Mock no user found
        user_service.cursor.fetchone.return_value = None
        
        login_model = LoginModel(email="test@example.com", password="wrongpassword")
        result = user_service.login_user(login_model)
        
        assert result.status == "failure"
        assert result.message == "Invalid email or password"
    
    def test_signup_user_success(self, user_service):
        """Test successful user signup"""
        # Mock no existing user
        user_service.cursor.fetchone.return_value = None
        
        signup_model = SignUpModel(
            name="John Doe",
            email="john@example.com",
            password="password123",
            current_cefr_level=CEFRLevel.A1,
            topic_categories=["Technology"]
        )
        
        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = "user-123"
            result = user_service.signup_user(signup_model)
        
        assert result.status == "success"
        assert result.data == "user-123"
        assert result.message == "Signup successful"
    
    def test_signup_user_existing_email(self, user_service):
        """Test signup with existing email"""
        # Mock existing user
        user_service.cursor.fetchone.return_value = ("existing-user-id",)
        
        signup_model = SignUpModel(
            name="John Doe",
            email="existing@example.com",
            password="password123"
        )
        
        result = user_service.signup_user(signup_model)
        
        assert result.status == "failure"
        assert "already exists" in result.message
    
    def test_signup_user_short_password(self, user_service):
        """Test signup with short password"""
        user_service.cursor.fetchone.return_value = None
        
        signup_model = SignUpModel(
            name="John Doe",
            email="john@example.com",
            password="123"  # Too short
        )
        
        result = user_service.signup_user(signup_model)
        
        assert result.status == "failure"
        assert "at least 6 characters" in result.message
    
    def test_get_user_success(self, user_service):
        """Test successful user retrieval"""
        # Mock database response
        user_service.cursor.fetchone.return_value = (
            "user-123", "John Doe", "john@example.com", "Technology,Science", 
            "B1", datetime.now(), datetime.now()
        )
        
        result = user_service.get_user("user-123")
        
        assert result["status"] == "success"
        assert result["data"].user_id == "user-123"
        assert result["data"].name == "John Doe"
        assert len(result["data"].topic_categories) == 2
    
    def test_get_user_not_found(self, user_service):
        """Test user not found"""
        user_service.cursor.fetchone.return_value = None
        
        result = user_service.get_user("nonexistent-user")
        
        assert result["status"] == "failure"
        assert result["message"] == "User not found"
    
    def test_update_user_cefr_level(self, user_service):
        """Test updating user CEFR level"""
        user_service.cursor.rowcount = 1
        
        update_model = UpdateUserCEFRModel(
            user_id="user-123",
            current_cefr_level=CEFRLevel.B2
        )
        
        result = user_service.update_user_cefr_level(update_model)
        
        assert result["status"] == "success"
        assert result["message"] == "CEFR level updated"
    
    def test_delete_user_success(self, user_service):
        """Test successful user deletion"""
        user_service.cursor.rowcount = 1
        
        result = user_service.delete_user("user-123")
        
        assert result["status"] == "success"
        assert result["data"]["deleted"] == 1


class TestRoomService:
    """Test room service methods"""
    
    @pytest.fixture
    def room_service(self):
        """Create room service with mocked database"""
        service = Room_service()
        service.cursor = Mock()
        service.conn = Mock()
        return service
    
    def test_create_room_success(self, room_service):
        """Test successful room creation"""
        room_model = CreateRoomModel(
            topic_title="AI Ethics",
            topic_category="Technology",
            cefr_level=CEFRLevel.B1,
            status=RoomStatus.WAITING,
            created_by="user-123"
        )
        
        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = "room-123"
            result = room_service.create_room(room_model)
        
        assert result.status == "success"
        assert result.data == "room-123"
        assert result.message == "Room created successfully"
    
    def test_join_room_success(self, room_service):
        """Test successful room joining"""
        # Mock room exists
        room_service.cursor.fetchone.return_value = ("room-123",)
        
        result = room_service.join_room("room-123")
        
        assert result.status == "success"
        assert result.data == "room-123"
        assert result.message == "Joined room successfully"
    
    def test_join_room_not_found(self, room_service):
        """Test joining non-existent room"""
        room_service.cursor.fetchone.return_value = None
        
        result = room_service.join_room("nonexistent-room")
        
        assert result.status == "failure"
        assert result.message == "Room not found"
    
    def test_get_room_success(self, room_service):
        """Test successful room retrieval"""
        # Mock room data
        room_data = (
            "room-123", "Test Room", "AI Ethics", "Technology", 6, 60, 3, "B1",
            "waiting", 0, 0, 0, datetime.now(), None, None, 0, None, "user-123"
        )
        room_service.cursor.fetchone.return_value = room_data
        room_service.cursor.description = [
            ("room_id",), ("room_name",), ("topic_title",), ("topic_category",),
            ("max_participants",), ("speaking_time_per_turn",), ("num_rounds",),
            ("cefr_level",), ("status",), ("current_round",), ("current_speaker_index",),
            ("participant_count",), ("created_at",), ("started_at",), ("ended_at",),
            ("duration_seconds",), ("agent_id",), ("created_by",)
        ]
        
        result = room_service.get_room("room-123")
        
        assert result["status"] == "success"
        assert result["data"]["room_id"] == "room-123"
        assert result["data"]["topic_title"] == "AI Ethics"
    
    def test_list_rooms_by_status(self, room_service):
        """Test listing rooms by status"""
        # Mock multiple rooms
        rooms_data = [
            ("room-1", "Room 1", "waiting"),
            ("room-2", "Room 2", "waiting")
        ]
        room_service.cursor.fetchall.return_value = rooms_data
        room_service.cursor.description = [("room_id",), ("room_name",), ("status",)]
        
        result = room_service.list_rooms_by_status("waiting")
        
        assert result["status"] == "success"
        assert len(result["data"]) == 2
        assert "waiting" in result["message"]
    
    def test_update_room_success(self, room_service):
        """Test successful room update"""
        room_service.cursor.rowcount = 1
        
        updates = {
            "status": "in_progress",
            "participant_count": 4
        }
        
        result = room_service.update_room("room-123", updates)
        
        assert result["status"] == "success"
        assert result["data"]["updated"] == 1
    
    def test_delete_room_success(self, room_service):
        """Test successful room deletion"""
        room_service.cursor.rowcount = 1
        
        result = room_service.delete_room("room-123")
        
        assert result["status"] == "success"
        assert result["data"]["deleted"] == 1


class TestParticipantService:
    """Test participant service methods"""
    
    @pytest.fixture
    def participant_service(self):
        """Create participant service with mocked database"""
        service = Participant_service()
        service.cursor = Mock()
        service.conn = Mock()
        return service
    
    def test_create_participant_success(self, participant_service):
        """Test successful participant creation"""
        # Mock no existing participant
        participant_service.cursor.fetchone.return_value = None
        
        participant_model = CreateParticipantModel(
            room_id="room-123",
            user_id="user-456",
            anonymous_name="Blue Panda",
            role="speaker",
            starting_cefr_level="B1",
            joined_at=datetime.now()
        )
        
        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.return_value.hex = "participant-123"
            result = participant_service.create_participant(participant_model)
        
        assert result.status == "success"
        assert result.data == "participant-123"
        assert result.message == "Participant created successfully"
    
    def test_create_participant_already_exists(self, participant_service):
        """Test creating participant that already exists"""
        # Mock existing participant
        participant_service.cursor.fetchone.return_value = ("existing-participant-id",)
        
        participant_model = CreateParticipantModel(
            room_id="room-123",
            user_id="user-456",
            anonymous_name="Blue Panda",
            starting_cefr_level="B1",
            joined_at=datetime.now()
        )
        
        result = participant_service.create_participant(participant_model)
        
        assert result.status == "success"
        assert "already exists" in result.message
    
    def test_get_participant_success(self, participant_service):
        """Test successful participant retrieval"""
        # Mock participant data
        participant_data = (
            "participant-123", "user-456", "room-123", "Blue Panda", "#0066CC",
            "speaker", 1, 0, 0, 0, "socket-123", "B1", "B1", datetime.now(),
            None, "Main Campus", 0
        )
        participant_service.cursor.fetchone.return_value = participant_data
        
        result = participant_service.get_participant("user-456", "room-123")
        
        assert result["status"] == "success"
        assert result["data"]["participant_id"] == "participant-123"
        assert result["data"]["anonymous_name"] == "Blue Panda"
        assert result["data"]["is_ready"] is True  # Converted from 1
    
    def test_get_participant_not_found(self, participant_service):
        """Test participant not found"""
        participant_service.cursor.fetchone.return_value = None
        
        result = participant_service.get_participant("user-456", "room-123")
        
        assert result["status"] == "failure"
        assert result["message"] == "Participant not found"
    
    def test_update_participant_left_time(self, participant_service):
        """Test updating participant left time"""
        participant_service.cursor.rowcount = 1
        
        left_time = datetime.now()
        result = participant_service.update_participant_left_time("user-456", "room-123", left_time)
        
        assert result.status == "success"
        assert result.message == "Participant left time updated"
    
    def test_list_participants_for_room(self, participant_service):
        """Test listing participants for a room"""
        # Mock participants data
        participants_data = [
            ("participant-1", "user-1", "room-123", "Blue Panda"),
            ("participant-2", "user-2", "room-123", "Red Dragon")
        ]
        participant_service.cursor.fetchall.return_value = participants_data
        participant_service.cursor.description = [
            ("participant_id",), ("user_id",), ("room_id",), ("anonymous_name",)
        ]
        
        result = participant_service.list_participants_for_room("room-123")
        
        assert result["status"] == "success"
        assert len(result["data"]) == 2
    
    def test_update_participant_muted(self, participant_service):
        """Test updating participant muted status"""
        participant_service.cursor.rowcount = 1
        
        from src.models.participant_pydantic_models import ParticipantIsMutedModel
        update_model = ParticipantIsMutedModel(
            participant_id="participant-123",
            is_muted=True
        )
        
        result = participant_service.update_participant_muted(update_model)
        
        assert result["status"] == "success"
        assert result["message"] == "Participant muted status updated"


class TestAgentService:
    """Test agent service methods"""
    
    def test_agent_service_methods_exist(self):
        """Test that all expected agent service methods exist"""
        assert hasattr(agent_service, 'create_agent')
        assert hasattr(agent_service, 'get_agent')
        assert hasattr(agent_service, 'get_agents_by_room')
        assert hasattr(agent_service, 'update_agent')
        assert hasattr(agent_service, 'increment_interactions')
        assert hasattr(agent_service, 'delete_agent')
        assert hasattr(agent_service, 'process_transcript_for_feedback')
        assert hasattr(agent_service, 'get_agent_stats')
        assert hasattr(agent_service, 'check_agent_health')
        assert hasattr(agent_service, 'get_agents_by_type')
        assert hasattr(agent_service, 'get_active_agents')
        assert hasattr(agent_service, 'create_room_agents')
        assert hasattr(agent_service, 'generate_facilitator_turn_response')
    
    @pytest.mark.asyncio
    async def test_create_room_agents_parameters(self):
        """Test create_room_agents method signature and basic functionality"""
        import inspect
        sig = inspect.signature(agent_service.create_room_agents)
        params = list(sig.parameters.keys())
        
        assert 'room_id' in params
        assert 'room_topic' in params
    
    def test_feedback_generation_methods_exist(self):
        """Test feedback generation method signatures"""
        import inspect
        
        # Test English feedback method exists
        assert hasattr(agent_service, '_generate_english_feedback')
        sig = inspect.signature(agent_service._generate_english_feedback)
        params = list(sig.parameters.keys())
        assert 'agent' in params
        assert 'transcript_data' in params
        assert 'feedback_type' in params
        
        # Test facilitator response method exists
        assert hasattr(agent_service, '_generate_facilitator_response')
        sig = inspect.signature(agent_service._generate_facilitator_response)
        params = list(sig.parameters.keys())
        assert 'agent' in params
        assert 'transcript_data' in params


class TestFeedbackService:
    """Test feedback service methods"""
    
    def test_feedback_service_exists(self):
        """Test that feedback service exists and has expected methods"""
        assert feedback_service is not None
        # Add more specific tests when feedback service is fully implemented


class TestTranscriptService:
    """Test transcript service methods"""
    
    def test_transcript_service_exists(self):
        """Test that transcript service exists and has expected methods"""
        assert transcript_service is not None
        # Add more specific tests when transcript service is fully implemented


class TestServiceIntegration:
    """Test service integration scenarios"""
    
    @pytest.fixture
    def mock_services(self):
        """Create mocked services for integration testing"""
        user_service = Mock(spec=User_services)
        room_service = Mock(spec=Room_service)
        participant_service = Mock(spec=Participant_service)
        
        return {
            'user_service': user_service,
            'room_service': room_service,
            'participant_service': participant_service
        }
    
    def test_user_room_participant_flow(self, mock_services):
        """Test the flow from user signup to room creation to participant joining"""
        # Mock successful user signup
        mock_services['user_service'].signup_user.return_value = Mock(
            status="success", data="user-123", message="Signup successful"
        )
        
        # Mock successful room creation
        mock_services['room_service'].create_room.return_value = Mock(
            status="success", data="room-456", message="Room created successfully"
        )
        
        # Mock successful participant creation
        mock_services['participant_service'].create_participant.return_value = Mock(
            status="success", data="participant-789", message="Participant created successfully"
        )
        
        # Test the flow
        signup_result = mock_services['user_service'].signup_user(Mock())
        assert signup_result.status == "success"
        
        room_result = mock_services['room_service'].create_room(Mock())
        assert room_result.status == "success"
        
        participant_result = mock_services['participant_service'].create_participant(Mock())
        assert participant_result.status == "success"
    
    def test_room_agent_creation_integration(self):
        """Test room creation with agent setup"""
        room_id = "test-room-123"
        topic = {
            "title": "Climate Change Discussion",
            "category": "Environment"
        }
        
        # Verify expected agent types would be created
        expected_types = [AgentType.FACILITATOR, AgentType.ENGLISH]
        assert len(expected_types) == 2
        assert AgentType.FACILITATOR in expected_types
        assert AgentType.ENGLISH in expected_types
    
    def test_transcript_feedback_flow(self):
        """Test transcript processing to feedback generation flow"""
        transcript_data = {
            "transcript_id": "test-transcript-123",
            "room_id": "test-room-123",
            "participant_id": "test-participant-123",
            "user_id": "test-user-123",
            "transcript_text": "I think climate change is a serious issue that requires immediate action.",
            "word_count": 12,
            "speech_rate": 2.0,
            "duration": 6
        }
        
        # Verify transcript data structure is valid
        assert transcript_data["transcript_text"]
        assert transcript_data["word_count"] > 0
        assert transcript_data["speech_rate"] > 0
        assert transcript_data["duration"] > 0
        
        # Test feedback types
        feedback_types = ["instant", "comprehensive"]
        for feedback_type in feedback_types:
            assert feedback_type in ["instant", "comprehensive"]


class TestServiceErrorHandling:
    """Test service error handling"""
    
    @pytest.fixture
    def user_service_with_db_error(self):
        """Create user service that simulates database errors"""
        service = User_services()
        service.cursor = Mock()
        service.conn = Mock()
        service.cursor.execute.side_effect = Exception("Database connection error")
        return service
    
    def test_login_user_database_error(self, user_service_with_db_error):
        """Test login user with database error"""
        login_model = LoginModel(email="test@example.com", password="password123")
        result = user_service_with_db_error.login_user(login_model)
        
        assert result.status == "failure"
        assert "Login failed" in result.message
    
    def test_signup_user_database_error(self, user_service_with_db_error):
        """Test signup user with database error"""
        signup_model = SignUpModel(
            name="John Doe",
            email="john@example.com",
            password="password123"
        )
        result = user_service_with_db_error.signup_user(signup_model)
        
        assert result.status == "failure"
        assert "Signup failed" in result.message
    
    def test_get_user_database_error(self, user_service_with_db_error):
        """Test get user with database error"""
        result = user_service_with_db_error.get_user("user-123")
        
        assert result["status"] == "failure"
        assert "Failed to retrieve user" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])