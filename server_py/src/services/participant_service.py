import uuid
import sys
import os
from datetime import datetime

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.participant_pydantic_models import CreateParticipantModel, ParticipantResponseModel
from src.database.db_connection import conn, cursor

class Participant_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor
        
    def create_participant(self, participant_model: CreateParticipantModel) -> ParticipantResponseModel:
        """Service to handle participant creation"""
        try:
            # Check if participant already exists in the session
            self.cursor.execute(
                "SELECT user_id FROM participants WHERE user_id=? AND session_id=?",
                (participant_model.user_id, participant_model.session_id)
            )
            existing_participant = self.cursor.fetchone()
            
            if existing_participant:
                return ParticipantResponseModel(
                    status="success",
                    data=participant_model.user_id,
                    message="Participant already exists in this session"
                )
            
            # Insert new participant
            self.cursor.execute(
                """INSERT INTO participants 
                (user_id, session_id, anonymous_name, campus, location, joined_at, speaking_time_seconds) 
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    participant_model.user_id,
                    participant_model.session_id,
                    participant_model.anonymous_name,
                    participant_model.campus,
                    participant_model.location,
                    participant_model.joined_at,
                    0  # Initial speaking time
                )
            )
            self.conn.commit()
            
            return ParticipantResponseModel(
                status="success",
                data=participant_model.user_id,
                message="Participant created successfully"
            )
        except Exception as e:
            print(f"[Backend] Error during participant creation: {e}")
            self.conn.rollback()
            return ParticipantResponseModel(
                status="failure",
                data="",
                message="Participant creation failed"
            )
    
    def get_participant(self, user_id: str, session_id: str) -> dict:
        """Get participant details"""
        try:
            self.cursor.execute(
                """SELECT user_id, session_id, anonymous_name, campus, location, 
                joined_at, left_at, speaking_time_seconds 
                FROM participants WHERE user_id=? AND session_id=?""",
                (user_id, session_id)
            )
            participant = self.cursor.fetchone()
            
            if participant:
                return {
                    "status": "success",
                    "data": {
                        "user_id": participant[0],
                        "session_id": participant[1],
                        "anonymous_name": participant[2],
                        "campus": participant[3],
                        "location": participant[4],
                        "joined_at": participant[5],
                        "left_at": participant[6],
                        "speaking_time_seconds": participant[7]
                    },
                    "message": "Participant found"
                }
            else:
                return {
                    "status": "failure",
                    "data": None,
                    "message": "Participant not found"
                }
        except Exception as e:
            print(f"[Backend] Error getting participant: {e}")
            return {
                "status": "failure",
                "data": None,
                "message": "Failed to retrieve participant"
            }
    
    def update_participant_left_time(self, user_id: str, session_id: str, left_at: datetime) -> ParticipantResponseModel:
        """Update participant left time"""
        try:
            self.cursor.execute(
                "UPDATE participants SET left_at=? WHERE user_id=? AND session_id=?",
                (left_at, user_id, session_id)
            )
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return ParticipantResponseModel(
                    status="success",
                    data=user_id,
                    message="Participant left time updated"
                )
            else:
                return ParticipantResponseModel(
                    status="failure",
                    data="",
                    message="Participant not found"
                )
        except Exception as e:
            print(f"[Backend] Error updating participant left time: {e}")
            self.conn.rollback()
            return ParticipantResponseModel(
                status="failure",
                data="",
                message="Failed to update participant left time"
            )
