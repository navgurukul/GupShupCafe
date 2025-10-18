import uuid
import sys
import os

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.room_pydantic_models import CreateRoomModel, RoomResponseModel
from src.database.db_connection import conn, cursor

class Room_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor
        
    def create_room(self, room_model: CreateRoomModel) -> RoomResponseModel:
        """Service to handle room creation"""
        try:
            room_id = uuid.uuid4().hex
            participant_count = 0  # Initial participant count
            duration_seconds = 0  # Initial duration
            status = "waiting"  # Initial status
            max_participants = 6  # Default max participants
            self.cursor.execute(
                "INSERT INTO rooms (room_id, room_name,topic_title,topic_category,participant_count, started_at,ended_at,duration_seconds,rounds_completed,created_at, status,cefr_level, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (room_id, room_model.room_name, room_model.room_topic, room_model.topic_category, participant_count, room_model.started_at, room_model.ended_at, duration_seconds, room_model.rounds_completed, room_model.created_at, status, room_model.cefr_level, getattr(room_model, 'created_by', None))
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
                message="Room creation failed"
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

    def update_room(self, room_id: str, updates: dict) -> dict:
        try:
            allowed = {"room_name", "topic_title", "topic_category", "participant_count", "started_at", "ended_at", "duration_seconds", "rounds_completed", "status", "cefr_level"}
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