"""
Data Models
Domain models for the application
"""
from .base_dict_model import BaseDictModel, DictMixin
from .participant_pydantic_models import (
    CreateParticipantModel, 
    CreateParticipantResponseModel,
    GetParticipantModel,
    ParticipantModel,
    ListParticipantsResponseModel,
    UpdateParticipantModel,
    UpdateParticipantResponseModel,
    DeleteParticipantResponseModel
)
from .room_pydantic_models import (
    CreateRoomModel,
    CreateRoomResponseModel,
    GetRoomModel,
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
    GetUserModel,
    UserModel,
    ListUsersResponseModel,
    UpdateUserModel,
    UpdateUserResponseModel,
    DeleteUserResponseModel
)
from .feedback_pydantic_models import (
    CreateInstantFeedbackModel,
    GetInstantFeedbackModel,
    InstantFeedbackModel,
    CreateComprehensiveFeedbackModel,
    GetComprehensiveFeedbackModel,
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
    GetTranscriptModel,
    TranscriptModel,
    ListTranscriptsResponseModel,
    UpdateTranscriptModel,
    UpdateTranscriptResponseModel,
    DeleteTranscriptResponseModel,
)
from .agent_pydantic_models import (
    CreateAgentModel,
    CreateAgentResponseModel,
    GetAgentModel,
    AgentModel,
    AgentReplyModel,
    AgentReplyResponseModel,
    AgentStatus,
    AgentType,
    AgentModelSource,
    ListAgentsResponseModel,
    UpdateAgentModel,
    UpdateAgentResponseModel,
    DeleteAgentResponseModel
)
from .enums import CEFRLevel, ParticipantRole


__all__ = [
    # Base Classes
    "BaseDictModel",
    "DictMixin",
    # Participant Models
    "CreateParticipantModel",
    "CreateParticipantResponseModel",
    "GetParticipantModel",
    "ParticipantModel",
    "ListParticipantsResponseModel",
    "UpdateParticipantModel",
    "UpdateParticipantResponseModel",
    "DeleteParticipantResponseModel",
    # Room Models
    "CreateRoomModel",
    "CreateRoomResponseModel",
    "GetRoomModel",
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
    "GetUserModel",
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
    "GetInstantFeedbackModel",
    "InstantFeedbackModel",
    "CreateComprehensiveFeedbackModel",
    "GetComprehensiveFeedbackModel",
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
    "GetTranscriptModel",
    "TranscriptModel",
    "ListTranscriptsResponseModel",
    "UpdateTranscriptModel",
    "UpdateTranscriptResponseModel",
    "DeleteTranscriptResponseModel",
    # Agent Models
    "CreateAgentModel",
    "CreateAgentResponseModel",
    "GetAgentModel",
    "AgentModel",
    "AgentReplyModel",
    "AgentReplyResponseModel",
    "AgentStatus",
    "AgentType",
    "AgentModelSource",
    "ListAgentsResponseModel",
    "UpdateAgentModel",
    "UpdateAgentResponseModel",
    "DeleteAgentResponseModel",
    # Enums
    "CEFRLevel",
    "ParticipantRole",
]
