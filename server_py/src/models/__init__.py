"""
Data Models
Domain models for the application
"""
from .base_dict_model import BaseDictModel, DictMixin
from .participant_pydantic_models import (
    CreateParticipantModel, 
    CreateParticipantResponseModel,
    ParticipantModel,
    ParticipantLeftModel,
    ParticipantIsMutedModel,
    ParticipantIsSpeakingModel,
    ParticipantIsReadyModel
)
from .room_pydantic_models import (
    CreateRoomModel,
    CreateRoomResponseModel,
    RoomModel,
    ListRoomsResponseModel,
    UpdateRoomModel,
    UpdateRoomResponseModel,
    DeleteRoomResponseModel,
    RoomStatus
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
    CreateInstantFeedbackModel,
    InstantFeedbackModel,
    CreateComprehensiveFeedbackModel,
    ComprehensiveFeedbackModel,
)
from .transcript_pydantic_models import (
    CreateTranscriptModel,
    TranscriptModel,
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


__all__ = [
    # Base Classes
    "BaseDictModel",
    "DictMixin",
    # Participant Models
    "CreateParticipantModel",
    "ParticipantModel",
    "CreateParticipantResponseModel",
    "ParticipantUpdateModel",
    "ParticipantLeftModel",
    "ParticipantIsMutedModel",
    "ParticipantIsSpeakingModel",
    "ParticipantIsReadyModel",
    "ParticipantRole",
    # Room Models
    "CreateRoomModel",
    "CreateRoomResponseModel",
    "RoomModel",
    "ListRoomsResponseModel",
    "UpdateRoomModel",
    "UpdateRoomResponseModel",
    "DeleteRoomResponseModel",
    "RoomStatus",
    # User Models
    "LoginSignUpResponseModel",
    "LoginModel",
    "SignUpModel",
    "UserModel",
    "UpdateUserCEFRModel",
    "UpdateUserLastActiveModel",
    "UpdateUserPasswordModel",
    # Feedback Models
    "CreateInstantFeedbackModel",
    "InstantFeedbackModel",
    "CreateComprehensiveFeedbackModel",
    "ComprehensiveFeedbackModel",
    # Transcript Models
    "CreateTranscriptModel",
    "TranscriptModel",
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
