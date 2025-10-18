import uuid
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.feedback_pydantic_models import InstantFeedbackModel, ComprehensiveFeedbackModel
from src.database.db_connection import conn, cursor

class FeedbackService:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor

    def create_instant_feedback(self, model: InstantFeedbackModel) -> Dict[str, Any]:
        try:
            feedback_id = uuid.uuid4().hex
            self.cursor.execute(
                """
                INSERT INTO feedback (
                    feedback_id, room_id, participant_id, user_id, feedback_type,
                    display_message, grammar_issues, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    feedback_id,
                    model.room_id,
                    model.participant_id,
                    model.participant_id,  # user_id not guaranteed; fallback to participant for MVP
                    "instant",
                    model.feedback_message,
                    str(model.grammar_issues),
                    model.created_at,
                ),
            )
            self.conn.commit()
            return {"success": True, "data": {"id": feedback_id}}
        except Exception as e:
            print(f"[Backend] Error creating instant feedback: {e}")
            self.conn.rollback()
            return {"success": False, "error": "Failed to save instant feedback"}

    def create_comprehensive_feedback(self, model: ComprehensiveFeedbackModel) -> Dict[str, Any]:
        try:
            feedback_id = uuid.uuid4().hex
            self.cursor.execute(
                """
                INSERT INTO feedback (
                    feedback_id, room_id, participant_id, user_id, feedback_type,
                    display_message, cefr_level, grammar_score, vocabulary_score, fluency_score, overall_score,
                    grammar_issues, vocabulary_suggestions, fluency_issues, suggestions, strengths,
                    agent_id, agent_model, generation_time_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    feedback_id,
                    model.room_id,
                    model.participant_id,
                    model.participant_id,  # user_id not guaranteed; fallback
                    "comprehensive",
                    model.display_message,
                    model.cefr_level,
                    model.grammar_score,
                    model.vocabulary_score,
                    model.fluency_score,
                    model.overall_score,
                    str(model.grammar_issues),
                    str(model.vocabulary_suggestions),
                    str(model.fluency_issues),
                    str(model.suggestions),
                    str(model.strengths),
                    model.agent_id,
                    model.agent_model,
                    model.generation_time_ms,
                    model.created_at,
                ),
            )
            self.conn.commit()
            return {"success": True, "data": {"id": feedback_id}}
        except Exception as e:
            print(f"[Backend] Error creating comprehensive feedback: {e}")
            self.conn.rollback()
            return {"success": False, "error": "Failed to save comprehensive feedback"}

    def list_feedback_for_participant(self, participant_id: str) -> Dict[str, Any]:
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
            return {"success": False, "error": "Failed to fetch feedback"}

    def list_feedback_for_room(self, room_id: str) -> Dict[str, Any]:
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
            return {"success": False, "error": "Failed to fetch feedback"}

    def get_feedback(self, feedback_id: str) -> Dict[str, Any]:
        try:
            self.cursor.execute("SELECT * FROM feedback WHERE feedback_id=?", (feedback_id,))
            row = self.cursor.fetchone()
            if not row:
                return {"success": False, "error": "Feedback not found"}
            cols = [d[0] for d in self.cursor.description]
            return {"success": True, "data": dict(zip(cols, row))}
        except Exception as e:
            print(f"[Backend] Error fetching feedback: {e}")
            return {"success": False, "error": "Failed to fetch feedback"}

    def delete_feedback(self, feedback_id: str) -> Dict[str, Any]:
        try:
            self.cursor.execute("DELETE FROM feedback WHERE feedback_id=?", (feedback_id,))
            self.conn.commit()
            return {"success": True, "data": {"deleted": self.cursor.rowcount}}
        except Exception as e:
            print(f"[Backend] Error deleting feedback: {e}")
            self.conn.rollback()
            return {"success": False, "error": "Failed to delete feedback"}
