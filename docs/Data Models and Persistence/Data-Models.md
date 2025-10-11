# Data Models and Persistence

## Overview

This document describes the data models, database schema, and data persistence strategy for GupShup Cafe.

---

## Database Technology

**Engine**: SQLite 3.x

**Why SQLite**:
- Zero configuration
- Serverless (file-based)
- Lightweight and fast
- Sufficient for application scale
- Easy to backup and migrate
- ACID compliant

**Limitations**:
- Single writer at a time
- Not suitable for distributed systems
- File-based (not cloud-native)

**Location**: `server/data/discussions.db`

---

## Database Schema

### Entity Relationship Diagram

```
┌──────────────────────────────┐
│         sessions             │
├──────────────────────────────┤
│ id (TEXT, PK)                │
│ room_id (TEXT)               │
│ topic (TEXT)                 │
│ participant_count (INTEGER)  │
│ started_at (DATETIME)        │
│ ended_at (DATETIME)          │
│ duration_seconds (INTEGER)   │
│ rounds_completed (INTEGER)   │
└───────────┬──────────────────┘
            │
            │ 1:N
            │
┌───────────▼──────────────────┐
│       participants           │
├──────────────────────────────┤
│ id (INTEGER, PK, AI)         │
│ session_id (TEXT, FK)        │
│ user_id (TEXT)               │
│ anonymous_name (TEXT)        │
│ role (TEXT)                  │
│ joined_at (DATETIME)         │
└──────────────────────────────┘

┌──────────────────────────────┐
│          topics              │
├──────────────────────────────┤
│ id (INTEGER, PK, AI)         │
│ title (TEXT)                 │
│ description (TEXT)           │
│ category (TEXT)              │
│ source (TEXT)                │
│ used_count (INTEGER)         │
│ created_at (DATETIME)        │
└──────────────────────────────┘
```

---

## Table Definitions

### sessions

Stores information about discussion sessions.

**SQL Schema**:
```sql
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY,
  room_id TEXT NOT NULL,
  topic TEXT,
  participant_count INTEGER DEFAULT 0,
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  ended_at DATETIME,
  duration_seconds INTEGER,
  rounds_completed INTEGER DEFAULT 0
)
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | TEXT | No | UUID v4, primary key |
| `room_id` | TEXT | No | Room identifier (e.g., 'general') |
| `topic` | TEXT | Yes | JSON stringified topic object |
| `participant_count` | INTEGER | No | Number of participants at start |
| `started_at` | DATETIME | No | Session start timestamp |
| `ended_at` | DATETIME | Yes | Session end timestamp (null if ongoing) |
| `duration_seconds` | INTEGER | Yes | Total session duration |
| `rounds_completed` | INTEGER | No | Number of rounds completed |

**Indexes**: None (primary key index automatic)

**Example Row**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "room_id": "general",
  "topic": "{\"title\":\"The Future of Education\",\"category\":\"Education\"}",
  "participant_count": 4,
  "started_at": "2025-10-11 09:00:00",
  "ended_at": "2025-10-11 09:15:00",
  "duration_seconds": 900,
  "rounds_completed": 3
}
```

---

### participants

Stores participant information for each session.

**SQL Schema**:
```sql
CREATE TABLE IF NOT EXISTS participants (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  user_id TEXT NOT NULL,
  anonymous_name TEXT,
  role TEXT DEFAULT 'listener',
  joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (session_id) REFERENCES sessions(id)
)
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INTEGER | No | Auto-increment primary key |
| `session_id` | TEXT | No | Foreign key to sessions.id |
| `user_id` | TEXT | No | User UUID |
| `anonymous_name` | TEXT | Yes | Display name (e.g., 'Brave Lion') |
| `role` | TEXT | No | 'speaker' or 'listener' |
| `joined_at` | DATETIME | No | When user joined session |

**Indexes**: Foreign key index on `session_id`

**Example Row**:
```json
{
  "id": 1,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "anonymous_name": "Brave Lion",
  "role": "speaker",
  "joined_at": "2025-10-11 09:00:00"
}
```

---

### topics

Stores topics and their usage statistics.

**SQL Schema**:
```sql
CREATE TABLE IF NOT EXISTS topics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  description TEXT,
  category TEXT,
  source TEXT DEFAULT 'fallback',
  used_count INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

