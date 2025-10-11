# Data Models and Persistence

## Overview

This document describes the data models, database schema, and persistence layer of the GupShup Cafe platform. The system uses SQLite for data storage with in-memory state management for real-time operations.

---

## Database Architecture

### Technology Stack

- **Database:** SQLite 3
- **Driver:** sqlite3 (Node.js)
- **Location:** `./data/roundtable.db`
- **Backup:** File-based (easy copy/restore)

### Database Schema Diagram

```
┌─────────────────────────────────┐
│         sessions                │
├─────────────────────────────────┤
│ id (TEXT, PK)                   │
│ room_id (TEXT)                  │
│ topic_title (TEXT)              │
│ topic_category (TEXT)           │
│ participant_count (INTEGER)     │
│ started_at (DATETIME)           │
│ ended_at (DATETIME)             │
│ duration_seconds (INTEGER)      │
│ rounds_completed (INTEGER)      │
│ created_at (DATETIME)           │
└────────────┬────────────────────┘
             │ 1:N
             │
             ▼
┌─────────────────────────────────┐
│       participants              │
├─────────────────────────────────┤
│ id (TEXT, PK)                   │
│ session_id (TEXT, FK)           │
│ user_id (TEXT)                  │
│ anonymous_name (TEXT)           │
│ campus (TEXT)                   │
│ location (TEXT)                 │
│ joined_at (DATETIME)            │
│ left_at (DATETIME)              │
│ speaking_time_seconds (INTEGER) │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│          topics                 │
├─────────────────────────────────┤
│ id (INTEGER, PK, AUTOINCREMENT) │
│ title (TEXT)                    │
│ description (TEXT)              │
│ category (TEXT)                 │
│ source (TEXT)                   │
│ used_count (INTEGER)            │
│ created_at (DATETIME)           │
└─────────────────────────────────┘
```

---

## Tables

### 1. Sessions Table

**Purpose:** Store discussion session records.

**Schema:**

```sql
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  room_id TEXT NOT NULL,
  topic_title TEXT,
  topic_category TEXT,
  participant_count INTEGER,
  started_at DATETIME,
  ended_at DATETIME,
  duration_seconds INTEGER,
  rounds_completed INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| id | TEXT | Unique session identifier (UUID) |
| room_id | TEXT | Room identifier |
| topic_title | TEXT | Discussion topic title |
| topic_category | TEXT | Topic category |
| participant_count | INTEGER | Number of participants |
| started_at | DATETIME | Session start timestamp |
| ended_at | DATETIME | Session end timestamp |
| duration_seconds | INTEGER | Session duration in seconds |
| rounds_completed | INTEGER | Number of completed rounds |
| created_at | DATETIME | Record creation timestamp |

**Indexes:**

```sql
CREATE INDEX idx_sessions_room_id ON sessions(room_id);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_sessions_topic_category ON sessions(topic_category);
```

**Example Data:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "room_id": "room-1642512000",
  "topic_title": "The Future of Education",
  "topic_category": "Education",
  "participant_count": 5,
  "started_at": "2024-01-15T10:00:00.000Z",
  "ended_at": "2024-01-15T10:30:00.000Z",
  "duration_seconds": 1800,
  "rounds_completed": 3,
  "created_at": "2024-01-15T10:00:00.000Z"
}
```

---

### 2. Participants Table

**Purpose:** Track participant information for each session.

**Schema:**

```sql
CREATE TABLE IF NOT EXISTS participants (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  user_id TEXT,
  anonymous_name TEXT,
  campus TEXT,
  location TEXT,
  joined_at DATETIME,
  left_at DATETIME,
  speaking_time_seconds INTEGER DEFAULT 0,
  FOREIGN KEY (session_id) REFERENCES sessions (id)
);
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| id | TEXT | Unique participant record ID |
| session_id | TEXT | Reference to session (Foreign Key) |
| user_id | TEXT | User identifier |
| anonymous_name | TEXT | Anonymous display name |
| campus | TEXT | User's campus |
| location | TEXT | User's location |
| joined_at | DATETIME | Join timestamp |
| left_at | DATETIME | Leave timestamp (NULL if still active) |
| speaking_time_seconds | INTEGER | Total speaking time in seconds |

**Indexes:**

```sql
CREATE INDEX idx_participants_session_id ON participants(session_id);
CREATE INDEX idx_participants_user_id ON participants(user_id);
```

**Example Data:**

```json
{
  "id": "participant-001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "user-123",
  "anonymous_name": "Wise Owl",
  "campus": "Delhi Campus",
  "location": "India",
  "joined_at": "2024-01-15T10:00:00.000Z",
  "left_at": "2024-01-15T10:30:00.000Z",
  "speaking_time_seconds": 180
}
```

---

### 3. Topics Table

**Purpose:** Store and track discussion topics.

**Schema:**

```sql
CREATE TABLE IF NOT EXISTS topics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  category TEXT,
  source TEXT DEFAULT 'fallback',
  used_count INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Auto-incrementing primary key |
