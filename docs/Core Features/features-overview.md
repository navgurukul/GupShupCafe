# Core Features Documentation

## Overview

This document details the core features of the GupShup Cafe (AI Roundtable Discussion Platform), including implementation details, user flows, and technical specifications.

---

## 1. User Authentication & Onboarding

### Description

Simple ID-based authentication system with anonymous name generation for discussions.

### User Flow

```
┌─────────────┐
│ Login Page  │
└──────┬──────┘
       │ Enter Details
       ├── User ID
       ├── Full Name
       ├── Campus
       └── Location
       │
       ▼
┌─────────────────┐
│ Generate        │
│ Anonymous Name  │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│   Save to   │
│  LocalStorage│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Navigate to │
│    Lobby    │
└─────────────┘
```

### Implementation

**Location:** `client/src/pages/LoginPage.jsx`, `client/src/contexts/AuthContext.jsx`

**Key Features:**
- Form validation for all fields
- Anonymous name generation (e.g., "Wise Owl", "Clever Fox")
- LocalStorage persistence
- Redirect after successful login

**Code Example:**

```javascript
// Anonymous name generation
const animals = ['Owl', 'Fox', 'Eagle', 'Wolf', 'Bear', 'Lion'];
const adjectives = ['Wise', 'Clever', 'Swift', 'Bold', 'Calm', 'Bright'];

const generateAnonymousName = () => {
  const animal = animals[Math.floor(Math.random() * animals.length)];
  const adjective = adjectives[Math.floor(Math.random() * adjectives.length)];
  return `${adjective} ${animal}`;
};
```

**Validation:**
```javascript
const validateForm = () => {
  const errors = {};
  if (!id.trim()) errors.id = 'ID is required';
  if (!name.trim()) errors.name = 'Name is required';
  if (!campus.trim()) errors.campus = 'Campus is required';
  if (!location.trim()) errors.location = 'Location is required';
  return errors;
};
```

### Security Considerations

- No password required (educational use case)
- User data stored in localStorage
- Anonymous names protect privacy
- Session-based identification

---

## 2. Lobby System

### Description

Waiting room where participants gather before starting the discussion.

### User Flow

```
┌──────────────┐
│ Enter Lobby  │
└──────┬───────┘
       │
       ▼
┌────────────────┐
│  Join/Create   │
│     Room       │
└──────┬─────────┘
       │
       ▼
┌────────────────┐
│ Select Role    │
│ Speaker/       │
│ Listener       │
└──────┬─────────┘
       │
       ▼
┌────────────────┐
│ Request Audio  │
│  Permission    │
└──────┬─────────┘
       │
       ▼
┌────────────────┐
│ Mark as Ready  │
└──────┬─────────┘
       │
       ▼
┌────────────────┐
│ Wait for All   │
│   to be Ready  │
└──────┬─────────┘
       │ All Ready
       ▼
┌────────────────┐
│   Discussion   │
│     Starts     │
└────────────────┘
```

### Implementation

**Location:** `client/src/pages/LobbyPage.jsx`

**Key Features:**
- Real-time participant updates
- Audio permission management
- Role selection (Speaker/Listener)
- Ready status indicator
- Minimum participant requirement
- Automatic discussion start

**Room Management:**

```javascript
const joinRoom = () => {
  const roomId = `room-${Date.now()}`;
  socket.emit('join-room', roomId, { role: selectedRole });
  setRoomId(roomId);
};

socket.on('participants-update', (updatedParticipants) => {
  setParticipants(updatedParticipants);
  
  // Check if all ready
  const allReady = updatedParticipants.every(p => p.isReady);
  const minMet = updatedParticipants.length >= minParticipants;
  
  setCanStart(allReady && minMet);
});
```

**Audio Permissions:**

```javascript
const requestAudioPermission = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true
      }
    });
    
    setAudioPermission('granted');
    setLocalStream(stream);
  } catch (error) {
    console.error('Microphone access denied:', error);
    setAudioPermission('denied');
  }
};
```

### Visual States

**Participant Card States:**
- Waiting (Gray)
- Ready (Green)
- Audio Enabled (Microphone icon)
- Audio Disabled (Muted icon)

---

## 3. AI Topic Generation

### Description

Generates discussion topics using Hugging Face's free AI API, with fallback to curated topics.

### Topic Generation Flow

