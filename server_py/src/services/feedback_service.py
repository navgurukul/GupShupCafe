import uuid
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.feedback_pydantic_models import InstantFeedbackModel, ComprehensiveFeedbackModel
from src.database.db_connection import conn, cursor

class Feedback_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor

    def create_instant_feedback(self, model: InstantFeedbackModel) -> Dict[str, Any]:
        """Create instant feedback
        
        # FLAG: NOT CONVERTIBLE - This function returns Dict instead of pydantic model
        # TODO: Convert to use CreateInstantFeedbackResponseModel
        """
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
            return {"success": True, "data": {"id": feedback_id}}
        except Exception as e:
            print(f"[Backend] Error creating instant feedback: {e}")
            self.conn.rollback()
            return {"success": False, "error": f"Failed to save instant feedback: {e}"}

    def create_comprehensive_feedback(self, model: ComprehensiveFeedbackModel) -> Dict[str, Any]:
        """Create comprehensive feedback
        
        # FLAG: NOT CONVERTIBLE - This function returns Dict instead of pydantic model
        # TODO: Convert to use CreateComprehensiveFeedbackResponseModel
        """
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
            return {"success": True, "data": {"id": feedback_id}}
        except Exception as e:
            print(f"[Backend] Error creating comprehensive feedback: {e}")
            self.conn.rollback()
            return {"success": False, "error": f"Failed to save comprehensive feedback: {e}"}

    def list_feedback_for_participant(self, participant_id: str) -> Dict[str, Any]:
        """List feedback for participant
        
        # FLAG: NOT CONVERTIBLE - This function returns Dict instead of pydantic model
        # TODO: Convert to use ListFeedbackResponseModel
        """
        try:
            self.cursor.execute(
                "SELECT * FROM feedback WHERE participant_id=? ORDER BY created_at DESC",
                (participant_id,),
            )
            rows = self.cursor.fetchall()
            cols = [desc[0] for desc in self.cursor.description]
            return {"success": True, "data": [dict(zip(cols, row)) for row in rows]}
        except Exception as e:
            print(f"[Backend] Error fetching feedback: {e}")
            return {"success": False, "error": f"Failed to fetch feedback: {e}"}

    def list_feedback_for_room(self, room_id: str) -> Dict[str, Any]:
        """List feedback for room
        
        # FLAG: NOT CONVERTIBLE - This function returns Dict instead of pydantic model
        # TODO: Convert to use ListFeedbackResponseModel
        """
        try:
            self.cursor.execute(
                "SELECT * FROM feedback WHERE room_id=? ORDER BY created_at DESC",
                (room_id,),
            )
            rows = self.cursor.fetchall()
            cols = [desc[0] for desc in self.cursor.description]
            return {"success": True, "data": [dict(zip(cols, row)) for row in rows]}
        except Exception as e:
            print(f"[Backend] Error fetching feedback for room: {e}")
            return {"success": False, "error": f"Failed to fetch feedback for room: {e}"}

    def get_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """Get single feedback
        
        # FLAG: NOT CONVERTIBLE - This function returns Dict instead of pydantic model
        # TODO: Convert to use appropriate get feedback response model
        """
        try:
            self.cursor.execute("SELECT * FROM feedback WHERE id=?", (feedback_id,))
            row = self.cursor.fetchone()
            if not row:
                return {"success": False, "error": "Feedback not found"}
            cols = [d[0] for d in self.cursor.description]
            return {"success": True, "data": dict(zip(cols, row))}
        except Exception as e:
            print(f"[Backend] Error fetching feedback: {e}")
            return {"success": False, "error": f"Failed to fetch feedback: {e}"}

    def delete_feedback(self, feedback_id: str) -> Dict[str, Any]:
        """Delete feedback
        
        # FLAG: NOT CONVERTIBLE - This function returns Dict instead of pydantic model
        # TODO: Convert to use DeleteFeedbackResponseModel
        """
        try:
            self.cursor.execute("DELETE FROM feedback WHERE id=?", (feedback_id,))
            self.conn.commit()
            return {"success": True, "data": {"deleted": self.cursor.rowcount}}
        except Exception as e:
            print(f"[Backend] Error deleting feedback: {e}")
            self.conn.rollback()
            return {"success": False, "error": f"Failed to delete feedback: {e}"}

# Singleton instance
feedback_service = Feedback_service()