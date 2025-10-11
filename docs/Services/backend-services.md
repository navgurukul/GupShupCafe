# Services Documentation

## Overview

This document describes the backend services and modules that power the GupShup Cafe platform. Each service is responsible for a specific domain of functionality.

---

## Service Architecture

```
┌─────────────────────────────────────────────────┐
│              Express.js Server                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐  ┌──────────────┐           │
│  │ API Routes   │  │Socket Handler│           │
│  │  Service     │  │   Service    │           │
│  └──────┬───────┘  └──────┬───────┘           │
│         │                  │                    │
│         └─────────┬────────┘                    │
│                   │                             │
│  ┌────────────────▼────────────┐               │
│  │      Core Services          │               │
│  ├─────────────────────────────┤               │
│  │ • Room Manager              │               │
│  │ • Topic Generator           │               │
│  │ • Database Service          │               │
│  └─────────────────────────────┘               │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## 1. Room Manager Service

**Location:** `server/src/socket/roomManager.js`

**Purpose:** Manages discussion rooms and participant state.

### Class: RoomManager

**Responsibilities:**
- Room creation and deletion
- Participant management
- Discussion state tracking
- Room cleanup

### API Reference

#### `getRoom(roomId: string): Room`

Get or create a room.

```javascript
const room = roomManager.getRoom('room-123');
console.log('Participants:', room.participants.length);
```

**Returns:**
```javascript
{
  id: string,
  participants: Participant[],
  discussion: Discussion,
  createdAt: Date
}
```

#### `addUserToRoom(roomId: string, userData: UserData): Room`

Add a user to a room.

```javascript
const room = roomManager.addUserToRoom('room-123', {
  id: 'user-123',
  socketId: socket.id,
  anonymousName: 'Wise Owl',
  campus: 'Delhi Campus',
  location: 'India',
  role: 'speaker'
});
```

**Features:**
- Prevents duplicate participants
- Handles reconnections
- Updates participant list

#### `removeUserFromRoom(roomId: string, userId: string): void`

Remove a user from a room.

```javascript
roomManager.removeUserFromRoom('room-123', 'user-123');
```

**Auto-cleanup:**
- Deletes room if empty
- Clears timers
- Saves session data

#### `updateUserReady(roomId: string, userId: string, isReady: boolean): Room`

Update user's ready status.

```javascript
const room = roomManager.updateUserReady('room-123', 'user-123', true);

const allReady = room.participants.every(p => p.isReady);
```

#### `startDiscussion(roomId: string, topic: Topic): Room`

Start a discussion with a topic.

```javascript
const topic = await generateDiscussionTopic();
const room = roomManager.startDiscussion('room-123', topic);

console.log('Discussion started:', room.discussion.active);
```

**Sets:**
- `discussion.active = true`
- `discussion.topic = topic`
- `discussion.currentSpeakerIndex = 0`
- `discussion.startedAt = new Date()`

#### `advanceSpeaker(roomId: string): { room: Room, speaker: Participant }`

Advance to the next speaker.

```javascript
const { room, speaker } = roomManager.advanceSpeaker('room-123');

console.log('Current speaker:', speaker.anonymousName);
console.log('Round:', room.discussion.round);
```

**Logic:**
- Increments speaker index
- Wraps to 0 when reaching end
- Increments round when full cycle

#### `endDiscussion(roomId: string): Room`

End the discussion.

```javascript
const room = roomManager.endDiscussion('room-123');

console.log('Duration:', room.discussion.endedAt - room.discussion.startedAt);
```

**Cleanup:**
- Stops timer
- Sets `active = false`
- Records end time
- Saves session to database

#### `getAllRooms(): Map<string, Room>`

Get all active rooms.

```javascript
const rooms = roomManager.getAllRooms();

console.log('Active rooms:', rooms.size);
```

#### `deleteRoom(roomId: string): void`

Delete a room.

```javascript
roomManager.deleteRoom('room-123');
```

### Implementation Example

```javascript
class RoomManager {
  constructor() {
    this.rooms = new Map();
  }
  
