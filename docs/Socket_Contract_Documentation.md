# Socket Contract Documentation

## Overview

This document defines the complete socket communication contract between the GupShup Cafe client (React) and server_py (FastAPI + Socket.io). All events use Socket.io for real-time bidirectional communication.

**Server URL**: `http://localhost:3003` (development)  
**Transport**: Socket.io with polling/websocket upgrade  
**Namespace**: Default namespace (`/`)

---

## Connection Events

### Client → Server: Connection Authentication

**Event**: `connection` (automatic)  
**Trigger**: When socket connects to server  
**Auth Data**:
```json
{
  "userId": "string",
  "name": "string", 
  "campusOrLocation": "string|null"
}
```

### Server → Client: Connection Acknowledgment

**Event**: `connection-ack`  
**Trigger**: Immediately after successful connection  
**Payload**:
```json
{
  "sid": "string",
  "connectedAt": "ISO8601 timestamp",
  "serverPid": "number"
}
```

---

## Room Management Events

### Client → Server: Join Room

**Event**: `join-room`  
**Trigger**: User joins a discussion room  
**Parameters**: `(roomId, userData, roomMetadata?)`

**roomId**: `string` - Room identifier  
**userData**:
```json
{
  "userId": "string",
  "name": "string",
  "campusOrLocation": "string|null",
  "anonymousName": "string",
  "role": "speaker|listener|host"
}
```

**roomMetadata** (optional):
```json
{
  "name": "string",
  "topic_category": "string", 
  "cefr_level": "A1|A2|B1|B2|C1|C2"
}
```

### Client → Server: Leave Room

**Event**: `leave-room`  
**Trigger**: User explicitly leaves room  
**Payload**: None

### Server → Client: Participants Update

**Event**: `participants-update`  
**Trigger**: When participants join/leave/change status  
**Payload**: Array of participant objects
```json
[
  {
    "id": "string",
    "socketId": "string", 
    "anonymousName": "string",
    "name": "string",
    "campus": "string|null",
    "location": "string|null",
    "role": "speaker|listener|host",
    "isReady": "boolean",
    "joinedAt": "ISO8601 timestamp"
  }
]
```

### Server → Client: Participant Joined

**Event**: `participant-joined`  
**Trigger**: When a new participant joins  
**Payload**:
```json
{
  "participant": {
    "id": "string",
    "socketId": "string",
    "anonymousName": "string", 
    "role": "speaker|listener|host",
    "isReady": "boolean"
  }
}
```

### Server → Client: Participant Left

**Event**: `participant-left`  
**Trigger**: When a participant leaves  
**Payload**:
```json
{
  "participantId": "string",
  "anonymousName": "string",
  "wasHost": "boolean",
  "newHost": "string|null"
}
```

---

## User Status Events

### Client → Server: User Ready

**Event**: `user-ready`  
**Trigger**: User signals ready to start discussion  
**Payload** (optional):
```json
{
  "isReady": "boolean"
}
```

### Client → Server: Change Role

**Event**: `change-role`  
**Trigger**: User requests role change  
**Payload**:
```json
{
  "userId": "string",
  "role": "speaker|listener",
  "roomId": "string|null"
}
```

### Server → Client: Role Changed

**Event**: `role-changed`  
**Trigger**: When user role is successfully changed  
**Payload**:
```json
{
  "userId": "string", 
  "role": "speaker|listener"
}
```

### Server → Client: Role Change Failed

**Event**: `role-change-failed`  
**Trigger**: When role change is rejected  
**Payload**:
```json
{
  "error": "string"
}
```

---

## Discussion Flow Events

### Client → Server: Start Discussion

**Event**: `start-discussion`  
**Trigger**: Host manually starts discussion  
**Payload**: None (optional data object)

### Server → Client: Discussion Started

**Event**: `discussion-started`  
**Trigger**: When discussion begins  
**Payload**:
```json
{
  "topic": {
    "title": "string",
    "category": "string"
  },
  "firstSpeaker": {
    "id": "string",
    "anonymousName": "string",
    "role": "speaker"
  } | null,
  "duration": "number"
}
```

### Server → Client: Turn Started

**Event**: `turn-started`  
**Trigger**: When a speaker's turn begins  
**Payload**:
```json
{
  "speaker_index": "number",
  "speaker": {
    "id": "string", 
    "anonymousName": "string",
    "role": "speaker"
  },
  "timer": "number"
}
```

### Client → Server: End Turn

**Event**: `end-turn`  
**Trigger**: Speaker ends their turn early  
**Payload**: Optional data object

### Server → Client: Turn Ended

