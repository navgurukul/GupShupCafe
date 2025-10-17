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
socket.emit('join-room', roomId, { role: 'speaker' });
```

**Parameters:**
- `roomId` (string) - Unique room identifier
- `options` (object) - Join options
  - `role` (string) - User role: 'speaker' or 'listener'

**Server Response:**
- Emits `participants-update` to all room members
- Emits `user-joined` notification to room

**Example:**
```javascript
const roomId = 'room-abc123';
const options = { role: 'speaker' };

socket.emit('join-room', roomId, options);

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
socket.emit('user-ready', true);
```

**Parameters:**
- `isReady` (boolean) - Ready state

**Server Response:**
- Emits `participants-update` with updated ready states
- Automatically starts discussion when all users are ready

**Flow Diagram:**
```
User clicks "Ready" 
    → emit('user-ready', true)
    → Server updates participant state
    → Server emits 'participants-update'
    → Check if all ready
    → If yes: emit 'discussion-start'
```

**Example:**
```javascript
// Mark as ready
socket.emit('user-ready', true);

// Listen for discussion start
socket.on('discussion-start', (data) => {
  console.log('Discussion starting!', data);
});
```

---

#### `next-speaker`

Request to advance to the next speaker.

**Emit:**
```javascript
socket.emit('next-speaker');
```

**Server Response:**
- Emits `next-turn` with new speaker information
- Updates timer and speaker index

**Example:**
```javascript
// Advance to next speaker
socket.emit('next-speaker');

// Listen for turn change
socket.on('next-turn', (turnData) => {
  console.log('Next speaker:', turnData.currentSpeaker);
  console.log('Time:', turnData.timeRemaining);
});
```

---

#### `mute-toggle`

Toggle microphone mute state.

**Emit:**
```javascript
socket.emit('mute-toggle', { userId: 'user-123', isMuted: true });
```

**Parameters:**
- `userId` (string) - User ID
- `isMuted` (boolean) - Mute state

**Server Response:**
- Broadcasts mute state to all room participants

**Example:**
```javascript
const handleMuteToggle = (isMuted) => {
  socket.emit('mute-toggle', {
    userId: user.id,
    isMuted: isMuted
  });
};
```

---

### WebRTC Signaling

#### `webrtc-offer`

Send WebRTC connection offer to peer.

**Emit:**
```javascript
socket.emit('webrtc-offer', {
  to: 'peer-socket-id',
  offer: rtcOffer
});
```

**Parameters:**
- `to` (string) - Target peer socket ID
- `offer` (RTCSessionDescriptionInit) - WebRTC offer

**Server Response:**
- Forwards offer to target peer

**Example:**
```javascript
const peerConnection = new RTCPeerConnection(config);

peerConnection.createOffer()
  .then(offer => peerConnection.setLocalDescription(offer))
  .then(() => {
    socket.emit('webrtc-offer', {
      to: targetSocketId,
      offer: peerConnection.localDescription
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
  answer: rtcAnswer
});
```

**Parameters:**
- `to` (string) - Target peer socket ID
- `answer` (RTCSessionDescriptionInit) - WebRTC answer

**Server Response:**
- Forwards answer to target peer

**Example:**
```javascript
socket.on('webrtc-offer', async ({ from, offer }) => {
  await peerConnection.setRemoteDescription(offer);
  const answer = await peerConnection.createAnswer();
  await peerConnection.setLocalDescription(answer);
  
  socket.emit('webrtc-answer', {
    to: from,
    answer: answer
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
- Forwards candidate to target peer

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
    campus: 'Delhi Campus',
    location: 'India',
    isReady: true,
    role: 'speaker'
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

#### `user-joined`

Notification when a user joins the room.

**Receive:**
```javascript
socket.on('user-joined', (user) => {
  console.log(`${user.anonymousName} joined!`);
});
```

**Payload:**
```javascript
{
  id: 'user-123',
  anonymousName: 'Wise Owl',
  campus: 'Delhi Campus',
  location: 'India'
}
```

---

#### `user-left`

Notification when a user leaves the room.

**Receive:**
```javascript
socket.on('user-left', (user) => {
  console.log(`${user.anonymousName} left!`);
});
```

**Payload:**
```javascript
{
  id: 'user-123',
  anonymousName: 'Wise Owl'
}
```

---

### Discussion Events

#### `discussion-start`

Emitted when the discussion begins.

**Receive:**
```javascript
socket.on('discussion-start', (data) => {
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
socket.on('discussion-start', (data) => {
  setDiscussionActive(true);
  setTopic(data.topic);
  setParticipants(data.participants);
  setCurrentSpeaker(data.currentSpeaker);
  setSpeakingTime(data.speakingTime);
  
  // Navigate to roundtable
  navigate('/roundtable');
});
```

---

#### `discussion-end`

Emitted when the discussion ends.

**Receive:**
```javascript
socket.on('discussion-end', (data) => {
  console.log('Discussion ended!', data);
});
```

**Payload:**
```javascript
{
  reason: 'completed' | 'insufficient_participants',
  stats: {
    duration: 1800,
    roundsCompleted: 3,
    participantCount: 5
  }
}
```

---

#### `next-turn`

Emitted when it's the next speaker's turn.

**Receive:**
```javascript
socket.on('next-turn', (turnData) => {
  console.log('Next turn:', turnData);
});
```

**Payload:**
```javascript
{
  currentSpeaker: {
    id: 'user-456',
    anonymousName: 'Clever Fox',
    socketId: 'socket-xyz'
  },
  speakerIndex: 1,
  round: 1,
  timeRemaining: 60,
  totalRounds: 3
}
```

**Example:**
```javascript
socket.on('next-turn', (turnData) => {
  setCurrentSpeaker(turnData.currentSpeaker);
  setTimeRemaining(turnData.timeRemaining);
  setCurrentRound(turnData.round);
  
  // Update audio state
  const isMyTurn = turnData.currentSpeaker.id === user.id;
  updateAudioState(isMyTurn ? 'speaker' : 'listener');
});
```

---

#### `timer-update`

Periodic updates of speaking time remaining.

**Receive:**
```javascript
socket.on('timer-update', (data) => {
  console.log('Time remaining:', data.timeRemaining);
});
```

**Payload:**
```javascript
{
  timeRemaining: 45,
  speakerId: 'user-123'
}
```

**Example:**
```javascript
socket.on('timer-update', (data) => {
  setTimeRemaining(data.timeRemaining);
  
  // Visual warning when time is low
  if (data.timeRemaining <= 10) {
    showTimeWarning();
  }
});
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