  getRoom(roomId) {
    if (!this.rooms.has(roomId)) {
      this.rooms.set(roomId, {
        id: roomId,
        participants: [],
        discussion: {
          active: false,
          topic: null,
          currentSpeakerIndex: 0,
          speakingTime: 60,
          timeRemaining: 0,
          round: 1,
          timer: null,
          startedAt: null,
          endedAt: null
        },
        createdAt: new Date()
      });
    }
    return this.rooms.get(roomId);
  }
  
  addUserToRoom(roomId, userData) {
    const room = this.getRoom(roomId);
    
    // Remove if already exists (reconnection)
    this.removeUserFromRoom(roomId, userData.id);
    
    // Add user
    room.participants.push({
      ...userData,
      isReady: false,
      joinedAt: new Date()
    });
    
    return room;
  }
  
  removeUserFromRoom(roomId, userId) {
    const room = this.rooms.get(roomId);
    if (!room) return;
    
    room.participants = room.participants.filter(p => p.id !== userId);
    
    // Cleanup empty rooms
    if (room.participants.length === 0) {
      this.deleteRoom(roomId);
    }
    
    return room;
  }
}

export const roomManager = new RoomManager();
```

---

## 2. Topic Generator Service

**Location:** `server/src/ai/topicGenerator.js`

**Purpose:** Generate discussion topics using AI or fallback library.

### Functions

#### `generateDiscussionTopic(category?: string): Promise<Topic>`

Generate a discussion topic using AI.

```javascript
const topic = await generateDiscussionTopic('Education');

console.log('Title:', topic.title);
console.log('Category:', topic.category);
console.log('Questions:', topic.questions);
```

**Parameters:**
- `category` (optional) - Topic category filter

**Returns:**
```javascript
{
  title: string,
  description: string,
  category: string,
  questions: string[],
  source: 'ai' | 'fallback'
}
```

**Flow:**
1. Tries AI generation via Hugging Face
2. Falls back to curated topics if AI fails
3. Returns formatted topic object

**AI Generation:**

```javascript
const response = await fetch(HUGGINGFACE_API_URL, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    inputs: generatePrompt(category),
    parameters: {
      max_new_tokens: 250,
      temperature: 0.7,
      top_p: 0.9
    }
  })
});
```

#### `getAllFallbackTopics(): Topic[]`

Get all fallback topics.

```javascript
const topics = getAllFallbackTopics();

console.log('Available topics:', topics.length);
```

**Returns:** Array of 10 curated educational topics

#### `getTopicByCategory(category: string): Topic | null`

Get a fallback topic by category.

```javascript
const topic = getTopicByCategory('Technology');

if (topic) {
  console.log('Found topic:', topic.title);
}
```

**Categories:**
- Education
- Technology
- Health
- Environment
- Arts & Culture
- Science
- Social Issues
- Career Development

### Fallback Topics

```javascript
const fallbackTopics = [
  {
    title: "The Future of Education",
    description: "How will technology reshape learning in the next decade?",
    category: "Education",
    questions: [
      "What role should AI play in personalized learning?",
      "How can we maintain human connection in digital education?",
      "What skills will be most important for future students?"
    ]
  },
  // ... 9 more topics
];
```

### Prompt Engineering

```javascript
const generatePrompt = (category) => {
  return `Generate an educational discussion topic${category ? ` about ${category}` : ''}.

Format:
Title: [Engaging topic title]
Description: [Brief description]
Questions:
1. [Discussion question 1]
2. [Discussion question 2]
3. [Discussion question 3]

Requirements:
- Make it relevant and thought-provoking
- Suitable for group discussion
- Educational value
- Multiple perspectives possible`;
};
```

### Error Handling

```javascript
try {
  const topic = await generateDiscussionTopic(category);
  return topic;
} catch (error) {
  console.error('AI generation failed:', error);
  
  // Fallback to curated topics
  return getTopicByCategory(category) || getFallbackTopic();
}
```

---

## 3. Database Service

**Location:** `server/src/database/database.js`

**Purpose:** Manage SQLite database operations.

### Functions

#### `initializeDatabase(): Promise<Database>`

Initialize database connection and create tables.

```javascript
await initializeDatabase();
console.log('Database initialized');
```

**Creates tables:**
- sessions
- participants
- topics

#### `getDatabase(): Database`

Get database instance.

```javascript
const db = getDatabase();

