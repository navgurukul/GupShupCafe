# Services Documentation

## Overview

This document describes the core services/modules in the GupShup Cafe backend that handle business logic and infrastructure.

---

## 1. Room Management Service

### Location
`server/src/socket/roomManager.js`

### Purpose
Manages discussion rooms, participants, and room state in memory.

### Class: RoomManager

Singleton instance that maintains a Map of active rooms.

---

### Data Structures

#### Room Object
```javascript
{
  id: string,              // Room identifier
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

#### Participant Object
```javascript
{
  id: string,              // User ID
  socketId: string,        // Socket.IO connection ID
  anonymousName: string,   // Display name
  name: string,
  campus: string,
  location: string,
  role: 'speaker' | 'listener',
  isReady: boolean,
  joinedAt: Date
}
```

---

### Public Methods

#### getRoom(roomId)

Get or create a room by ID. Lazy initialization pattern.

**Parameters**:
- `roomId` (string): Room identifier

**Returns**: `Room` object

**Behavior**:
- If room exists: Return existing room
- If room doesn't exist: Create new room with default values

**Example**:
```javascript
const room = roomManager.getRoom('general')
console.log(room.participants.length)
```

**Default Room State**:
```javascript
{
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
}
```

---

#### addUserToRoom(roomId, userData)

Add a user to a room. Handles reconnections.

**Parameters**:
- `roomId` (string): Room identifier
- `userData` (object): User data
  ```javascript
  {
    id: string,
    socketId: string,
    anonymousName: string,
    name: string,
    campus: string,
    location: string,
    role: 'speaker' | 'listener',
    isReady: boolean,
    joinedAt: Date
  }
  ```

**Returns**: `void`

**Behavior**:
- Removes user if already in room (reconnection)
- Adds user to participants array
- Does NOT auto-cleanup empty rooms

**Example**:
```javascript
roomManager.addUserToRoom('general', {
  id: 'user-123',
  socketId: 'socket-abc',
  anonymousName: 'Brave Lion',
  name: 'John Doe',
  campus: 'NavGurukul',
  location: 'Bangalore',
  role: 'listener',
  isReady: false,
  joinedAt: new Date()
})
```

**Side Effects**:
- Logs participant count
- Prevents cleanup during operation

---

#### removeUserFromRoom(roomId, userId)

Remove a user from a room.

**Parameters**:
- `roomId` (string): Room identifier
- `userId` (string): User ID to remove

**Returns**: `void`

**Behavior**:
- Filters user from participants array
- Cleans up empty rooms (unless in skipCleanup mode)

**Example**:
```javascript
roomManager.removeUserFromRoom('general', 'user-123')
```

**Side Effects**:
- Logs removal
- May delete room if empty

---

#### updateUser(roomId, userId, updates)

Update specific fields of a user in a room.

**Parameters**:
- `roomId` (string): Room identifier
- `userId` (string): User ID
- `updates` (object): Partial user data to update

**Returns**: `void`

**Example**:
```javascript
roomManager.updateUser('general', 'user-123', { isReady: true })
```

**Common Updates**:
- `isReady`: Signal ready status
- `role`: Change speaker/listener role
- `socketId`: Update on reconnection

---

#### getRoomParticipants(roomId)

Get sanitized participant list for a room.

**Parameters**:
- `roomId` (string): Room identifier

**Returns**: `Participant[]` (sanitized)

**Sanitized Fields**:
```javascript
{
  id: string,
  anonymousName: string,
  isReady: boolean,
  joinedAt: Date,
  socketId: string,
  role: 'speaker' | 'listener'
}
```

**Example**:
```javascript
const participants = roomManager.getRoomParticipants('general')
io.to('general').emit('participants-update', participants)
```

**Note**: Omits sensitive fields like full name, campus, location

---

#### getDiscussionState(roomId)

Get current discussion state for a room.

**Parameters**:
- `roomId` (string): Room identifier

**Returns**: `DiscussionState`
```javascript
{
  active: boolean,
  topic: Topic,
  currentSpeaker: Participant | null,
  timeRemaining: number,
  round: number,
  participantCount: number
}
```

**Example**:
```javascript
const state = roomManager.getDiscussionState('general')
if (state.active) {
  console.log(`Current speaker: ${state.currentSpeaker.anonymousName}`)
}
```

---

#### changeUserRole(roomId, userId, newRole)

Change a user's role between speaker and listener.

**Parameters**:
- `roomId` (string): Room identifier
- `userId` (string): User ID
- `newRole` (string): 'speaker' or 'listener'

**Returns**: `boolean` (success status)

**Validation**:
- Role must be 'speaker' or 'listener'
- User must exist in room

**Example**:
```javascript
const success = roomManager.changeUserRole('general', 'user-123', 'speaker')
if (success) {
  io.to('general').emit('role-changed', { userId: 'user-123', newRole: 'speaker' })
}
```

**Side Effects**:
- Logs role change
- Updates user object

---

#### canBecomeSpeaker(roomId, maxSpeakers)

Check if room has capacity for more speakers.

**Parameters**:
- `roomId` (string): Room identifier
- `maxSpeakers` (number): Maximum allowed speakers (default: 6)

**Returns**: `boolean`

**Example**:
```javascript
if (roomManager.canBecomeSpeaker('general')) {
  // Allow role change to speaker
} else {
  socket.emit('role-change-error', { message: 'Speaker limit reached' })
}
```

---

#### getRoleStats(roomId)

Get role statistics for a room.

**Parameters**:
- `roomId` (string): Room identifier

**Returns**: `RoleStats`
```javascript
{
  totalParticipants: number,
  speakers: number,
  listeners: number,
  speakerList: Participant[],
  listenerList: Participant[]
}
```

**Example**:
```javascript
const stats = roomManager.getRoleStats('general')
console.log(`Speakers: ${stats.speakers}, Listeners: ${stats.listeners}`)
```

---

#### cleanupRoom(roomId)

Clean up room resources and delete room.

**Parameters**:
- `roomId` (string): Room identifier

**Returns**: `void`

**Behavior**:
- Clears any active timers
- Deletes room from Map
- Logs cleanup

**Example**:
```javascript
roomManager.cleanupRoom('general')
```

**Automatic Cleanup**:
- Called when last participant leaves
- Called on server shutdown (recommended)

---

#### getAllRooms()

Get summaries of all active rooms (debugging/monitoring).

**Parameters**: None

**Returns**: `RoomSummary[]`
```javascript
{
  id: string,
  participantCount: number,
  discussionActive: boolean,
  round: number,
  createdAt: Date
}
```

**Example**:
```javascript
const rooms = roomManager.getAllRooms()
console.log(`Active rooms: ${rooms.length}`)
```

---

#### getStats()

Get server-wide statistics.

**Parameters**: None

**Returns**: `ServerStats`
```javascript
{
  totalRooms: number,
  totalParticipants: number,
  activeDiscussions: number,
  timestamp: Date
}
```

**Example**:
```javascript
const stats = roomManager.getStats()
console.log(`Total participants across all rooms: ${stats.totalParticipants}`)
```

---

### Usage Patterns

#### Complete Room Lifecycle

```javascript
// User joins
roomManager.addUserToRoom('general', userData)
const participants = roomManager.getRoomParticipants('general')
io.to('general').emit('participants-update', participants)