**Event**: `turn-ended`  
**Trigger**: When a speaker's turn ends  
**Payload**:
```json
{
  "speaker": {
    "id": "string",
    "anonymousName": "string"
  }
}
```

### Client → Server: Next Speaker

**Event**: `next-speaker`  
**Trigger**: Manual request to advance to next speaker  
**Payload**: Optional data object

### Server → Client: Round Complete

**Event**: `round-complete`  
**Trigger**: When all speakers in a round have spoken  
**Payload**:
```json
{
  "round": "number",
  "next": "number"
}
```

### Server → Client: Discussion Ended

**Event**: `discussion-ended`  
**Trigger**: When discussion is complete  
**Payload**:
```json
{
  "roomId": "string",
  "roundsCompleted": "number"
}
```

### Server → Client: Speaker Changed

**Event**: `speaker-changed`  
**Trigger**: When the current speaker changes (used by RoundtablePage)  
**Payload**: Speaker object
```json
{
  "id": "string",
  "anonymousName": "string",
  "role": "speaker"
}
```

### Server → Client: Topic Update

**Event**: `topic-update`  
**Trigger**: When discussion topic is updated (used by RoundtablePage)  
**Payload**: Topic object
```json
{
  "title": "string",
  "category": "string"
}
```

---

## Timer Events

### Server → Client: Timer Warning

**Event**: `timer-warning`  
**Trigger**: When speaking time is running low  
**Payload**:
```json
{
  "remaining": "number"
}
```

---

## Host Management Events

### Server → Client: Host Changed

**Event**: `host-changed`  
**Trigger**: When room host changes  
**Payload**:
```json
{
  "newHost": {
    "id": "string",
    "anonymousName": "string",
    "role": "host"
  },
  "previousHost": "string"
}
```

---

## Reconnection Events

### Server → Client: User Reconnected

**Event**: `user-reconnected`  
**Trigger**: When a user reconnects to their previous session  
**Payload**:
```json
{
  "userId": "string",
  "anonymousName": "string", 
  "wasHost": "boolean",
  "preservedState": {
    "isReady": "boolean",
    "role": "speaker|listener|host"
  }
}
```

### Client → Server: User Reconnection Ack

**Event**: `user-reconnection-ack`  
**Trigger**: Client acknowledges successful reconnection  
**Payload**: None

### Server → Client: Participant Reconnected

**Event**: `participant-reconnected`  
**Trigger**: Notifies others when a participant reconnects  
**Payload**:
```json
{
  "participantId": "string",
  "anonymousName": "string",
  "socketId": "string"
}
```

---

## WebRTC Audio Events

### Client → Server: Ready for WebRTC

**Event**: `ready-for-webrtc`  
**Trigger**: Client has audio stream and is ready for peer connections  
**Payload**: None

### Server → Client: Peer Ready

**Event**: `peer-ready`  
**Trigger**: Another participant is ready for WebRTC  
**Payload**:
```json
{
  "socketId": "string"
}
```

### Client → Server: WebRTC Offer

**Event**: `webrtc-offer`  
**Trigger**: Initiating WebRTC connection  
**Payload**:
```json
{
  "to": "string",
  "sdp": "string"
}
```

### Server → Client: WebRTC Offer (Relay)

**Event**: `webrtc-offer`  
**Trigger**: Relayed from another peer  
**Payload**:
```json
{
  "from": "string",
  "sdp": "string"
}
```

### Client → Server: WebRTC Answer

**Event**: `webrtc-answer`  
**Trigger**: Responding to WebRTC offer  
**Payload**:
```json
{
  "to": "string",
  "sdp": "string"
}
```

### Server → Client: WebRTC Answer (Relay)

**Event**: `webrtc-answer`  
**Trigger**: Relayed from another peer  
**Payload**:
```json
{
  "from": "string", 
  "sdp": "string"
}
```

### Client → Server: WebRTC ICE Candidate

**Event**: `webrtc-ice-candidate`  
**Trigger**: Sharing ICE candidates for connection  
**Payload**:
```json
{
  "to": "string",
  "candidate": "RTCIceCandidate object"
}
```

### Server → Client: WebRTC ICE Candidate (Relay)

**Event**: `webrtc-ice-candidate`  
**Trigger**: Relayed from another peer  
**Payload**:
```json
{
  "from": "string",
  "candidate": "RTCIceCandidate object"
}
```

---

## Chat Events

### Client → Server: Message

**Event**: `message`  
**Trigger**: User sends chat message  
**Payload**: `string` - Message text

### Server → Client: Message

**Event**: `message`  
**Trigger**: Broadcast chat message to room  
**Payload**:
```json
{
  "id": "string",
  "userId": "string",
  "anonymousName": "string", 
  "message": "string",
  "timestamp": "ISO8601 timestamp"
}
```

