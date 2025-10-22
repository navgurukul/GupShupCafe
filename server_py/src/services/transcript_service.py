import uuid
import sys
import os
from typing import Dict, Any

# Add the project root directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.models import (
    CreateTranscriptModel,
    CreateTranscriptModelResponse,
    TranscriptModel,
    ListTranscriptsResponseModel,
    UpdateTranscriptResponseModel,
    DeleteTranscriptResponseModel,
    UpdateTranscriptProcessingModel,
    UpdateTranscriptAudioURLModel
)
from src.database.db_connection import conn, cursor

class Transcript_service:
    def __init__(self):
        self.conn = conn
        self.cursor = cursor

    def create_transcript(self, model: CreateTranscriptModel) -> CreateTranscriptModelResponse:
        """Create a new transcript"""
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
            
            # Create the transcript model for response
            transcript_model = TranscriptModel(
                transcript_id=transcript_id,
                room_id=model.room_id,
                participant_id=model.participant_id,
                user_id=model.user_id,
                round_number=model.round_number,
                turn_order=model.turn_order,
                transcript_text=model.transcript_text,
                language=model.language,
                stt_confidence=model.stt_confidence,
                started_at=model.started_at,
                ended_at=model.ended_at,
                duration_seconds=model.duration_seconds,
                word_count=model.word_count,
                speech_rate=model.speech_rate,
                is_processed=model.is_processed,
                processed_at=model.processed_at,
                audio_file_url=model.audio_file_url,
                created_at=created_at
            )
            
            return CreateTranscriptModelResponse(
                status="success",
                data=transcript_model,
                message="Transcript created successfully"
            )
        except Exception as e:
            print(f"[Backend] Error creating transcript: {e}")
            self.conn.rollback()
            return CreateTranscriptModelResponse(
                status="error",
                data=None,
                message=f"Failed to save transcript: {e}"
            )

    def list_transcripts_for_room(self, room_id: str) -> ListTranscriptsResponseModel:
        """List transcripts for a room"""
        try:
            self.cursor.execute(
                "SELECT * FROM transcripts WHERE room_id=? ORDER BY created_at ASC",
                (room_id,),
            )
            rows = self.cursor.fetchall()
            cols = [desc[0] for desc in self.cursor.description]
            
            # Convert rows to TranscriptModel objects
            transcripts = []
            for row in rows:
                row_dict = dict(zip(cols, row))
                # Convert is_processed back to boolean
                row_dict['is_processed'] = bool(row_dict['is_processed'])
                transcripts.append(TranscriptModel(**row_dict))
            
            return ListTranscriptsResponseModel(
                status="success",
                data=transcripts,
                message=f"Found {len(transcripts)} transcripts for room {room_id}"
            )
        except Exception as e:
            print(f"[Backend] Error fetching transcripts: {e}")
            return ListTranscriptsResponseModel(
                status="error",
                data=[],
                message=f"Failed to fetch transcripts: {str(e)}"
            )

    def get_transcript(self, transcript_id: str) -> TranscriptModel:
        """Get a single transcript"""
        try:
            self.cursor.execute("SELECT * FROM transcripts WHERE transcript_id=?", (transcript_id,))
            row = self.cursor.fetchone()
            if not row:
                raise ValueError("Transcript not found")
            cols = [d[0] for d in self.cursor.description]
            row_dict = dict(zip(cols, row))
            # Convert is_processed back to boolean
            row_dict['is_processed'] = bool(row_dict['is_processed'])
            return TranscriptModel(**row_dict)
        except Exception as e:
            print(f"[Backend] Error fetching transcript: {e}")
            raise e

    def delete_transcript(self, transcript_id: str) -> DeleteTranscriptResponseModel:
        """Delete a transcript"""
        try:
            self.cursor.execute("DELETE FROM transcripts WHERE transcript_id=?", (transcript_id,))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return DeleteTranscriptResponseModel(
                    status="success",
                    data=transcript_id,
                    message="Transcript deleted successfully"
                )
            else:
                return DeleteTranscriptResponseModel(
                    status="error",
                    data=transcript_id,
                    message="Transcript not found"
                )
        except Exception as e:
            print(f"[Backend] Error deleting transcript: {e}")
            self.conn.rollback()
            return DeleteTranscriptResponseModel(
                status="error",
                data=transcript_id,
                message=f"Failed to delete transcript: {str(e)}"
            )

    def update_transcript_processing(self, update: UpdateTranscriptProcessingModel) -> UpdateTranscriptResponseModel:
        """Update transcript processing status"""
        try:
            # Convert boolean to integer for SQLite
            is_processed_int = 1 if update.is_processed else 0
            self.cursor.execute(
                "UPDATE transcripts SET is_processed=?, processed_at=? WHERE transcript_id=?",
                (is_processed_int, update.processed_at, update.transcript_id)
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return UpdateTranscriptResponseModel(
                    status="success",
                    data=update,
                    message="Transcript processing status updated successfully"
                )
            else:
                return UpdateTranscriptResponseModel(
                    status="error",
                    data=update,
                    message="Transcript not found"
                )
        except Exception as e:
            print(f"[Backend] Error updating transcript processing: {e}")
            self.conn.rollback()
            return UpdateTranscriptResponseModel(
                status="error",
                data=update,
                message=f"Failed to update transcript processing: {str(e)}"
            )

    def update_transcript_audio_url(self, update: UpdateTranscriptAudioURLModel) -> UpdateTranscriptResponseModel:
        """Update transcript audio file URL"""
        try:
            self.cursor.execute(
                "UPDATE transcripts SET audio_file_url=? WHERE transcript_id=?",
                (update.audio_file_url, update.transcript_id)
            )
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return UpdateTranscriptResponseModel(
                    status="success",
                    data=update,
                    message="Transcript audio URL updated successfully"
                )
            else:
                return UpdateTranscriptResponseModel(
                    status="error",
                    data=update,
                    message="Transcript not found"
                )
        except Exception as e:
            print(f"[Backend] Error updating transcript audio URL: {e}")
            self.conn.rollback()
            return UpdateTranscriptResponseModel(
                status="error",
                data=update,
                message=f"Failed to update transcript audio URL: {str(e)}"
            )

# Singleton instance
transcript_service = Transcript_service()