from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict

class FeedbackModel(BaseModel):
    """
    AI-generated English feedback for a transcript.
    Matches the schema from product_system_design.md
    """
    id: str = Field(..., description="Feedback UUID")
    room_id: str = Field(..., description="Room ID")
    participant_id: str = Field(..., description="Participant ID")
    user_id: str = Field(..., description="User ID")
    
    # Feedback Type
    feedback_type: str = Field(..., description="Feedback type: 'instant' (2-3s) or 'comprehensive'")
    
    # Display Message (for UI modal, MVP)
    display_message: str | None = Field(default=None, description="Formatted feedback for modal")

    # Grammar Feedback (optional, extended)
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
    id: str = Field(..., description="UUID, Primary Key")
    room_id: str = Field(..., description="Foreign Key from {{Room}}")
    participant_id: str = Field(..., description="Foreign Key from {{Participant}}")
    user_id: str = Field(..., description="Foreign Key (from {{User}})")

    # Feedback Type
    feedback_type: str = Field(..., description="Feedback type: 'instant' (2-3s) or 'comprehensive'")

    # --- Instant Feedback Fields ---
    # (Populated if feedback_type == "instant")
    # random insights from any 5 points from the comprehensive fields below
    # Display Message (For UI)
    display_message: str = Field(..., description="Formatted feedback for modal")

    # AI Agent Info
    agent_id: str = Field(..., description="AI Agent instance")
    agent_model: str = Field(..., description='"gemini-2.5-flash" or "bedrock-models"')

    created_at: datetime = Field(..., description="Feedback creation timestamp")

class ComprehensiveFeedbackModel(BaseModel):
    """Detailed feedback at the end of discussion"""
    id: str = Field(..., description="UUID, Primary Key")
    room_id: str = Field(..., description="Foreign Key from {{Room}}")
    participant_id: str = Field(..., description="Foreign Key from {{Participant}}")
    user_id: str = Field(..., description="Foreign Key (from {{User}})")

    # Feedback Type
    feedback_type: str = Field(..., description='"instant" or "comprehensive"')

    # --- Comprehensive Feedback Fields ---
    # (Populated if feedback_type == "comprehensive")

    # CEFR Level Summary
    cefr_speaking: str = Field(..., description="CEFR speaking level (e.g., 'A0', 'A1', 'A2', 'B1', 'B2', 'C1','C2')")
    cefr_listening: str = Field(..., description="CEFR listening level (e.g., 'A0', 'A1', 'A2', 'B1', 'B2', 'C1','C2')")

    # Listening & Responsiveness
    listening_activity: str = Field(..., description="Describe how actively they listen")
    response_effectiveness: str = Field(..., description="Mention if they respond to others’ points effectively")
    listening_positive_observation: str = Field(..., description="Positive observation about listening")
    listening_improvement_suggestion: str = Field(..., description="Specific suggestion, e.g., connecting your ideas more closely to others or acknowledging their points before speaking")

    # Speaking Quality
    fluency: str = Field(..., description="Speaking fluency (e.g., 'steady flow', 'some pauses')")
    sentence_complexity: str = Field(..., description="Sentence complexity (e.g., 'simple', 'medium', 'complex')")
    pace: str = Field(..., description="Speaking pace (e.g., 'smooth', 'rushed', 'hesitant')")
    filler_examples: str = Field(..., description="Filler examples (e.g., ['um', 'like'])")
    grammar: str = Field(..., description="Grammar accuracy (e.g., 'mostly accurate', 'needs improvement')")

    # Vocabulary & Expression
    vocab_examples: str = Field(..., description="Vocabulary examples (e.g., ['adequate', 'perform'])")
    vocab_analysis: str = Field(..., description="Vocabulary analysis (e.g., 'range', 'confidence', 'basic usage')")
    vocab_positive_observation: str = Field(..., description="Positive observation about vocabulary (e.g., tried new words or expressions)")
    vocab_improvement_suggestion: str = Field(..., description="Vocabulary improvement suggestion, e.g., try using more descriptive words or synonyms to make your points stronger.")

    # Depth of Understanding & Content
    understanding_level: str = Field(..., description="Depth of understanding (e.g., 'basic', 'fair', 'deep')")
    explanation_quality: str = Field(..., description="Explanation quality (e.g., 'logical', 'reflective', 'opinion-based')")
    interaction_style: str = Field(..., description="Interaction style (e.g., 'compare, build on, or respond')")
    depth_of_understanding_suggestion: str = Field(..., description="Suggestion for depth of understanding (e.g., use examples, explanations, or comparisons)")

    # Comparative Reflection (Optional)
    comparative_performance: str = Field(..., description="Comparative performance (e.g., more fluent / more confident / less detailed / more reflective compared to others)")
    comparative_suggestion: str = Field(..., description="Specific suggestion (e.g., summarizing others’ points, asking questions, or elaborating more)")

    # Summary Feedback
    summary_strength: str = Field(..., description="Strength area (e.g., expressing your opinions clearly or staying engaged)")
    summary_improvement_area: str = Field(..., description="Specific improvement area (e.g., reducing fillers, using longer sentences, expanding vocabulary, or deepening reasoning)")
    target_cefr_level: str = Field(..., description="Target CEFR level (e.g., 'B2')")



    # AI Agent Info
    agent_id: str  # EnglishFeedbackAgent instance
    agent_model: str  # "gemini-1.5-flash" or "bedrock-claude-3"
    
    created_at: datetime