// User signals ready
roomManager.updateUser('general', userId, { isReady: true })

// Discussion starts
const room = roomManager.getRoom('general')
room.discussion.active = true
room.discussion.topic = topic

// User changes role
roomManager.changeUserRole('general', userId, 'speaker')

// User leaves
roomManager.removeUserFromRoom('general', userId)
// Room auto-cleaned up if empty
```

---

### Performance Considerations

**Memory Usage**:
- Each room: ~1-5 KB
- 100 rooms with 8 participants each: ~100 KB
- Suitable for 1000s of concurrent users

**Lookup Performance**:
- Map operations: O(1)
- Finding user in room: O(n) where n = participants
- Typically n < 10, so negligible

**Scaling Limitations**:
- In-memory state (lost on restart)
- Single server only
- No cross-server communication

**Recommended for Scaling**:
- Use Redis for distributed state
- Implement room persistence
- Add server affinity in load balancer

---

## 2. Socket Handlers Service

### Location
`server/src/socket/socketHandlers.js`

### Purpose
Handles all Socket.IO events and orchestrates room/discussion management.

---

### Main Function: setupSocketHandlers(io)

Initialize Socket.IO event handlers.

**Parameters**:
- `io` (Socket.IO Server): Socket.IO server instance

**Returns**: `void`

**Usage**:
```javascript
import { Server } from 'socket.io'
import { setupSocketHandlers } from './socket/socketHandlers.js'

