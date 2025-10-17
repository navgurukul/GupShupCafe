import uuid
import sys
import os

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.session_pydantic_models import CreateSessionModel, SessionResponseModel
from src.database.db_connection import conn, cursor

class Session_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor
        
    def create_session(self, session_model: CreateSessionModel) -> SessionResponseModel:
        """Service to handle session creation"""
        try:
            session_id = uuid.uuid4().hex
            room_id = uuid.uuid4().hex
            participant_count = 0  # Initial participant count
            duration_seconds = 0
            status = 'active'
            self.cursor.execute(
                "INSERT INTO sessions (session_id, room_id,room_name,topic_title,topic_category,participant_count,started_at,ended_at,duration_seconds,rounds_completed,created_at, status,crf_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (session_id, room_id, session_model.room_name, session_model.room_topic, session_model.topic_category, participant_count, session_model.started_at, session_model.ended_at, duration_seconds, session_model.rounds_completed, session_model.created_at, status, session_model.crf_level)
            )
            self.conn.commit()
            return SessionResponseModel(
                status="success",
                data=session_id,
                message="Session created successfully"
            )
        except Exception as e:
            print(f"Error during session creation: {e}")
            return SessionResponseModel(
                status="failure",
                data="",
                message="Session creation failed"
            )
