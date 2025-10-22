import uuid
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models import (
    InstantFeedbackModel, 
    ComprehensiveFeedbackModel,
    CreateInstantFeedbackResponseModel,
    CreateComprehensiveFeedbackResponseModel,
    ListFeedbackResponseModel,
    DeleteFeedbackResponseModel
)
from src.database.db_connection import conn, cursor

class Feedback_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor

    def create_instant_feedback(self, model: InstantFeedbackModel) -> CreateInstantFeedbackResponseModel:
        """Create instant feedback"""
        try:
            from datetime import datetime
            feedback_id = model.id if hasattr(model, 'id') and model.id else uuid.uuid4().hex
            created_at = model.created_at if hasattr(model, 'created_at') and model.created_at else datetime.now()
            
            self.cursor.execute(
                """
                INSERT INTO feedback (
                    id, room_id, participant_id, user_id, feedback_type,
                    display_message, agent_id, agent_model, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    feedback_id,
                    model.room_id,
                    model.participant_id,
                    model.user_id,
                    model.feedback_type.value,
                    model.display_message,
                    model.agent_id,
                    model.agent_model.value,
                    created_at,
                ),
            )
            self.conn.commit()
            
            # Create the feedback model for response
            created_feedback = InstantFeedbackModel(
                id=feedback_id,
                room_id=model.room_id,
                participant_id=model.participant_id,
                user_id=model.user_id,
                feedback_type=model.feedback_type,
                display_message=model.display_message,
                agent_id=model.agent_id,
                agent_model=model.agent_model,
                created_at=created_at
            )
            
            return CreateInstantFeedbackResponseModel(
                status="success",
                data=created_feedback,
                message="Instant feedback created successfully"
            )
        except Exception as e:
            print(f"[Backend] Error creating instant feedback: {e}")
            self.conn.rollback()
            return CreateInstantFeedbackResponseModel(
                status="failure",
                data=None,
                message=f"Failed to save instant feedback: {e}"
            )

    def create_comprehensive_feedback(self, model: ComprehensiveFeedbackModel) -> CreateComprehensiveFeedbackResponseModel:
        """Create comprehensive feedback"""
        try:
            from datetime import datetime
            feedback_id = uuid.uuid4().hex
            created_at = datetime.now()
            
            self.cursor.execute(
                """
                INSERT INTO feedback (
                    id, room_id, participant_id, user_id, feedback_type,
                    display_message, agent_id, agent_model, created_at,
                    cefr_speaking, cefr_listening, listening_activity, response_effectiveness,
                    listening_positive_observation, listening_improvement_suggestion,
                    fluency, sentence_complexity, pace, filler_examples, grammar,
                    vocab_examples, vocab_analysis, vocab_positive_observation, vocab_improvement_suggestion,
                    understanding_level, explanation_quality, interaction_style, depth_of_understanding_suggestion,
                    comparative_performance, comparative_suggestion,
                    summary_strength, summary_improvement_area, target_cefr_level
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    feedback_id,
                    model.room_id,
                    model.participant_id,
                    model.user_id,
                    model.feedback_type.value,
                    None,  # display_message not in comprehensive model
                    model.agent_id,
                    model.agent_model.value,
                    created_at,
                    model.cefr_speaking.value,
                    model.cefr_listening.value,
                    model.listening_activity,
                    model.response_effectiveness,
                    model.listening_positive_observation,
                    model.listening_improvement_suggestion,
                    model.fluency.value,
                    model.sentence_complexity.value,
                    model.pace.value,
                    model.filler_examples,  # Already a string in model
                    model.grammar.value,
                    model.vocab_examples,  # Already a string in model
                    model.vocab_analysis,
                    model.vocab_positive_observation,
                    model.vocab_improvement_suggestion,
                    model.understanding_level.value,
                    model.explanation_quality.value,
                    model.interaction_style,
                    model.depth_of_understanding_suggestion,
                    model.comparative_performance,
                    model.comparative_suggestion,
                    model.summary_strength,
                    model.summary_improvement_area,
                    model.target_cefr_level.value,
                ),
            )
            self.conn.commit()
            
            # Create the feedback model for response
            created_feedback = ComprehensiveFeedbackModel(
                id=feedback_id,
                room_id=model.room_id,
                participant_id=model.participant_id,
                user_id=model.user_id,
                feedback_type=model.feedback_type,
                agent_id=model.agent_id,
                agent_model=model.agent_model,
                cefr_speaking=model.cefr_speaking,
                cefr_listening=model.cefr_listening,
                listening_activity=model.listening_activity,
                response_effectiveness=model.response_effectiveness,
                listening_positive_observation=model.listening_positive_observation,
                listening_improvement_suggestion=model.listening_improvement_suggestion,
                fluency=model.fluency,
                sentence_complexity=model.sentence_complexity,
                pace=model.pace,
                filler_examples=model.filler_examples,
                grammar=model.grammar,
                vocab_examples=model.vocab_examples,
                vocab_analysis=model.vocab_analysis,
                vocab_positive_observation=model.vocab_positive_observation,
                vocab_improvement_suggestion=model.vocab_improvement_suggestion,
                understanding_level=model.understanding_level,
                explanation_quality=model.explanation_quality,
                interaction_style=model.interaction_style,
                depth_of_understanding_suggestion=model.depth_of_understanding_suggestion,
                comparative_performance=model.comparative_performance,
                comparative_suggestion=model.comparative_suggestion,
                summary_strength=model.summary_strength,
                summary_improvement_area=model.summary_improvement_area,
                target_cefr_level=model.target_cefr_level,
                created_at=created_at
            )
            
            return CreateComprehensiveFeedbackResponseModel(
                status="success",
                data=created_feedback,
                message="Comprehensive feedback created successfully"
            )
        except Exception as e:
            print(f"[Backend] Error creating comprehensive feedback: {e}")
            self.conn.rollback()
            return CreateComprehensiveFeedbackResponseModel(
                status="failure",
                data=None,
                message=f"Failed to save comprehensive feedback: {e}"
            )

    def list_feedback_for_participant(self, participant_id: str) -> ListFeedbackResponseModel:
        """List feedback for participant"""
        try:
            self.cursor.execute(
                "SELECT * FROM feedback WHERE participant_id=? ORDER BY created_at DESC",
                (participant_id,),
            )
            rows = self.cursor.fetchall()
            cols = [desc[0] for desc in self.cursor.description]
            feedback_data = [dict(zip(cols, row)) for row in rows]
            
            return ListFeedbackResponseModel(
                status="success",
                data=feedback_data,
                message="Feedback listed successfully"
            )
        except Exception as e:
            print(f"[Backend] Error fetching feedback: {e}")
            return ListFeedbackResponseModel(
                status="failure",
                data=[],
                message=f"Failed to fetch feedback: {e}"
            )

    def list_feedback_for_room(self, room_id: str) -> ListFeedbackResponseModel:
        """List feedback for room"""
        try:
            self.cursor.execute(
                "SELECT * FROM feedback WHERE room_id=? ORDER BY created_at DESC",
                (room_id,),
            )
            rows = self.cursor.fetchall()
            cols = [desc[0] for desc in self.cursor.description]
            feedback_data = [dict(zip(cols, row)) for row in rows]
            
            return ListFeedbackResponseModel(
                status="success",
                data=feedback_data,
                message="Room feedback listed successfully"
            )
        except Exception as e:
            print(f"[Backend] Error fetching feedback for room: {e}")
            return ListFeedbackResponseModel(
                status="failure",
                data=[],
                message=f"Failed to fetch feedback for room: {e}"
            )

    def get_feedback(self, feedback_id: str):
        """Get single feedback"""
        try:
            self.cursor.execute("SELECT * FROM feedback WHERE id=?", (feedback_id,))
            row = self.cursor.fetchone()
            if not row:
                return {"success": False, "error": "Feedback not found"}
            
            cols = [d[0] for d in self.cursor.description]
            feedback_data = dict(zip(cols, row))
            return {"success": True, "data": feedback_data}
        except Exception as e:
            print(f"[Backend] Error fetching feedback: {e}")
            return {"success": False, "error": f"Failed to fetch feedback: {e}"}

    def delete_feedback(self, feedback_id: str) -> DeleteFeedbackResponseModel:
        """Delete feedback"""
        try:
            self.cursor.execute("DELETE FROM feedback WHERE id=?", (feedback_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return DeleteFeedbackResponseModel(
                    status="success",
                    data=feedback_id,
                    message="Feedback deleted successfully"
                )
            else:
                return DeleteFeedbackResponseModel(
                    status="failure",
                    data=feedback_id,
                    message="Feedback not found"
                )
        except Exception as e:
            print(f"[Backend] Error deleting feedback: {e}")
            self.conn.rollback()
            return DeleteFeedbackResponseModel(
                status="failure",
                data=feedback_id,
                message=f"Failed to delete feedback: {e}"
            )

# Singleton instance
feedback_service = Feedback_service()