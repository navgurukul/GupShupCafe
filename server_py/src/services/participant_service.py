import uuid
import sys
import os
from datetime import datetime

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.participant_pydantic_models import CreateParticipantModel, ParticipantResponseModel, ParticipantUpdateModel
from src.database.db_connection import conn, cursor

class Participant_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor
        
    def create_participant(self, participant_model: CreateParticipantModel) -> ParticipantResponseModel:
        """Service to handle participant creation"""
        try:
            # Check if participant already exists in the room
            self.cursor.execute(
                "SELECT participant_id FROM participants WHERE user_id=? AND room_id=?",
                (participant_model.user_id, participant_model.room_id)
            )
            existing_participant = self.cursor.fetchone()
            
            if existing_participant:
                return ParticipantResponseModel(
                    status="success",
                    data=participant_model.user_id,
                    message="Participant already exists in this room"
                )
            
            # Insert new participant
            participant_id = participant_model.participant_id or uuid.uuid4().hex
            self.cursor.execute(
                """INSERT INTO participants 
                (participant_id, user_id, room_id, anonymous_name, campus, location, joined_at, left_at, speaking_time_seconds) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    participant_id,
                    participant_model.user_id,
                    participant_model.room_id,
                    participant_model.anonymous_name,
                    participant_model.campus,
                    participant_model.location,
                    participant_model.joined_at,
                    None,
                    0  # Initial speaking time
                )
            )
            self.conn.commit()
            
            return ParticipantResponseModel(
                status="success",
                data=participant_id,
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
    
    def get_participant(self, user_id: str, room_id: str) -> dict:
        """Get participant details"""
        try:
            self.cursor.execute(
                """SELECT participant_id, user_id, room_id, anonymous_name, campus, location, 
                joined_at, left_at, speaking_time_seconds 
                FROM participants WHERE user_id=? AND room_id=?""",
                (user_id, room_id)
            )
            participant = self.cursor.fetchone()
            
            if participant:
                return {
                    "status": "success",
                    "data": {
                        "participant_id": participant[0],
                        "user_id": participant[1],
                        "room_id": participant[2],
                        "anonymous_name": participant[3],
                        "campus": participant[4],
                        "location": participant[5],
                        "joined_at": participant[6],
                        "left_at": participant[7],
                        "speaking_time_seconds": participant[8]
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
    
    def update_participant_left_time(self, user_id: str, room_id: str, left_at: datetime) -> ParticipantResponseModel:
        """Update participant left time"""
        try:
            self.cursor.execute(
                "UPDATE participants SET left_at=? WHERE user_id=? AND room_id=?",
                (left_at, user_id, room_id)
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

        def list_participants_for_room(self, room_id: str) -> dict:
            try:
                self.cursor.execute(
                    "SELECT * FROM participants WHERE room_id=? ORDER BY joined_at ASC",
                    (room_id,),
                )
                rows = self.cursor.fetchall()
                cols = [d[0] for d in self.cursor.description]
                return {"status": "success", "data": [dict(zip(cols, r)) for r in rows], "message": "Participants listed"}
            except Exception as e:
                print(f"[Backend] Error listing participants: {e}")
                return {"status": "failure", "data": [], "message": "Failed to list participants"}

        def update_participant(self, participant_id: str, update: ParticipantUpdateModel) -> dict:
            try:
                fields = []
                values = []
                if update.left_at is not None:
                    fields.append("left_at=?")
                    values.append(update.left_at)
                if update.speaking_time_seconds is not None:
                    fields.append("speaking_time_seconds=?")
                    values.append(update.speaking_time_seconds)
                if not fields:
                    return {"status": "failure", "data": None, "message": "No fields to update"}
                values.append(participant_id)
                sql = f"UPDATE participants SET {', '.join(fields)} WHERE participant_id=?"
                self.cursor.execute(sql, tuple(values))
                self.conn.commit()
                return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Participant updated"}
            except Exception as e:
                print(f"[Backend] Error updating participant: {e}")
                self.conn.rollback()
                return {"status": "failure", "data": None, "message": "Failed to update participant"}

        def delete_participant(self, participant_id: str) -> dict:
            try:
                self.cursor.execute("DELETE FROM participants WHERE participant_id=?", (participant_id,))
                self.conn.commit()
                return {"status": "success", "data": {"deleted": self.cursor.rowcount}, "message": "Participant deleted"}
            except Exception as e:
                print(f"[Backend] Error deleting participant: {e}")
                self.conn.rollback()
                return {"status": "failure", "data": None, "message": "Failed to delete participant"}
