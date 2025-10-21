# WebSocket API Reference (Socket.io)

## Overview

The GupShup Cafe platform uses Socket.io for real-time bidirectional communication between clients and the server. This enables instant updates for participant actions, discussion state changes, and audio coordination.

**Server URL**: `http://localhost:3003` (development)  
**Transport**: Socket.io with polling/websocket upgrade  
**Namespace**: Default namespace (`/`)

## Connection

### Client Connection

```javascript
import { io } from 'socket.io-client';
import { API_CONFIG, SOCKET_EVENTS } from '../utils/constants.js';

const socket = io(API_CONFIG.SOCKET_URL, {
  auth: {
    userId: 'user-123',
    name: 'John Doe',
    campusOrLocation: 'Delhi Campus, India',
    anonymousName: 'Wise Owl'
  },
  transports: ['polling', 'websocket'],
  reconnection: true,
  reconnectionAttempts: 15,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 10000,
  timeout: 20000
});
```

### Connection Events

#### `connect`

Fired when successfully connected to the server.

```javascript
socket.on(SOCKET_EVENTS.CONNECT, () => {
  console.log('Connected:', socket.id);
});
```

#### `disconnect`

Fired when disconnected from the server.

```javascript
socket.on(SOCKET_EVENTS.DISCONNECT, (reason) => {
  console.log('Disconnected:', reason);
  // Reasons: 'transport close', 'ping timeout', 'transport error', etc.
});
```

#### `connect_error`

Fired when connection fails.

```javascript
socket.on(SOCKET_EVENTS.CONNECT_ERROR, (error) => {
  console.error('Connection error:', error);
});
```

#### `connection-ack`

Server acknowledgment of successful connection.

```javascript
socket.on('connection-ack', (data) => {
  console.log('Connection acknowledged:', data);
  // { sid: 'socket-id', connectedAt: 'timestamp', serverPid: 12345 }
});
```

---

## Client to Server Events

These events are emitted by the client to the server.

### Room Management

#### `join-room`

Join a discussion room.

**Emit:**
```javascript
socket.emit(SOCKET_EVENTS.JOIN_ROOM, roomId, userData, roomMetadata);
```

**Parameters:**
- `roomId` (string) - Unique room identifier
- `userData` (object) - User information
  - `userId` (string) - User ID
  - `name` (string) - Real name
  - `campusOrLocation` (string) - Location info
  - `anonymousName` (string) - Display name
  - `role` (string) - User role: 'speaker', 'listener', or 'host'
- `roomMetadata` (object, optional) - Room configuration
  - `name` (string) - Room name
  - `topic_category` (string) - Topic category
  - `cefr_level` (string) - Language level

**Server Response:**
- Emits `participant-joined` to all room members
- Emits `participants-update` to all room members

**Example:**
```javascript
const roomId = 'room-abc123';
const userData = {
  userId: 'user-123',
  name: 'John Doe',
  campusOrLocation: 'Delhi Campus',
  anonymousName: 'Wise Owl',
  role: USER_ROLES.SPEAKER
};

socket.emit(SOCKET_EVENTS.JOIN_ROOM, roomId, userData);

// Listen for confirmation
socket.on(SOCKET_EVENTS.PARTICIPANTS_UPDATE, (participants) => {
  console.log('Room joined, participants:', participants);
});
```

---

#### `leave-room`

Leave the current discussion room.

**Emit:**
```javascript
socket.emit(SOCKET_EVENTS.LEAVE_ROOM);
```

**Server Response:**
- Emits `participants-update` to remaining room members
- Emits `participant-left` notification to room

**Example:**
```javascript
socket.emit(SOCKET_EVENTS.LEAVE_ROOM);

// Clean up local state
socket.off(SOCKET_EVENTS.PARTICIPANTS_UPDATE);
socket.off(SOCKET_EVENTS.DISCUSSION_STARTED);
```

---

### Discussion Control

#### `user-ready`

Mark user as ready to start the discussion.

**Emit:**
```javascript
socket.emit(SOCKET_EVENTS.USER_READY, { isReady: true });
```

**Parameters:**
- `isReady` (boolean) - Ready state

**Server Response:**
- Emits `participants-update` with updated ready states
- Automatically starts discussion when minimum participants are ready

**Flow Diagram:**
```
User clicks "Ready" 
    → emit('user-ready', { isReady: true })
    → Server updates participant state
    → Server emits 'participants-update'
    → Check if minimum ready
    → If yes: emit 'discussion-started'
```

