import uuid
import sys
import os
from datetime import datetime
from typing import Optional, Iterable

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.participant_pydantic_models import (
    CreateParticipantModel, CreateParticipantResponseModel, UpdateParticipantModel,
    ParticipantLeftModel, ParticipantIsMutedModel, ParticipantIsSpeakingModel, ParticipantIsReadyModel
)
from src.database.db_connection import conn, cursor

class Participant_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor
        
    def create_participant(self, participant_model: CreateParticipantModel) -> CreateParticipantResponseModel:
        """Service to handle participant creation"""
        try:
            # Check if participant already exists in the room
            self.cursor.execute(
                "SELECT participant_id FROM participants WHERE user_id=? AND room_id=?",
                (participant_model.user_id, participant_model.room_id)
            )
            existing_participant = self.cursor.fetchone()
            
            if existing_participant:
                return CreateParticipantResponseModel(
                    status="success",
                    data=participant_model.user_id,
                    message="Participant already exists in this room"
                )
            
            # Insert new participant
            participant_id = uuid.uuid4().hex
            # Convert booleans to integers for SQLite
            is_ready_int = 1 if participant_model.is_ready else 0
            is_speaking_int = 1 if participant_model.is_speaking else 0
            is_muted_int = 1 if participant_model.is_muted else 0

            # Set ending_cefr_level to starting_cefr_level if not provided
            ending_cefr_level = participant_model.ending_cefr_level if participant_model.ending_cefr_level else participant_model.starting_cefr_level

            self.cursor.execute(
                """INSERT INTO participants 
                (participant_id, user_id, room_id, anonymous_name, avatar_color,
                role, is_ready, turn_order, is_speaking, is_muted, socket_id,
                starting_cefr_level, ending_cefr_level, joined_at, left_at, 
                campusOrLocation, speaking_time_seconds) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    participant_id,
                    participant_model.user_id,
                    participant_model.room_id,
                    participant_model.anonymous_name,
                    participant_model.avatar_color,
                    participant_model.role,
                    is_ready_int,
                    participant_model.turn_order,
                    is_speaking_int,
                    is_muted_int,
                    participant_model.socket_id,
                    participant_model.starting_cefr_level,
                    ending_cefr_level,
                    participant_model.joined_at,
                    participant_model.left_at,
                    participant_model.campusOrLocation,
                    0  # Initial speaking time
                )
            )
            self.conn.commit()
            
            return CreateParticipantResponseModel(
                status="success",
                data=participant_id,
                message="Participant created successfully"
            )
        except Exception as e:
            print(f"[Backend] Error during participant creation: {e}")
            self.conn.rollback()
            return CreateParticipantResponseModel(
                status="failure",
                data="",
                message=f"Participant creation failed: {e}"
            )
    
    def get_participant(self, user_id: str, room_id: str) -> dict:
        """Get participant details"""
        try:
            self.cursor.execute(
                """SELECT participant_id, user_id, room_id, anonymous_name, avatar_color,
                role, is_ready, turn_order, is_speaking, is_muted, socket_id,
                starting_cefr_level, ending_cefr_level, joined_at, left_at, 
                campusOrLocation, speaking_time_seconds 
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
                        "avatar_color": participant[4],
                        "role": participant[5],
                        "is_ready": bool(participant[6]),
                        "turn_order": participant[7],
                        "is_speaking": bool(participant[8]),
                        "is_muted": bool(participant[9]),
                        "socket_id": participant[10],
                        "starting_cefr_level": participant[11],
                        "ending_cefr_level": participant[12],
                        "joined_at": participant[13],
                        "left_at": participant[14],
                        "campusOrLocation": participant[15],
                        "speaking_time_seconds": participant[16]
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
                "message": f"Failed to retrieve participant: {e}"
            }
    
    def update_participant_left_time(self, user_id: str, room_id: str, left_at: datetime) -> CreateParticipantResponseModel:
        """Update participant left time"""
        try:
            self.cursor.execute(
                "UPDATE participants SET left_at=? WHERE user_id=? AND room_id=?",
                (left_at, user_id, room_id)
            )
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return CreateParticipantResponseModel(
                    status="success",
                    data=user_id,
                    message="Participant left time updated"
                )
            else:
                return CreateParticipantResponseModel(
                    status="failure",
                    data="",
                    message="Participant not found"
                )
        except Exception as e:
            print(f"[Backend] Error updating participant left time: {e}")
            self.conn.rollback()
            return CreateParticipantResponseModel(
                status="failure",
                data="",
                message=f"Failed to update participant left time: {e}"
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
            return {"status": "failure", "data": [], "message": f"Failed to list participants: {e}"}

    def update_participant(self, participant_id: str, update: UpdateParticipantModel) -> dict:
        try:
            fields = []
            values = []
            if update.left_at is not None:
                fields.append("left_at=?")
                values.append(update.left_at)
            if update.speaking_time_seconds is not None:
                fields.append("speaking_time_seconds=?")
                values.append(update.speaking_time_seconds)
            if update.ending_cefr_level is not None:
                fields.append("ending_cefr_level=?")
                values.append(update.ending_cefr_level)
            if update.is_muted is not None:
                fields.append("is_muted=?")
                values.append(1 if update.is_muted else 0)
            if update.is_speaking is not None:
                fields.append("is_speaking=?")
                values.append(1 if update.is_speaking else 0)
            if update.is_ready is not None:
                fields.append("is_ready=?")
                values.append(1 if update.is_ready else 0)
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
            return {"status": "failure", "data": None, "message": f"Failed to update participant: {e}"}

    def delete_participant(self, participant_id: str) -> dict:
        try:
            self.cursor.execute("DELETE FROM participants WHERE participant_id=?", (participant_id,))
            self.conn.commit()
            return {"status": "success", "data": {"deleted": self.cursor.rowcount}, "message": "Participant deleted"}
        except Exception as e:
            print(f"[Backend] Error deleting participant: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": f"Failed to delete participant: {e}"}

    def update_participant_left(self, update: ParticipantLeftModel) -> dict:
        """Update participant left status"""
        try:
            fields = []
            values = []
            if update.left_at is not None:
                fields.append("left_at=?")
                values.append(update.left_at)
            if update.ending_cefr_level is not None:
                fields.append("ending_cefr_level=?")
                values.append(update.ending_cefr_level)
            if not fields:
                return {"status": "failure", "data": None, "message": "No fields to update"}
            values.append(update.participant_id)
            sql = f"UPDATE participants SET {', '.join(fields)} WHERE participant_id=?"
            self.cursor.execute(sql, tuple(values))
            self.conn.commit()
            return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Participant left status updated"}
        except Exception as e:
            print(f"[Backend] Error updating participant left: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": f"Failed to update participant left status: {e}"}

    def update_participant_muted(self, update: ParticipantIsMutedModel) -> dict:
        """Update participant muted status"""
        try:
            # Convert boolean to integer for SQLite
            is_muted_int = 1 if update.is_muted else 0
            self.cursor.execute(
                "UPDATE participants SET is_muted=? WHERE participant_id=?",
                (is_muted_int, update.participant_id)
            )
            self.conn.commit()
            return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Participant muted status updated"}
        except Exception as e:
            print(f"[Backend] Error updating participant muted: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": f"Failed to update participant muted status: {e}"}

    def update_participant_speaking(self, update: ParticipantIsSpeakingModel) -> dict:
        """Update participant speaking status"""
        try:
            # Convert boolean to integer for SQLite
            is_speaking_int = 1 if update.is_speaking else 0
            self.cursor.execute(
                "UPDATE participants SET is_speaking=? WHERE participant_id=?",
                (is_speaking_int, update.participant_id)
            )
            self.conn.commit()
            return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Participant speaking status updated"}
        except Exception as e:
            print(f"[Backend] Error updating participant speaking: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": f"Failed to update participant speaking status: {e}"}

    def update_participant_ready(self, update: ParticipantIsReadyModel) -> dict:
        """Update participant ready status"""
        try:
            # Convert boolean to integer for SQLite
            is_ready_int = 1 if update.is_ready else 0
            self.cursor.execute(
                "UPDATE participants SET is_ready=? WHERE participant_id=?",
                (is_ready_int, update.participant_id)
            )
            self.conn.commit()
            return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Participant ready status updated"}
        except Exception as e:
            print(f"[Backend] Error updating participant ready: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": f"Failed to update participant ready status: {e}"}

# Singleton instance
participant_service = Participant_service()