```
┌──────────────────┐
│ Request Topic    │
└────────┬─────────┘
         │
         ▼
    ┌────────────┐
    │ Try AI Gen │
    └────┬───────┘
         │
    ┌────▼────┐
    │ Success?│
    └────┬────┘
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    │    ┌────▼────────┐
    │    │  Fallback   │
    │    │   Topics    │
    │    └────┬────────┘
    │         │
    └────┬────┘
         │
         ▼
┌──────────────────┐
│  Return Topic    │
└──────────────────┘
```

### Implementation

**Location:** `server/src/ai/topicGenerator.js`

**Key Features:**
- Hugging Face API integration
- Fallback topic library
- Category-based selection
- Topic caching
- Usage tracking

**Topic Structure:**

```javascript
{
  title: string,
  description: string,
  category: string,
  questions: string[],
  source: 'ai' | 'fallback'
}
```

**AI Generation:**

```javascript
export async function generateDiscussionTopic(category = null) {
  try {
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
    
    const data = await response.json();
    return parseAIResponse(data);
  } catch (error) {
    console.error('AI generation failed:', error);
    return getFallbackTopic(category);
  }
}
```

**Prompt Engineering:**

```javascript
const generatePrompt = (category) => {
  return `Generate an educational discussion topic${category ? ` about ${category}` : ''}.
  
Format:
Title: [Engaging topic title]
Description: [Brief description]
Questions:
1. [Discussion question 1]
2. [Discussion question 2]
3. [Discussion question 3]`;
};
```

### Topic Categories

- Education
- Technology
- Health & Wellness
- Environment & Sustainability
- Arts & Culture
- Science & Innovation
- Social Issues
- Career & Professional Development

---

## 4. Real-time Discussion Management

### Description

Turn-based speaking system with timer management and automatic speaker rotation.

### Discussion Flow

```
┌────────────────┐
│ Discussion     │
│   Starts       │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Generate Topic │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Set Speaker 1  │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Start Timer    │
│   (60s)        │
└────────┬───────┘
         │
    ┌────▼────┐
    │ Timer   │
    │ Update  │
    └────┬────┘
         │
    ┌────▼────┐
    │Time Up? │
    └────┬────┘
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    │    └─────┐
    │          │
    ▼          │
┌────────────┐ │
│Next Speaker│ │
└────┬───────┘ │
     │         │
     └─────────┘
```

### Implementation

**Location:** `server/src/socket/socketHandlers.js`

**Key Components:**

1. **Speaker Management:**
```javascript
const advanceSpeaker = (room) => {
  const { discussion, participants } = room;
  
  // Advance to next speaker
  discussion.currentSpeakerIndex = 
    (discussion.currentSpeakerIndex + 1) % participants.length;
  
  // Check if round completed
  if (discussion.currentSpeakerIndex === 0) {
    discussion.round++;
  }
  
  // Reset timer
  discussion.timeRemaining = discussion.speakingTime;
  
  return participants[discussion.currentSpeakerIndex];
};
```

2. **Timer Management:**
```javascript
const startTimer = (room, io) => {
  // Clear existing timer
  if (room.discussion.timer) {
    clearInterval(room.discussion.timer);
  }
  
  room.discussion.timer = setInterval(() => {
    room.discussion.timeRemaining--;
    
    // Emit timer update
    io.to(room.id).emit('timer-update', {
      timeRemaining: room.discussion.timeRemaining,
      speakerId: getCurrentSpeaker(room).id
    });
    
    // Check if time is up
    if (room.discussion.timeRemaining <= 0) {
      clearInterval(room.discussion.timer);
      advanceToNextSpeaker(room, io);
    }
  }, 1000);
};
```

3. **Round Management:**
```javascript
const checkDiscussionCompletion = (room) => {
  const maxRounds = 3;
  
  if (room.discussion.round > maxRounds) {
    endDiscussion(room);
    return true;
  }
  
  return false;
};
```

### Speaking Rules

- Default speaking time: 60 seconds
- Automatic advancement when time expires
- Manual advancement allowed via "Next" button
- 3 rounds by default
- All participants speak in each round

---

## 5. WebRTC Audio Communication

### Description

Peer-to-peer audio streaming using WebRTC for real-time voice communication.

### WebRTC Connection Flow

```
┌─────────────┐              ┌─────────────┐
│  Speaker A  │              │  Speaker B  │
└──────┬──────┘              └──────┬──────┘
       │                            │
       │ 1. Create Offer            │
       ├────────────────────────────►
       │                            │
       │      2. Send Answer        │
       │◄────────────────────────────┤
       │                            │
       │ 3. Exchange ICE Candidates │
       │◄────────────────────────────►
       │                            │
       │                            │
       │ 4. Establish Connection    │
       ╞════════════════════════════╡
       │                            │
       │  5. Audio Stream Flows     │
       │◄───────────────────────────►
       │                            │
```

