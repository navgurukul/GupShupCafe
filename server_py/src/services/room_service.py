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
                "INSERT INTO rooms (room_id, room_name,topic_title,topic_category,participant_count,max_participants, started_at,ended_at,duration_seconds,rounds_completed,created_at, status,cefr_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (room_id, room_model.room_name, room_model.room_topic, room_model.topic_category, participant_count, max_participants, room_model.started_at, room_model.ended_at, duration_seconds, room_model.rounds_completed, room_model.created_at, status, room_model.cefr_level)
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