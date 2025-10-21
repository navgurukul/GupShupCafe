from pydantic import Field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

from .base_dict_model import BaseDictModel
from .enums import CEFRLevel
from .agent_pydantic_models import AgentModelSource

# --- Base Name Models ---

class BaseFeedbackModel(BaseDictModel):
    """Base model with name field for any model type"""
    name: str = Field(..., min_length=1, description="Model name (e.g., Transcript, User, etc.)")

# --- New Enums Defined ---

class FeedbackType(str, Enum):
    INSTANT = "instant"
    COMPREHENSIVE = "comprehensive"

class VocabularyLevel(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class FluencyLevel(str, Enum):
    STEADY_FLOW = "steady flow"
    SOME_PAUSES = "some pauses"
    HESITANT = "hesitant"

class ComplexityLevel(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"

class SpeakingPace(str, Enum):
    SMOOTH = "smooth"
    RUSHED = "rushed"
    HESITANT = "hesitant"

class GrammarAccuracy(str, Enum):
    MOSTLY_ACCURATE = "mostly accurate"
    NEEDS_IMPROVEMENT = "needs improvement"

class UnderstandingLevel(str, Enum):
    BASIC = "basic"
    FAIR = "fair"
    DEEP = "deep"

class ExplanationQuality(str, Enum):
    LOGICAL = "logical"
    REFLECTIVE = "reflective"
    OPINION_BASED = "opinion-based"


# --- Updated Pydantic Models ---

class CreateInstantFeedbackModel(BaseFeedbackModel):
    """Quick feedback during speaking (2-3 seconds response time)"""
    room_id: str = Field(..., description="Foreign Key from {{Room}}")
    participant_id: str = Field(..., description="Foreign Key from {{Participant}}")
    user_id: str = Field(..., description="Foreign Key (from {{User}})")

    # Feedback Type
    feedback_type: FeedbackType = Field(..., description="Feedback type: 'instant' (2-3s) or 'comprehensive'")

    # --- Instant Feedback Fields ---
    # (Populated if feedback_type == "instant")
    # random insights from any 5 points from the comprehensive fields below
    # Display Message (For UI)
    display_message: str = Field(..., description="Formatted feedback for modal")

    # AI Agent Info
    agent_id: str = Field(..., description="AI Agent instance")
    agent_model: AgentModelSource = Field(..., description='"gemini-2.5-flash" or "bedrock-models"')

# --- Model for data read from DB (includes PK and creation time) ---

class InstantFeedbackModel(CreateInstantFeedbackModel):
    """Full feedback model as represented in the database."""
    feedback_id: str = Field(..., description="UUID, Primary Key")
    created_at: datetime = Field(..., description="Feedback creation timestamp")

    class Config:
        from_attributes = True

class CreateComprehensiveFeedbackModel(BaseFeedbackModel):
    """Detailed feedback at the end of discussion"""
    room_id: str = Field(..., description="Foreign Key from {{Room}}")
    participant_id: str = Field(..., description="Foreign Key from {{Participant}}")
    user_id: str = Field(..., description="Foreign Key (from {{User}})")

    # Feedback Type
    feedback_type: FeedbackType = Field(..., description='"instant" or "comprehensive"')

    # --- Comprehensive Feedback Fields ---
    # (Populated if feedback_type == "comprehensive")

    # CEFR Level Summary
    cefr_speaking: CEFRLevel = Field(..., description="CEFR speaking level (e.g., 'A0', 'A1', 'A2', 'B1', 'B2', 'C1','C2')")
    cefr_listening: CEFRLevel = Field(..., description="CEFR listening level (e.g., 'A0', 'A1', 'A2', 'B1', 'B2', 'C1','C2')")

    # Listening & Responsiveness
    listening_activity: str = Field(..., description="Describe how actively they listen")
    response_effectiveness: str = Field(..., description="Mention if they respond to others’ points effectively")
    listening_positive_observation: str = Field(..., description="Positive observation about listening")
    listening_improvement_suggestion: str = Field(..., description="Specific suggestion, e.g., connecting your ideas more closely to others or acknowledging their points before speaking")

    # Speaking Quality
    fluency: FluencyLevel = Field(..., description="Speaking fluency (e.g., 'steady flow', 'some pauses')")
    sentence_complexity: ComplexityLevel = Field(..., description="Sentence complexity (e.g., 'simple', 'medium', 'complex')")
    pace: SpeakingPace = Field(..., description="Speaking pace (e.g., 'smooth', 'rushed', 'hesitant')")
    filler_examples: str = Field(..., description="Filler examples (e.g., ['um', 'like'])") # Stays as str, likely for JSON list
    grammar: GrammarAccuracy = Field(..., description="Grammar accuracy (e.g., 'mostly accurate', 'needs improvement')")

    # Vocabulary & Expression
    vocab_examples: str = Field(..., description="Vocabulary examples (e.g., ['adequate', 'perform'])") # Stays as str, likely for JSON list
    vocab_analysis: str = Field(..., description="Vocabulary analysis (e.g., 'range', 'confidence', 'basic usage')")
    vocab_positive_observation: str = Field(..., description="Positive observation about vocabulary (e.g., tried new words or expressions)")
    vocab_improvement_suggestion: str = Field(..., description="Vocabulary improvement suggestion, e.g., try using more descriptive words or synonyms to make your points stronger.")

    # Depth of Understanding & Content
    understanding_level: UnderstandingLevel = Field(..., description="Depth of understanding (e.g., 'basic', 'fair', 'deep')")
    explanation_quality: ExplanationQuality = Field(..., description="Explanation quality (e.g., 'logical', 'reflective', 'opinion-based')")
    interaction_style: str = Field(..., description="Interaction style (e.g., 'compare, build on, or respond')")
    depth_of_understanding_suggestion: str = Field(..., description="Suggestion for depth of understanding (e.g., use examples, explanations, or comparisons)")

    # Comparative Reflection (Optional)
    comparative_performance: str = Field(..., description="Comparative performance (e.g., more fluent / more confident / less detailed / more reflective compared to others)")
    comparative_suggestion: str = Field(..., description="Specific suggestion (e.g., summarizing others’ points, asking questions, or elaborating more)")

    # Summary Feedback
    summary_strength: str = Field(..., description="Strength area (e.g., expressing your opinions clearly or staying engaged)")
    summary_improvement_area: str = Field(..., description="Specific improvement area (e.g., reducing fillers, using longer sentences, expanding vocabulary, or deepening reasoning)")
    target_cefr_level: CEFRLevel = Field(..., description="Target CEFR level (e.g., 'B2')")

    # AI Agent Info
    agent_id: str  # AI Agent instance
    agent_model: AgentModelSource  # "gemini-2.5-flash" or "bedrock-claude-3"
    
# --- Model for data read from DB (includes PK and creation time) ---

class ComprehensiveFeedbackModel(CreateComprehensiveFeedbackModel):
		"""Full feedback model as represented in the database."""
		feedback_id: str = Field(..., description="UUID, Primary Key")
		
		created_at: datetime = Field(..., description="Feedback creation timestamp")

		class Config:
				from_attributes = True


# --- Response Models for Instant Feedback ---

class CreateInstantFeedbackResponseModel(BaseDictModel):
    """Response model for instant feedback creation"""
    status: str = Field(..., description="Feedback creation status message")
    data: InstantFeedbackModel = Field(..., description="Created instant feedback data")
    message: Optional[str] = Field(None, description="Additional message")

# --- Response Models for Comprehensive Feedback ---

class CreateComprehensiveFeedbackResponseModel(BaseDictModel):
    """Response model for comprehensive feedback creation"""
    status: str = Field(..., description="Feedback creation status message")
    data: ComprehensiveFeedbackModel = Field(..., description="Created comprehensive feedback data")
    message: Optional[str] = Field(None, description="Additional message")

# --- List Models ---

class ListFeedbackResponseModel(BaseDictModel):
    """Response model for listing feedback"""
    status: str = Field(..., description="List operation status")
    data: List[Dict] = Field(..., description="List of feedback (mixed instant and comprehensive)")
    message: Optional[str] = Field(None, description="Additional message")

class ListInstantFeedbackResponseModel(BaseDictModel):
    """Response model for listing instant feedback"""
    status: str = Field(..., description="List operation status")
    data: List[InstantFeedbackModel] = Field(..., description="List of instant feedback")
    message: Optional[str] = Field(None, description="Additional message")

class ListComprehensiveFeedbackResponseModel(BaseDictModel):
    """Response model for listing comprehensive feedback"""
    status: str = Field(..., description="List operation status")
    data: List[ComprehensiveFeedbackModel] = Field(..., description="List of comprehensive feedback")
    message: Optional[str] = Field(None, description="Additional message")

# --- Update Models ---

class UpdateInstantFeedbackModel(BaseDictModel):
    """Model for updating instant feedback details."""
    display_message: Optional[str] = Field(None, description="Updated display message")
    agent_id: Optional[str] = Field(None, description="Updated AI Agent instance")
    agent_model: Optional[AgentModelSource] = Field(None, description="Updated agent model")

class UpdateInstantFeedbackResponseModel(BaseDictModel):
    """Response model for updating instant feedback"""
    status: str = Field(..., description="Update operation status")
    data: UpdateInstantFeedbackModel = Field(..., description="Updated instant feedback data")
    message: Optional[str] = Field(None, description="Additional message")

class UpdateComprehensiveFeedbackModel(BaseDictModel):
    """Model for updating comprehensive feedback details."""
    cefr_speaking: Optional[CEFRLevel] = Field(None, description="Updated CEFR speaking level")
    cefr_listening: Optional[CEFRLevel] = Field(None, description="Updated CEFR listening level")
    listening_activity: Optional[str] = Field(None, description="Updated listening activity description")
    response_effectiveness: Optional[str] = Field(None, description="Updated response effectiveness")
    listening_positive_observation: Optional[str] = Field(None, description="Updated positive listening observation")
    listening_improvement_suggestion: Optional[str] = Field(None, description="Updated listening improvement suggestion")
    fluency: Optional[FluencyLevel] = Field(None, description="Updated speaking fluency")
    sentence_complexity: Optional[ComplexityLevel] = Field(None, description="Updated sentence complexity")
    pace: Optional[SpeakingPace] = Field(None, description="Updated speaking pace")
    filler_examples: Optional[str] = Field(None, description="Updated filler examples")
    grammar: Optional[GrammarAccuracy] = Field(None, description="Updated grammar accuracy")
    vocab_examples: Optional[str] = Field(None, description="Updated vocabulary examples")
    vocab_analysis: Optional[str] = Field(None, description="Updated vocabulary analysis")
    vocab_positive_observation: Optional[str] = Field(None, description="Updated vocabulary positive observation")
    vocab_improvement_suggestion: Optional[str] = Field(None, description="Updated vocabulary improvement suggestion")
    understanding_level: Optional[UnderstandingLevel] = Field(None, description="Updated understanding level")
    explanation_quality: Optional[ExplanationQuality] = Field(None, description="Updated explanation quality")
    interaction_style: Optional[str] = Field(None, description="Updated interaction style")
    depth_of_understanding_suggestion: Optional[str] = Field(None, description="Updated depth understanding suggestion")
    comparative_performance: Optional[str] = Field(None, description="Updated comparative performance")
    comparative_suggestion: Optional[str] = Field(None, description="Updated comparative suggestion")
    summary_strength: Optional[str] = Field(None, description="Updated summary strength")
    summary_improvement_area: Optional[str] = Field(None, description="Updated summary improvement area")
    target_cefr_level: Optional[CEFRLevel] = Field(None, description="Updated target CEFR level")
    agent_id: Optional[str] = Field(None, description="Updated AI Agent instance")
    agent_model: Optional[AgentModelSource] = Field(None, description="Updated agent model")

class UpdateComprehensiveFeedbackResponseModel(BaseDictModel):
    """Response model for updating comprehensive feedback"""
    status: str = Field(..., description="Update operation status")
    data: UpdateComprehensiveFeedbackModel = Field(..., description="Updated comprehensive feedback data")
    message: Optional[str] = Field(None, description="Additional message")

# --- Delete Models ---

class DeleteFeedbackResponseModel(BaseDictModel):
    """Response model for deleting feedback"""
    status: str = Field(..., description="Delete operation status")
    data: str = Field(..., description="Deleted feedback ID")
    message: Optional[str] = Field(None, description="Additional message")
   