### Implementation

**Location:** `client/src/contexts/AudioContext.jsx`

**Key Components:**

1. **Peer Connection Setup:**
```javascript
const createPeerConnection = (targetSocketId) => {
  const config = {
    iceServers: [
      { urls: 'stun:stun.l.google.com:19302' },
      { urls: 'stun:stun1.l.google.com:19302' }
    ]
  };
  
  const peerConnection = new RTCPeerConnection(config);
  
  // Add local stream tracks
  if (localStream) {
    localStream.getTracks().forEach(track => {
      peerConnection.addTrack(track, localStream);
    });
  }
  
  // Handle incoming tracks
  peerConnection.ontrack = (event) => {
    handleRemoteStream(targetSocketId, event.streams[0]);
  };
  
  // Handle ICE candidates
  peerConnection.onicecandidate = (event) => {
    if (event.candidate) {
      socket.emit('webrtc-ice-candidate', {
        to: targetSocketId,
        candidate: event.candidate
      });
    }
  };
  
  return peerConnection;
};
```

2. **Offer/Answer Exchange:**
```javascript
// Create and send offer
const createOffer = async (targetSocketId) => {
  const pc = createPeerConnection(targetSocketId);
  peerConnections.set(targetSocketId, pc);
  
  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  
  socket.emit('webrtc-offer', {
    to: targetSocketId,
    offer: offer
  });
};

// Handle incoming offer
socket.on('webrtc-offer', async ({ from, offer }) => {
  const pc = createPeerConnection(from);
  peerConnections.set(from, pc);
  
  await pc.setRemoteDescription(offer);
  const answer = await pc.createAnswer();
  await pc.setLocalDescription(answer);
  
  socket.emit('webrtc-answer', {
    to: from,
    answer: answer
  });
});
```

3. **ICE Candidate Exchange:**
```javascript
socket.on('webrtc-ice-candidate', async ({ from, candidate }) => {
  const pc = peerConnections.get(from);
  
  if (pc) {
    await pc.addIceCandidate(new RTCIceCandidate(candidate));
  }
});
```

### Audio Controls

**Microphone Management:**
```javascript
const toggleMute = () => {
  if (localStream) {
    localStream.getAudioTracks().forEach(track => {
      track.enabled = !track.enabled;
    });
    setIsMuted(!isMuted);
  }
};
```

**Audio Level Detection:**
```javascript
const getAudioLevel = (stream) => {
  const audioContext = new AudioContext();
  const analyser = audioContext.createAnalyser();
  const source = audioContext.createMediaStreamSource(stream);
  
  source.connect(analyser);
  analyser.fftSize = 256;
  
  const dataArray = new Uint8Array(analyser.frequencyBinCount);
  
  const checkLevel = () => {
    analyser.getByteFrequencyData(dataArray);
    const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
    setAudioLevel(average / 255);
    requestAnimationFrame(checkLevel);
  };
  
  checkLevel();
  
  return audioContext;
};
```

### Audio Constraints

```javascript
const audioConstraints = {
  audio: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    sampleRate: 48000,
    channelCount: 1
  }
};
```

---

## 6. Room State Management

### Description

Server-side room state management for discussion sessions.

### Room State Structure

```javascript
{
  id: string,              // Room identifier
  participants: [          // Array of participants
    {
      id: string,
      socketId: string,
      anonymousName: string,
      campus: string,
      location: string,
      isReady: boolean,
      role: 'speaker' | 'listener'
    }
  ],
  discussion: {
    active: boolean,       // Is discussion active
    topic: object,         // Current topic
    currentSpeakerIndex: number,
    speakingTime: number,  // Time per speaker (seconds)
    timeRemaining: number, // Time remaining
    round: number,         // Current round
    timer: NodeJS.Timer,   // Timer reference
    startedAt: Date,
    endedAt: Date
  },
  createdAt: Date
}
```

### Implementation

**Location:** `server/src/socket/roomManager.js`

**Key Functions:**

```javascript
class RoomManager {
  constructor() {
    this.rooms = new Map();
  }
  
  getRoom(roomId) {
    if (!this.rooms.has(roomId)) {
      this.rooms.set(roomId, this.createRoom(roomId));
    }
    return this.rooms.get(roomId);
  }
  
  addUserToRoom(roomId, userData) {
    const room = this.getRoom(roomId);
    
    // Remove if already exists
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
    
    // Clean up empty rooms
    if (room.participants.length === 0) {
      this.deleteRoom(roomId);
    }
  }
  
  startDiscussion(roomId, topic) {
    const room = this.getRoom(roomId);
    
    room.discussion.active = true;
    room.discussion.topic = topic;
    room.discussion.currentSpeakerIndex = 0;
    room.discussion.timeRemaining = room.discussion.speakingTime;
    room.discussion.startedAt = new Date();
    
    return room;
  }
}
```

