# Core Features Documentation

## Overview

This document describes the core features of the GupShup Cafe platform and their implementation details.

---

## 1. Authentication System

### Feature Description

Anonymous authentication system that allows users to join discussions without creating accounts. Users provide basic information and are assigned memorable animal-based anonymous names.

### Implementation

**Location**: `client/src/contexts/AuthContext.jsx`, `client/src/pages/LoginPage.jsx`

**Flow Diagram**:
```
User opens app
     ↓
LoginPage renders
     ↓
User enters: name, campus, location
     ↓
System generates anonymous names
     ↓
User selects/confirms anonymous name
     ↓
Form validation
     ↓
Store in AuthContext + localStorage
     ↓
Redirect to Lobby
```

**Data Structure**:
```javascript
{
  user: {
    id: string, // UUID v4
    name: string,
    campus: string,
    location: string
  },
  anonymousName: string, // e.g., "Brave Lion"
  isAuthenticated: boolean
}
```

**Anonymous Name Generation**:
- Adjectives: 50+ options (Brave, Wise, Swift, etc.)
- Animals: 50+ options (Lion, Eagle, Dolphin, etc.)
- Pattern: `{Adjective} {Animal}`
- 3 suggestions generated on page load
- User can regenerate or customize

**Persistence**:
- Stored in localStorage
- Restored on page reload
- Cleared on logout

**Security Considerations**:
- No passwords required
- User identity not verified
- Suitable for educational/casual discussions
- Campus/location for grouping only

---

## 2. Real-Time Communication

### Feature Description

Bidirectional real-time communication between clients and server using WebSocket protocol via Socket.IO.

### Implementation

**Location**: `client/src/contexts/SocketContext.jsx`, `server/src/socket/socketHandlers.js`

**Connection Lifecycle**:
```
Client                          Server
  |                              |
  |---connect (with auth)------->|
  |<--connection confirmed-------|
  |                              |
  |---join-room----------------->|
  |<--participants-update--------|
  |                              |
  |---user-ready---------------->|
  |<--participants-update--------|
  |                              |
  |<--discussion-started---------|
  |<--timer-update (every 1s)----|
  |                              |
  |---disconnect---------------->|
  |<--user-disconnected----------|
```

**Key Features**:

1. **Authentication Handshake**:
   ```javascript
   socket = io(SERVER_URL, {
     auth: {
       userId: user.id,
       name: user.name,
       campus: user.campus,
       location: user.location,
       anonymousName: anonymousName
     }
   })
   ```

2. **Room Management**:
   - Users automatically join "general" room
   - Single room per user (leaving previous room on join)
   - Room state managed server-side

3. **Event Broadcasting**:
   - `io.to(roomId).emit()`: Broadcast to entire room
   - `socket.to(roomId).emit()`: Broadcast to all except sender
   - `socket.emit()`: Send to specific client

4. **Automatic Reconnection**:
   - Built-in Socket.IO reconnection
   - Exponential backoff
   - Restores room state on reconnect

**Performance Optimizations**:
- Events only sent when data changes
- Minimal payload sizes
- No polling (pure WebSocket when available)

**Error Handling**:
- Connection errors displayed to user
- Graceful degradation to polling if WebSocket fails
- Timeout handling for slow connections

---

## 3. Audio/WebRTC System

### Feature Description

Peer-to-peer audio streaming using WebRTC for real-time voice communication during discussions.

### Implementation

**Location**: `client/src/contexts/AudioContext.jsx`

**Architecture**:
```
┌──────────────┐         ┌──────────────┐
│   Speaker    │         │   Listener   │
│              │         │              │
│ Microphone   │         │  No Audio    │
│   Stream     │         │   Output     │
└──────┬───────┘         └──────┬───────┘
       │                        │
       │ P2P Audio Streaming    │
       │◄──────────────────────►│
       │                        │
       │ (via WebRTC)           │
       │                        │
       │   Signaling via        │
       │   Socket.IO Server     │
       └────────┬───────────────┘
                │
        ┌───────▼────────┐
        │  Server        │
        │  (Signaling)   │
        └────────────────┘
```

**WebRTC Flow**:
```
Speaker                    Server                    Listener
  |                         |                         |
  |--getUserMedia()-------->|                         |
  |<-MediaStream------------|                         |
  |                         |                         |
  |--createOffer()--------->|                         |
  |--emit(webrtc-offer)---->|                         |
  |                         |----webrtc-offer-------->|
  |                         |                         |
  |                         |<---webrtc-answer--------|
  |<--emit(webrtc-answer)---|                         |
  |                         |                         |
  |--ICE candidates-------->|----ICE candidates------>|
  |<----ICE candidates------|<---ICE candidates-------|
  |                         |                         |
  |◄────────────P2P Audio Connection──────────────────►|
```

