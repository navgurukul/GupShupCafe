"""
Data Models
Domain models for the application
"""
from .base_dict_model import BaseDictModel, DictMixin
from .participant_pydantic_models import (
    CreateParticipantModel, 
    CreateParticipantResponseModel,
    ParticipantModel,
    ListParticipantsResponseModel,
    UpdateParticipantModel,
    UpdateParticipantResponseModel,
    DeleteParticipantResponseModel,
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
    ListUsersResponseModel,
    UpdateUserModel,
    UpdateUserResponseModel,
    DeleteUserResponseModel,
    UpdateUserCEFRModel,
    UpdateUserLastActiveModel,
    UpdateUserPasswordModel,
)
from .feedback_pydantic_models import (
    CreateInstantFeedbackModel,
    InstantFeedbackModel,
    CreateComprehensiveFeedbackModel,
    ComprehensiveFeedbackModel,
    CreateInstantFeedbackResponseModel,
    CreateComprehensiveFeedbackResponseModel,
    ListFeedbackResponseModel,
    ListInstantFeedbackResponseModel,
    ListComprehensiveFeedbackResponseModel,
    UpdateInstantFeedbackModel,
    UpdateInstantFeedbackResponseModel,
    UpdateComprehensiveFeedbackModel,
    UpdateComprehensiveFeedbackResponseModel,
    DeleteFeedbackResponseModel
)
from .transcript_pydantic_models import (
    CreateTranscriptModel,
    TranscriptModel,
    ListTranscriptsResponseModel,
    UpdateTranscriptModel,
    UpdateTranscriptResponseModel,
    DeleteTranscriptResponseModel,
    UpdateTranscriptProcessingModel,
    UpdateTranscriptAudioURLModel,
)
from .agent_pydantic_models import (
    CreateAgentModel,
    CreateAgentResponseModel,
    AgentModel,
    AgentResponseModel,
    AgentStatus,
    AgentType,
    AgentModelSource,
    ListAgentsResponseModel,
    UpdateAgentModel,
    UpdateAgentResponseModel,
    DeleteAgentResponseModel,
    AgentUpdateModel,
    AgentTranscriptProcessingModel,
    AgentFeedbackGenerationModel,
    AgentInteractionStatsModel,
    AgentHealthModel
)
from .enums import CEFRLevel, ParticipantRole


__all__ = [
    # Base Classes
    "BaseDictModel",
    "DictMixin",
    # Participant Models
    "CreateParticipantModel",
    "CreateParticipantResponseModel",
    "ParticipantModel",
    "ListParticipantsResponseModel",
    "UpdateParticipantModel",
    "UpdateParticipantResponseModel",
    "DeleteParticipantResponseModel",
    "ParticipantLeftModel",
    "ParticipantIsMutedModel",
    "ParticipantIsSpeakingModel",
    "ParticipantIsReadyModel",
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
    "ListUsersResponseModel",
    "UpdateUserModel",
    "UpdateUserResponseModel",
    "DeleteUserResponseModel",
    "UpdateUserCEFRModel",
    "UpdateUserLastActiveModel",
    "UpdateUserPasswordModel",
    # Feedback Models
    "CreateInstantFeedbackModel",
    "InstantFeedbackModel",
    "CreateComprehensiveFeedbackModel",
    "ComprehensiveFeedbackModel",
    "CreateInstantFeedbackResponseModel",
    "CreateComprehensiveFeedbackResponseModel",
    "ListFeedbackResponseModel",
    "ListInstantFeedbackResponseModel",
    "ListComprehensiveFeedbackResponseModel",
    "UpdateInstantFeedbackModel",
    "UpdateInstantFeedbackResponseModel",
    "UpdateComprehensiveFeedbackModel",
    "UpdateComprehensiveFeedbackResponseModel",
    "DeleteFeedbackResponseModel",
    # Transcript Models
    "CreateTranscriptModel",
    "TranscriptModel",
    "ListTranscriptsResponseModel",
    "UpdateTranscriptModel",
    "UpdateTranscriptResponseModel",
    "DeleteTranscriptResponseModel",
    "UpdateTranscriptProcessingModel",
    "UpdateTranscriptAudioURLModel",
    # Agent Models
    "CreateAgentModel",
    "CreateAgentResponseModel",
    "AgentModel",
    "AgentResponseModel",
    "AgentStatus",
    "AgentType",
    "AgentModelSource",
    "ListAgentsResponseModel",
    "UpdateAgentModel",
    "UpdateAgentResponseModel",
    "DeleteAgentResponseModel",
    "AgentUpdateModel",
    "AgentTranscriptProcessingModel",
    "AgentFeedbackGenerationModel",
    "AgentInteractionStatsModel",
    "AgentHealthModel",
    # Enums
    "CEFRLevel",
    "ParticipantRole",
]