**Example:**
```javascript
// Mark as ready
socket.emit(SOCKET_EVENTS.USER_READY, { isReady: true });

// Listen for discussion start
socket.on(SOCKET_EVENTS.DISCUSSION_STARTED, (data) => {
  console.log('Discussion starting!', data);
});
```

---

#### `next-speaker`

Request to advance to the next speaker.

**Emit:**
```javascript
socket.emit(SOCKET_EVENTS.NEXT_SPEAKER);
```

**Server Response:**
- Emits `turn-ended` for current speaker
- Emits `turn-started` for next speaker
- Updates timer and speaker index

**Example:**
```javascript
// Advance to next speaker
socket.emit(SOCKET_EVENTS.NEXT_SPEAKER);

// Listen for turn change
socket.on('turn-started', (turnData) => {
  console.log('Next speaker:', turnData.speaker);
  console.log('Time:', turnData.timer);
});
```

---

#### `role-change`

Request to change user role between speaker and listener.

**Emit:**
```javascript
socket.emit(SOCKET_EVENTS.ROLE_CHANGE, { userId: 'user-123', role: 'speaker' });
```

**Parameters:**
- `userId` (string) - User ID
- `role` (string) - New role: 'speaker' or 'listener'
- `roomId` (string, optional) - Room ID

**Server Response:**
- Emits `participants-update` with updated roles
- Emits `role-changed` on success
- May emit `role-change-failed` if change not allowed

**Example:**
```javascript
const handleRoleChange = (newRole) => {
  socket.emit(SOCKET_EVENTS.ROLE_CHANGE, {
    userId: user.id,
    role: newRole,
    roomId: currentRoom
  });
};

// Listen for role change confirmation
socket.on('role-changed', (data) => {
  console.log('Role changed:', data);
});

socket.on('role-change-failed', (error) => {
  console.error('Role change failed:', error);
});
```

---

### WebRTC Signaling

#### `webrtc-offer`

Send WebRTC connection offer to peer.

**Emit:**
```javascript
socket.emit(SOCKET_EVENTS.WEBRTC_OFFER, {
  to: 'peer-socket-id',
  sdp: rtcOffer.sdp
});
```

**Parameters:**
- `to` (string) - Target peer socket ID
- `sdp` (string) - WebRTC SDP offer

**Server Response:**
- Forwards offer to target peer

**Example:**
```javascript
const peerConnection = new RTCPeerConnection(WEBRTC_CONFIG);

peerConnection.createOffer()
  .then(offer => peerConnection.setLocalDescription(offer))
  .then(() => {
    socket.emit(SOCKET_EVENTS.WEBRTC_OFFER, {
      to: targetSocketId,
      sdp: peerConnection.localDescription.sdp
    });
  });
```

---

#### `webrtc-answer`

Send WebRTC connection answer to peer.

**Emit:**
```javascript
socket.emit(SOCKET_EVENTS.WEBRTC_ANSWER, {
  to: 'peer-socket-id',
  sdp: rtcAnswer.sdp
});
```

**Parameters:**
- `to` (string) - Target peer socket ID
- `sdp` (string) - WebRTC SDP answer

**Server Response:**
- Forwards answer to target peer

**Example:**
```javascript
socket.on(SOCKET_EVENTS.WEBRTC_OFFER, async ({ from, sdp }) => {
  await peerConnection.setRemoteDescription({ type: 'offer', sdp });
  const answer = await peerConnection.createAnswer();
  await peerConnection.setLocalDescription(answer);
  
  socket.emit(SOCKET_EVENTS.WEBRTC_ANSWER, {
    to: from,
    sdp: answer.sdp
  });
});
```

---

#### `webrtc-ice-candidate`

Send ICE candidate to peer for connection establishment.

**Emit:**
```javascript
socket.emit(SOCKET_EVENTS.WEBRTC_ICE_CANDIDATE, {
  to: 'peer-socket-id',
  candidate: iceCandidate
});
```

**Parameters:**
- `to` (string) - Target peer socket ID
- `candidate` (RTCIceCandidate) - ICE candidate

**Server Response:**
- Forwards candidate to target peer

**Example:**
```javascript
peerConnection.onicecandidate = (event) => {
  if (event.candidate) {
    socket.emit(SOCKET_EVENTS.WEBRTC_ICE_CANDIDATE, {
      to: targetSocketId,
      candidate: event.candidate
    });
  }
};
```

#### `ready-for-webrtc`

Signal that client is ready for WebRTC connections.

**Emit:**
```javascript
socket.emit(SOCKET_EVENTS.READY_FOR_WEBRTC);
```

**Server Response:**
- Emits `peer-ready` to other participants

