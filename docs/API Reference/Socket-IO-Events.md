# Socket.IO Events Reference

## Overview

GupShup Cafe uses Socket.IO for real-time bidirectional communication between the client and server. This document describes all Socket.IO events.

**Connection URL**: `ws://localhost:3003` (development) or your deployed backend WebSocket URL

---

## Client → Server Events

### Authentication & Room Management

#### `join-room`

Join a discussion room. User automatically leaves any previous room.

**Payload**:
```javascript
socket.emit('join-room', roomId, userData)
```

**Parameters**:
- `roomId` (string): Room identifier (e.g., "general")
- `userData` (object): User information
  ```javascript
  {
    userId: "user-123",
    name: "John Doe",
    campus: "NavGurukul Bangalore",
    location: "Bangalore",
    anonymousName: "Brave Lion",
    role: "listener" // or "speaker"
  }
  ```

**Response Events**: 
- `participants-update`: Updated list of participants
- `discussion-started`: If discussion is already active

---

#### `leave-room`

Leave the current discussion room.

**Payload**:
```javascript
socket.emit('leave-room')
```

**Response Events**:
- `participants-update`: Updated participant list for remaining users
- `user-disconnected`: Notification to other participants

---

### Discussion Control

#### `user-ready`

Signal that the user is ready to start the discussion.

**Payload**:
```javascript
socket.emit('user-ready')
```

**Response Events**:
- `participants-update`: Updated participant list with ready status
- `discussion-started`: If minimum participants are ready

---

#### `next-speaker`

Request to advance to the next speaker in the discussion.

**Payload**:
```javascript
socket.emit('next-speaker')
```

**Response Events**:
- `speaker-changed`: Next speaker information
- `timer-update`: New timer value

---

#### `start-discussion-manual`

Manually trigger discussion start (for testing purposes).

**Payload**:
```javascript
socket.emit('start-discussion-manual')
```

**Response Events**:
- `discussion-started`: If conditions are met

---

### Role Management

#### `role-change`

Request to change user's role between speaker and listener.

**Payload**:
```javascript
socket.emit('role-change', {
  userId: "user-123",
  newRole: "speaker", // or "listener"
  roomId: "general" // optional
})
```

**Response Events**:
- `role-changed`: Role change successful (to all participants)
- `role-change-success`: Confirmation to requester
- `role-change-error`: If role change fails

---

### WebRTC Signaling

#### `ready-for-webrtc`

Signal that the client is ready for WebRTC connections.

**Payload**:
```javascript
socket.emit('ready-for-webrtc')
```

**Response Events**:
- `participants-update`: Full participant list to trigger peer connections

---

#### `webrtc-offer`

Send WebRTC offer to a peer.

**Payload**:
```javascript
socket.emit('webrtc-offer', {
  to: "socket-id-123",
  sdp: offerSdp
})
```

**Relayed to**: Target peer as `webrtc-offer` event

---

#### `webrtc-answer`

Send WebRTC answer to a peer.

**Payload**:
```javascript
socket.emit('webrtc-answer', {
  to: "socket-id-123",
  sdp: answerSdp
})
```

**Relayed to**: Target peer as `webrtc-answer` event

---

#### `webrtc-ice-candidate`

Send ICE candidate to a peer.

**Payload**:
```javascript
socket.emit('webrtc-ice-candidate', {
  to: "socket-id-123",
  candidate: iceCandidate
})
```

**Relayed to**: Target peer as `webrtc-ice-candidate` event

---

### Messaging

#### `message`

Send a chat message to the room (future enhancement).

**Payload**:
```javascript
socket.emit('message', "Hello everyone!")
```

**Response Events**:
- `message`: Broadcast to all other participants in room

---

## Server → Client Events

### Room & Participant Updates

#### `participants-update`

Updated list of participants in the room.

**Payload**:
```javascript
[
  {
    id: "user-123",
    anonymousName: "Brave Lion",
    isReady: true,
    joinedAt: "2025-10-11T09:00:00.000Z",
    socketId: "socket-abc-123",
    role: "speaker"
  }
]
```

**Triggered by**:
- User joins room
- User leaves room
- User signals ready
- Role change

---

#### `user-disconnected`

Notification that a user has disconnected from the room.

**Payload**:
```javascript
{
  userId: "user-123",
  participants: [...] // Updated participant list
}
```

**Triggered by**:
- User disconnects
- User leaves room

---

### Discussion Events

#### `discussion-started`

Discussion has started with a topic and first speaker.

**Payload**:
```javascript
{
  topic: {
    title: "The Future of Education",
    description: "How will technology reshape learning in the next decade?",
    category: "Education",
    questions: [...]
  },
  firstSpeaker: {
    id: "user-123",
    anonymousName: "Brave Lion",
    role: "speaker"
  },
  duration: 60, // seconds
  timeRemaining: 60,
  currentSpeaker: {...},
  round: 1
}
```