**Key Components**:

1. **Microphone Access**:
   ```javascript
   const stream = await navigator.mediaDevices.getUserMedia({
     audio: {
       echoCancellation: true,
       noiseSuppression: true,
       autoGainControl: true
     }
   })
   ```

2. **Peer Connection Setup**:
   ```javascript
   const pc = new RTCPeerConnection({
     iceServers: [
       { urls: 'stun:stun.l.google.com:19302' }
     ]
   })
   ```

3. **Audio Level Monitoring**:
   - Web Audio API for visualization
   - Real-time frequency analysis
   - Visual feedback for speaker

4. **Role Management**:
   - **Speaker**: Can enable microphone, streams audio
   - **Listener**: Receives audio, no microphone access
   - Dynamic role switching supported

**Audio Optimization**:
- Opus codec prioritization
- Echo cancellation enabled
- Noise suppression enabled
- Auto gain control
- Minimal latency settings

**Error Handling**:
- Microphone permission denied handling
- Connection failure fallback
- Network issue detection
- User-friendly error messages

---

## 4. Discussion Management

### Feature Description

Automated turn-based discussion system with AI-generated topics, speaking timers, and round management.

### Implementation

**Location**: `server/src/socket/socketHandlers.js`

**Discussion Lifecycle**:
```
Lobby State
     ↓
Check: Min participants ready?
     ↓ (Yes)
Generate Topic (AI/Fallback)
     ↓
Create Session in DB
     ↓
Start Discussion
     ↓
┌────────────────┐
│ Round 1, 2, 3  │
│                │
│ For each user: │
│  1. Highlight  │
│  2. Start timer│
│  3. Audio on   │
│  4. Timer ends │
│  5. Next user  │
└────────────────┘
     ↓
All rounds complete
     ↓
End Discussion
     ↓
Save Analytics
     ↓
Return to Lobby
```

**State Management**:
```javascript
{
  active: boolean,
  topic: Topic,
  currentSpeakerIndex: number,
  speakingTime: number, // seconds
  timeRemaining: number,
  round: number, // 1, 2, or 3
  timer: NodeJS.Timer,
  startedAt: Date,
  endedAt: Date
}
```

**Key Functions**:

1. **checkAndStartDiscussion(roomId)**:
   - Validates minimum participant count
   - Checks ready status
   - Generates discussion topic
   - Initializes discussion state
   - Starts timer

2. **startSpeakingTimer(roomId)**:
   - Creates interval timer (1 second)
   - Decrements timeRemaining
   - Broadcasts timer updates
   - Advances speaker on time expiry

3. **advanceToNextSpeaker(roomId)**:
   - Moves to next participant
   - Increments round if cycled through all
   - Ends discussion after 3 rounds
   - Resets timer

4. **endDiscussion(roomId)**:
   - Stops timer
   - Updates database
   - Broadcasts end event
   - Cleans up room state

**Configuration**:
- Min participants: 1 (configurable via env)
- Max participants: 8 (configurable via env)
- Speaking time: 60 seconds (configurable)
- Rounds: 3 (hardcoded)

**Analytics Tracking**:
- Session start/end times
- Duration calculation
- Participant count
- Rounds completed
- Topic usage statistics

---

## 5. AI Topic Generation

### Feature Description

Generates discussion topics using Hugging Face AI API with intelligent fallback to curated topics.

### Implementation

**Location**: `server/src/ai/topicGenerator.js`

**Generation Flow**:
```
Request Topic
     ↓
Check: Hugging Face API key?
     ↓ (Yes)
Call Hugging Face API
     ↓
API Success?
     ↓ (Yes)        ↓ (No)
Parse Response   Fallback Topics
     ↓                ↓
AI Topic      Random Selection
     ↓                ↓
     └────────┬───────┘
              ↓
        Return Topic
```

**Fallback Topics**:
- 8 curated categories
- 3 questions per topic
- Topics cover:
  - Education
  - Technology
  - Health
  - Environment
  - Career
  - Culture
  - Business
  - Personal Development

**API Integration**:
```javascript
// Hugging Face API call
const response = await fetch(
  'https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      inputs: prompt,
      parameters: {
        max_length: 300,
        temperature: 0.8
      }
    })
  }
)
```

**Error Handling**:
- API key validation
- Network error handling
- Response parsing errors
- Automatic fallback
- Logging for debugging

**Future Enhancements**:
- Category-based generation
- User preference learning
- Topic difficulty levels
- Multi-language support

---

## 6. Room Management

### Feature Description

Server-side management of discussion rooms and participant state.