const io = new Server(server, { cors: { ... } })
setupSocketHandlers(io)
```

---

### Event Handlers

#### Connection: 'connection'

Handles new client connections.

**Flow**:
1. Extract user data from handshake auth
2. Register all event listeners
3. Log connection

**User Data Extraction**:
```javascript
const userData = {
  id: socket.handshake.auth.userId || socket.id,
  socketId: socket.id,
  name: socket.handshake.auth.name,
  campus: socket.handshake.auth.campus,
  location: socket.handshake.auth.location,
  anonymousName: socket.handshake.auth.anonymousName,
  isReady: false,
  joinedAt: new Date()
}
```

---

#### Event: 'join-room'

User joins a discussion room.

**Parameters**: `(roomId, clientUserData?)`

**Flow**:
```
1. Leave any existing rooms
2. Join new room (socket.join)
3. Add user to room manager
4. Emit participants-update to room
5. Sync active discussion state (if any)
6. Check if discussion can start
```

**Special Handling**:
- Syncs ongoing discussion state with new user
- Sends current speaker and timer

---

#### Event: 'user-ready'

User signals ready to start discussion.

**Parameters**: None (uses socket's current room)

**Flow**:
```
1. Update user's ready status
2. Emit participants-update
3. Check if minimum participants ready
4. Start discussion if ready
```

---

#### Event: 'next-speaker'

Request to advance to next speaker.

**Parameters**: None

**Flow**:
```
1. Validate room and discussion active
2. Call advanceToNextSpeaker()
```

---

#### Event: 'role-change'

Request to change user's role.

**Parameters**: `{ userId, newRole, roomId? }`

**Flow**:
```
1. Validate role ('speaker' or 'listener')
2. Check speaker limit if becoming speaker
3. Update role in room manager
4. Emit role-changed to all participants
5. Emit confirmation to requester
```

---

#### Event: 'webrtc-offer', 'webrtc-answer', 'webrtc-ice-candidate'

WebRTC signaling relay.

**Flow**: Simple passthrough from sender to target peer

**Example**:
```javascript
socket.on('webrtc-offer', ({ to, sdp }) => {
  io.to(to).emit('webrtc-offer', { from: socket.id, sdp })
})
```

---

#### Event: 'disconnect'

Handle user disconnection.

**Flow**:
```
1. Remove user from room
2. Emit participants-update
3. Emit user-disconnected event
4. Check if discussion should continue
```

---

### Helper Functions

#### checkAndStartDiscussion(roomId)

Check if discussion can start and start if ready.

**Conditions**:
- Minimum participants in room
- Minimum participants ready
- Discussion not already active

**Flow**:
```
1. Validate conditions
2. Generate topic (AI/fallback)
3. Record topic usage (non-blocking)
4. Initialize discussion state
5. Save session to database
6. Emit discussion-started
7. Start speaking timer
```

---

#### startSpeakingTimer(roomId)

Start countdown timer for current speaker.

**Behavior**:
- Interval: 1 second
- Emits: timer-update every second
- Auto-advances when time expires

**Implementation**:
```javascript
room.discussion.timer = setInterval(() => {
  room.discussion.timeRemaining--
  io.to(roomId).emit('timer-update', room.discussion.timeRemaining)
  
  if (room.discussion.timeRemaining <= 0) {
    advanceToNextSpeaker(roomId)
  }
}, 1000)
```

---

#### advanceToNextSpeaker(roomId)

Move to next speaker in sequence.

**Flow**:
```
1. Clear current timer
2. Increment speaker index (circular)
3. Check if round completed
4. End discussion if 3 rounds complete
5. Reset timer
6. Emit speaker-changed
7. Start new timer
```

---

#### endDiscussion(roomId)

End the discussion and clean up.

**Flow**:
```
1. Clear timer
2. Mark discussion as inactive
3. Update session in database
4. Emit discussion-ended
```

---

#### checkDiscussionContinuation(roomId)

Check if discussion should continue after user leaves.

**Behavior**:
- End discussion if below minimum participants

---

## 3. AI Topic Generator Service

### Location
`server/src/ai/topicGenerator.js`

### Purpose
Generate discussion topics using AI or curated fallback topics.

---

### Functions

#### generateDiscussionTopic()

Main function to generate a discussion topic.

**Returns**: `Promise<Topic>`

**Topic Structure**:
```javascript
{
  title: string,
  description: string,
  category: string,
  questions: string[],
  source: 'AI Generated' | 'fallback'
}
```

**Flow**:
```
1. Try AI generation (if API key present)
2. If AI fails/unavailable: Use fallback
3. Return topic object
```

**Example**:
```javascript
const topic = await generateDiscussionTopic()
console.log(topic.title) // "The Future of Education"
```

---

#### generateTopicWithAI()

Generate topic using Hugging Face API.

**Returns**: `Promise<Topic | null>`

**API Details**:
- **Model**: microsoft/DialoGPT-medium
- **Endpoint**: https://api-inference.huggingface.co/models/...
- **Method**: POST
- **Auth**: Bearer token

**Parameters**:
```javascript
{
  inputs: prompt,
  parameters: {
    max_length: 300,
    temperature: 0.8,
    num_return_sequences: 1
  }
}
```

**Error Handling**:
- API key missing: Return null
- Network error: Return null
- Parse error: Return fallback topic

---

#### getRandomFallbackTopic()

Get a random topic from curated list.

**Returns**: `Topic`

**Fallback Topics**: 8 categories
- Education
- Environment
- Technology
- Health
- Career
- Culture
- Business
- Personal Development

**Example**:
```javascript
const topic = getRandomFallbackTopic()
```

---

#### getAllFallbackTopics()

Get all available fallback topics.

**Returns**: `Topic[]`

**Usage**: API endpoint to list available topics

---

#### getTopicByCategory(category)

Get a specific fallback topic by category.

**Parameters**:
- `category` (string): Topic category

**Returns**: `Topic | null`

**Example**:
```javascript
const topic = getTopicByCategory('Education')
if (topic) {
  console.log(topic.title)
}
```

---

### Configuration

**Environment Variable**: `HUGGINGFACE_API_KEY`

**Setup**:
1. Sign up at https://huggingface.co
2. Generate API token
3. Add to `.env`: `HUGGINGFACE_API_KEY=hf_xxxxx`

**Fallback Behavior**:
- If key missing: Always use fallback topics
- If API fails: Log warning, use fallback
- No interruption to user experience

---

### Future Enhancements

**Planned Features**:
- Category-based generation
- Difficulty levels
- User preferences
- Multi-language support
- Custom topic prompts

**Better AI Integration**:
- Use GPT-4 or Claude
- Structured output parsing
- Topic validation
- Dynamic question generation

---

## Service Integration Diagram

```
┌─────────────────────────────────────────┐
│         Socket Handlers                  │
│      (Event Orchestration)               │
└───────┬───────────────────┬─────────────┘
        │                   │
        │                   │