---

## Transcript & AI Events

### Client → Server: Speech Transcript

**Event**: `speech-transcript`  
**Trigger**: Speech-to-text result from client  
**Payload**:
```json
{
  "text": "string",
  "speakerId": "string"
}
```

### Client → Server: Transcript Received

**Event**: `transcript-received`  
**Trigger**: Complete transcript from speaking turn  
**Payload**:
```json
{
  "text": "string",
  "participantId": "string",
  "round": "number",
  "turnOrder": "number", 
  "confidence": "number",
  "startedAt": "ISO8601 timestamp",
  "endedAt": "ISO8601 timestamp",
  "duration": "number"
}
```

### Server → Client: Transcript Saved

**Event**: `transcript-saved`  
**Trigger**: Confirmation that transcript was saved  
**Payload**:
```json
{
  "transcriptId": "string",
  "participantId": "string"
}
```

### Client → Server: Request Facilitator Response

**Event**: `request-facilitator-response`  
**Trigger**: Request AI facilitator to speak  
**Payload**: None

### Server → Client: Facilitator Speaking

**Event**: `facilitator-speaking`  
**Trigger**: AI facilitator provides response  
**Payload**:
```json
{
  "text": "string",
  "timestamp": "ISO8601 timestamp"
}
```

### Client → Server: Get Instant Feedback

**Event**: `get-instant-feedback`  
**Trigger**: Request feedback for participant  
**Payload**:
```json
{
  "participantId": "string"
}
```

### Server → Client: Instant Feedback

**Event**: `instant-feedback`  
**Trigger**: AI-generated feedback response  
**Payload**:
```json
{
  "participantId": "string",
  "feedback": "string",
  "timestamp": "ISO8601 timestamp"
}
```

---

## Broadcast Test Events (Development Only)

### Client → Server: Join Broadcast Test

**Event**: `join-broadcast-test`  
**Trigger**: User joins broadcast test room for WebRTC testing  
**Payload**: None

### Server → Client: Broadcast Test Role

**Event**: `broadcast-test-role`  
**Trigger**: Server assigns role in broadcast test  
**Payload**: `string` - Role ("broadcaster" or "listener")

### Server → Client: Broadcast Test Participants

**Event**: `broadcast-test-participants`  
**Trigger**: Participant list update in broadcast test  
**Payload**: Array of participant objects

### Server → Client: Broadcast Test Reset

**Event**: `broadcast-test-reset`  
**Trigger**: Broadcast test room is reset  
**Payload**: None

### Server → Client: New Listener Joined

**Event**: `new-listener-joined`  
**Trigger**: New listener joins broadcast test  
**Payload**:
```json
{
  "socketId": "string"
}
```

---

## Debug Events

### Client → Server: Debug Ping

**Event**: `debug-ping`  
**Trigger**: Latency/connectivity test  
**Payload**: Any data for echo

### Server → Client: Debug Pong

**Event**: `debug-pong`  
**Trigger**: Response to debug ping  
**Payload**:
```json
{
  "echo": "any",
  "serverTime": "ISO8601 timestamp",
  "sid": "string"
}
```

### Client → Server: Debug Whoami

**Event**: `debug-whoami`  
**Trigger**: Request current session info  
**Payload**: None

### Server → Client: Debug Whoami

**Event**: `debug-whoami`  
**Trigger**: Response with session info  
**Payload**:
```json
{
  "sid": "string",
  "auth": "object|null",
  "serverTime": "ISO8601 timestamp"
}
```

### Client → Server: Debug Room State

**Event**: `debug-room-state`  
**Trigger**: Request current room state  
**Payload**: None

### Server → Client: Debug Room State

**Event**: `debug-room-state`  
**Trigger**: Response with room state  
**Payload**:
```json
{
  "roomId": "string",
  "status": "waiting|in_progress|completed",
  "topic": "object|null",
  "participantsCount": "number",
  "participants": "array",
  "currentSpeakerIndex": "number|null",
  "currentRound": "number|null", 
  "speakingTime": "number|null",
  "timeRemaining": "number|null",
  "activeRoomId": "string|null",
  "serverTime": "ISO8601 timestamp"
}
```

---

## Connection State Events

### Server → Client: Socket.io Built-in Events

**Event**: `connect`  
**Trigger**: Socket connection established  

**Event**: `disconnect`  
**Trigger**: Socket connection lost  
**Payload**: `string` - Disconnect reason

**Event**: `connect_error`  
**Trigger**: Connection failed  
**Payload**: Error object

