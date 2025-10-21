"""
Test new routes and services for all data models
"""
import pytest
from datetime import datetime
from src.models import (
    UpdateUserCEFRModel, UpdateUserLastActiveModel, UpdateUserPasswordModel,
    UpdateRoomStatusModel, UpdateRoomStateModel, UpdateRoomEndModel,
    ParticipantLeftModel, ParticipantIsMutedModel, ParticipantIsSpeakingModel, ParticipantIsReadyModel,
    UpdateTranscriptProcessingModel, UpdateTranscriptAudioURLModel,
    CEFRLevel, RoomStatus
)


class TestUserServiceExtensions:
    """Test user service update methods"""
    
    def test_update_user_cefr_model(self):
        """Test UpdateUserCEFRModel creation"""
        model = UpdateUserCEFRModel(
            user_id="test-user-id",
            current_cefr_level=CEFRLevel.B1
        )
        assert model.user_id == "test-user-id"
        assert model.current_cefr_level == CEFRLevel.B1
    
    def test_update_user_last_active_model(self):
        """Test UpdateUserLastActiveModel creation"""
        now = datetime.now()
        model = UpdateUserLastActiveModel(
            user_id="test-user-id",
            last_active=now
        )
        assert model.user_id == "test-user-id"
        assert model.last_active == now
    
    def test_update_user_password_model(self):
        """Test UpdateUserPasswordModel creation"""
        model = UpdateUserPasswordModel(
            user_id="test-user-id",
            old_password="12345678",
            new_password="87654321"
        )
        assert model.user_id == "test-user-id"
        assert model.old_password == "12345678"
        assert model.new_password == "87654321"


class TestRoomServiceExtensions:
    """Test room service update methods"""
    
    def test_update_room_status_model(self):
        """Test UpdateRoomStatusModel creation"""
        now = datetime.now()
        model = UpdateRoomStatusModel(
            room_id="test-room-id",
            status=RoomStatus.IN_PROGRESS,
            started_at=now
        )
        assert model.room_id == "test-room-id"
        assert model.status == RoomStatus.IN_PROGRESS
        assert model.started_at == now
    
    def test_update_room_state_model(self):
        """Test UpdateRoomStateModel creation"""
        model = UpdateRoomStateModel(
            room_id="test-room-id",
            current_round=2,
            current_speaker_index=1,
            participant_count=5
        )
        assert model.room_id == "test-room-id"
        assert model.current_round == 2
        assert model.current_speaker_index == 1
        assert model.participant_count == 5
    
    def test_update_room_end_model(self):
        """Test UpdateRoomEndModel creation"""
        now = datetime.now()
        model = UpdateRoomEndModel(
            room_id="test-room-id",
            status=RoomStatus.COMPLETED,
            ended_at=now,
            duration_seconds=300
        )
        assert model.room_id == "test-room-id"
        assert model.status == RoomStatus.COMPLETED
        assert model.ended_at == now
        assert model.duration_seconds == 300


class TestParticipantServiceExtensions:
    """Test participant service update methods"""
    
    def test_participant_left_model(self):
        """Test ParticipantLeftModel creation"""
        now = datetime.now()
        model = ParticipantLeftModel(
            participant_id="test-participant-id",
            left_at=now,
            ending_cefr_level="B2"
        )
        assert model.participant_id == "test-participant-id"
        assert model.left_at == now
        assert model.ending_cefr_level == "B2"
    
    def test_participant_is_muted_model(self):
        """Test ParticipantIsMutedModel creation"""
        model = ParticipantIsMutedModel(
            participant_id="test-participant-id",
            is_muted=True
        )
        assert model.participant_id == "test-participant-id"
        assert model.is_muted is True
    
    def test_participant_is_speaking_model(self):
        """Test ParticipantIsSpeakingModel creation"""
        model = ParticipantIsSpeakingModel(
            participant_id="test-participant-id",
            is_speaking=True
        )
        assert model.participant_id == "test-participant-id"
        assert model.is_speaking is True
    
    def test_participant_is_ready_model(self):
        """Test ParticipantIsReadyModel creation"""
        model = ParticipantIsReadyModel(
            participant_id="test-participant-id",
            is_ready=True
        )
        assert model.participant_id == "test-participant-id"
        assert model.is_ready is True


class TestTranscriptServiceExtensions:
    """Test transcript service update methods"""
    
    def test_update_transcript_processing_model(self):
        """Test UpdateTranscriptProcessingModel creation"""
        now = datetime.now()
        model = UpdateTranscriptProcessingModel(
            transcript_id="test-transcript-id",
            is_processed=True,
            processed_at=now
        )
        assert model.transcript_id == "test-transcript-id"
        assert model.is_processed is True
        assert model.processed_at == now
    
    def test_update_transcript_audio_url_model(self):
        """Test UpdateTranscriptAudioURLModel creation"""
        model = UpdateTranscriptAudioURLModel(
            transcript_id="test-transcript-id",
            audio_file_url="https://example.com/audio.mp3"
        )
        assert model.transcript_id == "test-transcript-id"
        assert model.audio_file_url == "https://example.com/audio.mp3"


class TestCEFRLevel:
    """Test CEFRLevel enum"""
    
    def test_cefr_levels(self):
        """Test all CEFR levels"""
        levels = [
            CEFRLevel.A0, CEFRLevel.A1, CEFRLevel.A2,
            CEFRLevel.B1, CEFRLevel.B2,
            CEFRLevel.C1, CEFRLevel.C2
        ]
        assert len(levels) == 7
        assert CEFRLevel.A0.value == "A0"
        assert CEFRLevel.C2.value == "C2"


class TestRoomStatus:
    """Test RoomStatus enum"""
    
    def test_room_statuses(self):
        """Test all room statuses"""
        statuses = [
            RoomStatus.WAITING,
            RoomStatus.IN_PROGRESS,
            RoomStatus.COMPLETED,
            RoomStatus.CANCELLED
        ]
        assert len(statuses) == 4
        assert RoomStatus.WAITING.value == "waiting"
        assert RoomStatus.IN_PROGRESS.value == "in_progress"
        assert RoomStatus.COMPLETED.value == "completed"
        assert RoomStatus.CANCELLED.value == "cancelled"