db.run('SELECT * FROM sessions', [], (err, rows) => {
  // Handle query
});
```

#### `saveSession(sessionData: SessionData): Promise<number>`

Save a discussion session.

```javascript
const sessionId = await saveSession({
  id: 'session-123',
  roomId: 'room-123',
  topic: {
    title: 'The Future of Education',
    category: 'Education'
  },
  participantCount: 5,
  startedAt: new Date(),
  endedAt: new Date(),
  durationSeconds: 1800,
  roundsCompleted: 3
});
```

**Returns:** Last inserted ID

#### `saveParticipant(participantData: ParticipantData): Promise<number>`

Save participant data.

```javascript
await saveParticipant({
  id: 'participant-123',
  sessionId: 'session-123',
  userId: 'user-123',
  anonymousName: 'Wise Owl',
  campus: 'Delhi Campus',
  location: 'India',
  joinedAt: new Date(),
  speakingTime: 60
});
```

#### `recordTopicUsage(topic: Topic): Promise<number>`

Record or update topic usage.

```javascript
await recordTopicUsage({
  title: 'The Future of Education',
  description: 'How will technology reshape learning?',
  category: 'Education',
  source: 'fallback'
});
```

**Behavior:**
- Creates topic if doesn't exist
- Increments `used_count` if exists

#### `getSessionAnalytics(limit?: number): Promise<Session[]>`

Get session analytics.

```javascript
const sessions = await getSessionAnalytics(20);

sessions.forEach(session => {
  console.log('Session:', session.id);
  console.log('Participants:', session.participant_count);
  console.log('Duration:', session.duration_seconds);
});
```

#### `getTopicAnalytics(): Promise<Topic[]>`

Get topic usage statistics.

```javascript
const topics = await getTopicAnalytics();

topics.forEach(topic => {
  console.log('Topic:', topic.title);
  console.log('Used:', topic.used_count, 'times');
});
```

#### `getServerStats(): Promise<ServerStats>`

Get server statistics.

```javascript
const stats = await getServerStats();

console.log('Total sessions:', stats.totalSessions);
console.log('Total participants:', stats.totalParticipants);
console.log('Average duration:', stats.averageSessionDuration);
```

**Returns:**
```javascript
{
  totalSessions: number,
  totalParticipants: number,
  totalTopics: number,
  averageSessionDuration: number,
  averageParticipantsPerSession: number
}
```

---

## 4. Socket Handler Service

**Location:** `server/src/socket/socketHandlers.js`

**Purpose:** Handle Socket.io events and real-time communication.

### Function: `setupSocketHandlers(io: Server)`

Initialize Socket.io event handlers.

```javascript
import { setupSocketHandlers } from './socket/socketHandlers.js';