| title | TEXT | Topic title |
| description | TEXT | Topic description |
| category | TEXT | Topic category |
| source | TEXT | 'ai' or 'fallback' |
| used_count | INTEGER | Number of times used |
| created_at | DATETIME | Creation timestamp |

**Indexes:**

```sql
CREATE INDEX idx_topics_category ON topics(category);
CREATE INDEX idx_topics_used_count ON topics(used_count);
```

**Example Data:**

```json
{
  "id": 1,
  "title": "The Future of Education",
  "description": "How will technology reshape learning in the next decade?",
  "category": "Education",
  "source": "fallback",
  "used_count": 15,
  "created_at": "2024-01-01T00:00:00.000Z"
}
```

---

## Data Models

### In-Memory Models

These models exist in server memory for real-time operations.

#### Room Model

```typescript
interface Room {
  id: string;
  participants: Participant[];
  discussion: Discussion;
  createdAt: Date;
}

interface Participant {
  id: string;
  socketId: string;
  anonymousName: string;
  campus: string;
  location: string;
  isReady: boolean;
  role: 'speaker' | 'listener';
  joinedAt: Date;
}

interface Discussion {
  active: boolean;
  topic: Topic | null;
  currentSpeakerIndex: number;
  speakingTime: number;
  timeRemaining: number;
  round: number;
  timer: NodeJS.Timer | null;
  startedAt: Date | null;
  endedAt: Date | null;
}
```

**Location:** `server/src/socket/roomManager.js`

**Lifecycle:**
- Created when first user joins
- Updated during discussion
- Deleted when empty or expired

---

#### Topic Model

```typescript
interface Topic {
  title: string;
  description: string;
  category: string;
  questions: string[];
  source?: 'ai' | 'fallback';
}
```

**Example:**
```json
{
  "title": "The Future of Education",
  "description": "How will technology reshape learning in the next decade?",
  "category": "Education",
  "questions": [
    "What role should AI play in personalized learning?",
    "How can we maintain human connection in digital education?",
    "What skills will be most important for future students?"
  ],
  "source": "fallback"
}
```

---

#### User Model

```typescript
interface User {
  id: string;
  name: string;
  campus: string;
  location: string;
  anonymousName: string;
}
```

**Storage:** LocalStorage (client-side)

**Key:** `user`

**Example:**
```json
{
  "id": "user-123",
  "name": "John Doe",
  "campus": "Delhi Campus",
  "location": "India",
  "anonymousName": "Wise Owl"
}
```

---

## Database Operations

### Initialization

**Function:** `initializeDatabase()`

**Location:** `server/src/database/database.js`

```javascript
export async function initializeDatabase() {
  try {
    const dbPath = process.env.DATABASE_URL || './data/roundtable.db';
    
    // Ensure data directory exists
    await mkdir(dirname(dbPath), { recursive: true });
    
    // Create database connection
    db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('Database connection error:', err.message);
        throw err;
      }
      console.log('📊 Connected to SQLite database');
    });

    // Create tables
    await createTables();
    
    return db;
  } catch (error) {
    console.error('Database initialization error:', error);
    throw error;
  }
}
```

---

### Session Operations

#### Save Session