**Columns**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INTEGER | No | Auto-increment primary key |
| `title` | TEXT | No | Topic title |
| `description` | TEXT | Yes | Topic description |
| `category` | TEXT | Yes | Category (Education, Technology, etc.) |
| `source` | TEXT | No | 'AI Generated' or 'fallback' |
| `used_count` | INTEGER | No | Number of times used |
| `created_at` | DATETIME | No | When topic was first used |

**Indexes**: None

**Example Row**:
```json
{
  "id": 1,
  "title": "The Future of Education",
  "description": "How will technology reshape learning in the next decade?",
  "category": "Education",
  "source": "fallback",
  "used_count": 15,
  "created_at": "2025-10-01 00:00:00"
}
```

---

## Data Access Layer

### Location

`server/src/database/database.js`

### Functions

#### initializeDatabase()

Initialize database connection and create tables if they don't exist.

**Returns**: `Promise<void>`

**Usage**:
```javascript
await initializeDatabase()
```

**Side Effects**:
- Creates database file if it doesn't exist
- Creates all tables
- Establishes connection

---

#### saveSession(sessionData)

Save a new discussion session.

**Parameters**:
```javascript
{
  id: string,
  roomId: string,
  topic: object,
  participantCount: number,
  startedAt: Date,
  endedAt: Date | null,
  durationSeconds: number | null,
  roundsCompleted: number
}
```

**Returns**: `Promise<void>`

**Example**:
```javascript
await saveSession({
  id: uuidv4(),
  roomId: 'general',
  topic: { title: 'The Future of Education', ... },
  participantCount: 4,
  startedAt: new Date(),
  endedAt: null,
  durationSeconds: null,
  roundsCompleted: 0
})
```

---

#### updateSessionEnd(sessionData)

Update session when discussion ends.

**Parameters**:
```javascript
{
  id: string,
  endedAt: Date,
  durationSeconds: number,
  roundsCompleted: number,
  participantCount: number
}
```

**Returns**: `Promise<void>`

**Example**:
```javascript
await updateSessionEnd({
  id: sessionId,
  endedAt: new Date(),
  durationSeconds: 900,
  roundsCompleted: 3,
  participantCount: 4
})
```

---

#### saveParticipant(participantData)

Save participant information.

**Parameters**:
```javascript
{
  sessionId: string,
  userId: string,
  anonymousName: string,
  role: 'speaker' | 'listener',
  joinedAt: Date
}
```

**Returns**: `Promise<void>`

---

#### recordTopicUsage(topic)

Record or update topic usage statistics.

**Parameters**:
```javascript
{
  title: string,
  description: string,
  category: string,
  source: 'AI Generated' | 'fallback'
}
```

**Returns**: `Promise<void>`

**Behavior**:
- If topic exists: Increment `used_count`
- If new topic: Insert with `used_count = 1`

---

#### getSessionAnalytics(limit)

Retrieve recent session analytics.

**Parameters**:
- `limit` (number): Number of sessions to return (default: 10)

**Returns**: `Promise<Session[]>`

**Example**:
```javascript
const sessions = await getSessionAnalytics(20)
console.log(sessions)
```

---

#### getTopicAnalytics()

Get topic usage statistics.

**Returns**: `Promise<Topic[]>`

**Example**:
```javascript
const topics = await getTopicAnalytics()
topics.forEach(topic => {
  console.log(`${topic.title}: used ${topic.used_count} times`)
})
```

---

#### getServerStats()

Get aggregated server statistics.

**Returns**: `Promise<ServerStats>`

**Return Type**:
```javascript
{
  totalSessions: number,
  totalParticipants: number,
  avgSessionDuration: number,
  avgParticipantsPerSession: number,
  topCategories: [
    { category: string, count: number }
  ]
}
```