**Event**: `reconnect`  
**Trigger**: Successfully reconnected  
**Payload**: `number` - Attempt number

**Event**: `reconnect_attempt`  
**Trigger**: Attempting to reconnect  
**Payload**: `number` - Attempt number

**Event**: `reconnect_error`  
**Trigger**: Reconnection failed  
**Payload**: Error object

**Event**: `reconnect_failed`  
**Trigger**: All reconnection attempts failed  

---

## Event Flow Patterns

### Typical Room Join Flow:
1. Client connects → `connection` with auth
2. Server responds → `connection-ack`
3. Client → `join-room` with user data and optional room metadata
4. Server → `participant-joined` to all in room
5. Server → `participants-update` to all in room
6. If reconnecting: Server → `user-reconnected` to user, then `user-reconnection-ack` from client

### Discussion Start Flow:
1. Participants → `user-ready` (sets isReady: true)
2. Server → `participants-update` (with updated ready status)
3. When minimum participants ready → Server automatically → `discussion-started`
4. Server → `participants-update` (after discussion started)
5. Server → `turn-started` for first speaker
6. Timer starts automatically

### WebRTC Connection Flow:
1. Client gets audio stream and participants list → `ready-for-webrtc`
2. Server → `peer-ready` to other participants
3. Speakers initiate → `webrtc-offer` to all peers
4. Peers respond → `webrtc-answer` back to speakers
5. Both exchange → `webrtc-ice-candidate` until P2P connection established

### Turn Management Flow:
1. Server → `turn-started` with speaker, timer duration
2. Optional: Server → `timer-warning` at 10s remaining
3. Client → `end-turn` OR timer expires automatically
4. Server → `turn-ended` with speaker info
5. Server → `turn-started` for next speaker OR `round-complete` if round finished
6. If all rounds complete → Server → `discussion-ended`

### Host Management Flow:
1. First participant to join becomes host automatically
2. If host disconnects → Server preserves host state
3. If host reconnects → Server → `user-reconnected` with wasHost: true
4. If host leaves permanently → Server assigns new host → `host-changed`
5. New host gets full privileges (can start discussion, etc.)

---

## Error Handling

- All socket events should handle connection drops gracefully
- Client implements automatic reconnection with preserved state
- Server preserves host privileges during disconnections
- WebRTC connections are re-established after reconnection
- Failed events do not crash the application

---

## Data Structures

### Participant Object (Standard Format)
Used across multiple events (`participants-update`, `participant-joined`, etc.):
```json
{
  "id": "string",           // User ID (persists across reconnections)
  "socketId": "string",     // Socket ID (changes on reconnection)
  "anonymousName": "string", // Display name for the session
  "name": "string",         // Real user name
  "campus": "string|null",  // Campus location
  "location": "string|null", // Geographic location  
  "role": "speaker|listener|host", // Current role in discussion
  "isReady": "boolean",     // Ready to start discussion
  "joinedAt": "ISO8601 timestamp" // When they joined the room
}
```

### Topic Object (Discussion Topics)
```json
{
  "title": "string",        // Topic title/question
  "category": "string"      // Category (Technology, Current Events, etc.)
}
```

### Room Metadata (Optional on join-room)
```json
{
  "name": "string",         // Human-readable room name
  "topic_category": "string", // Topic category preference
  "cefr_level": "A1|A2|B1|B2|C1|C2" // Language proficiency level
}
```

---

## Implementation Notes

### Connection & Authentication
- All timestamps use ISO8601 format
- Socket IDs are unique per connection and change on reconnection
- User IDs persist across reconnections for state preservation
- Authentication data is passed during initial connection handshake

### Room Management
- Room IDs are lobby identifiers, separate from database room IDs
- Active room IDs are generated for database tracking when discussions start
- Host privileges are automatically assigned to first participant
- Host state is preserved during temporary disconnections

### WebRTC & Audio
- WebRTC events are relayed through server but audio flows peer-to-peer
- Only speakers initiate WebRTC connections (send offers)
- Listeners wait to receive offers from speakers
- Audio streams are optimized for voice (Opus codec, echo cancellation)

### Discussion Flow
- Timer events are server-driven and automatic
- Minimum participants required to start (configurable, default: 1)
- Speaking turns advance automatically on timer expiry or manual end-turn
- Discussion progresses through multiple rounds until completion

### Error Handling & Reconnection
- Client implements automatic reconnection with exponential backoff
- Server preserves participant state during brief disconnections
- WebRTC connections are re-established after socket reconnection
- Failed events should not crash the application

### Development & Testing
- Debug events are for development/troubleshooting only
- Broadcast test events are used for WebRTC testing in development
- Connection acknowledgment helps with client-side connection validation