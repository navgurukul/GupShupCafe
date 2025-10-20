#!/usr/bin/env python3
"""
Database Migration Script for GupShup Cafe
Handles schema updates and data migrations for different versions
"""

import asyncio
import aiosqlite
import os
import sys
from pathlib import Path
from datetime import datetime

class DatabaseMigrator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations = [
            self.migration_001_add_rounds_completed,
            self.migration_002_remove_foreign_keys,
            self.migration_003_fix_participants_schema,
            self.migration_004_add_missing_indexes,
        ]
    
    async def migrate(self):
        """Run all pending migrations"""
        print(f"Starting database migration for: {self.db_path}")
        
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Create migrations table if it doesn't exist
            await self.create_migrations_table(db)
            
            # Get list of completed migrations
            completed_migrations = await self.get_completed_migrations(db)
            
            # Run pending migrations
            for migration in self.migrations:
                migration_name = migration.__name__
                if migration_name not in completed_migrations:
                    print(f"Running migration: {migration_name}")
                    try:
                        await migration(db)
                        await self.mark_migration_completed(db, migration_name)
                        print(f"Migration {migration_name} completed successfully")
                    except Exception as e:
                        print(f"Migration {migration_name} failed: {str(e)}")
                        raise
                else:
                    print(f"Migration {migration_name} already completed, skipping")
            
            await db.commit()
            print("All migrations completed successfully!")
    
    async def create_migrations_table(self, db):
        """Create migrations tracking table"""
        await db.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT UNIQUE NOT NULL,
                executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """)
        await db.commit()
    
    async def get_completed_migrations(self, db):
        """Get list of completed migrations"""
        cursor = await db.execute("SELECT migration_name FROM migrations")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    async def mark_migration_completed(self, db, migration_name):
        """Mark a migration as completed"""
        await db.execute(
            "INSERT INTO migrations (migration_name, description) VALUES (?, ?)",
            (migration_name, f"Migration executed at {datetime.now().isoformat()}")
        )
    
    async def migration_001_add_rounds_completed(self, db):
        """Add rounds_completed column to rooms table"""
        # Check if column exists
        cursor = await db.execute("PRAGMA table_info(rooms)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'rounds_completed' not in column_names:
            print("  Adding rounds_completed column to rooms table")
            await db.execute("ALTER TABLE rooms ADD COLUMN rounds_completed INTEGER DEFAULT 0")
        else:
            print("  rounds_completed column already exists")
    
    async def migration_002_remove_foreign_keys(self, db):
        """Remove problematic foreign key constraints"""
        # Check if agents table has foreign key constraints
        cursor = await db.execute("PRAGMA foreign_key_list(agents)")
        fk_constraints = await cursor.fetchall()
        
        if fk_constraints:
            print("  Removing foreign key constraints from agents table")
            # Create new table without foreign keys
            await db.execute("""
                CREATE TABLE agents_new (
                    agent_id TEXT PRIMARY KEY,
                    room_id TEXT NOT NULL,
                    agent_model TEXT NOT NULL,
                    agent_type TEXT DEFAULT 'english',
                    status TEXT DEFAULT 'active',
                    system_prompt TEXT,
                    total_interactions INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """)
            
            # Copy data from old table to new table
            await db.execute("""
                INSERT INTO agents_new 
                SELECT agent_id, room_id, agent_model, agent_type, status, 
                       system_prompt, total_interactions, created_at
                FROM agents
            """)
            
            # Drop old table and rename new table
            await db.execute("DROP TABLE agents")
            await db.execute("ALTER TABLE agents_new RENAME TO agents")
        else:
            print("  No foreign key constraints found in agents table")
    
    async def migration_003_fix_participants_schema(self, db):
        """Fix participants table schema issues"""
        # Check if participants table has the correct columns
        cursor = await db.execute("PRAGMA table_info(participants)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Check for problematic columns that might exist in old schema
        problematic_columns = ['campus', 'location']
        has_problematic_columns = any(col in column_names for col in problematic_columns)
        
        if has_problematic_columns:
            print("  Fixing participants table schema")
            
            # Create new participants table with correct schema
            await db.execute("""
                CREATE TABLE participants_new (
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
                    
                    -- Tracking
                    speaking_time_seconds INTEGER DEFAULT 0
                )
            """)
            
            # Copy data from old table, combining campus and location
            await db.execute("""
                INSERT INTO participants_new (
                    participant_id, user_id, room_id, anonymous_name, avatar_color,
                    role, is_ready, turn_order, is_speaking, is_muted, socket_id,
                    starting_cefr_level, ending_cefr_level, joined_at, left_at,
                    campusOrLocation, speaking_time_seconds
                )
                SELECT 
                    participant_id, user_id, room_id, anonymous_name, avatar_color,
                    role, is_ready, turn_order, is_speaking, is_muted, socket_id,
                    starting_cefr_level, ending_cefr_level, joined_at, left_at,
                    CASE 
                        WHEN campus IS NOT NULL AND location IS NOT NULL THEN campus || ', ' || location
                        WHEN campus IS NOT NULL THEN campus
                        WHEN location IS NOT NULL THEN location
                        ELSE NULL
                    END as campusOrLocation,
                    speaking_time_seconds
                FROM participants
            """)
            
            # Drop old table and rename new table
            await db.execute("DROP TABLE participants")
            await db.execute("ALTER TABLE participants_new RENAME TO participants")
        else:
            print("  Participants table schema is already correct")
    
    async def migration_004_add_missing_indexes(self, db):
        """Add missing indexes for better performance"""
        indexes = [
            ("idx_rooms_status", "CREATE INDEX IF NOT EXISTS idx_rooms_status ON rooms(status)"),
            ("idx_participants_room_id", "CREATE INDEX IF NOT EXISTS idx_participants_room_id ON participants(room_id)"),
            ("idx_participants_user_id", "CREATE INDEX IF NOT EXISTS idx_participants_user_id ON participants(user_id)"),
            ("idx_agents_room_id", "CREATE INDEX IF NOT EXISTS idx_agents_room_id ON agents(room_id)"),
            ("idx_transcripts_room_id", "CREATE INDEX IF NOT EXISTS idx_transcripts_room_id ON transcripts(room_id)"),
            ("idx_feedback_room_id", "CREATE INDEX IF NOT EXISTS idx_feedback_room_id ON feedback(room_id)"),
        ]
        
        for index_name, index_sql in indexes:
            try:
                await db.execute(index_sql)
                print(f"  Added index: {index_name}")
            except Exception as e:
                print(f"  Index {index_name} might already exist: {str(e)}")
    
    async def verify_migration(self):
        """Verify that migration was successful"""
        print("\nVerifying migration results...")
        
        async with aiosqlite.connect(self.db_path) as db:
            # Check rooms table
            cursor = await db.execute("PRAGMA table_info(rooms)")
            rooms_columns = [col[1] for col in await cursor.fetchall()]
            print(f"  Rooms table columns: {len(rooms_columns)} columns")
            if 'rounds_completed' in rooms_columns:
                print("  rounds_completed column exists")
            else:
                print("  rounds_completed column missing")
            
            # Check participants table
            cursor = await db.execute("PRAGMA table_info(participants)")
            participants_columns = [col[1] for col in await cursor.fetchall()]
            print(f"  Participants table columns: {len(participants_columns)} columns")
            if 'campusOrLocation' in participants_columns:
                print("  campusOrLocation column exists")
            else:
                print("  campusOrLocation column missing")
            
            # Check foreign keys
            cursor = await db.execute("PRAGMA foreign_key_list(agents)")
            fk_constraints = await cursor.fetchall()
            if not fk_constraints:
                print("  No foreign key constraints in agents table")
            else:
                print(f"  {len(fk_constraints)} foreign key constraints still exist in agents table")
            
            # Check migrations table
            cursor = await db.execute("SELECT COUNT(*) FROM migrations")
            migration_count = (await cursor.fetchone())[0]
            print(f"  Completed migrations: {migration_count}")

async def main():
    """Main migration function"""
    # Get database path from environment or use default
    db_path = os.getenv("DATABASE_URL", "./data/gupshup-database.db")
    
    print("GupShup Cafe Database Migration Tool")
    print("=" * 50)
    print(f"Database path: {db_path}")
    print(f"Migration date: {datetime.now().isoformat()}")
    print("=" * 50)
    
    try:
        migrator = DatabaseMigrator(db_path)
        await migrator.migrate()
        await migrator.verify_migration()
        
        print("\nMigration completed successfully!")
        print("Your database is now ready for the latest version of GupShup Cafe.")
        
    except Exception as e:
        print(f"\nMigration failed: {str(e)}")
        print("Please check the error message above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