**Example**:
```javascript
const stats = await getServerStats()
console.log(`Total sessions: ${stats.totalSessions}`)
```

---

## In-Memory State

### Room State

**Not persisted to database** (volatile, in-memory only)

**Data Structure**:
```javascript
Map<roomId, Room> where Room = {
  id: string,
  participants: Participant[],
  discussion: {
    active: boolean,
    topic: Topic,
    currentSpeakerIndex: number,
    speakingTime: number,
    timeRemaining: number,
    round: number,
    timer: NodeJS.Timer,
    startedAt: Date,
    endedAt: Date
  },
  createdAt: Date
}
```

**Why In-Memory**:
- Fast access (no I/O)
- Temporary state (cleared on restart)
- Reduces database writes
- Simplifies implementation

**Trade-offs**:
- Lost on server restart
- Cannot scale horizontally
- No cross-server synchronization

**Future**: Use Redis for persistent, distributed state

---

## Data Flow Diagrams

### Session Creation Flow

```
Discussion Started
       ↓
Generate UUID
       ↓
Create Session Object
       ↓
saveSession(data)
       ↓
INSERT INTO sessions
       ↓
Store session_id in activeSessions Map
       ↓
For each participant:
  saveParticipant(data)
       ↓
  INSERT INTO participants
```

---

### Session Completion Flow

```
Discussion Ended
       ↓
Calculate duration
       ↓
Get session_id from activeSessions Map
       ↓
updateSessionEnd(data)
       ↓
UPDATE sessions SET ended_at, duration_seconds, rounds_completed
       ↓
Remove from activeSessions Map
```

---

### Topic Usage Flow

```
Topic Generated/Selected
       ↓
recordTopicUsage(topic)
       ↓
Query: SELECT * FROM topics WHERE title = ?
       ↓
Exists?
   ↓          ↓
  Yes        No
   ↓          ↓
UPDATE     INSERT
used_count  new row
+= 1
```

---

## Data Consistency

### ACID Properties

SQLite provides ACID guarantees:

- **Atomicity**: Transactions are all-or-nothing
- **Consistency**: Database constraints enforced
- **Isolation**: Transactions don't interfere
- **Durability**: Committed data persists

### Concurrent Access

**Write Lock**: SQLite allows only one writer at a time

**Handling**:
- Database writes are async (non-blocking Node.js)
- Write conflicts are rare (low write volume)
- Errors are logged and handled gracefully

**Future**: Use write-ahead logging (WAL) mode for better concurrency

---

## Backup and Recovery

### Backup Strategy

**Manual Backup**:
```bash
cp server/data/discussions.db server/data/discussions.db.backup
```

**Automated Backup** (Recommended):
```bash
# Daily backup script
0 2 * * * cp /path/to/discussions.db /path/to/backups/discussions-$(date +\%Y\%m\%d).db
```

### Recovery

**From Backup**:
```bash
cp server/data/discussions.db.backup server/data/discussions.db
```

**Data Loss Scenarios**:
- Server crash: Recent sessions lost (if not yet written to DB)
- Database corruption: Restore from backup
- Accidental deletion: Restore from backup

---

## Database Migrations

### Current Implementation

**No migrations framework** (simple schema, stable)

**Tables created on first run** via `CREATE TABLE IF NOT EXISTS`

### Future Migrations

**Recommended Tools**:
- `node-sqlite3-migrations`
- `knex.js` (migration + query builder)

**Migration Pattern**:
```javascript
// migrations/001-add-user-table.js
export const up = (db) => {
  db.run(`ALTER TABLE participants ADD COLUMN email TEXT`)
}

export const down = (db) => {
  db.run(`ALTER TABLE participants DROP COLUMN email`)
}
```

---

## Performance Optimization

### Query Optimization

**Current**:
- Simple queries (no complex joins)
- Indexes on primary keys (automatic)
- Small dataset (< 10k rows typically)

