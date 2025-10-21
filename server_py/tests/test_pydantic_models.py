"""
Comprehensive Tests for Pydantic Models
Tests all Pydantic models for validation, serialization, and edge cases
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from typing import List

from src.models import (
    # User Models
    LoginModel, SignUpModel, LoginSignUpResponseModel, UserModel,
    UpdateUserCEFRModel, UpdateUserLastActiveModel, UpdateUserPasswordModel,
    
    # Room Models
    CreateRoomModel, RoomModel, RoomResponseModel, RoomStatus,
    UpdateRoomStatusModel, UpdateRoomStateModel, UpdateRoomEndModel,
    
    # Participant Models
    CreateParticipantModel, ParticipantModel, CreateParticipantResponseModel,
    ParticipantLeftModel, ParticipantIsMutedModel, ParticipantIsSpeakingModel,
    ParticipantIsReadyModel,
    
    # Feedback Models
    CreateInstantFeedbackModel, InstantFeedbackModel,
    CreateComprehensiveFeedbackModel, ComprehensiveFeedbackModel,
    
    # Transcript Models
    CreateTranscriptModel, TranscriptModel,
    UpdateTranscriptProcessingModel, UpdateTranscriptAudioURLModel,
    
    # Agent Models
    CreateAgentModel, AgentModel, AgentUpdateModel,
    AgentTranscriptProcessingModel, AgentFeedbackGenerationModel,
    AgentResponseModel, AgentInteractionStatsModel, AgentHealthModel,
    
    # Enums
    CEFRLevel, ParticipantRole, AgentStatus, AgentType, AgentModelSource
)


class TestUserModels:
    """Test user-related Pydantic models"""
    
    def test_login_model_valid(self):
        """Test valid LoginModel creation"""
        login = LoginModel(
            email="test@example.com",
            password="password123"
        )
        assert login.email == "test@example.com"
        assert login.password == "password123"
    
    def test_login_model_invalid_email(self):
        """Test LoginModel with invalid email"""
        with pytest.raises(ValidationError):
            LoginModel(
                email="invalid-email",
                password="password123"
            )
    
    def test_signup_model_valid(self):
        """Test valid SignUpModel creation"""
        signup = SignUpModel(
            name="John Doe",
            email="john@example.com",
            password="password123",
            current_cefr_level=CEFRLevel.B1,
            topic_categories=["Technology", "Education"]
        )
        assert signup.name == "John Doe"
        assert signup.current_cefr_level == CEFRLevel.B1
        assert len(signup.topic_categories) == 2
    
    def test_signup_model_defaults(self):
        """Test SignUpModel with default values"""
        signup = SignUpModel(
            name="Jane Doe",
            email="jane@example.com",
            password="password123"
        )
        assert signup.current_cefr_level == CEFRLevel.A0
        assert signup.topic_categories == []
    
    def test_signup_model_validation_errors(self):
        """Test SignUpModel validation errors"""
        # Short name
        with pytest.raises(ValidationError):
            SignUpModel(
                name="J",
                email="j@example.com",
                password="password123"
            )
        
        # Short password
        with pytest.raises(ValidationError):
            SignUpModel(
                name="John Doe",
                email="john@example.com",
                password="123"
            )
    
    def test_user_model_complete(self):
        """Test complete UserModel"""
        now = datetime.now()
        user = UserModel(
            user_id="user-123",
            created_at=now,
            last_active=now,
            email="user@example.com",
            name="Test User",
            current_cefr_level=CEFRLevel.B2,
            topic_categories=["Science", "Arts"]
        )
        assert user.user_id == "user-123"
        assert user.current_cefr_level == CEFRLevel.B2
        assert len(user.topic_categories) == 2
    
    def test_update_user_cefr_model(self):
        """Test UpdateUserCEFRModel"""
        update = UpdateUserCEFRModel(
            user_id="user-123",
            current_cefr_level=CEFRLevel.C1
        )
        assert update.user_id == "user-123"
        assert update.current_cefr_level == CEFRLevel.C1
    
    def test_update_user_password_model(self):
        """Test UpdateUserPasswordModel"""
        update = UpdateUserPasswordModel(
            user_id="user-123",
            old_password="oldpass",
            new_password="newpass"
        )
        assert update.user_id == "user-123"
        assert update.old_password == "oldpass"
        assert update.new_password == "newpass"


class TestRoomModels:
    """Test room-related Pydantic models"""
    
    def test_create_room_model_valid(self):
        """Test valid CreateRoomModel"""
        room = CreateRoomModel(
            topic_title="Climate Change Discussion",
            topic_category="Environment",
            cefr_level=CEFRLevel.B1,
            status=RoomStatus.WAITING,
            created_by="user-123"
        )
        assert room.topic_title == "Climate Change Discussion"
        assert room.max_participants == 6  # Default value
        assert room.speaking_time_per_turn == 60  # Default value
        assert room.num_rounds == 3  # Default value
        assert room.status == RoomStatus.WAITING
    
    def test_create_room_model_custom_values(self):
        """Test CreateRoomModel with custom values"""
        room = CreateRoomModel(
            room_name="Custom Room",
            topic_title="AI Ethics",
            topic_category="Technology",
            max_participants=4,
            speaking_time_per_turn=90,
            num_rounds=2,
            cefr_level=CEFRLevel.C1,
            status=RoomStatus.IN_PROGRESS,
            current_round=1,
            current_speaker_index=2,
            participant_count=3,
            created_by="user-456"
        )
        assert room.room_name == "Custom Room"
        assert room.max_participants == 4
        assert room.speaking_time_per_turn == 90
        assert room.num_rounds == 2
        assert room.current_round == 1
    
    def test_room_model_with_id(self):
        """Test RoomModel with ID and timestamps"""
        now = datetime.now()
        room = RoomModel(
            room_id="room-123",
            created_at=now,
            topic_title="Test Topic",
            topic_category="Test",
            cefr_level=CEFRLevel.A1,
            status=RoomStatus.WAITING,
            created_by="user-123"
        )
        assert room.room_id == "room-123"
        assert room.created_at == now
    
    def test_update_room_status_model(self):
        """Test UpdateRoomStatusModel"""
        now = datetime.now()
        update = UpdateRoomStatusModel(
            room_id="room-123",
            status=RoomStatus.IN_PROGRESS,
            started_at=now
        )
        assert update.room_id == "room-123"
        assert update.status == RoomStatus.IN_PROGRESS
        assert update.started_at == now
    
    def test_update_room_state_model(self):
        """Test UpdateRoomStateModel"""
        update = UpdateRoomStateModel(
            room_id="room-123",
            current_round=2,
            current_speaker_index=1,
            participant_count=4
        )
        assert update.room_id == "room-123"
        assert update.current_round == 2
        assert update.current_speaker_index == 1
        assert update.participant_count == 4
    
    def test_update_room_end_model(self):
        """Test UpdateRoomEndModel"""
        now = datetime.now()
        update = UpdateRoomEndModel(
            room_id="room-123",
            status=RoomStatus.COMPLETED,
            ended_at=now,
            duration_seconds=1800
        )
        assert update.room_id == "room-123"
        assert update.status == RoomStatus.COMPLETED
        assert update.duration_seconds == 1800


class TestParticipantModels:
    """Test participant-related Pydantic models"""
    
    def test_create_participant_model_valid(self):
        """Test valid CreateParticipantModel"""
        now = datetime.now()
        participant = CreateParticipantModel(
            room_id="room-123",
            user_id="user-456",
            anonymous_name="Blue Panda",
            avatar_color="#0066CC",
            role="speaker",
            starting_cefr_level="B1",
            joined_at=now,
            campusOrLocation="Main Campus"
        )
        assert participant.room_id == "room-123"
        assert participant.user_id == "user-456"
        assert participant.anonymous_name == "Blue Panda"
        assert participant.role == "speaker"
        assert participant.is_ready is False  # Default value
        assert participant.is_speaking is False  # Default value
        assert participant.is_muted is False  # Default value
    
    def test_participant_model_with_id(self):
        """Test ParticipantModel with ID"""
        now = datetime.now()
        participant = ParticipantModel(
            participant_id="participant-123",
            created_at=now,
            room_id="room-123",
            user_id="user-456",
            anonymous_name="Red Dragon",
            starting_cefr_level="A2",
            joined_at=now
        )
        assert participant.participant_id == "participant-123"
        assert participant.created_at == now
    
    def test_participant_left_model(self):
        """Test ParticipantLeftModel"""
        now = datetime.now()
        left = ParticipantLeftModel(
            participant_id="participant-123",
            left_at=now,
            ending_cefr_level="B1"
        )
        assert left.participant_id == "participant-123"
        assert left.left_at == now
        assert left.ending_cefr_level == "B1"
    
    def test_participant_status_models(self):
        """Test participant status update models"""
        # Muted model
        muted = ParticipantIsMutedModel(
            participant_id="participant-123",
            is_muted=True
        )
        assert muted.is_muted is True
        
        # Speaking model
        speaking = ParticipantIsSpeakingModel(
            participant_id="participant-123",
            is_speaking=True
        )
        assert speaking.is_speaking is True
        
        # Ready model
        ready = ParticipantIsReadyModel(
            participant_id="participant-123",
            is_ready=True
        )
        assert ready.is_ready is True


class TestFeedbackModels:
    """Test feedback-related Pydantic models"""
    
    def test_create_instant_feedback_model(self):
        """Test CreateInstantFeedbackModel"""
        feedback = CreateInstantFeedbackModel(
            room_id="room-123",
            participant_id="participant-456",
            user_id="user-789",
            feedback_type="instant",
            display_message="Great pronunciation!",
            agent_id="agent-123",
            agent_model=AgentModelSource.GEMINI
        )
        assert feedback.room_id == "room-123"
        assert feedback.feedback_type == "instant"
        assert feedback.agent_model == AgentModelSource.GEMINI
    
    def test_instant_feedback_model_with_id(self):
        """Test InstantFeedbackModel with ID"""
        now = datetime.now()
        feedback = InstantFeedbackModel(
            feedback_id="feedback-123",
            created_at=now,
            room_id="room-123",
            participant_id="participant-456",
            user_id="user-789",
            feedback_type="instant",
            display_message="Good vocabulary usage!",
            agent_id="agent-123",
            agent_model=AgentModelSource.BEDROCK
        )
        assert feedback.feedback_id == "feedback-123"
        assert feedback.created_at == now
    
    def test_create_comprehensive_feedback_model(self):
        """Test CreateComprehensiveFeedbackModel"""
        feedback = CreateComprehensiveFeedbackModel(
            room_id="room-123",
            participant_id="participant-456",
            user_id="user-789",
            feedback_type="comprehensive",
            cefr_speaking=CEFRLevel.B1,
            cefr_listening=CEFRLevel.B2,
            listening_activity="Active listening demonstrated",
            response_effectiveness="Responds well to others",
            listening_positive_observation="Good eye contact",
            listening_improvement_suggestion="Try to ask more follow-up questions",
            fluency="steady flow",
            sentence_complexity="medium",
            pace="smooth",
            filler_examples="['um', 'like']",
            grammar="mostly accurate",
            vocab_examples="['adequate', 'perform']",
            vocab_analysis="Good range of vocabulary",
            vocab_positive_observation="Used varied expressions",
            vocab_improvement_suggestion="Try more advanced synonyms",
            understanding_level="fair",
            explanation_quality="logical",
            interaction_style="builds on others' ideas",
            depth_of_understanding_suggestion="Use more examples",
            comparative_performance="More confident than average",
            comparative_suggestion="Try to elaborate more",
            summary_strength="Clear expression of ideas",
            summary_improvement_area="Reduce filler words",
            target_cefr_level=CEFRLevel.B2,
            agent_id="agent-123",
            agent_model=AgentModelSource.GEMINI
        )
        assert feedback.cefr_speaking == CEFRLevel.B1
        assert feedback.cefr_listening == CEFRLevel.B2
        assert feedback.target_cefr_level == CEFRLevel.B2


class TestTranscriptModels:
    """Test transcript-related Pydantic models"""
    
    def test_create_transcript_model_valid(self):
        """Test valid CreateTranscriptModel"""
        now = datetime.now()
        transcript = CreateTranscriptModel(
            room_id="room-123",
            participant_id="participant-456",
            user_id="user-789",
            round_number=1,
            turn_order=2,
            transcript_text="This is a test transcript of speech.",
            language="en",
            stt_confidence=0.95,
            started_at=now,
            ended_at=now,
            duration_seconds=30,
            word_count=8,
            speech_rate=120.0,
            audio_file_url="https://example.com/audio.mp3"
        )
        assert transcript.room_id == "room-123"
        assert transcript.transcript_text == "This is a test transcript of speech."
        assert transcript.word_count == 8
        assert transcript.speech_rate == 120.0
        assert transcript.is_processed is False  # Default value
    
    def test_transcript_model_with_id(self):
        """Test TranscriptModel with ID"""
        now = datetime.now()
        transcript = TranscriptModel(
            transcript_id="transcript-123",
            created_at=now,
            room_id="room-123",
            participant_id="participant-456",
            round_number=1,
            turn_order=1,
            transcript_text="Hello everyone!",
            started_at=now,
            ended_at=now,
            duration_seconds=5,
            word_count=2,
            speech_rate=100.0
        )
        assert transcript.transcript_id == "transcript-123"
        assert transcript.created_at == now
    
    def test_transcript_validation_errors(self):
        """Test transcript validation errors"""
        now = datetime.now()
        
        # Empty transcript text
        with pytest.raises(ValidationError):
            CreateTranscriptModel(
                room_id="room-123",
                participant_id="participant-456",
                round_number=1,
                turn_order=1,
                transcript_text="",  # Empty text should fail
                started_at=now,
                ended_at=now,
                duration_seconds=5,
                word_count=0,
                speech_rate=0.0
            )
    
    def test_update_transcript_models(self):
        """Test transcript update models"""
        now = datetime.now()
        
        # Processing update
        processing_update = UpdateTranscriptProcessingModel(
            transcript_id="transcript-123",
            is_processed=True,
            processed_at=now
        )
        assert processing_update.is_processed is True
        
        # Audio URL update
        audio_update = UpdateTranscriptAudioURLModel(
            transcript_id="transcript-123",
            audio_file_url="https://example.com/new-audio.mp3"
        )
        assert "new-audio.mp3" in audio_update.audio_file_url


class TestAgentModels:
    """Test agent-related Pydantic models"""
    
    def test_create_agent_model_valid(self):
        """Test valid CreateAgentModel"""
        agent = CreateAgentModel(
            room_id="room-123",
            agent_model=AgentModelSource.GEMINI,
            agent_type=AgentType.FACILITATOR
        )
        assert agent.room_id == "room-123"
        assert agent.agent_model == AgentModelSource.GEMINI
        assert agent.agent_type == AgentType.FACILITATOR
        assert agent.status == AgentStatus.ACTIVE  # Default value
    
    def test_agent_model_with_id(self):
        """Test AgentModel with ID"""
        now = datetime.now()
        agent = AgentModel(
            agent_id="agent-123",
            room_id="room-456",
            agent_model="Gemini",
            agent_type="english",
            status="active",
            total_interactions=5,
            created_at=now
        )
        assert agent.agent_id == "agent-123"
        assert agent.total_interactions == 5
        assert agent.created_at == now
    
    def test_agent_update_model(self):
        """Test AgentUpdateModel"""
        update = AgentUpdateModel(
            status=AgentStatus.INACTIVE,
            agent_type=AgentType.TUTOR
        )
        assert update.status == AgentStatus.INACTIVE
        assert update.agent_type == AgentType.TUTOR
    
    def test_agent_interaction_models(self):
        """Test agent interaction models"""
        # Transcript processing
        processing = AgentTranscriptProcessingModel(
            agent_id="agent-123",
            transcript_id="transcript-456",
            processing_type="instant_feedback"
        )
        assert processing.processing_type == "instant_feedback"
        
        # Feedback generation
        feedback_gen = AgentFeedbackGenerationModel(
            agent_id="agent-123",
            transcript_id="transcript-456",
            participant_id="participant-789",
            feedback_type="comprehensive"
        )
        assert feedback_gen.feedback_type == "comprehensive"
        
        # Agent response
        response = AgentResponseModel(
            agent_id="agent-123",
            response_text="Great job on pronunciation!",
            processing_time=2.5,
            confidence_score=0.85,
            tokens_used=150
        )
        assert response.processing_time == 2.5
        assert response.confidence_score == 0.85
    
    def test_agent_analytics_models(self):
        """Test agent analytics models"""
        now = datetime.now()
        
        # Interaction stats
        stats = AgentInteractionStatsModel(
            agent_id="agent-123",
            total_interactions=100,
            instant_feedback_count=60,
            comprehensive_feedback_count=40,
            average_processing_time=1.8,
            last_interaction=now
        )
        assert stats.total_interactions == 100
        assert stats.instant_feedback_count == 60
        
        # Health model
        health = AgentHealthModel(
            agent_id="agent-123",
            status=AgentStatus.ACTIVE,
            last_health_check=now,
            error_count=2,
            uptime_percentage=99.5
        )
        assert health.status == AgentStatus.ACTIVE
        assert health.uptime_percentage == 99.5


class TestEnums:
    """Test enumeration types"""
    
    def test_cefr_level_enum(self):
        """Test CEFRLevel enum"""
        assert CEFRLevel.A0.value == "A0"
        assert CEFRLevel.C2.value == "C2"
        assert len(list(CEFRLevel)) == 7
    
    def test_participant_role_enum(self):
        """Test ParticipantRole enum"""
        assert ParticipantRole.HOST.value == "host"
        assert ParticipantRole.PARTICIPANT.value == "speaker"
        assert ParticipantRole.LISTENER.value == "listener"
    
    def test_room_status_enum(self):
        """Test RoomStatus enum"""
        assert RoomStatus.WAITING.value == "waiting"
        assert RoomStatus.IN_PROGRESS.value == "in_progress"
        assert RoomStatus.COMPLETED.value == "completed"
        assert RoomStatus.CANCELLED.value == "cancelled"
    
    def test_agent_enums(self):
        """Test agent-related enums"""
        # Agent Status
        assert AgentStatus.ACTIVE.value == "active"
        assert AgentStatus.INACTIVE.value == "inactive"
        assert AgentStatus.ERROR.value == "error"
        assert AgentStatus.PROCESSING.value == "processing"
        
        # Agent Type
        assert AgentType.FACILITATOR.value == "facilitator"
        assert AgentType.ENGLISH.value == "english"
        assert AgentType.TUTOR.value == "tutor"
        assert AgentType.MODERATOR.value == "moderator"
        
        # Agent Model Source
        assert AgentModelSource.GEMINI.value == "Gemini"
        assert AgentModelSource.BEDROCK.value == "Bedrock"


class TestModelSerialization:
    """Test model serialization and deserialization"""
    
    def test_user_model_serialization(self):
        """Test UserModel JSON serialization"""
        now = datetime.now()
        user = UserModel(
            user_id="user-123",
            created_at=now,
            email="test@example.com",
            name="Test User",
            current_cefr_level=CEFRLevel.B1,
            topic_categories=["Tech", "Science"]
        )
        
        # Test dict conversion
        user_dict = user.model_dump()
        assert user_dict["user_id"] == "user-123"
        assert user_dict["current_cefr_level"] == "B1"
        assert len(user_dict["topic_categories"]) == 2
    
    def test_room_model_serialization(self):
        """Test RoomModel JSON serialization"""
        now = datetime.now()
        room = RoomModel(
            room_id="room-123",
            created_at=now,
            topic_title="Test Topic",
            topic_category="Education",
            cefr_level=CEFRLevel.A2,
            status=RoomStatus.WAITING,
            created_by="user-123"
        )
        
        room_dict = room.model_dump()
        assert room_dict["status"] == "waiting"
        assert room_dict["cefr_level"] == "A2"
    
    def test_agent_model_serialization(self):
        """Test AgentModel JSON serialization"""
        now = datetime.now()
        agent = AgentModel(
            agent_id="agent-123",
            room_id="room-456",
            agent_model="Gemini",
            agent_type="facilitator",
            status="active",
            total_interactions=10,
            created_at=now
        )
        
        agent_dict = agent.model_dump()
        assert agent_dict["agent_type"] == "facilitator"
        assert agent_dict["total_interactions"] == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])