```javascript
export async function saveSession(sessionData) {
  return new Promise((resolve, reject) => {
    const {
      id,
      roomId,
      topic,
      participantCount,
      startedAt,
      endedAt,
      durationSeconds,
      roundsCompleted
    } = sessionData;

    const query = `
      INSERT INTO sessions (
        id, room_id, topic_title, topic_category, participant_count,
        started_at, ended_at, duration_seconds, rounds_completed
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;

    db.run(query, [
      id,
      roomId,
      topic?.title,
      topic?.category,
      participantCount,
      startedAt,
      endedAt,
      durationSeconds,
      roundsCompleted
    ], function(err) {
      if (err) {
        console.error('Error saving session:', err);
        reject(err);
        return;
      }
      resolve(this.lastID);
    });
  });
}
```

#### Update Session End

```javascript
export async function updateSessionEnd(sessionId, endedAt, durationSeconds) {
  return new Promise((resolve, reject) => {
    const query = `
      UPDATE sessions 
      SET ended_at = ?, duration_seconds = ? 
      WHERE id = ?
    `;

    db.run(query, [endedAt, durationSeconds, sessionId], function(err) {
      if (err) reject(err);
      else resolve(this.changes);
    });
  });
}
```

#### Get Session Analytics

```javascript
export async function getSessionAnalytics(limit = 10) {
  return new Promise((resolve, reject) => {
    const query = `
      SELECT * FROM sessions 
      ORDER BY created_at DESC 
      LIMIT ?
    `;

    db.all(query, [limit], (err, rows) => {
      if (err) {
        console.error('Error getting session analytics:', err);
        reject(err);
        return;
      }
      resolve(rows);
    });
  });
}
```

---

### Participant Operations

#### Save Participant

```javascript
export async function saveParticipant(participantData) {
  return new Promise((resolve, reject) => {
    const {
      id,
      sessionId,
      userId,
      anonymousName,
      campus,
      location,
      joinedAt,
      speakingTime
    } = participantData;

    const query = `
      INSERT INTO participants (
        id, session_id, user_id, anonymous_name, campus, 
        location, joined_at, speaking_time_seconds
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `;

    db.run(query, [
      id,
      sessionId,
      userId,
      anonymousName,
      campus,
      location,
      joinedAt,
      speakingTime || 0
    ], function(err) {
      if (err) reject(err);
      else resolve(this.lastID);
    });
  });
}
```

---

### Topic Operations

#### Record Topic Usage

```javascript
export async function recordTopicUsage(topic) {
  return new Promise((resolve, reject) => {
    // First, check if topic exists
    const selectQuery = `
      SELECT id FROM topics 
      WHERE title = ?
    `;

    db.get(selectQuery, [topic.title], (err, row) => {
      if (err) {
        reject(err);
        return;
      }

      if (row) {
        // Update usage count
        const updateQuery = `
          UPDATE topics 
          SET used_count = used_count + 1 
          WHERE id = ?
        `;
        
        db.run(updateQuery, [row.id], (err) => {
          if (err) reject(err);
          else resolve(row.id);
        });
      } else {
        // Insert new topic
        const insertQuery = `
          INSERT INTO topics (
            title, description, category, source, used_count
          ) VALUES (?, ?, ?, ?, 1)
        `;

        db.run(insertQuery, [
          topic.title,
          topic.description,
          topic.category,
          topic.source || 'fallback'
        ], function(err) {
          if (err) reject(err);
          else resolve(this.lastID);
        });
      }
    });
  });
}
```

#### Get Topic Analytics

```javascript
export async function getTopicAnalytics() {
  return new Promise((resolve, reject) => {
    const query = `
      SELECT * FROM topics 
      ORDER BY used_count DESC
    `;

    db.all(query, [], (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}
```

---

### Statistics Operations

#### Get Server Statistics

```javascript
export async function getServerStats() {
  return new Promise((resolve, reject) => {
    const stats = {
      totalSessions: 0,
      totalParticipants: 0,
      totalTopics: 0,
      averageSessionDuration: 0,
      averageParticipantsPerSession: 0
    };

    let completed = 0;
    const total = 5;

    function checkComplete() {
      completed++;
      if (completed === total) {
        resolve(stats);
      }
    }

    // Get total sessions
    db.get('SELECT COUNT(*) as count FROM sessions', [], (err, row) => {
      if (!err) stats.totalSessions = row.count;
      checkComplete();
    });

    // Get total participants
    db.get('SELECT COUNT(*) as count FROM participants', [], (err, row) => {
      if (!err) stats.totalParticipants = row.count;
      checkComplete();
    });

    // Get total topics
    db.get('SELECT COUNT(*) as count FROM topics', [], (err, row) => {
      if (!err) stats.totalTopics = row.count;
      checkComplete();
    });

    // Get average session duration
    db.get('SELECT AVG(duration_seconds) as avg FROM sessions', [], (err, row) => {
      if (!err) stats.averageSessionDuration = Math.round(row.avg || 0);
      checkComplete();
    });

    // Get average participants per session
    db.get('SELECT AVG(participant_count) as avg FROM sessions', [], (err, row) => {
      if (!err) stats.averageParticipantsPerSession = Math.round(row.avg || 0);
      checkComplete();
    });
  });
}
```

---

## Data Flow

### Session Lifecycle

```
1. User joins lobby
   └─> In-memory room created

2. Users mark ready
   └─> Room state updated

3. Discussion starts
   ├─> Session record created in DB
   └─> Participants saved to DB

4. Discussion proceeds
   └─> In-memory state updates

5. Discussion ends
   ├─> Session end time updated
   ├─> Final stats saved
   └─> Room cleaned from memory
```

### Data Persistence Strategy

**Real-time Operations:**
- Use in-memory data structures (RoomManager)
- Fast read/write for active sessions
- Socket.io event broadcasting

**Historical Data:**
- Write to SQLite asynchronously
- Analytics queries on demand
- Batch operations when possible

---

## Data Validation

### Server-Side Validation

```javascript
const validateSessionData = (data) => {
  const errors = [];
  
  if (!data.id) errors.push('Session ID required');
  if (!data.roomId) errors.push('Room ID required');
  if (!data.topic) errors.push('Topic required');
  if (data.participantCount < 1) errors.push('Invalid participant count');
  
  return errors;
};
```

### Client-Side Validation

```javascript
const validateUserData = (data) => {
  const errors = {};
  
  if (!data.id?.trim()) errors.id = 'ID is required';
  if (!data.name?.trim()) errors.name = 'Name is required';
  if (!data.campus?.trim()) errors.campus = 'Campus is required';
  if (!data.location?.trim()) errors.location = 'Location is required';
  
  return errors;
};
```

---

## Backup and Recovery

### Database Backup

**Manual Backup:**
```bash
cp data/roundtable.db data/roundtable_backup_$(date +%Y%m%d).db
```

**Automated Backup (Recommended):**
```javascript
import { copyFile } from 'fs/promises';

const backupDatabase = async () => {
  const date = new Date().toISOString().split('T')[0];
  const source = './data/roundtable.db';
  const dest = `./backups/roundtable_${date}.db`;
  
  await copyFile(source, dest);
  console.log('Database backed up:', dest);
};

// Run daily
setInterval(backupDatabase, 24 * 60 * 60 * 1000);
```

### Data Recovery

```javascript
import { copyFile } from 'fs/promises';

const restoreDatabase = async (backupFile) => {
  await copyFile(backupFile, './data/roundtable.db');
  console.log('Database restored from:', backupFile);
};
```

---

## Performance Optimization

### Query Optimization

**Use Indexes:**
```sql
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_participants_session_id ON participants(session_id);
```

**Use Prepared Statements:**
```javascript
const stmt = db.prepare('SELECT * FROM sessions WHERE id = ?');
stmt.get(sessionId, callback);
stmt.finalize();
```

### Connection Pooling

Currently using single connection. For high load:

```javascript
// Consider using better-sqlite3 for synchronous operations
import Database from 'better-sqlite3';

const db = new Database('./data/roundtable.db');
db.pragma('journal_mode = WAL');
```

---

## Data Privacy

### User Data Handling

- **No passwords stored**
- **Anonymous names for discussions**
- **Location data limited to city/region**
- **Session data aggregated for analytics**
- **No personally identifiable information (PII)**

### Data Retention

- **Active sessions:** Until discussion ends
- **Historical sessions:** Indefinite (for analytics)
- **Participant records:** Linked to sessions
- **Topics:** Permanent (with usage tracking)

### GDPR Compliance

For production deployment:
- Implement data deletion requests
- Add user consent mechanisms
- Provide data export functionality
- Anonymize or delete old records

---

## Migration and Versioning

### Schema Versioning

```javascript
const SCHEMA_VERSION = 1;

// Store version in database
db.run('CREATE TABLE IF NOT EXISTS schema_info (version INTEGER)');
db.run('INSERT OR REPLACE INTO schema_info VALUES (?)', [SCHEMA_VERSION]);
```

### Future Migrations

```javascript
const migrations = {
  2: `ALTER TABLE sessions ADD COLUMN session_type TEXT DEFAULT 'roundtable'`,
  3: `CREATE TABLE recordings (id TEXT PRIMARY KEY, session_id TEXT, url TEXT)`
};

const runMigrations = async (currentVersion) => {
  for (let version = currentVersion + 1; version in migrations; version++) {
    await db.run(migrations[version]);
    await db.run('UPDATE schema_info SET version = ?', [version]);
  }
};
```

---

## Troubleshooting

### Common Issues

**Database Locked:**
```javascript
// Use WAL mode
db.run('PRAGMA journal_mode = WAL');
```

**Connection Errors:**
```javascript
// Check database file permissions
// Ensure data directory exists
```

**Memory Leaks:**
```javascript
// Clean up old rooms
setInterval(() => {
  roomManager.cleanupInactiveRooms();
}, 60000);
```

---

## Testing

### Database Testing

```javascript
// Test database operations
describe('Database Operations', () => {
  beforeEach(async () => {
    await initializeDatabase();
  });
  
  test('Save session', async () => {
    const session = {
      id: 'test-session',
      roomId: 'test-room',
      topic: { title: 'Test Topic' },
      participantCount: 3,
      startedAt: new Date(),
      endedAt: new Date(),
      durationSeconds: 1800,
      roundsCompleted: 3
    };
    
    const result = await saveSession(session);
    expect(result).toBeDefined();
  });
});
```

---

## Support

For data-related issues:
- Check database file existence and permissions
- Verify SQLite version compatibility
- Review error logs for database operations
- Ensure proper connection handling
