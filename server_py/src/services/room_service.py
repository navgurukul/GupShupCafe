import uuid
import sys
import os

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.room_pydantic_models import (
    CreateRoomModel, RoomResponseModel, UpdateRoomStatusModel,
    UpdateRoomStateModel, UpdateRoomEndModel
)
from src.database.db_connection import conn, cursor

class Room_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor
        
    def create_room(self, room_model: CreateRoomModel) -> RoomResponseModel:
        """Service to handle room creation"""
        try:
            from datetime import datetime
            room_id = uuid.uuid4().hex
            created_at = datetime.now()
            
            self.cursor.execute(
                """INSERT INTO rooms (
                    room_id, room_name, topic_title, topic_category, 
                    max_participants, speaking_time_per_turn, num_rounds, cefr_level,
                    status, current_round, current_speaker_index,
                    participant_count, created_at, started_at, ended_at, 
                    duration_seconds, agent_id, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    room_id, 
                    room_model.room_name, 
                    room_model.topic_title, 
                    room_model.topic_category,
                    room_model.max_participants,
                    room_model.speaking_time_per_turn,
                    room_model.num_rounds,
                    room_model.cefr_level.value,
                    room_model.status.value,
                    room_model.current_round,
                    room_model.current_speaker_index,
                    room_model.participant_count,
                    created_at,
                    room_model.started_at,
                    room_model.ended_at,
                    room_model.duration_seconds,
                    room_model.agent_id,
                    room_model.created_by
                )
            )
            self.conn.commit()
            return RoomResponseModel(
                status="success",
                data=room_id,
                message="Room created successfully"
            )
        except Exception as e:
            print(f"Error during room creation: {e}")
            return RoomResponseModel(
                status="failure",
                data="",
                message=f"Room creation failed: {e}"
            )

    def join_room(self, room_id: str) -> RoomResponseModel:
        """Service to handle joining a room"""
        try:
            self.cursor.execute("SELECT room_id FROM rooms WHERE room_id=?", (room_id,))
            room = self.cursor.fetchone()
            
            if room:
                return RoomResponseModel(
                    status="success",
                    data=room_id,
                    message="Joined room successfully"
                )
            return RoomResponseModel(
                status="failure",
                data="",
                message="Room not found"
            )
        except Exception as e:
            print(f"Error during joining room: {e}")
            return RoomResponseModel(
                status="failure",
                data="",
                message="Failed to join room"
            )

    def get_room(self, room_id: str) -> dict:
        try:
            self.cursor.execute("SELECT * FROM rooms WHERE room_id=?", (room_id,))
            row = self.cursor.fetchone()
            if not row:
                return {"status": "failure", "data": None, "message": "Room not found"}
            cols = [d[0] for d in self.cursor.description]
            return {"status": "success", "data": dict(zip(cols, row)), "message": "Room found"}
        except Exception as e:
            print(f"Error getting room: {e}")
            return {"status": "failure", "data": None, "message": "Failed to get room"}

    def list_rooms(self) -> dict:
        try:
            self.cursor.execute("SELECT * FROM rooms ORDER BY created_at DESC")
            rows = self.cursor.fetchall()
            cols = [d[0] for d in self.cursor.description]
            return {"status": "success", "data": [dict(zip(cols, r)) for r in rows], "message": "Rooms listed"}
        except Exception as e:
            print(f"Error listing rooms: {e}")
            return {"status": "failure", "data": [], "message": "Failed to list rooms"}

    def list_rooms_by_status(self, status: str) -> dict:
        """List rooms filtered by status"""
        try:
            self.cursor.execute(
                "SELECT * FROM rooms WHERE status=? ORDER BY created_at DESC",
                (status,)
            )
            rows = self.cursor.fetchall()
            cols = [d[0] for d in self.cursor.description]
            return {
                "status": "success",
                "data": [dict(zip(cols, r)) for r in rows],
                "message": f"Rooms listed for status='{status}'",
            }
        except Exception as e:
            print(f"Error listing rooms by status: {e}")
            return {
                "status": "failure",
                "data": [],
                "message": "Failed to list rooms by status",
            }

    def update_room(self, room_id: str, updates: dict) -> dict:
        try:
            allowed = {
                "room_name", "topic_title", "topic_category", "max_participants",
                "speaking_time_per_turn", "num_rounds", "cefr_level", "status",
                "current_round", "current_speaker_index", "participant_count",
                "started_at", "ended_at", "duration_seconds", "agent_id"
            }
            fields = []
            values = []
            for k, v in updates.items():
                if k in allowed and v is not None:
                    fields.append(f"{k}=?")
                    values.append(v)
            if not fields:
                return {"status": "failure", "data": None, "message": "No fields to update"}
            values.append(room_id)
            sql = f"UPDATE rooms SET {', '.join(fields)} WHERE room_id=?"
            self.cursor.execute(sql, tuple(values))
            self.conn.commit()
            return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Room updated"}
        except Exception as e:
            print(f"Error updating room: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": "Failed to update room"}

    def delete_room(self, room_id: str) -> dict:
        try:
            self.cursor.execute("DELETE FROM rooms WHERE room_id=?", (room_id,))
            self.conn.commit()
            return {"status": "success", "data": {"deleted": self.cursor.rowcount}, "message": "Room deleted"}
        except Exception as e:
            print(f"Error deleting room: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": "Failed to delete room"}

    def update_room_status(self, room_id: str, update: UpdateRoomStatusModel) -> dict:
        """Update room status"""
        try:
            fields = ["status=?"]
            values = [update.status.value]
            if update.started_at is not None:
                fields.append("started_at=?")
                values.append(update.started_at)
            values.append(room_id)
            sql = f"UPDATE rooms SET {', '.join(fields)} WHERE room_id=?"
            self.cursor.execute(sql, tuple(values))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Room status updated"}
            return {"status": "failure", "data": None, "message": "Room not found"}
        except Exception as e:
            print(f"Error updating room status: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": "Failed to update room status"}

    def update_room_state(self, room_id: str, update: UpdateRoomStateModel) -> dict:
        """Update room discussion state"""
        try:
            fields = []
            values = []
            if update.current_round is not None:
                fields.append("current_round=?")
                values.append(update.current_round)
            if update.current_speaker_index is not None:
                fields.append("current_speaker_index=?")
                values.append(update.current_speaker_index)
            if update.participant_count is not None:
                fields.append("participant_count=?")
                values.append(update.participant_count)
            if not fields:
                return {"status": "failure", "data": None, "message": "No fields to update"}
            values.append(room_id)
            sql = f"UPDATE rooms SET {', '.join(fields)} WHERE room_id=?"
            self.cursor.execute(sql, tuple(values))
            self.conn.commit()
            return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Room state updated"}
        except Exception as e:
            print(f"Error updating room state: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": "Failed to update room state"}

    def end_room(self, room_id: str, update: UpdateRoomEndModel) -> dict:
        """Mark room as finished"""
        try:
            self.cursor.execute(
                "UPDATE rooms SET status=?, ended_at=?, duration_seconds=? WHERE room_id=?",
                (update.status.value, update.ended_at, update.duration_seconds, room_id)
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return {"status": "success", "data": {"updated": self.cursor.rowcount}, "message": "Room ended"}
            return {"status": "failure", "data": None, "message": "Room not found"}
        except Exception as e:
            print(f"Error ending room: {e}")
            self.conn.rollback()
            return {"status": "failure", "data": None, "message": "Failed to end room"}