**Example:**
```javascript
// After getting audio stream and participants list
if (localStream && participants.length > 0) {
  socket.emit(SOCKET_EVENTS.READY_FOR_WEBRTC);
}
```

---

### Chat (Future Feature)

#### `message`

Send a chat message to the room.

**Emit:**
```javascript
socket.emit('message', 'Hello everyone!');
```

**Parameters:**
- `message` (string) - Chat message text

**Server Response:**
- Broadcasts message to all room participants

---

## Server to Client Events

These events are emitted by the server to the client.

### Room Updates

#### `participants-update`

Sent when participants list changes (join, leave, ready state).

**Receive:**
```javascript
socket.on(SOCKET_EVENTS.PARTICIPANTS_UPDATE, (participants) => {
  console.log('Updated participants:', participants);
});
```

**Payload:**
```javascript
[
  {
    id: 'user-123',
    socketId: 'socket-abc',
    anonymousName: 'Wise Owl',
    campus: 'Delhi Campus',
    location: 'India',
    isReady: true,
    role: 'speaker'
  }
]
```

**Example:**
```javascript
socket.on(SOCKET_EVENTS.PARTICIPANTS_UPDATE, (participants) => {
  setParticipants(participants);
  
  // Check if we can start
  const allReady = participants.every(p => p.isReady);
  const minParticipants = DISCUSSION_CONFIG.MIN_PARTICIPANTS;
  setCanStart(allReady && participants.length >= minParticipants);
});
```

---

#### `participant-joined`

Notification when a user joins the room.

**Receive:**
```javascript
socket.on('participant-joined', (data) => {
  console.log(`${data.participant.anonymousName} joined!`);
});
```

**Payload:**
```javascript
{
  participant: {
    id: 'user-123',
    socketId: 'socket-abc',
    anonymousName: 'Wise Owl',
    role: 'speaker',
    isReady: false
  }
}
```

---

#### `participant-left`

Notification when a user leaves the room.

**Receive:**
```javascript
socket.on('participant-left', (data) => {
  console.log(`${data.anonymousName} left!`);
});
```

**Payload:**
```javascript
{
  participantId: 'user-123',
  anonymousName: 'Wise Owl',
  wasHost: false,
  newHost: null
}
```

---

#### `room-update`

Notification when room state changes.

**Receive:**
```javascript
socket.on(SOCKET_EVENTS.ROOM_UPDATE, (roomData) => {
  console.log('Room updated:', roomData);
});
```

**Payload:**
```javascript
{
  roomId: 'room-123',
  status: 'in_progress',
  participantCount: 4,
  maxParticipants: 6
}
```

---

### Discussion Events

#### `discussion-started`

Emitted when the discussion begins.

**Receive:**
```javascript
socket.on(SOCKET_EVENTS.DISCUSSION_STARTED, (data) => {
  console.log('Discussion started!', data);
});
```

**Payload:**
```javascript
{
  topic: {
    title: 'The Future of Education',
    description: 'How will technology reshape learning...',
    category: 'Education',
    questions: [
      'What role should AI play?',
      'How can we maintain human connection?'
    ]
  },
  participants: [...],
  speakingTime: 60,
  currentSpeaker: {
    id: 'user-123',
    anonymousName: 'Wise Owl'
  }
}
```

**Example:**
```javascript
socket.on(SOCKET_EVENTS.DISCUSSION_STARTED, (data) => {
  setDiscussionActive(true);
  setTopic(data.topic);
  setCurrentSpeaker(data.firstSpeaker);
  setSpeakingTime(data.duration);
  
  // Navigate to roundtable
  navigate('/roundtable');
});
```

---

#### `discussion-ended`

Emitted when the discussion ends.

**Receive:**
```javascript
socket.on(SOCKET_EVENTS.DISCUSSION_ENDED, (data) => {
  console.log('Discussion ended!', data);
});
```

**Payload:**
```javascript
{
  roomId: 'active-room-uuid',
  roundsCompleted: 3
}
```

---

#### `turn-started`

Emitted when it's a speaker's turn to speak.

**Receive:**
```javascript
socket.on('turn-started', (turnData) => {
  console.log('Turn started:', turnData);
});
```

**Payload:**
```javascript
{
  speaker_index: 1,
  speaker: {
    id: 'user-456',
    anonymousName: 'Clever Fox',
    role: 'speaker'
  },
  timer: 60
}
```

