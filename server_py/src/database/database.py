"""
Database Management
Simple SQLite database for storing session data and analytics
"""

import aiosqlite
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime


class Database:
    def __init__(self):
        self.db: Optional[aiosqlite.Connection] = None
        self.db_path: str = ""

    async def initialize(self, db_path: str = "./database/gupshup_database.db"):
        """Initialize the database connection and create tables"""
        self.db_path = db_path
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create database connection
        self.db = await aiosqlite.connect(db_path)
        self.db.row_factory = aiosqlite.Row
        
        print(f"📊 Connected to SQLite database at {db_path}")
        
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
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    category TEXT, 
                    crf_level INTEGER NOT NULL DEFAULT 0
                    )
            """)
            
        
            
            # Sessions table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    room_name TEXT NOT NULL,
                    topic_title TEXT,
                    topic_category TEXT,
                    participant_count INTEGER,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ended_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration_seconds INTEGER,
                    rounds_completed INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'active',
                    crf_level INTEGER NOT NULL DEFAULT 0
                )
            """)
            
            # Participants table
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS participants (
                    user_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    anonymous_name TEXT,
                    campus TEXT,
                    location TEXT,
                    joined_at DATETIME,
                    left_at DATETIME,
                    speaking_time_seconds INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
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
            
            await self.db.commit()
        
        print("✅ Database tables created/verified")

    async def save_session(self, session_data: Dict[str, Any]) -> int:
        """Save a discussion session"""
        query = """
            INSERT INTO sessions (
                session_id, room_id, room_name, topic_title, topic_category, participant_count,started_at, ended_at, duration_seconds, rounds_completed, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        topic = session_data.get("topic", {})
        cursor = await self.db.execute(query, (
            session_data.get("session_id"),
            session_data.get("room_id"),
            session_data.get("room_name"),
            topic.get("title") if topic else None,
            topic.get("category") if topic else None,
            session_data.get("participantCount"),
            session_data.get("startedAt"),
            session_data.get("endedAt"),
            session_data.get("durationSeconds"),
            session_data.get("roundsCompleted")
        ))
        
        await self.db.commit()
        return cursor.lastrowid

    async def save_participant(self, participant_data: Dict[str, Any]) -> int:
        """Save participant data"""
        query = """
            INSERT INTO participants (
                user_id, session_id, anonymous_name, campus, location,
                joined_at, left_at, speaking_time_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor = await self.db.execute(query, (
            participant_data.get("user_id"),
            participant_data.get("session_id"),
            participant_data.get("anonymous_name"),
            participant_data.get("campus"),
            participant_data.get("location"),
            participant_data.get("joinedAt"),
            participant_data.get("leftAt"),
            participant_data.get("speakingTimeSeconds", 0)
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

    async def get_session_analytics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get session analytics"""
        query = """
            SELECT 
                s.id,
                s.room_id,
                s.topic_title,
                s.topic_category,
                s.participant_count,
                s.started_at,
                s.ended_at,
                s.duration_seconds,
                s.rounds_completed,
                COUNT(p.id) as recorded_participants
            FROM sessions s
            LEFT JOIN participants p ON s.id = p.session_id
            GROUP BY s.id
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
        
        # Total sessions
        async with self.db.execute("SELECT COUNT(*) as count FROM sessions") as cursor:
            row = await cursor.fetchone()
            stats["totalSessions"] = dict(row) if row else {"count": 0}
        
        # Total participants
        async with self.db.execute("SELECT COUNT(DISTINCT user_id) as count FROM participants") as cursor:
            row = await cursor.fetchone()
            stats["totalParticipants"] = dict(row) if row else {"count": 0}
        
        # Average session duration
        async with self.db.execute(
            "SELECT AVG(duration_seconds) as avg FROM sessions WHERE duration_seconds > 0"
        ) as cursor:
            row = await cursor.fetchone()
            stats["avgSessionDuration"] = dict(row) if row else {"avg": 0}
        
        # Average participants per session
        async with self.db.execute(
            "SELECT AVG(participant_count) as avg FROM sessions"
        ) as cursor:
            row = await cursor.fetchone()
            stats["avgParticipantsPerSession"] = dict(row) if row else {"avg": 0}
        
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

    async def update_session_end(self, session_data: Dict[str, Any]) -> int:
        """Update session end metadata"""
        query = """
            UPDATE sessions
            SET ended_at = ?, duration_seconds = ?, rounds_completed = ?, participant_count = ?
            WHERE id = ?
        """
        
        cursor = await self.db.execute(query, (
            session_data.get("endedAt"),
            session_data.get("durationSeconds"),
            session_data.get("roundsCompleted"),
            session_data.get("participantCount"),
            session_data.get("id")
        ))
        
        await self.db.commit()
        return cursor.rowcount

    async def close(self):
        """Close database connection"""
        if self.db:
            await self.db.close()
            print("📊 Database connection closed")


# Singleton instance
db = Database()