---

## 7. Session Analytics

### Description

Track and analyze discussion sessions for insights and improvements.

### Data Collected

**Session Data:**
- Session ID
- Room ID
- Topic information
- Participant count
- Start and end times
- Duration
- Rounds completed

**Participant Data:**
- User ID
- Anonymous name
- Campus and location
- Join and leave times
- Speaking time

**Topic Analytics:**
- Topic usage frequency
- Category popularity
- Source (AI vs fallback)

### Implementation

**Location:** `server/src/database/database.js`

**Recording Session:**
```javascript
export async function saveSession(sessionData) {
  const query = `
    INSERT INTO sessions (
      id, room_id, topic_title, topic_category, 
      participant_count, started_at, ended_at, 
      duration_seconds, rounds_completed
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `;
  
  return new Promise((resolve, reject) => {
    db.run(query, [
      sessionData.id,
      sessionData.roomId,
      sessionData.topic?.title,
      sessionData.topic?.category,
      sessionData.participantCount,
      sessionData.startedAt,
      sessionData.endedAt,
      sessionData.durationSeconds,
      sessionData.roundsCompleted
    ], function(err) {
      if (err) reject(err);
      else resolve(this.lastID);
    });
  });
}
```

**Retrieving Analytics:**
```javascript
export async function getSessionAnalytics(limit = 10) {
  const query = `
    SELECT * FROM sessions 
    ORDER BY created_at DESC 
    LIMIT ?
  `;
  
  return new Promise((resolve, reject) => {
    db.all(query, [limit], (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}
```

---

## 8. Error Handling & Recovery

### Description

Comprehensive error handling for robust user experience.

### Error Categories

1. **Network Errors**
   - Connection failures
   - Timeout errors
   - Reconnection handling

2. **Permission Errors**
   - Microphone access denied
   - Browser incompatibility
   - WebRTC failures

3. **Application Errors**
   - Invalid room state
   - Missing participants
   - Topic generation failures

### Implementation

**Automatic Reconnection:**
```javascript
socket.on('disconnect', () => {
  console.log('Disconnected. Attempting to reconnect...');
  
  // Socket.io handles automatic reconnection
  // Rejoin room on reconnect
  socket.on('connect', () => {
    if (currentRoom) {
      socket.emit('join-room', currentRoom, { role: userRole });
    }
  });
});
```

**Error Boundaries:**
```javascript
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    
    return this.props.children;
  }
}
```

---

## Feature Configuration

### Environment Variables

```bash
# Server Configuration
PORT=3003
NODE_ENV=development

# Participant Limits
MIN_PARTICIPANTS=1
MAX_PARTICIPANTS=8

# Speaking Time
DEFAULT_SPEAKING_TIME=60

# AI Integration
HUGGINGFACE_API_KEY=your_api_key

# CORS
ALLOWED_ORIGINS=http://localhost:5173,https://your-domain.com

# Database
DATABASE_URL=./data/roundtable.db
```

### Feature Flags

```javascript
const features = {
  aiTopics: !!process.env.HUGGINGFACE_API_KEY,
  analytics: true,
  feedback: true,
  chat: false,  // Future feature
  recording: false  // Future feature
};
```

---

## Performance Optimizations

### Client-Side

1. **Code Splitting:** Route-based lazy loading
2. **Memoization:** React.memo for expensive components
3. **Debouncing:** Event throttling for frequent updates
4. **Asset Optimization:** Vite's automatic optimization

### Server-Side

1. **Event Batching:** Reduced socket emissions
2. **Memory Management:** Room cleanup
3. **Database Queries:** Optimized SQLite queries
4. **Caching:** Topic and config caching

---

## Future Enhancements

### Planned Features

1. **Text Chat:** In-discussion messaging
2. **Recording:** Session recording and playback
3. **Transcription:** AI-powered transcription
4. **Reactions:** Emoji reactions during discussion
5. **Breakout Rooms:** Smaller group discussions
6. **Polls:** Quick polls during discussion
7. **Screen Sharing:** Visual content sharing
8. **Mobile App:** Native mobile applications

---

## Support

For feature-related questions:
- Review implementation in source code
- Check environment configuration
- Test individual features in isolation
- Consult GitHub issues for known bugs