**Example:**
```javascript
socket.on('turn-started', (turnData) => {
  setCurrentSpeaker(turnData.speaker);
  setTimeRemaining(turnData.timer);
  setSpeakerIndex(turnData.speaker_index);
  
  // Update audio state
  const isMyTurn = turnData.speaker.id === user.id;
  updateAudioState(isMyTurn ? 'speaker' : 'listener');
});
```

---

#### `turn-ended`

Emitted when a speaker's turn ends.

**Receive:**
```javascript
socket.on('turn-ended', (data) => {
  console.log('Turn ended:', data);
});
```

**Payload:**
```javascript
{
  speaker: {
    id: 'user-456',
    anonymousName: 'Clever Fox'
  }
}
```

---

#### `round-complete`

Emitted when all speakers in a round have finished.

**Receive:**
```javascript
socket.on('round-complete', (data) => {
  console.log('Round complete:', data);
});
```

**Payload:**
```javascript
{
  round: 1,
  next: 2
}
```

---

#### `timer-warning`

Sent when speaking time is running low.

**Receive:**
```javascript
socket.on('timer-warning', (data) => {
  console.log('Time warning:', data.remaining);
});
```

**Payload:**
```javascript
{
  remaining: 10
}
```

**Example:**
```javascript
socket.on('timer-warning', (data) => {
  setTimeRemaining(data.remaining);
  
  // Show visual warning
  showTimeWarning(`${data.remaining} seconds remaining!`);
});
```

---

#### `speaker-change`

Emitted when the current speaker changes.

**Receive:**
```javascript
socket.on(SOCKET_EVENTS.SPEAKER_CHANGE, (speaker) => {
  console.log('Speaker changed:', speaker);
});
```

**Payload:**
```javascript
{
  id: 'user-456',
  anonymousName: 'Clever Fox',
  role: 'speaker'
}
```

---

### WebRTC Events

#### `webrtc-offer`

Received WebRTC offer from peer.

**Receive:**
```javascript
socket.on('webrtc-offer', async ({ from, offer }) => {
  // Handle offer
});
```

**Payload:**
```javascript
{
  from: 'socket-abc',
  offer: {
    type: 'offer',
    sdp: '...'
  }
}
```

---

#### `webrtc-answer`

Received WebRTC answer from peer.

**Receive:**
```javascript
socket.on('webrtc-answer', async ({ from, answer }) => {
  // Handle answer
});
```

**Payload:**
```javascript
{
  from: 'socket-xyz',
  answer: {
    type: 'answer',
    sdp: '...'
  }
}
```

---

#### `webrtc-ice-candidate`

Received ICE candidate from peer.

**Receive:**
```javascript
socket.on('webrtc-ice-candidate', async ({ from, candidate }) => {
  // Add ICE candidate
});
```

**Payload:**
```javascript
{
  from: 'socket-abc',
  candidate: {
    candidate: 'candidate:...',
    sdpMLineIndex: 0,
    sdpMid: '0'
  }
}
```

---

### Feedback Events

#### `english-feedback`

AI-generated English feedback for participants.

**Receive:**
```javascript
socket.on(SOCKET_EVENTS.ENGLISH_FEEDBACK, (feedback) => {
  console.log('English feedback received:', feedback);
});
```

**Payload:**
```javascript
{
  participantId: 'user-123',
  feedback: 'Great use of vocabulary! Try to speak more slowly.',
  timestamp: '2025-10-21T17:30:00Z'
}
```

---

#### `transcript-update`

Real-time transcript updates during speaking.

**Receive:**
```javascript
socket.on(SOCKET_EVENTS.TRANSCRIPT_UPDATE, (transcript) => {
  console.log('Transcript update:', transcript);
});
```

**Payload:**
```javascript
{
  participantId: 'user-123',
  text: 'I think that technology will...',
  timestamp: '2025-10-21T17:30:00Z',
  isPartial: true
}
```

---

### Error Events

#### `error`

General error notification.

**Receive:**
```javascript
socket.on('error', (message) => {
  console.error('Socket error:', message);
});
```

**Payload:**
```javascript
"Failed to update ready status"
```

**Example:**
```javascript
socket.on('error', (message) => {
  showNotification({
    type: 'error',
    message: message || 'An error occurred'
  });
});
```

---

## Event Flow Diagrams

### Room Join Flow

```
Client                          Server                          Other Clients
  |                               |                                    |
  |----join-room('room-123')----->|                                    |
  |                               |                                    |
  |                               |---participant-joined-------------->|
  |<---participant-joined---------|                                    |
  |                               |                                    |
  |                               |---participants-update------------->|
  |<---participants-update--------|                                    |
```

### Discussion Start Flow

