"""
Database Management
Simple SQLite database for storing room data and analytics
"""

import aiosqlite
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.db: Optional[aiosqlite.Connection] = None
        self.db_path: str = ""

    async def initialize(self, db_path: str = "./data/gupshup-database.db"):
        """Initialize the database connection and create tables"""
        self.db_path = db_path

        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

        # Create database connection
        self.db = await aiosqlite.connect(db_path)
        self.db.row_factory = aiosqlite.Row

        # Improve concurrency: enable WAL and set a busy timeout
        # WAL allows concurrent reads during writes; busy_timeout mitigates transient lock errors
        await self.db.execute("PRAGMA journal_mode=WAL;")
        await self.db.execute("PRAGMA synchronous=NORMAL;")
        await self.db.execute("PRAGMA busy_timeout=5000;")

        print(f"📊 Connected to SQLite database at {db_path}")

        # Enforce foreign key constraints for this connection
        await self.db.execute("PRAGMA foreign_keys = ON;")
        await self.db.commit()  # Commit the PRAGMA

        # Create tables
        await self._create_tables()

        return self.db

    async def _create_tables(self):
        """Create database tables if they don't exist"""
        async with self.db.execute("BEGIN"):
            # Users table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    hashed_password TEXT NOT NULL,
                    current_cefr_level TEXT DEFAULT 'A0',
                    topic_categories TEXT, -- Stored as JSON string
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    last_active DATETIME
                )
            """)

            # Rooms table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    room_id TEXT PRIMARY KEY,
                    room_name TEXT,
                    
                    -- Room Configuration
                    topic_title TEXT NOT NULL,
                    topic_category TEXT NOT NULL,
                    max_participants INTEGER DEFAULT 6,
                    speaking_time_per_turn INTEGER DEFAULT 60,
                    num_rounds INTEGER DEFAULT 3,
                    cefr_level TEXT NOT NULL,
                    
                    -- Room State
                    status TEXT NOT NULL,
                    current_round INTEGER DEFAULT 0,
                    current_speaker_index INTEGER DEFAULT 0,
                    rounds_completed INTEGER DEFAULT 0,
                    
                    -- Participants
                    participant_count INTEGER DEFAULT 0,
                    
                    -- Timing
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    started_at DATETIME,
                    ended_at DATETIME,
                    duration_seconds INTEGER DEFAULT 0,
                    
                    -- Facilitator Agent
                    agent_id TEXT,
                    
                    -- Metadata
                    created_by TEXT NOT NULL
                )
            """)

            # Participants table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS participants (
                    participant_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    room_id TEXT NOT NULL,
                    
                    -- Identity
                    anonymous_name TEXT NOT NULL,
                    avatar_color TEXT,
                    
                    -- Room Config
                    role TEXT DEFAULT 'participant',
                    is_ready INTEGER DEFAULT 0,
                    turn_order INTEGER DEFAULT 0,
                    
                    -- Real-Time State
                    is_speaking INTEGER DEFAULT 0,
                    is_muted INTEGER DEFAULT 0,
                    socket_id TEXT,
                    
                    -- CEFR Level
                    starting_cefr_level TEXT NOT NULL,
                    ending_cefr_level TEXT,
                    
                    -- Connection
                    joined_at DATETIME NOT NULL,
                    left_at DATETIME,
                    
                    -- Optional Info
                    campusOrLocation TEXT,
                    
                    -- Tracking (from previous schema)
                    speaking_time_seconds INTEGER DEFAULT 0,
                    
                    -- Foreign Keys
                    FOREIGN KEY (room_id) REFERENCES rooms (room_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Helpful indexes
            await self.db.execute("""
                CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status)
            """)

            # Transcripts table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS transcripts (
                    transcript_id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    participant_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    
                    -- Context
                    round_number INTEGER NOT NULL,
                    turn_order INTEGER NOT NULL,
                    
                    -- Content
                    transcript_text TEXT NOT NULL,
                    language TEXT DEFAULT 'en',
                    stt_confidence REAL DEFAULT 0.0,
                    
                    -- Timing
                    started_at DATETIME NOT NULL,
                    ended_at DATETIME NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    
                    -- Audio Metadata
                    word_count INTEGER NOT NULL,
                    speech_rate REAL NOT NULL,
                    
                    -- Processing Status
                    is_processed INTEGER NOT NULL DEFAULT 0,
                    processed_at DATETIME,
                    
                    -- Audio Reference
                    audio_file_url TEXT,
                    
                    -- Record Timestamp
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    
                    -- Foreign Keys
                    FOREIGN KEY (room_id) REFERENCES rooms (room_id),
                    FOREIGN KEY (participant_id) REFERENCES participants (participant_id)
                )
            """)

            # Feedback table (MVP)
            # This table combines all fields from FeedbackModel, InstantFeedbackModel,
            # and ComprehensiveFeedbackModel. The 'feedback_type' column
            # distinguishes which fields are populated.
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    participant_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    feedback_type TEXT NOT NULL, -- 'instant' or 'comprehensive'
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,

                    -- Instant Feedback / Common Fields
                    display_message TEXT,
                    agent_id TEXT,
                    agent_model TEXT,

                    -- Comprehensive Feedback Fields
                    cefr_speaking TEXT,
                    cefr_listening TEXT,
                    listening_activity TEXT,
                    response_effectiveness TEXT,
                    listening_positive_observation TEXT,
                    listening_improvement_suggestion TEXT,
                    fluency TEXT,
                    sentence_complexity TEXT,
                    pace TEXT,
                    filler_examples TEXT, -- Stored as JSON string
                    grammar TEXT,
                    vocab_examples TEXT, -- Stored as JSON string
                    vocab_analysis TEXT,
                    vocab_positive_observation TEXT,
                    vocab_improvement_suggestion TEXT,
                    understanding_level TEXT,
                    explanation_quality TEXT,
                    interaction_style TEXT,
                    depth_of_understanding_suggestion TEXT,
                    comparative_performance TEXT,
                    comparative_suggestion TEXT,
                    summary_strength TEXT,
                    summary_improvement_area TEXT,
                    target_cefr_level TEXT,

                    
                    -- Foreign Keys
                    FOREIGN KEY (room_id) REFERENCES rooms (room_id),
                    FOREIGN KEY (participant_id) REFERENCES participants (participant_id),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Topics table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS topics (
                    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    source TEXT DEFAULT 'fallback',
                    used_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Agent table for storing AI agent instances
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    agent_model TEXT NOT NULL, -- Gemini or Bedrock
                    agent_type TEXT DEFAULT 'english',
                    status TEXT DEFAULT 'active',
                    system_prompt TEXT,
                    total_interactions INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """)

            await self.db.commit()

        print("Database tables created/verified")

    async def save_room(self, room_data: Dict[str, Any]) -> int:
        """Save a discussion room"""
        query = """
            INSERT INTO rooms (
                room_id, room_name, topic_title, topic_category, participant_count,
                started_at, ended_at, duration_seconds, rounds_completed, status, cefr_level, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        topic = room_data.get("topic", {})
        # Get room_id and use it for room_name if not provided
        room_id = room_data.get("room_id") or room_data.get("roomId")
        room_name = room_data.get("room_name") or room_data.get(
            "roomName") or room_id or "general"

        # Get a valid created_by user ID
        created_by = room_data.get("createdBy") or room_data.get("created_by")
        if not created_by or created_by == "system":
            # Get the first available user ID
            cursor = await self.db.execute("SELECT user_id FROM users LIMIT 1")
            user_row = await cursor.fetchone()
            created_by = user_row[0] if user_row else "system"

        cursor = await self.db.execute(query, (
            room_id,
            room_name,
            topic.get("title") if topic else "General Discussion",
            topic.get("category") if topic else "general",
            room_data.get("participantCount") or room_data.get(
                "participant_count") or 0,
            room_data.get("startedAt") or room_data.get("started_at"),
            room_data.get("endedAt") or room_data.get("ended_at"),
            room_data.get("durationSeconds") or room_data.get(
                "duration_seconds") or 0,
            room_data.get("roundsCompleted") or room_data.get(
                "rounds_completed") or 0,
            room_data.get("status", "waiting"),
            room_data.get("cefrLevel") or room_data.get("cefr_level", "A1"),
            created_by
        ))

        await self.db.commit()
        return cursor.lastrowid

    async def save_participant(self, participant_data: Dict[str, Any]) -> int:
        """Save participant data"""
        query = """
            INSERT INTO participants (
                participant_id, user_id, room_id, anonymous_name, campusOrLocation,
                joined_at, left_at, speaking_time_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Combine campus and location into campusOrLocation
        campus = participant_data.get("campus")
        location = participant_data.get("location")
        campus_or_location = None
        if campus and location:
            campus_or_location = f"{campus}, {location}"
        elif campus:
            campus_or_location = campus
        elif location:
            campus_or_location = location

        cursor = await self.db.execute(query, (
            participant_data.get(
                "participant_id") or participant_data.get("participantId"),
            participant_data.get("user_id") or participant_data.get("userId"),
            participant_data.get("room_id") or participant_data.get("roomId"),
            participant_data.get(
                "anonymous_name") or participant_data.get("anonymousName"),
            campus_or_location,
            participant_data.get(
                "joinedAt") or participant_data.get("joined_at"),
            participant_data.get("leftAt") or participant_data.get("left_at"),
            participant_data.get("speakingTimeSeconds") or participant_data.get(
                "speaking_time_seconds", 0)
        ))

        await self.db.commit()
        return cursor.lastrowid

    async def record_topic_usage(self, topic: Dict[str, Any]):
        """Record topic usage"""
        # Try to update existing topic
        update_query = """
            UPDATE topics 
            SET used_count = used_count + 1 
            WHERE title = ? AND category = ?
        """

        cursor = await self.db.execute(update_query, (
            topic.get("title"),
            topic.get("category")
        ))

        await self.db.commit()

        # If no rows were updated, insert new topic
        if cursor.rowcount == 0:
            insert_query = """
                INSERT INTO topics (title, description, category, source, used_count)
                VALUES (?, ?, ?, ?, 1)
            """

            await self.db.execute(insert_query, (
                topic.get("title"),
                topic.get("description"),
                topic.get("category"),
                topic.get("source", "fallback")
            ))

            await self.db.commit()

    async def get_room_analytics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get room analytics"""
        query = """
            SELECT 
                s.room_id,
                s.room_name,
                s.topic_title,
                s.topic_category,
                s.participant_count,
                s.started_at,
                s.ended_at,
                s.duration_seconds,
                s.rounds_completed,
                COUNT(p.user_id) as recorded_participants
            FROM rooms s
            LEFT JOIN participants p ON s.room_id = p.room_id
            GROUP BY s.room_id
            ORDER BY s.started_at DESC
            LIMIT ?
        """

        async with self.db.execute(query, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_topic_analytics(self) -> List[Dict[str, Any]]:
        """Get topic analytics"""
        query = """
            SELECT 
                title,
                category,
                source,
                used_count,
                created_at
            FROM topics
            ORDER BY used_count DESC, created_at DESC
        """

        async with self.db.execute(query) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        stats = {}

        # Total rooms
        async with self.db.execute("SELECT COUNT(*) as count FROM rooms") as cursor:
            row = await cursor.fetchone()
            stats["totalRooms"] = dict(row) if row else {"count": 0}

        # Total participants
        async with self.db.execute("SELECT COUNT(DISTINCT user_id) as count FROM participants") as cursor:
            row = await cursor.fetchone()
            stats["totalParticipants"] = dict(row) if row else {"count": 0}

        # Average room duration
        async with self.db.execute(
            "SELECT AVG(duration_seconds) as avg FROM rooms WHERE duration_seconds > 0"
        ) as cursor:
            row = await cursor.fetchone()
            stats["avgRoomDuration"] = dict(row) if row else {"avg": 0}

        # Average participants per room
        async with self.db.execute(
            "SELECT AVG(participant_count) as avg FROM rooms"
        ) as cursor:
            row = await cursor.fetchone()
            stats["avgParticipantsPerRoom"] = dict(row) if row else {"avg": 0}

        # Top categories
        query = """
            SELECT category, COUNT(*) as count 
            FROM topics 
            WHERE used_count > 0 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 5
        """
        async with self.db.execute(query) as cursor:
            rows = await cursor.fetchall()
            stats["topCategories"] = [dict(row) for row in rows]

        return stats

    async def update_room(self, room_id: str, room_data: Dict[str, Any]) -> int:
        """Update room data"""
        # Build dynamic query based on provided fields
        fields = []
        values = []
        
        for key, value in room_data.items():
            if value is not None:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return 0
            
        query = f"UPDATE rooms SET {', '.join(fields)} WHERE room_id = ?"
        values.append(room_id)
        
        cursor = await self.db.execute(query, values)
        await self.db.commit()
        return cursor.rowcount

    async def update_room_end(self, room_data: Dict[str, Any]) -> int:
        """Update room end metadata"""
        query = """
            UPDATE rooms
            SET ended_at = ?, duration_seconds = ?, rounds_completed = ?, participant_count = ?
            WHERE room_id = ?
        """

        cursor = await self.db.execute(query, (
            room_data.get("endedAt") or room_data.get("ended_at"),
            room_data.get("durationSeconds") or room_data.get(
                "duration_seconds"),
            room_data.get("roundsCompleted") or room_data.get(
                "rounds_completed"),
            room_data.get("participantCount") or room_data.get(
                "participant_count"),
            room_data.get("id") or room_data.get("room_id")
        ))

        await self.db.commit()
        return cursor.rowcount

    async def create_agent(self, agent_data: Dict[str, Any]) -> str:
        """Create a new agent instance"""
        query = """
            INSERT INTO agents (
                agent_id, room_id, agent_model, agent_type, status, 
                system_prompt, total_interactions
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        await self.db.execute(query, (
            agent_data.get("agent_id"),
            agent_data.get("room_id"),
            agent_data.get("agent_model"),
            agent_data.get("agent_type", "english"),
            agent_data.get("status", "active"),
            agent_data.get("system_prompt"),
            agent_data.get("total_interactions", 0)
        ))

        await self.db.commit()
        return agent_data.get("agent_id")

    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID"""
        query = "SELECT * FROM agents WHERE agent_id = ?"

        async with self.db.execute(query, (agent_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_agents_by_room(self, room_id: str) -> List[Dict[str, Any]]:
        """Get all agents for a specific room"""
        query = "SELECT * FROM agents WHERE room_id = ? ORDER BY created_at"

        async with self.db.execute(query, (room_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def update_agent_interactions(self, agent_id: str, increment: int = 1) -> int:
        """Update agent interaction count"""
        query = """
            UPDATE agents 
            SET total_interactions = total_interactions + ? 
            WHERE agent_id = ?
        """

        cursor = await self.db.execute(query, (increment, agent_id))
        await self.db.commit()
        return cursor.rowcount

    async def update_agent_status(self, agent_id: str, status: str) -> int:
        """Update agent status"""
        query = "UPDATE agents SET status = ? WHERE agent_id = ?"

        cursor = await self.db.execute(query, (status, agent_id))
        await self.db.commit()
        return cursor.rowcount

    async def delete_agent(self, agent_id: str) -> int:
        """Delete an agent"""
        query = "DELETE FROM agents WHERE agent_id = ?"

        cursor = await self.db.execute(query, (agent_id,))
        await self.db.commit()
        return cursor.rowcount

    async def get_transcript(self, transcript_id: str) -> Optional[Dict[str, Any]]:
        """Get transcript by ID"""
        query = "SELECT * FROM transcripts WHERE transcript_id = ?"

        async with self.db.execute(query, (transcript_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def save_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """Save feedback to database"""
        query = """
            INSERT INTO feedback (
                id, room_id, participant_id, user_id, feedback_type,
                display_message, agent_id, agent_model, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """

        await self.db.execute(query, (
            feedback_data.get("id"),
            feedback_data.get("room_id"),
            feedback_data.get("participant_id"),
            feedback_data.get("user_id"),
            feedback_data.get("feedback_type"),
            feedback_data.get("display_message"),
            feedback_data.get("agent_id"),
            feedback_data.get("agent_model")
        ))

        await self.db.commit()
        return feedback_data.get("id")

    async def get_recent_transcripts(self, room_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent transcripts for a room"""
        query = """
            SELECT * FROM transcripts 
            WHERE room_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """

        async with self.db.execute(query, (room_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_feedback_by_room(self, room_id: str, feedback_type: str = None) -> List[Dict[str, Any]]:
        """Get feedback for a room, optionally filtered by type"""
        if feedback_type:
            query = """
                SELECT * FROM feedback 
                WHERE room_id = ? AND feedback_type = ? 
                ORDER BY created_at DESC
            """
            params = (room_id, feedback_type)
        else:
            query = """
                SELECT * FROM feedback 
                WHERE room_id = ? 
                ORDER BY created_at DESC
            """
            params = (room_id,)

        async with self.db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def save_transcript(self, transcript_data: Dict[str, Any]) -> str:
        """Save transcript to database"""
        query = """
            INSERT INTO transcripts (
                transcript_id, room_id, participant_id, user_id, round_number, turn_order,
                transcript_text, language, stt_confidence, started_at, ended_at, 
                duration_seconds, word_count, speech_rate, is_processed, audio_file_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        await self.db.execute(query, (
            transcript_data.get("transcript_id"),
            transcript_data.get("room_id"),
            transcript_data.get("participant_id"),
            transcript_data.get("user_id"),
            transcript_data.get("round_number", 1),
            transcript_data.get("turn_order", 0),
            transcript_data.get("transcript_text"),
            transcript_data.get("language", "en"),
            transcript_data.get("stt_confidence", 0.0),
            transcript_data.get("started_at"),
            transcript_data.get("ended_at"),
            transcript_data.get("duration_seconds", 0),
            transcript_data.get("word_count", 0),
            transcript_data.get("speech_rate", 0.0),
            transcript_data.get("is_processed", 0),
            transcript_data.get("audio_file_url")
        ))

        await self.db.commit()
        return transcript_data.get("transcript_id")

    async def close(self):
        """Close database connection"""
        if self.db:
            await self.db.close()
            print("Database connection closed")


# Singleton instance
db = Database()

if __name__ == "__main__":
    import asyncio

    async def main():
        await db.initialize(os.getenv("DATABASE_URL", "./data/gupshup-database.db"))
        # You can add test calls here to verify functionality
        await db.close()

    asyncio.run(main())
