from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

class FeedbackModel(BaseModel):
    """
    AI-generated English feedback for a transcript.
    Matches the schema from product_system_design.md
    """
    id: str = Field(..., description="Feedback UUID")
    session_id: str = Field(..., description="Session ID")
    participant_id: str = Field(..., description="Participant ID")
    user_id: str = Field(..., description="User ID")
    
    # Feedback Type
    feedback_type: str = Field(..., description="Feedback type: 'instant' (2-3s) or 'comprehensive'")
    
    # Grammar Feedback
    grammar_issues: List[Dict] = Field(
        default_factory=list,
        description="List of grammar issues with original, corrected, reason, and severity"
    )
    
    # Vocabulary Feedback
    vocabulary_level: Optional[str] = Field(None, description="Vocabulary level: basic, intermediate, advanced")
    vocabulary_suggestions: List[Dict] = Field(
        default_factory=list,
        description="Vocabulary suggestions with word_used, alternatives, and context"
    )
    
    # Fluency Feedback
    fluency_issues: List[str] = Field(default_factory=list, description="List of fluency issues")
    fluency_comments: Optional[str] = Field(None, description="Detailed fluency comments")
    
    # Improvement Suggestions
    suggestions: List[str] = Field(default_factory=list, description="Top 3-5 actionable suggestions")
    
    # Positive Feedback
    strengths: List[str] = Field(default_factory=list, description="What the user did well")
    
    # Metadata
    created_at: datetime = Field(..., description="Feedback creation timestamp")

class InstantFeedbackModel(BaseModel):
    """Quick feedback during speaking (2-3 seconds response time)"""
    participant_id: str = Field(..., description="Participant receiving feedback")
    transcript: str = Field(..., description="Recent speech transcript")
    feedback_message: str = Field(..., description="Instant feedback message")
    grammar_issues: List[Dict] = Field(default_factory=list, description="Quick grammar corrections")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")

class ComprehensiveFeedbackModel(BaseModel):
    """Detailed feedback at end of discussion"""
    participant_id: str = Field(..., description="Participant receiving feedback")
    session_id: str = Field(..., description="Session ID")
    
    # CEFR Assessment
    cefr_level: str = Field(..., description="Estimated CEFR level: A0, A1, A2, B1, B2, C1, C2")
    cefr_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in CEFR assessment")
    
    # Detailed Scores (0-10 scale)
    grammar_score: float = Field(..., ge=0.0, le=10.0, description="Grammar score")
    vocabulary_score: float = Field(..., ge=0.0, le=10.0, description="Vocabulary score")
    fluency_score: float = Field(..., ge=0.0, le=10.0, description="Fluency score")
    overall_score: float = Field(..., ge=0.0, le=10.0, description="Overall score (average)")
    
    # Detailed Feedback
    grammar_issues: List[Dict] = Field(default_factory=list, description="All grammar issues")
    vocabulary_suggestions: List[Dict] = Field(default_factory=list, description="Vocabulary improvements")
    fluency_issues: List[str] = Field(default_factory=list, description="Fluency problems")
    suggestions: List[str] = Field(default_factory=list, description="Actionable suggestions")
    strengths: List[str] = Field(default_factory=list, description="Positive aspects")
    
    # Display
    display_message: str = Field(..., description="Formatted feedback for UI modal")
    
    # Processing info
    agent_id: Optional[str] = Field(None, description="EnglishFeedbackAgent instance ID")
    agent_model: Optional[str] = Field(None, description="AI model used (e.g., gemini-1.5-flash)")
    generation_time_ms: Optional[int] = Field(None, description="Time to generate feedback in ms")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")