```
Client A              Client B              Server
  |                      |                     |
  |--user-ready(true)--->|                     |
  |                      |--user-ready(true)-->|
  |                      |                     |
  |<---participants-update--------------------|
  |                      |<-participants-update|
  |                      |                     |
  |                      |  (min ready met)    |
  |<---discussion-started---------------------|
  |                      |<--discussion-started|
  |                      |                     |
  |<---turn-started---------------------------|
  |                      |<--turn-started------|
```

### Speaker Turn Flow

```
Client (Speaker)         Server              Other Clients
  |                        |                       |
  |                        |---timer-warning------>|
  |<---timer-warning-------|                       |
  |                        |                       |
  |                        | (time expires)        |
  |                        |                       |
  |<---turn-ended----------|                       |
  |                        |---turn-ended--------->|
  |                        |                       |
  |<---turn-started--------|                       |
  |                        |---turn-started------->|
```

### WebRTC Connection Flow

```
Client A                 Server                Client B
  |                        |                       |
  |--webrtc-offer--------->|                       |
  |                        |---webrtc-offer------->|
  |                        |                       |
  |                        |<--webrtc-answer-------|
  |<--webrtc-answer--------|                       |
  |                        |                       |
  |--ice-candidate-------->|                       |
  |                        |---ice-candidate------>|
  |                        |<--ice-candidate-------|
  |<--ice-candidate--------|                       |
  |                        |                       |
  |<========= WebRTC Peer Connection ============>|
```

---

## Best Practices

### 1. Connection Management

```javascript
import { SOCKET_EVENTS } from '../utils/constants.js';

// Always clean up listeners
useEffect(() => {
  socket.on(SOCKET_EVENTS.PARTICIPANTS_UPDATE, handleParticipantsUpdate);
  
  return () => {
    socket.off(SOCKET_EVENTS.PARTICIPANTS_UPDATE, handleParticipantsUpdate);
  };
}, []);
```

### 2. Reconnection Handling

```javascript
socket.on(SOCKET_EVENTS.CONNECT, () => {
  // Rejoin room after reconnection
  if (currentRoom && userData) {
    socket.emit(SOCKET_EVENTS.JOIN_ROOM, currentRoom, userData);
  }
});
```

### 3. Error Handling

```javascript
socket.on(SOCKET_EVENTS.CONNECT_ERROR, (error) => {
  console.error('Connection failed:', error);
  // Show user-friendly message
  showNotification(ERROR_MESSAGES.SOCKET_CONNECTION_FAILED);
});
```

### 4. Event Debouncing

```javascript
import { UI_CONFIG } from '../utils/constants.js';

// Avoid rapid-fire events
const debouncedReadyToggle = debounce((isReady) => {
  socket.emit(SOCKET_EVENTS.USER_READY, { isReady });
}, UI_CONFIG.DEBOUNCE_DELAY);
```

---

## Testing WebSocket Events

### Manual Testing

```javascript
import { SOCKET_EVENTS, USER_ROLES } from '../utils/constants.js';

// Join room
const userData = {
  userId: 'test-user',
  name: 'Test User',
  campusOrLocation: 'Test Campus',
  anonymousName: 'Test Owl',
  role: USER_ROLES.SPEAKER
};
socket.emit(SOCKET_EVENTS.JOIN_ROOM, 'test-room', userData);

// Mark ready
socket.emit(SOCKET_EVENTS.USER_READY, { isReady: true });

// Advance speaker
socket.emit(SOCKET_EVENTS.NEXT_SPEAKER);

// Leave room
socket.emit(SOCKET_EVENTS.LEAVE_ROOM);
```

### Event Logging

```javascript
// Log all events
const events = [
  SOCKET_EVENTS.CONNECT,
  SOCKET_EVENTS.DISCONNECT,
  SOCKET_EVENTS.PARTICIPANTS_UPDATE,
  SOCKET_EVENTS.DISCUSSION_STARTED,
  SOCKET_EVENTS.SPEAKER_CHANGE,
  'timer-warning'
];

events.forEach(event => {
  socket.on(event, (...args) => {
    console.log(`[${event}]`, ...args);
  });
});
```

---

## Security Considerations

1. **Authentication:** User info sent via auth token on connection
2. **Room Isolation:** Events only broadcast to room members
3. **Input Validation:** Server validates all event data
4. **Rate Limiting:** Implement client-side debouncing
5. **WebRTC Security:** Use DTLS-SRTP for audio encryption

---

## Support

For WebSocket-related issues:
- Check server logs for connection errors
- Verify CORS and allowed origins
- Test with Socket.io client debugger
- See GitHub issues for known problems
