import uuid
import sys
import os
from typing import Dict, Any

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models.transcript_pydantic_models import (
    CreateTranscriptModel, UpdateTranscriptProcessingModel, UpdateTranscriptAudioURLModel
)
from src.database.db_connection import conn, cursor

class Transcript_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor

    def create_transcript(self, model: CreateTranscriptModel) -> Dict[str, Any]:
        try:
            from datetime import datetime
            transcript_id = uuid.uuid4().hex
            created_at = datetime.now()
            # Convert boolean to integer for SQLite
            is_processed_int = 1 if model.is_processed else 0
            
            self.cursor.execute(
                """
                INSERT INTO transcripts (
                    transcript_id, room_id, participant_id, user_id,
                    round_number, turn_order, transcript_text, language, stt_confidence,
                    started_at, ended_at, duration_seconds,
                    word_count, speech_rate, is_processed, processed_at,
                    audio_file_url, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transcript_id,
                    model.room_id,
                    model.participant_id,
                    model.user_id,
                    model.round_number,
                    model.turn_order,
                    model.transcript_text,
                    model.language,
                    model.stt_confidence,
                    model.started_at,
                    model.ended_at,
                    model.duration_seconds,
                    model.word_count,
                    model.speech_rate,
                    is_processed_int,
                    model.processed_at,
                    model.audio_file_url,
                    created_at,
                ),
            )
            self.conn.commit()
            return {"success": True, "data": {"id": transcript_id}}
        except Exception as e:
            print(f"[Backend] Error creating transcript: {e}")
            self.conn.rollback()
            return {"success": False, "error": f"Failed to save transcript: {e}"}

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

    def update_transcript_processing(self, update: UpdateTranscriptProcessingModel) -> Dict[str, Any]:
        """Update transcript processing status"""
        try:
            # Convert boolean to integer for SQLite
            is_processed_int = 1 if update.is_processed else 0
            self.cursor.execute(
                "UPDATE transcripts SET is_processed=?, processed_at=? WHERE transcript_id=?",
                (is_processed_int, update.processed_at, update.transcript_id)
            )
            self.conn.commit()
            return {"success": True, "data": {"updated": self.cursor.rowcount}}
        except Exception as e:
            print(f"[Backend] Error updating transcript processing: {e}")
            self.conn.rollback()
            return {"success": False, "error": "Failed to update transcript processing"}

    def update_transcript_audio_url(self, update: UpdateTranscriptAudioURLModel) -> Dict[str, Any]:
        """Update transcript audio file URL"""
        try:
            self.cursor.execute(
                "UPDATE transcripts SET audio_file_url=? WHERE transcript_id=?",
                (update.audio_file_url, update.transcript_id)
            )
            self.conn.commit()
            return {"success": True, "data": {"updated": self.cursor.rowcount}}
        except Exception as e:
            print(f"[Backend] Error updating transcript audio URL: {e}")
            self.conn.rollback()
            return {"success": False, "error": "Failed to update transcript audio URL"}

# Singleton instance
transcript_service = Transcript_service()