**Recommended Improvements**:
```sql
-- Index for frequent queries
CREATE INDEX idx_sessions_started_at ON sessions(started_at);
CREATE INDEX idx_participants_session_id ON participants(session_id);
CREATE INDEX idx_topics_category ON topics(category);
```

### Connection Pooling

**Not implemented** (single SQLite connection shared)

**Future**: Consider connection pool for concurrent operations

---

## Data Retention Policy

### Current Policy

**Retention**: Indefinite (no automatic deletion)

### Recommended Policy

**Options**:
1. **Time-based**: Delete sessions older than 6 months
2. **Size-based**: Keep last 10,000 sessions
3. **Archive**: Move old data to separate database

**Implementation**:
```sql
-- Delete sessions older than 6 months
DELETE FROM sessions 
WHERE started_at < datetime('now', '-6 months');

-- Also delete orphaned participants
DELETE FROM participants 
WHERE session_id NOT IN (SELECT id FROM sessions);
```

---

## Data Privacy

### Personal Data

**Stored**:
- User name (optional, user-provided)
- Campus/location (optional)
- Anonymous name (randomly generated)

**Not Stored**:
- Email addresses
- Passwords
- IP addresses
- Sensitive personal information

### GDPR Considerations

**Right to Access**: Users can request their data via API

**Right to Deletion**: Implement endpoint to delete user data
```javascript
// Recommended implementation
async function deleteUserData(userId) {
  await db.run('DELETE FROM participants WHERE user_id = ?', [userId])
  // Note: Sessions are anonymized, safe to keep
}
```

---

## Monitoring and Analytics

### Database Health Checks

**Check Connection**:
```javascript
function checkDatabaseHealth() {
  return new Promise((resolve, reject) => {
    db.get('SELECT 1', [], (err, row) => {
      if (err) reject(err)
      else resolve('healthy')
    })
  })
}
```

**Check File Size**:
```bash
ls -lh server/data/discussions.db
```

### Query Performance

**Enable Query Logging** (development):
```javascript
db.on('trace', (sql) => {
  console.log('[SQL]', sql)
})
```

**Measure Query Time**:
```javascript
console.time('query')
await getSessionAnalytics(100)
console.timeEnd('query')
```

---

## Scaling Considerations

### Current Limitations

- Single file database
- In-memory room state
- No horizontal scaling
- Single server deployment

### Scaling Strategy

**Step 1: Optimize SQLite**
- Enable WAL mode
- Add indexes
- Vacuum database periodically

**Step 2: Separate State from Storage**
- Use Redis for room state
- Keep SQLite for analytics

**Step 3: Migrate to PostgreSQL**
- Better concurrency
- Replication support
- Cloud-native options (RDS, etc.)

**Step 4: Horizontal Scaling**
- Load balancer
- Multiple app servers
- Shared Redis + PostgreSQL

---

## Sample Queries

### Recent Sessions with Participants

```sql
SELECT 
  s.id,
  s.topic,
  s.started_at,
  s.duration_seconds,
  s.rounds_completed,
  COUNT(p.id) as participant_count,
  GROUP_CONCAT(p.anonymous_name) as participants
FROM sessions s
LEFT JOIN participants p ON s.id = p.session_id
GROUP BY s.id
ORDER BY s.started_at DESC
LIMIT 10;
```

### Most Active Users

```sql
SELECT 
  user_id,
  anonymous_name,
  COUNT(*) as session_count
FROM participants
GROUP BY user_id
ORDER BY session_count DESC
LIMIT 10;
```

### Topic Popularity

```sql
SELECT 
  category,
  COUNT(*) as usage_count,
  AVG(used_count) as avg_uses_per_topic
FROM topics
GROUP BY category
ORDER BY usage_count DESC;
```

### Average Session Duration by Time of Day

```sql
SELECT 
  CAST(strftime('%H', started_at) AS INTEGER) as hour,
  AVG(duration_seconds) as avg_duration,
  COUNT(*) as session_count
FROM sessions
WHERE duration_seconds IS NOT NULL
GROUP BY hour
ORDER BY hour;
```