┌───────▼────────┐   ┌──────▼──────────┐
│ Room Manager   │   │  AI Generator   │
│  (State Mgmt)  │   │  (Topics)       │
└───────┬────────┘   └──────┬──────────┘
        │                   │
        │                   │
┌───────▼────────────────────▼─────────┐
│         Database Manager             │
│      (Persistence)                   │
└──────────────────────────────────────┘
```

---

## Error Handling Best Practices

### Graceful Degradation
```javascript
try {
  const aiTopic = await generateTopicWithAI()
  return aiTopic || getRandomFallbackTopic()
} catch (error) {
  console.error('AI generation failed:', error)
  return getRandomFallbackTopic()
}
```

### Logging
```javascript
console.log('[INFO] User joined room:', roomId)
console.warn('[WARN] AI API slow, using fallback')
console.error('[ERROR] Database write failed:', error)
```

### User Feedback
```javascript
socket.emit('error', 'Failed to join room')
socket.emit('role-change-error', { message: 'Speaker limit reached' })
```

---

## Testing Services

### Unit Test Example
```javascript
describe('RoomManager', () => {
  let roomManager
  
  beforeEach(() => {
    roomManager = new RoomManager()
  })
  
  test('creates room on getRoom', () => {
    const room = roomManager.getRoom('test')
    expect(room.id).toBe('test')
    expect(room.participants).toEqual([])
  })
  
  test('adds user to room', () => {
    roomManager.addUserToRoom('test', userData)
    const room = roomManager.getRoom('test')
    expect(room.participants).toHaveLength(1)
  })
})
```

### Integration Test Example
```javascript
describe('Socket Handlers', () => {
  let io, clientSocket
  
  beforeAll((done) => {
    // Setup test server
    done()
  })
  
  test('join-room emits participants-update', (done) => {
    clientSocket.emit('join-room', 'test-room')
    clientSocket.on('participants-update', (participants) => {
      expect(participants).toBeDefined()
      done()
    })
  })
})
```
