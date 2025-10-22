import uuid
import sys
import os
from datetime import datetime
from typing import Optional, Iterable

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models import (
    CreateParticipantModel, CreateParticipantResponseModel, UpdateParticipantModel,
    ParticipantModel, ListParticipantsResponseModel,
    UpdateParticipantResponseModel, DeleteParticipantResponseModel
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
    
    def get_participant(self, user_id: str, room_id: str) -> CreateParticipantResponseModel:
        """Get participant details"""
        try:
            self.cursor.execute(
                """SELECT participant_id, user_id, room_id, anonymous_name, avatar_color,
                role, is_ready, turn_order, is_speaking, is_muted, socket_id,
                starting_cefr_level, ending_cefr_level, joined_at, left_at, 
                campusOrLocation, speaking_time_seconds, created_at 
                FROM participants WHERE user_id=? AND room_id=?""",
                (user_id, room_id)
            )
            participant = self.cursor.fetchone()
            
            if participant:
                participant_data = ParticipantModel(
                    participant_id=participant[0],
                    user_id=participant[1],
                    room_id=participant[2],
                    anonymous_name=participant[3],
                    avatar_color=participant[4],
                    role=participant[5],
                    is_ready=bool(participant[6]),
                    turn_order=participant[7],
                    is_speaking=bool(participant[8]),
                    is_muted=bool(participant[9]),
                    socket_id=participant[10],
                    starting_cefr_level=participant[11],
                    ending_cefr_level=participant[12],
                    joined_at=participant[13],
                    left_at=participant[14],
                    campusOrLocation=participant[15],
                    speaking_time_seconds=participant[16],
                    created_at=participant[17] if participant[17] else datetime.now()
                )
                return CreateParticipantResponseModel(
                    status="success",
                    data=participant_data,
                    message="Participant found"
                )
            else:
                return CreateParticipantResponseModel(
                    status="failure",
                    data=None,
                    message="Participant not found"
                )
        except Exception as e:
            print(f"[Backend] Error getting participant: {e}")
            return CreateParticipantResponseModel(
                status="failure",
                data=None,
                message=f"Failed to retrieve participant: {e}"
            )
    
    def update_participant_left_time(self, user_id: str, room_id: str, left_at: datetime) -> UpdateParticipantResponseModel:
        """Update participant left time"""
        try:
            self.cursor.execute(
                "UPDATE participants SET left_at=? WHERE user_id=? AND room_id=?",
                (left_at, user_id, room_id)
            )
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                return UpdateParticipantResponseModel(
                    status="success",
                    data=user_id,
                    message="Participant left time updated"
                )
            else:
                return UpdateParticipantResponseModel(
                    status="failure",
                    data="",
                    message="Participant not found"
                )
        except Exception as e:
            print(f"[Backend] Error updating participant left time: {e}")
            self.conn.rollback()
            return UpdateParticipantResponseModel(
                status="failure",
                data="",
                message=f"Failed to update participant left time: {e}"
            )

    def list_participants_for_room(self, room_id: str) -> ListParticipantsResponseModel:
        """List participants for a room"""
        try:
            self.cursor.execute(
                """SELECT participant_id, user_id, room_id, anonymous_name, avatar_color,
                role, is_ready, turn_order, is_speaking, is_muted, socket_id,
                starting_cefr_level, ending_cefr_level, joined_at, left_at, 
                campusOrLocation, speaking_time_seconds, created_at 
                FROM participants WHERE room_id=? ORDER BY joined_at ASC""",
                (room_id,),
            )
            rows = self.cursor.fetchall()
            
            participants = []
            for row in rows:
                participant = ParticipantModel(
                    participant_id=row[0],
                    user_id=row[1],
                    room_id=row[2],
                    anonymous_name=row[3],
                    avatar_color=row[4],
                    role=row[5],
                    is_ready=bool(row[6]),
                    turn_order=row[7],
                    is_speaking=bool(row[8]),
                    is_muted=bool(row[9]),
                    socket_id=row[10],
                    starting_cefr_level=row[11],
                    ending_cefr_level=row[12],
                    joined_at=row[13],
                    left_at=row[14],
                    campusOrLocation=row[15],
                    speaking_time_seconds=row[16],
                    created_at=row[17] if row[17] else datetime.now()
                )
                participants.append(participant)
            
            return ListParticipantsResponseModel(
                status="success",
                data=participants,
                message="Participants listed"
            )
        except Exception as e:
            print(f"[Backend] Error listing participants: {e}")
            return ListParticipantsResponseModel(
                status="failure",
                data=[],
                message=f"Failed to list participants: {e}"
            )

    def update_participant(self, participant_id: str, update: UpdateParticipantModel) -> UpdateParticipantResponseModel:
        """Update participant details"""
        try:
            fields = []
            values = []
            
            # Handle all possible update fields
            if update.anonymous_name is not None:
                fields.append("anonymous_name=?")
                values.append(update.anonymous_name)
            if update.avatar_color is not None:
                fields.append("avatar_color=?")
                values.append(update.avatar_color)
            if update.role is not None:
                fields.append("role=?")
                values.append(update.role)
            if update.is_ready is not None:
                fields.append("is_ready=?")
                values.append(1 if update.is_ready else 0)
            if update.turn_order is not None:
                fields.append("turn_order=?")
                values.append(update.turn_order)
            if update.is_speaking is not None:
                fields.append("is_speaking=?")
                values.append(1 if update.is_speaking else 0)
            if update.is_muted is not None:
                fields.append("is_muted=?")
                values.append(1 if update.is_muted else 0)
            if update.socket_id is not None:
                fields.append("socket_id=?")
                values.append(update.socket_id)
            if update.ending_cefr_level is not None:
                fields.append("ending_cefr_level=?")
                values.append(update.ending_cefr_level)
            if update.left_at is not None:
                fields.append("left_at=?")
                values.append(update.left_at)
            if update.speaking_time_seconds is not None:
                fields.append("speaking_time_seconds=?")
                values.append(update.speaking_time_seconds)
            if update.campusOrLocation is not None:
                fields.append("campusOrLocation=?")
                values.append(update.campusOrLocation)
            
            if not fields:
                return UpdateParticipantResponseModel(
                    status="failure",
                    data=UpdateParticipantModel(),
                    message="No fields to update"
                )
            
            values.append(participant_id)
            sql = f"UPDATE participants SET {', '.join(fields)} WHERE participant_id=?"
            self.cursor.execute(sql, tuple(values))
            self.conn.commit()
            
            return UpdateParticipantResponseModel(
                status="success",
                data=update,
                message="Participant updated"
            )
        except Exception as e:
            print(f"[Backend] Error updating participant: {e}")
            self.conn.rollback()
            return UpdateParticipantResponseModel(
                status="failure",
                data=UpdateParticipantModel(),
                message=f"Failed to update participant: {e}"
            )

    def delete_participant(self, participant_id: str) -> DeleteParticipantResponseModel:
        """Delete participant"""
        try:
            self.cursor.execute("DELETE FROM participants WHERE participant_id=?", (participant_id,))
            self.conn.commit()
            return DeleteParticipantResponseModel(
                status="success",
                data=participant_id,
                message="Participant deleted"
            )
        except Exception as e:
            print(f"[Backend] Error deleting participant: {e}")
            self.conn.rollback()
            return DeleteParticipantResponseModel(
                status="failure",
                data="",
                message=f"Failed to delete participant: {e}"
            )



# Singleton instance
participant_service = Participant_service()