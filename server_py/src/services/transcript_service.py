import uuid
import sys
import os
from typing import Dict, Any

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.transcript_pydantic_models import CreateTranscriptModel
from src.database.db_connection import conn, cursor

class TranscriptService:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor

    def create_transcript(self, model: CreateTranscriptModel) -> Dict[str, Any]:
        try:
            transcript_id = uuid.uuid4().hex
            self.cursor.execute(
                """
                INSERT INTO transcripts (
                    transcript_id, room_id, participant_id, user_id, text, created_at, audio_file_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transcript_id,
                    model.room_id,
                    model.participant_id,
                    model.user_id,
                    model.text,
                    model.created_at,
                    model.audio_file_url,
                ),
            )
            self.conn.commit()
            return {"success": True, "data": {"id": transcript_id}}
        except Exception as e:
            print(f"[Backend] Error creating transcript: {e}")
            self.conn.rollback()
            return {"success": False, "error": "Failed to save transcript"}

    def list_transcripts_for_room(self, room_id: str) -> Dict[str, Any]:
        try:
            self.cursor.execute(
                "SELECT * FROM transcripts WHERE room_id=? ORDER BY created_at ASC",
                (room_id,),
            )
            rows = self.cursor.fetchall()
            cols = [desc[0] for desc in self.cursor.description]
            return {"success": True, "data": [dict(zip(cols, row)) for row in rows]}
        except Exception as e:
            print(f"[Backend] Error fetching transcripts: {e}")
            return {"success": False, "error": "Failed to fetch transcripts"}

    def get_transcript(self, transcript_id: str) -> Dict[str, Any]:
        try:
            self.cursor.execute("SELECT * FROM transcripts WHERE transcript_id=?", (transcript_id,))
            row = self.cursor.fetchone()
            if not row:
                return {"success": False, "error": "Transcript not found"}
            cols = [d[0] for d in self.cursor.description]
            return {"success": True, "data": dict(zip(cols, row))}
        except Exception as e:
            print(f"[Backend] Error fetching transcript: {e}")
            return {"success": False, "error": "Failed to fetch transcript"}

    def delete_transcript(self, transcript_id: str) -> Dict[str, Any]:
        try:
            self.cursor.execute("DELETE FROM transcripts WHERE transcript_id=?", (transcript_id,))
            self.conn.commit()
            return {"success": True, "data": {"deleted": self.cursor.rowcount}}
        except Exception as e:
            print(f"[Backend] Error deleting transcript: {e}")
            self.conn.rollback()
            return {"success": False, "error": "Failed to delete transcript"}