const io = new Server(server);
setupSocketHandlers(io);
```

### Event Handlers

#### Connection Events

**`connection`**
```javascript
io.on('connection', (socket) => {
  const userData = socket.handshake.auth;
  console.log('User connected:', userData.anonymousName);
});
```

**`disconnect`**
```javascript
socket.on('disconnect', () => {
  // Handle user disconnection
  // Remove from room
  // Notify others
});
```

#### Room Events

**`join-room`**
```javascript
socket.on('join-room', (roomId, options) => {
  // Add user to room
  const room = roomManager.addUserToRoom(roomId, userData);
  
  // Join socket room
  socket.join(roomId);
  
  // Notify all participants
  io.to(roomId).emit('participants-update', room.participants);
});
```

**`leave-room`**
```javascript
socket.on('leave-room', () => {
  // Remove user from room
  const roomId = socket.currentRoom;
  roomManager.removeUserFromRoom(roomId, userData.id);
  
  // Notify others
  io.to(roomId).emit('participants-update', participants);
});
```

**`user-ready`**
```javascript
socket.on('user-ready', (isReady) => {
  // Update ready status
  const room = roomManager.updateUserReady(roomId, userData.id, isReady);
  
  // Broadcast update
  io.to(roomId).emit('participants-update', room.participants);
  
  // Check if can start
  if (allReady && minParticipants) {
    startDiscussion(roomId);
  }
});
```

#### Discussion Events

**`next-speaker`**
```javascript
socket.on('next-speaker', () => {
  // Advance to next speaker
  const { room, speaker } = roomManager.advanceSpeaker(roomId);
  
  // Notify all
  io.to(roomId).emit('next-turn', {
    currentSpeaker: speaker,
    round: room.discussion.round,
    timeRemaining: room.discussion.timeRemaining
  });
});
```

#### Timer Management

```javascript
const startTimer = (room, io) => {
  // Clear existing timer
  if (room.discussion.timer) {
    clearInterval(room.discussion.timer);
  }
  
  // Start new timer
  room.discussion.timer = setInterval(() => {
    room.discussion.timeRemaining--;
    
    // Emit update
    io.to(room.id).emit('timer-update', {
      timeRemaining: room.discussion.timeRemaining,
      speakerId: getCurrentSpeaker(room).id
    });
    
    // Check if time's up
    if (room.discussion.timeRemaining <= 0) {
      clearInterval(room.discussion.timer);
      advanceToNextSpeaker(room, io);
    }
  }, 1000);
};
```

#### WebRTC Signaling

**`webrtc-offer`**
```javascript
socket.on('webrtc-offer', ({ to, offer }) => {
  // Forward offer to target peer
  io.to(to).emit('webrtc-offer', {
    from: socket.id,
    offer: offer
  });
});
```

**`webrtc-answer`**
```javascript
socket.on('webrtc-answer', ({ to, answer }) => {
  // Forward answer to peer
  io.to(to).emit('webrtc-answer', {
    from: socket.id,
    answer: answer
  });
});
```

**`webrtc-ice-candidate`**
```javascript
socket.on('webrtc-ice-candidate', ({ to, candidate }) => {
  // Forward ICE candidate
  io.to(to).emit('webrtc-ice-candidate', {
    from: socket.id,
    candidate: candidate
  });
});
```

---

## 5. API Routes Service

**Location:** `server/src/routes/api.js`

**Purpose:** RESTful API endpoints.

### Router Setup

```javascript
import express from 'express';
const router = express.Router();

// Health check
router.get('/health', healthCheckHandler);

// Topics
router.get('/topics', getTopicsHandler);
router.post('/topics/generate', generateTopicHandler);

// Analytics
router.get('/analytics/sessions', getSessionAnalyticsHandler);
router.get('/analytics/topics', getTopicAnalyticsHandler);