**Triggered by**:
- Minimum participants ready
- User joins ongoing discussion (sync state)

---

#### `speaker-changed`

The current speaker has changed.

**Payload**:
```javascript
{
  speaker: {
    id: "user-456",
    anonymousName: "Wise Owl",
    role: "speaker"
  },
  timeRemaining: 60,
  round: 1
}
```

**Triggered by**:
- Timer expires
- Manual next speaker request

---

#### `timer-update`

Speaking timer update (emitted every second).

**Payload**:
```javascript
45 // seconds remaining
```

**Triggered by**:
- Timer tick (every 1 second)

---

#### `discussion-ended`

Discussion has ended after completing all rounds.

**Payload**: No payload

**Triggered by**:
- 3 rounds completed
- Too few participants remaining

---

### Role Management

#### `role-changed`

A user's role has changed (broadcast to all participants).

**Payload**:
```javascript
{
  userId: "user-123",
  newRole: "speaker",
  roleStats: {
    totalParticipants: 4,
    speakers: 2,
    listeners: 2,
    speakerList: [...],
    listenerList: [...]
  },
  participants: [...] // Full participant list
}
```

**Triggered by**:
- Successful role change request

---

#### `role-change-success`

Confirmation that role change was successful (to requester only).

**Payload**:
```javascript
{
  newRole: "speaker"
}
```

---

#### `role-change-error`

Role change request failed.

**Payload**:
```javascript
{
  message: "Speaker limit reached"
}
```

**Common error messages**:
- "Not in a room"
- "Invalid role"
- "Speaker limit reached"
- "Failed to change role"

---

### WebRTC Signaling (Relayed)

#### `webrtc-offer`

WebRTC offer from a peer.

**Payload**:
```javascript
{
  from: "socket-id-456",
  sdp: offerSdp
}
```

---

#### `webrtc-answer`

WebRTC answer from a peer.

**Payload**:
```javascript
{
  from: "socket-id-456",
  sdp: answerSdp
}
```

---

#### `webrtc-ice-candidate`

ICE candidate from a peer.

**Payload**:
```javascript
{
  from: "socket-id-456",
  candidate: iceCandidate
}
```

---

### Error Events

#### `error`

General error notification.

**Payload**:
```javascript
"Error message describing the issue"
```

**Triggered by**:
- Failed to join room
- Failed to update ready status
- Other server-side errors

---

## Connection Lifecycle

### Connection Establishment

```javascript
// Client-side connection with authentication
const socket = io('http://localhost:3003', {
  auth: {
    userId: "user-123",
    name: "John Doe",
    campus: "NavGurukul Bangalore",
    location: "Bangalore",
    anonymousName: "Brave Lion"
  }
})
```

### Connection Events

```javascript
socket.on('connect', () => {
  console.log('Connected:', socket.id)
})

socket.on('disconnect', () => {
  console.log('Disconnected')
})

socket.on('connect_error', (error) => {
  console.error('Connection error:', error)
})
```

---

## Event Flow Diagrams

### Joining a Room

```
Client                          Server                          Other Clients
  |                              |                                    |
  |--join-room(roomId, data)---->|                                    |
  |                              |----participants-update------------>|
  |<---participants-update-------|                                    |
  |                              |                                    |
```

### Starting a Discussion

```
Client 1          Client 2          Server
  |                 |                 |
  |--user-ready---->|                 |
  |                 |--user-ready---->|
  |                 |                 |
  |<-------------discussion-started---|
  |                 |<-discussion-started
  |<-------------timer-update---------|
  |                 |<--timer-update--|
```

### WebRTC Peer Connection Setup

```
Peer A                          Server                          Peer B
  |                              |                                |
  |--webrtc-offer(to:B)--------->|                                |
  |                              |----webrtc-offer(from:A)------->|
  |                              |                                |
  |                              |<---webrtc-answer(to:A)---------|
  |<---webrtc-answer(from:B)-----|                                |
  |                              |                                |
  |--webrtc-ice-candidate------->|----webrtc-ice-candidate------->|
```

---

## Best Practices

1. **Always handle disconnection**: Implement reconnection logic with exponential backoff
2. **Validate events**: Check payload structure before processing
3. **Handle errors gracefully**: Listen for error events and display user-friendly messages
4. **Clean up listeners**: Remove event listeners when components unmount
5. **Use acknowledgments**: For critical operations, implement acknowledgment callbacks

---

## Testing Events

Use the Socket.IO client tools or browser console:

```javascript
// In browser console
const socket = io('http://localhost:3003', {
  auth: { userId: 'test', anonymousName: 'Test User' }
})

socket.emit('join-room', 'test-room', {
  userId: 'test',
  anonymousName: 'Test User'
})

socket.on('participants-update', (participants) => {
  console.log('Participants:', participants)
})
```
