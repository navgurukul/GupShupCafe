# WebSocket API Reference (Socket.io)

## Overview

The GupShup Cafe platform uses Socket.io for real-time bidirectional communication between clients and the server. This enables instant updates for participant actions, discussion state changes, and audio coordination.

## Connection

### Client Connection

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:3003', {
  auth: {
    userId: 'user-123',
    name: 'John Doe',
    campus: 'Delhi Campus',
    location: 'India',
    anonymousName: 'Wise Owl'
  },
  transports: ['websocket', 'polling'],
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000
});
```

### Connection Events

#### `connect`

Fired when successfully connected to the server.

```javascript
socket.on('connect', () => {
  console.log('Connected:', socket.id);
});
```

#### `disconnect`

Fired when disconnected from the server.

```javascript
socket.on('disconnect', (reason) => {
  console.log('Disconnected:', reason);
  // Reasons: 'transport close', 'ping timeout', 'transport error', etc.
});
```

#### `connect_error`

Fired when connection fails.

```javascript
socket.on('connect_error', (error) => {
  console.error('Connection error:', error);
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
socket.emit('join-room', roomId, userData, roomMetadata);
```

**Parameters:**
- `roomId` (string) - Unique room identifier
- `userData` (object) - User information
  - `userId` (string) - User ID
  - `name` (string) - User's real name
  - `campusOrLocation` (string) - Campus or location
  - `anonymousName` (string) - Anonymous display name
  - `role` (string) - User role: 'speaker' or 'listener'
- `roomMetadata` (object, optional) - Room configuration
  - `name` (string) - Room name
  - `topic_category` (string) - Topic category
  - `cefr_level` (number) - CEFR level (1-6)

**Server Response:**
- Emits `participants-update` to all room members
- Emits `participant-joined` notification to room
- Emits `user-reconnected` if user is reconnecting

**Example:**
```javascript
const roomId = 'room-abc123';
const userData = {
  userId: 'user-123',
  name: 'John Doe',
  campusOrLocation: 'Delhi Campus',
  anonymousName: 'Wise Owl',
  role: 'speaker'
};
const roomMetadata = {
  name: 'Discussion Room 1',
  topic_category: 'Education',
  cefr_level: 3
};

socket.emit('join-room', roomId, userData, roomMetadata);

// Listen for confirmation
socket.on('participants-update', (participants) => {
  console.log('Room joined, participants:', participants);
});
```

---

#### `leave-room`

Leave the current discussion room.

**Emit:**
```javascript
socket.emit('leave-room');
```

**Server Response:**
- Emits `participants-update` to remaining room members
- Emits `user-left` notification to room

**Example:**
```javascript
socket.emit('leave-room');

// Clean up local state
socket.off('participants-update');
socket.off('discussion-start');
```

---

### Discussion Control

#### `user-ready`

Mark user as ready to start the discussion.

**Emit:**
```javascript
socket.emit('user-ready', { isReady: true });
```

**Parameters:**
- `data` (object, optional) - Ready state data
  - `isReady` (boolean) - Ready state (default: true)

**Server Response:**
- Emits `participants-update` with updated ready states
- Automatically starts discussion when all users are ready (based on MIN_PARTICIPANTS config)

**Flow Diagram:**
```
User clicks "Ready" 
    → emit('user-ready', { isReady: true })
    → Server updates participant state
    → Server emits 'participants-update'
    → Check if all ready
    → If yes: emit 'discussion-started'
```

**Example:**
```javascript
// Mark as ready
socket.emit('user-ready', { isReady: true });

// Listen for discussion start
socket.on('discussion-started', (data) => {
  console.log('Discussion starting!', data);
});

// Mark as not ready
socket.emit('user-ready', { isReady: false });
```

---

#### `start-discussion`

Host manually starts the discussion (host-only event).

**Emit:**
```javascript
socket.emit('start-discussion');
```

**Authorization:**
- Only the room host can start the discussion
- All participants must be ready

**Server Response:**
- Starts the discussion if conditions are met
- Emits `discussion-started` to all room members
- Returns error if user is not host or not all ready

**Example:**
```javascript
// Host starts discussion
socket.emit('start-discussion');

// Listen for discussion start
socket.on('discussion-started', (data) => {
  console.log('Discussion started:', data);
});
```

---

#### `change-role`

Change user role in the current room.

**Emit:**
```javascript
socket.emit('change-role', { userId: 'user-123', role: 'speaker' });
```

**Parameters:**
- `userId` (string) - User identifier
- `role` (string) - New role: 'speaker' or 'listener'

**Server Response:**
- Emits `participants-update` with updated roles
- Emits `role-changed` notification
- Emits `role-change-failed` if max speakers reached

**Example:**
```javascript
socket.emit('change-role', {
  userId: user.id,
  role: 'speaker'
});

socket.on('role-changed', (data) => {
  console.log(`User ${data.userId} is now ${data.role}`);
});

socket.on('role-change-failed', (error) => {
  console.error('Role change failed:', error);
});
```

---

#### `next-speaker`

Request to advance to the next speaker (alias for `end-turn`).

**Emit:**
```javascript
socket.emit('next-speaker');
```

**Server Response:**
- Emits `turn-ended` with current speaker information
- Emits `turn-started` with next speaker information
- Updates timer and speaker index

**Example:**
```javascript
// Advance to next speaker
socket.emit('next-speaker');

// Listen for turn change
socket.on('turn-started', (turnData) => {
  console.log('Next speaker:', turnData.speaker);
  console.log('Time:', turnData.timer);
});
```

---

#### `end-turn`

End the current speaking turn.

**Emit:**
```javascript
socket.emit('end-turn');
```

**Server Response:**
- Cancels current timer
- Emits `turn-ended` with current speaker
- Advances to next speaker
- Emits `turn-started` for next speaker
- Emits `round-complete` if round finished
- Emits `discussion-ended` if all rounds complete

**Example:**
```javascript
socket.emit('end-turn');

socket.on('turn-ended', (data) => {
  console.log('Turn ended for:', data.speaker);
});

socket.on('turn-started', (data) => {
  console.log('Next turn:', data.speaker);
});
```

---

### WebRTC Signaling

#### `webrtc-offer`

Send WebRTC connection offer to peer.

**Emit:**
```javascript
socket.emit('webrtc-offer', {
  to: 'peer-socket-id',
  sdp: rtcOffer
});
```

**Parameters:**
- `to` (string) - Target peer socket ID
- `sdp` (RTCSessionDescription) - WebRTC SDP offer

**Server Response:**
- Forwards offer to target peer with `from` field

**Example:**
```javascript
const peerConnection = new RTCPeerConnection(config);

peerConnection.createOffer()
  .then(offer => peerConnection.setLocalDescription(offer))
  .then(() => {
    socket.emit('webrtc-offer', {
      to: targetSocketId,
      sdp: peerConnection.localDescription
    });
  });
```

---

#### `webrtc-answer`

Send WebRTC connection answer to peer.

**Emit:**
```javascript
socket.emit('webrtc-answer', {
  to: 'peer-socket-id',
  sdp: rtcAnswer
});
```

**Parameters:**
- `to` (string) - Target peer socket ID
- `sdp` (RTCSessionDescription) - WebRTC SDP answer

**Server Response:**
- Forwards answer to target peer with `from` field

**Example:**
```javascript
socket.on('webrtc-offer', async ({ from, sdp }) => {
  await peerConnection.setRemoteDescription(sdp);
  const answer = await peerConnection.createAnswer();
  await peerConnection.setLocalDescription(answer);
  
  socket.emit('webrtc-answer', {
    to: from,
    sdp: answer
  });
});
```

---

#### `webrtc-ice-candidate`

Send ICE candidate to peer for connection establishment.

**Emit:**
```javascript
socket.emit('webrtc-ice-candidate', {
  to: 'peer-socket-id',
  candidate: iceCandidate
});
```

**Parameters:**
- `to` (string) - Target peer socket ID
- `candidate` (RTCIceCandidate) - ICE candidate

**Server Response:**
- Forwards candidate to target peer with `from` field

**Example:**
```javascript
peerConnection.onicecandidate = (event) => {
  if (event.candidate) {
    socket.emit('webrtc-ice-candidate', {
      to: targetSocketId,
      candidate: event.candidate
    });
  }
};
```

---

#### `ready-for-webrtc`

Signal that client is ready to establish WebRTC connections.

**Emit:**
```javascript
socket.emit('ready-for-webrtc');
```

**Server Response:**
- Emits `peer-ready` to other participants with socket ID

**Example:**
```javascript
// After setting up local media stream
socket.emit('ready-for-webrtc');

socket.on('peer-ready', ({ socketId }) => {
  console.log('Peer ready:', socketId);
  // Initiate WebRTC offer
});
```

---

### Transcript & Feedback

#### `speech-transcript`

Submit speech transcript (deprecated, use `transcript-received`).

**Emit:**
```javascript
socket.emit('speech-transcript', {
  text: 'Transcript text',
  speakerId: 'user-123'
});
```

**Parameters:**
- `text` (string) - Transcript text
- `speakerId` (string) - Speaker user ID

**Server Response:**
- Saves transcript to database

---

#### `transcript-received`

Submit speech transcript with metadata for processing.

**Emit:**
```javascript
socket.emit('transcript-received', {
  text: 'Transcript text',
  participantId: 'user-123',
  round: 1,
  turnOrder: 0,
  confidence: 0.95,
  startedAt: '2024-01-15T10:00:00.000Z',
  endedAt: '2024-01-15T10:01:00.000Z',
  duration: 60
});
```

**Parameters:**
- `text` (string) - Transcript text
- `participantId` (string) - Participant ID
- `round` (number, optional) - Current round number
- `turnOrder` (number, optional) - Turn order in round
- `confidence` (number, optional) - STT confidence score
- `startedAt` (string, optional) - Start timestamp
- `endedAt` (string, optional) - End timestamp
- `duration` (number, optional) - Duration in seconds

**Server Response:**
- Saves transcript to database
- Triggers async English feedback agent processing
- Emits `transcript-saved` with transcript ID

**Example:**
```javascript
socket.emit('transcript-received', {
  text: transcriptText,
  participantId: userId,
  round: currentRound,
  turnOrder: turnIndex,
  confidence: 0.95,
  duration: 60
});

socket.on('transcript-saved', (data) => {
  console.log('Transcript saved:', data.transcriptId);
});
```

---

#### `get-instant-feedback`

Request instant feedback for a participant.

**Emit:**
```javascript
socket.emit('get-instant-feedback', {
  participantId: 'user-123'
});
```

**Parameters:**
- `participantId` (string) - Participant ID

**Server Response:**
- Emits `instant-feedback` with latest feedback

**Example:**
```javascript
socket.emit('get-instant-feedback', {
  participantId: userId
});

socket.on('instant-feedback', (data) => {
  console.log('Feedback:', data.feedback);
});
```

---

#### `request-facilitator-response`

Request AI facilitator to speak.

**Emit:**
```javascript
socket.emit('request-facilitator-response');
```

**Server Response:**
- Generates facilitator response based on recent transcripts
- Emits `facilitator-speaking` with text for TTS

**Example:**
```javascript
socket.emit('request-facilitator-response');

socket.on('facilitator-speaking', (data) => {
  console.log('Facilitator:', data.text);
  // Play TTS audio
});
```

---

### Debug Events

#### `debug-ping`

Roundtrip latency check.

**Emit:**
```javascript
socket.emit('debug-ping', { timestamp: Date.now() });
```

**Server Response:**
- Emits `debug-pong` with echo data and server time

---

#### `debug-whoami`

Get current socket information.

**Emit:**
```javascript
socket.emit('debug-whoami');
```

**Server Response:**
- Emits `debug-whoami` with socket ID and auth data

---

#### `debug-room-state`

Get current room state for debugging.

**Emit:**
```javascript
socket.emit('debug-room-state');
```

**Server Response:**
- Emits `debug-room-state` with full room information

---

### Chat

#### `message`

Send a chat message to the room.

**Emit:**
```javascript
socket.emit('message', 'Hello everyone!');
```

**Parameters:**
- `message` (string) - Chat message text

**Server Response:**
- Broadcasts message to all room participants (excluding sender)

**Example:**
```javascript
socket.emit('message', 'Great point!');

socket.on('message', (data) => {
  console.log(`${data.anonymousName}: ${data.message}`);
});
```

---

## Server to Client Events

These events are emitted by the server to the client.

### Connection Events

#### `connection-ack`

Acknowledgement sent immediately after connection.

**Receive:**
```javascript
socket.on('connection-ack', (data) => {
  console.log('Connected:', data);
});
```

**Payload:**
```javascript
{
  sid: 'socket-abc',
  connectedAt: '2024-01-15T10:00:00.000Z',
  serverPid: 12345
}
```

---

### Room Updates

#### `participants-update`

Sent when participants list changes (join, leave, ready state, role change).

**Receive:**
```javascript
socket.on('participants-update', (participants) => {
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
    name: 'John Doe',
    campus: 'Delhi Campus',
    location: 'India',
    isReady: true,
    role: 'speaker',
    joinedAt: '2024-01-15T10:00:00.000Z'
  }
]
```

**Example:**
```javascript
socket.on('participants-update', (participants) => {
  setParticipants(participants);
  
  // Check if we can start
  const allReady = participants.every(p => p.isReady);
  setCanStart(allReady && participants.length >= minParticipants);
});
```

---

#### `participant-joined`

Notification when a user joins the room.

**Receive:**
```javascript
socket.on('participant-joined', (data) => {
  console.log('New participant:', data.participant);
});
```

**Payload:**
```javascript
{
  participant: {
    id: 'user-123',
    anonymousName: 'Wise Owl',
    campus: 'Delhi Campus',
    location: 'India',
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
  newHost: 'user-456'  // Only present if new host assigned
}
```

---

#### `user-reconnected`

Emitted to a user who reconnected to preserve their state.

**Receive:**
```javascript
socket.on('user-reconnected', (data) => {
  console.log('Reconnected with preserved state:', data);
});
```

**Payload:**
```javascript
{
  userId: 'user-123',
  anonymousName: 'Wise Owl',
  wasHost: true,
  preservedState: {
    isReady: true,
    role: 'speaker'
  }
}
```

---

#### `participant-reconnected`

Notification to other users when someone reconnects.

**Receive:**
```javascript
socket.on('participant-reconnected', (data) => {
  console.log('Participant reconnected:', data);
});
```

**Payload:**
```javascript
{
  participantId: 'user-123',
  anonymousName: 'Wise Owl',
  socketId: 'socket-new-123'
}
```

---

#### `host-changed`

Notification when room host changes.

**Receive:**
```javascript
socket.on('host-changed', (data) => {
  console.log('New host assigned:', data);
});
```

**Payload:**
```javascript
{
  newHost: {
    id: 'user-456',
    anonymousName: 'Clever Fox',
    role: 'speaker'
  },
  previousHost: 'Wise Owl'
}
```

---

#### `role-changed`

Notification when user role changes.

**Receive:**
```javascript
socket.on('role-changed', (data) => {
  console.log('Role changed:', data);
});
```

**Payload:**
```javascript
{
  userId: 'user-123',
  role: 'speaker'
}
```

---

#### `role-change-failed`

Emitted when role change fails.

**Receive:**
```javascript
socket.on('role-change-failed', (data) => {
  console.error('Role change failed:', data.error);
});
```

**Payload:**
```javascript
{
  error: 'Maximum number of speakers reached'
}
```

---

### Discussion Events

#### `discussion-started`

Emitted when the discussion begins.

**Receive:**
```javascript
socket.on('discussion-started', (data) => {
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
  firstSpeaker: {
    id: 'user-123',
    anonymousName: 'Wise Owl',
    socketId: 'socket-abc'
  },
  duration: 60
}
```

**Example:**
```javascript
socket.on('discussion-started', (data) => {
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
socket.on('discussion-ended', (data) => {
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

Emitted when a new speaking turn begins.

**Receive:**
```javascript
socket.on('turn-started', (data) => {
  console.log('Turn started:', data);
});
```

**Payload:**
```javascript
{
  speaker_index: 0,
  speaker: {
    id: 'user-123',
    anonymousName: 'Wise Owl',
    socketId: 'socket-abc',
    role: 'speaker'
  },
  timer: 60
}
```

**Example:**
```javascript
socket.on('turn-started', (data) => {
  setCurrentSpeaker(data.speaker);
  setTimeRemaining(data.timer);
  
  // Update audio state
  const isMyTurn = data.speaker.id === user.id;
  updateAudioState(isMyTurn ? 'speaker' : 'listener');
});
```

---

#### `turn-ended`

Emitted when a speaking turn ends.

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
    id: 'user-123',
    anonymousName: 'Wise Owl'
  }
}
```

---

#### `round-complete`

Emitted when a discussion round is complete.

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

Sent when timer reaches warning threshold (default: 10 seconds).

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
  
  // Visual warning when time is low
  if (data.remaining <= 10) {
    showTimeWarning();
  }
});
```

---

### WebRTC Events

#### `peer-ready`

Emitted when a peer is ready for WebRTC connection.

**Receive:**
```javascript
socket.on('peer-ready', (data) => {
  console.log('Peer ready:', data.socketId);
});
```

**Payload:**
```javascript
{
  socketId: 'socket-abc'
}
```

---

#### `webrtc-offer`

Received WebRTC offer from peer.

**Receive:**
```javascript
socket.on('webrtc-offer', async ({ from, sdp }) => {
  // Handle offer
});
```

**Payload:**
```javascript
{
  from: 'socket-abc',
  sdp: {
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
socket.on('webrtc-answer', async ({ from, sdp }) => {
  // Handle answer
});
```

**Payload:**
```javascript
{
  from: 'socket-xyz',
  sdp: {
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

### Transcript & Feedback Events

#### `transcript-saved`

Confirmation that transcript was saved.

**Receive:**
```javascript
socket.on('transcript-saved', (data) => {
  console.log('Transcript saved:', data);
});
```

**Payload:**
```javascript
{
  transcriptId: 'transcript-uuid',
  participantId: 'user-123'
}
```

---

#### `instant-feedback`

Instant feedback for participant.

**Receive:**
```javascript
socket.on('instant-feedback', (data) => {
  console.log('Feedback:', data);
});
```

**Payload:**
```javascript
{
  participantId: 'user-123',
  feedback: 'Great use of vocabulary! Try to speak a bit slower.',
  timestamp: '2024-01-15T10:00:00.000Z'
}
```

---

#### `facilitator-speaking`

AI facilitator response for TTS.

**Receive:**
```javascript
socket.on('facilitator-speaking', (data) => {
  console.log('Facilitator:', data);
});
```

**Payload:**
```javascript
{
  text: 'That\'s an interesting point. Let\'s explore that further.',
  timestamp: '2024-01-15T10:00:00.000Z'
}
```

---

### Chat Events

#### `message`

Chat message from another participant.

**Receive:**
```javascript
socket.on('message', (data) => {
  console.log(`${data.anonymousName}: ${data.message}`);
});
```

**Payload:**
```javascript
{
  id: 'message-uuid',
  userId: 'user-123',
  anonymousName: 'Wise Owl',
  message: 'Hello everyone!',
  timestamp: '2024-01-15T10:00:00.000Z'
}
```

---

### Debug Events

#### `debug-pong`

Response to debug-ping.

**Receive:**
```javascript
socket.on('debug-pong', (data) => {
  console.log('Pong:', data);
});
```

**Payload:**
```javascript
{
  echo: { /* original data */ },
  serverTime: '2024-01-15T10:00:00.000Z',
  sid: 'socket-abc'
}
```

---

#### `debug-whoami`

Current socket information.

**Receive:**
```javascript
socket.on('debug-whoami', (data) => {
  console.log('Whoami:', data);
});
```

**Payload:**
```javascript
{
  sid: 'socket-abc',
  auth: {
    userId: 'user-123',
    name: 'John Doe'
  },
  serverTime: '2024-01-15T10:00:00.000Z'
}
```

---

#### `debug-room-state`

Full room state for debugging.

**Receive:**
```javascript
socket.on('debug-room-state', (data) => {
  console.log('Room state:', data);
});
```

**Payload:**
```javascript
{
  roomId: 'room-123',
  status: 'in_progress',
  topic: { /* topic object */ },
  participantsCount: 5,
  participants: [ /* participant objects */ ],
  currentSpeakerIndex: 0,
  currentRound: 1,
  speakingTime: 60,
  timeRemaining: 45,
  activeRoomId: 'active-uuid',
  serverTime: '2024-01-15T10:00:00.000Z'
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
  |                               |---participants-update------------->|
  |<---participants-update--------|                                    |
  |                               |                                    |
  |                               |---user-joined-------------------->|
  |<---user-joined----------------|                                    |
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
  |                      |    (all ready)      |
  |<---discussion-start------------------------|
  |                      |<--discussion-start--|
```

### Speaker Turn Flow

```
Client (Speaker)         Server              Other Clients
  |                        |                       |
  |                        |---timer-update------->|
  |<---timer-update--------|                       |
  |                        |                       |
  |                        | (time expires)        |
  |                        |                       |
  |<---next-turn-----------|                       |
  |                        |---next-turn---------->|
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
// Always clean up listeners
useEffect(() => {
  socket.on('participants-update', handleParticipantsUpdate);
  
  return () => {
    socket.off('participants-update', handleParticipantsUpdate);
  };
}, []);
```

### 2. Reconnection Handling

```javascript
socket.on('connect', () => {
  // Rejoin room after reconnection
  if (currentRoom) {
    socket.emit('join-room', currentRoom, { role: userRole });
  }
});
```

### 3. Error Handling

```javascript
socket.on('connect_error', (error) => {
  console.error('Connection failed:', error);
  // Show user-friendly message
  showNotification('Connection failed. Retrying...');
});
```

### 4. Event Debouncing

```javascript
// Avoid rapid-fire events
const debouncedReadyToggle = debounce((isReady) => {
  socket.emit('user-ready', isReady);
}, 300);
```

---

## Testing WebSocket Events

### Manual Testing

```javascript
// Join room
socket.emit('join-room', 'test-room', { role: 'speaker' });

// Mark ready
socket.emit('user-ready', true);

// Advance speaker
socket.emit('next-speaker');

// Leave room
socket.emit('leave-room');
```

### Event Logging

```javascript
// Log all events
const events = [
  'connect', 'disconnect', 'participants-update',
  'discussion-start', 'next-turn', 'timer-update'
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