export default router;
```

### Middleware

**Error Handler:**
```javascript
router.use((err, req, res, next) => {
  console.error('API Error:', err.stack);
  res.status(500).json({
    success: false,
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});
```

---

## Service Integration

### Example: Complete Discussion Flow

```javascript
// 1. User joins room
socket.on('join-room', async (roomId, options) => {
  const room = roomManager.addUserToRoom(roomId, userData);
  socket.join(roomId);
  io.to(roomId).emit('participants-update', room.participants);
});

// 2. Users mark ready
socket.on('user-ready', (isReady) => {
  const room = roomManager.updateUserReady(roomId, userData.id, isReady);
  io.to(roomId).emit('participants-update', room.participants);
  
  if (checkAllReady(room)) {
    startDiscussion(roomId);
  }
});

// 3. Start discussion
async function startDiscussion(roomId) {
  // Generate topic
  const topic = await generateDiscussionTopic();
  
  // Start in room manager
  const room = roomManager.startDiscussion(roomId, topic);
  
  // Save to database
  await saveSession({
    id: uuidv4(),
    roomId: roomId,
    topic: topic,
    participantCount: room.participants.length,
    startedAt: new Date()
  });
  
  // Notify clients
  io.to(roomId).emit('discussion-start', {
    topic: topic,
    participants: room.participants,
    currentSpeaker: room.participants[0]
  });
  
  // Start timer
  startTimer(room, io);
}

// 4. Timer advances speakers
function advanceToNextSpeaker(room, io) {
  const { speaker } = roomManager.advanceSpeaker(room.id);
  
  io.to(room.id).emit('next-turn', {
    currentSpeaker: speaker,
    round: room.discussion.round,
    timeRemaining: room.discussion.timeRemaining
  });
  
  startTimer(room, io);
}

// 5. End discussion
async function endDiscussion(roomId) {
  const room = roomManager.endDiscussion(roomId);
  
  // Update database
  await updateSessionEnd(
    room.sessionId,
    room.discussion.endedAt,
    calculateDuration(room)
  );
  
  // Notify clients
  io.to(roomId).emit('discussion-end', {
    reason: 'completed',
    stats: getSessionStats(room)
  });
}
```

---

## Service Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=./data/roundtable.db

# AI Service
HUGGINGFACE_API_KEY=your_api_key

# Room Settings
MIN_PARTICIPANTS=1
MAX_PARTICIPANTS=8
DEFAULT_SPEAKING_TIME=60

# Server
PORT=3003
NODE_ENV=development
```

---

## Error Handling

### Service-Level Errors

```javascript
try {
  const topic = await generateDiscussionTopic();
  return topic;
} catch (error) {
  console.error('Topic generation failed:', error);
  // Fallback to default topics
  return getTopicByCategory('Education');
}
```

### Database Errors

```javascript
try {
  await saveSession(sessionData);
} catch (error) {
  console.error('Failed to save session:', error);
  // Log error but don't crash
  // Session continues in memory
}
```

---

## Performance Optimization

### 1. Caching

```javascript
// Cache frequently used topics
const topicCache = new Map();

function getCachedTopic(category) {
  if (!topicCache.has(category)) {
    topicCache.set(category, getTopicByCategory(category));
  }
  return topicCache.get(category);
}
```

### 2. Batch Operations

```javascript
// Save multiple participants at once
async function saveParticipants(participants) {
  const promises = participants.map(p => saveParticipant(p));
  await Promise.all(promises);
}
```

### 3. Connection Pooling

For high-load scenarios, consider connection pooling:

```javascript
import { Pool } from 'generic-pool';

const pool = new Pool({
  create: () => createDatabaseConnection(),
  destroy: (db) => db.close()
});
```

---

## Monitoring

### Service Health Checks

```javascript
export async function checkServiceHealth() {
  const health = {
    database: 'unknown',
    aiService: 'unknown',
    roomManager: 'unknown'
  };
  
  // Check database
  try {
    await getDatabase().run('SELECT 1');
    health.database = 'healthy';
  } catch {
    health.database = 'unhealthy';
  }
  
  // Check AI service
  try {
    await fetch(HUGGINGFACE_API_URL, { method: 'HEAD' });
    health.aiService = 'healthy';
  } catch {
    health.aiService = 'unhealthy';
  }
  
  // Check room manager
  health.roomManager = roomManager.getAllRooms().size < MAX_ROOMS ? 'healthy' : 'overloaded';
  
  return health;
}
```

---

## Testing Services

### Unit Tests

```javascript
describe('RoomManager', () => {
  let roomManager;
  
  beforeEach(() => {
    roomManager = new RoomManager();
  });
  
  test('creates room on first access', () => {
    const room = roomManager.getRoom('test-room');
    expect(room).toBeDefined();
    expect(room.id).toBe('test-room');
  });
  
  test('adds user to room', () => {
    roomManager.addUserToRoom('test-room', {
      id: 'user-1',
      anonymousName: 'Test User'
    });
    
    const room = roomManager.getRoom('test-room');
    expect(room.participants.length).toBe(1);
  });
});
```

---

## Support

For service-related issues:
- Check service logs
- Verify configuration
- Test individual services
- Review error handling