### Implementation

**Location**: `server/src/socket/roomManager.js`

**Data Structure**:
```javascript
Room {
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

**Key Operations**:

1. **getRoom(roomId)**:
   - Lazy initialization
   - Creates room if doesn't exist
   - Returns room object

2. **addUserToRoom(roomId, userData)**:
   - Handles reconnections
   - Updates participant list
   - Broadcasts update

3. **removeUserFromRoom(roomId, userId)**:
   - Filters participant list
   - Cleans up empty rooms
   - Broadcasts update

4. **updateUser(roomId, userId, updates)**:
   - Partial user data update
   - Used for ready status, role changes

5. **changeUserRole(roomId, userId, newRole)**:
   - Validates role
   - Checks speaker limits
   - Updates and broadcasts

**Memory Management**:
- Rooms stored in Map
- Empty rooms automatically deleted
- No persistent storage (stateless)
- Clean up on server restart

**Scalability Limitations**:
- In-memory state (single server)
- No cross-server synchronization
- Redis recommended for scaling

---

## 7. Analytics & Monitoring

### Feature Description

Track discussion sessions, topic usage, and server statistics for insights and debugging.

### Implementation

**Location**: `server/src/database/database.js`, `server/src/routes/api.js`

**Database Tables**:

1. **sessions**:
   ```sql
   CREATE TABLE sessions (
     id TEXT PRIMARY KEY,
     room_id TEXT,
     topic TEXT,
     participant_count INTEGER,
     started_at DATETIME,
     ended_at DATETIME,
     duration_seconds INTEGER,
     rounds_completed INTEGER
   )
   ```

2. **participants**:
   ```sql
   CREATE TABLE participants (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     session_id TEXT,
     user_id TEXT,
     anonymous_name TEXT,
     role TEXT,
     joined_at DATETIME,
     FOREIGN KEY (session_id) REFERENCES sessions(id)
   )
   ```

3. **topics**:
   ```sql
   CREATE TABLE topics (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     title TEXT,
     description TEXT,
     category TEXT,
     source TEXT,
     used_count INTEGER DEFAULT 0,
     created_at DATETIME
   )
   ```

**Analytics Endpoints**:
- `GET /api/analytics/sessions`: Recent sessions
- `GET /api/analytics/topics`: Topic usage stats
- `GET /api/analytics/stats`: Server statistics

**Metrics Tracked**:
- Total sessions
- Total unique participants
- Average session duration
- Average participants per session
- Most popular topic categories
- Topic usage frequency

**Future Enhancements**:
- User engagement metrics
- Completion rates
- Time-series analysis
- Export functionality
- Dashboard visualization

---

## Feature Comparison Matrix

| Feature | Current | Planned | Priority |
|---------|---------|---------|----------|
| Anonymous Auth | ✅ | OAuth integration | Low |
| WebSocket | ✅ | - | - |
| WebRTC Audio | ✅ | Video support | Medium |
| AI Topics | ✅ | Better prompts | High |
| Turn-based | ✅ | Interrupt mode | Low |
| Analytics | ✅ | Dashboard | Medium |
| Mobile | ✅ | Native app | Low |
| Persistence | ✅ | Cloud DB | High |
| Scaling | ❌ | Redis state | High |
| Testing | ❌ | Unit/E2E tests | High |

---

## User Experience Flow

### Complete User Journey

```
1. Visit Website
   ↓
2. Login Page
   - Enter name, campus, location
   - Select anonymous name
   ↓
3. Lobby
   - See other participants
   - Request microphone permission
   - Click "Ready"
   - Wait for others
   ↓
4. Discussion Starts
   - View topic
   - See circular seating
   - Current speaker highlighted
   - Timer countdown
   ↓
5. Your Turn
   - Border highlights you
   - Microphone unmutes
   - Speak for 60 seconds
   - Timer warns at 10s
   ↓
6. Others' Turns
   - Listen to peers
   - See audio levels
   - Wait for your next turn
   ↓
7. Discussion Ends (after 3 rounds)
   - Summary displayed
   - Return to lobby
   - Can start new discussion
```

---

## Configuration Options

### Environment Variables

**Client** (`.env`):
```bash
VITE_API_URL=http://localhost:3003
```

**Server** (`.env`):
```bash
PORT=3003
NODE_ENV=development
MIN_PARTICIPANTS=1
MAX_PARTICIPANTS=8
DEFAULT_SPEAKING_TIME=60
HUGGINGFACE_API_KEY=hf_xxxxx
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174
```

### Runtime Configuration

- Participant limits: Via environment variables
- Speaking time: Per session configurable
- AI provider: Swappable (currently Hugging Face)
- Database: SQLite file location configurable
