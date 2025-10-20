"""
Data Models
Domain models for the application
"""
from .participant_pydantic_models import (
    CreateParticipantModel, 
    CreateParticipantResponseModel,
    ParticipantModel,
    ParticipantUpdateModel,
    ParticipantLeftModel,
    ParticipantIsMutedModel,
    ParticipantIsSpeakingModel,
    ParticipantIsReadyModel,
    Participant
)
from .room_pydantic_models import (
    RoomResponseModel, 
    CreateRoomModel, 
    RoomStatus,
    RoomModel,
    UpdateRoomStatusModel,
    UpdateRoomStateModel,
    UpdateRoomEndModel,
    Room
)
from .user_pydantic_models import (
    LoginSignUpResponseModel, 
    LoginModel, 
    SignUpModel,
    UserModel,
    UpdateUserCEFRModel,
    UpdateUserLastActiveModel,
    UpdateUserPasswordModel
)
from .feedback_pydantic_models import (
    InstantFeedbackModel,
    ComprehensiveFeedbackModel,
    FeedbackModel
)
from .transcript_pydantic_models import (
    CreateTranscriptModel,
    TranscriptModel,
    TranscriptOut,
    UpdateTranscriptProcessingModel,
    UpdateTranscriptAudioURLModel
)
from .agent_pydantic_models import (
    CreateAgentModel,
    CreateAgentResponseModel,
    AgentModel,
    AgentUpdateModel,
    AgentTranscriptProcessingModel,
    AgentFeedbackGenerationModel,
    AgentResponseModel,
    AgentInteractionStatsModel,
    AgentHealthModel,
    AgentStatus,
    AgentType,
    AgentModelSource
)
from .enums import CEFRLevel, ParticipantRole

# Aliases for backward compatibility
Participant = ParticipantModel

__all__ = [
    # Participant Models
    "CreateParticipantModel",
    "CreateParticipantResponseModel",
    "ParticipantModel",
    "Participant",  # Alias
    "ParticipantUpdateModel",
    "ParticipantLeftModel",
    "ParticipantIsMutedModel",
    "ParticipantIsSpeakingModel",
    "ParticipantIsReadyModel",
    "ParticipantRole",
    # Room Models
    "RoomResponseModel",
    "CreateRoomModel",
    "RoomModel",
    "RoomStatus",
    "UpdateRoomStatusModel",
    "UpdateRoomStateModel",
    "UpdateRoomEndModel",
    # User Models
    "LoginSignUpResponseModel",
    "LoginModel",
    "SignUpModel",
    "UserModel",
    "UpdateUserCEFRModel",
    "UpdateUserLastActiveModel",
    "UpdateUserPasswordModel",
    # Feedback Models
    "InstantFeedbackModel",
    "ComprehensiveFeedbackModel",
    "FeedbackModel",
    # Transcript Models
    "CreateTranscriptModel",
    "TranscriptModel",
    "TranscriptOut",
    "UpdateTranscriptProcessingModel",
    "UpdateTranscriptAudioURLModel",
    # Agent Models
    "CreateAgentModel",
    "CreateAgentResponseModel",
    "AgentModel",
    "AgentUpdateModel",
    "AgentTranscriptProcessingModel",
    "AgentFeedbackGenerationModel",
    "AgentResponseModel",
    "AgentInteractionStatsModel",
    "AgentHealthModel",
    "AgentStatus",
    "AgentType",
    "AgentModelSource",
    # Enums
    "CEFRLevel",
]
