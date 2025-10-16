# Frontend-Backend Integration Testing Guide

## Overview
This document provides a comprehensive guide for testing the frontend-backend integration of GupShup Cafe, ensuring that socket events, WebRTC signaling, and turn-based discussion flow work correctly according to the UML diagrams.

## Prerequisites
1. Backend server running: `cd server_py && python main.py`
2. Frontend development server running: `cd client && npm run dev`
3. At least 2 browser windows/tabs for multi-user testing
4. Browser console open for logging

## Test Scenarios

### 1. User Connection & Room Join

**Expected Flow (per `05-sequence-user-join-discussion.puml`)**:
1. User opens app → connects to Socket.io
2. User joins room with anonymous name
3. Backend emits `participant-joined` to all in room
4. Backend emits `participants-update` with full list
5. Frontend updates participant list

**Manual Testing Steps**:
```
1. Open browser console
2. Navigate to lobby page
3. Observe socket connection logs: "[Socket] Connected to server: <socket_id>"
4. Check participants list updates
5. Open second browser window
6. Join same room with different name
7. Verify both windows show 2 participants
```

**Expected Console Logs**:
```
[Socket] Connected to server: abc123
[Lobby][Debug] Calling joinRoom with roomId: general, role: speaker
[Backend] 📥 Blue Panda joining room: general
[Backend] Emitted participants-update
[Lobby][Debug] Received participants-update: [{id, anonymousName, role, isReady}]
```

**Backend Logs to Check**:
```
[Backend] Socket connected: abc123
[Backend] 📥 Blue Panda joining room: general
➕ Added Blue Panda to room general. Total: 1
[Backend] Emitted participants-update
```

---

### 2. Ready Check & Discussion Start

**Expected Flow (per `14-communication-diagram-events.puml`)**:
1. User clicks "I'm Ready"
2. Frontend emits `user-ready` event
3. Backend updates participant.is_ready = true
4. Backend emits `participants-update` to room
5. When min participants ready, backend starts discussion
6. Backend emits `discussion-started` with topic and first speaker
7. Backend emits `turn-started` with timer

**Manual Testing Steps**:
```
1. Both users click "I'm Ready" button
2. Verify "Ready" indicator appears on participant cards
3. Watch for "Discussion starting!" message
4. Verify redirect to /roundtable page
5. Verify topic is displayed
6. Verify first speaker is highlighted
7. Verify timer starts counting down from 60s
```

**Expected Console Logs (User 1 - First Speaker)**:
```
[Lobby][Debug] Signaling ready
[Backend] Starting discussion in room general
[Lobby][Debug] Received discussion-started event
[Roundtable] Discussion started: {topic, firstSpeaker, duration: 60}
[Roundtable] Current user is first speaker - enabling speaking
[Audio] Enabling speaking mode
```

**Expected Console Logs (User 2 - Listener)**:
```
[Roundtable] Discussion started: {topic, firstSpeaker, duration: 60}
[Roundtable] Current user is not first speaker
```

**Backend Logs to Check**:
```
[Backend] Starting discussion in room general
[Backend] Discussion started with topic: <topic_title>
[TimerManager] Started timer for room general: 60 seconds
```

---

### 3. Timer Warning & Auto Turn Progression

**Expected Flow (per timer management)**:
1. Timer counts down from 60 to 0
2. At 10 seconds remaining, backend emits `timer-warning`
3. Frontend shows warning notification
4. At 0 seconds, backend emits `turn-ended` and `turn-started` for next speaker
5. Timer restarts for next speaker

**Manual Testing Steps**:
```
1. Wait for timer to reach 10 seconds (or set DEFAULT_SPEAKING_TIME=15 in .env for faster testing)
2. Verify yellow warning notification appears at 10s
3. Wait for timer to reach 0
4. Verify turn automatically advances to next speaker
5. Verify new timer starts
```

**Expected Console Logs (at 10s)**:
```
[Roundtable] Timer warning: {remaining: 10}
[Roundtable] System message: "10 seconds remaining!"
```

**Expected Console Logs (at 0s)**:
```
[Roundtable] Turn ended: {speaker: {...}}
[Roundtable] Turn started: {speaker_index: 1, speaker: {...}, timer: 60}
[Audio] Disabling speaking mode (for previous speaker)
[Audio] Enabling speaking mode (for new speaker)
```

**Backend Logs to Check**:
```
[Backend] Timer warning sent for room general: 10s remaining
[Backend] Timer completed for room general, advancing turn
[Backend] Next speaker: Red Fox
[TimerManager] Started timer for room general: 60 seconds
```

---

### 4. Manual Turn Ending

**Expected Flow**:
1. User clicks "Next Speaker" or "End Turn" button
2. Frontend emits `end-turn` or `next-speaker` event
3. Backend cancels current timer
4. Backend advances to next speaker
5. Backend emits `turn-ended` and `turn-started`
6. Backend starts new timer

**Manual Testing Steps**:
```
1. During a turn, click "Next Speaker" button (if available in UI)
2. OR emit manually: socket.emit('end-turn', {})
3. Verify turn immediately advances to next speaker
4. Verify new timer starts
```

**Expected Console Logs**:
```
[Roundtable] Requesting next speaker
[Socket] Emitting: end-turn
[Roundtable] Turn ended: {speaker: {...}}
[Roundtable] Turn started: {speaker_index: 1, speaker: {...}, timer: 60}
```

**Backend Logs to Check**:
```
[TimerManager] Cancelled timer for room general
[Backend] Next speaker: Red Fox
[TimerManager] Started timer for room general: 60 seconds
```

---

### 5. Round Progression

**Expected Flow (per `Room.advance_turn()` logic)**:
1. After last speaker in round finishes, current_round increments
2. Backend emits `round-complete` event
3. Speaker index resets to 0
4. Backend emits `turn-started` for first speaker of new round

**Manual Testing Steps**:
```
1. Wait for all participants to complete their turns (or speed up with short timer)
2. After last speaker, verify "Round X complete!" notification
3. Verify discussion continues with first speaker again
4. Check round counter increases (Round 2, Round 3)
```

**Expected Console Logs**:
```
[Roundtable] Round complete: {round: 1, next: 2}
[Roundtable] System message: "Round 1 complete! Starting round 2..."
[Roundtable] Turn started: {speaker_index: 0, speaker: {...}, timer: 60}
```

**Backend Logs to Check**:
```
[Backend] Round complete, moving to round 2
[Backend] Next speaker: Blue Panda (index 0)
```

---

### 6. Discussion End (After 3 Rounds)

**Expected Flow (per `Room.advance_turn()` logic)**:
1. After last speaker of round 3 finishes
2. Room.status changes to COMPLETED
3. Backend emits `discussion-ended` event
4. Frontend shows completion modal
5. Session saved to database

**Manual Testing Steps**:
```
1. Complete all 3 rounds (adjust max_rounds in Room if needed for testing)
2. Verify "Discussion Completed!" modal appears
3. Verify options to join new discussion or logout
4. Check database for saved session
```

**Expected Console Logs**:
```
[Roundtable] Discussion ended: {sessionId: "...", roundsCompleted: 3}
[Roundtable] Setting discussionEnded to true
[Audio] Disabling speaking mode
```

**Backend Logs to Check**:
```
[Backend] Discussion completed in room general
[Backend] Updated session <session_id> with endedAt
[Backend] Emitting discussion-ended event
```

---

### 7. WebRTC Signaling (Audio)

**Expected Flow (per `06-sequence-webrtc-audio.puml`)**:
1. Participants emit `ready-for-webrtc` when audio is initialized
2. Backend relays `webrtc-offer` from peer A to peer B
3. Backend relays `webrtc-answer` from peer B to peer A
4. Backend relays `webrtc-ice-candidate` between peers
5. WebRTC connections established peer-to-peer

**Manual Testing Steps**:
```
1. Open 2 browser windows
2. Join same room in both
3. Open browser console in both
4. Check for WebRTC logs: "Creating peer connection for: <socket_id>"
5. Verify offer/answer/ICE candidate exchanges
6. Verify audio element appears in DOM: <audio data-peer="...">
7. Try speaking into microphone (if permitted)
```

**Expected Console Logs (Peer A - Initiator)**:
```
[Audio] Creating peer connection for: def456
[Audio] Creating offer for peer: def456
[Socket] Emitting: webrtc-offer to def456
[Audio] Received answer from peer: def456
```

**Expected Console Logs (Peer B - Receiver)**:
```
[Audio] Received offer from peer: abc123
[Audio] Creating answer for peer: abc123
[Socket] Emitting: webrtc-answer to abc123
[Audio] ICE candidate received from peer: abc123
```

**Backend Logs to Check**:
```
[Backend] Relaying WebRTC offer from abc123 to def456
[Backend] Relaying WebRTC answer from def456 to abc123
[Backend] Relaying ICE candidate from abc123 to def456
```

---

### 8. Speech Transcription

**Expected Flow (per `07-sequence-llm-agent-interaction.puml`)**:
1. User speaks into microphone
2. Web Speech API transcribes speech
3. Frontend emits `speech-transcript` event with text
4. Backend saves transcript to database
5. (Future) Backend triggers LLM analysis for feedback

**Manual Testing Steps**:
```
1. Enable microphone permission
2. Ensure it's your turn to speak
3. Speak into microphone (requires Web Speech API support)
4. Check console for transcript logs
5. Check database for saved transcripts
```

**Expected Console Logs**:
```
[SpeechToText] Starting speech recognition
[SpeechToText] Transcript: "Hello everyone, I think AI is fascinating"
[Socket] Emitting: speech-transcript
```

**Backend Logs to Check**:
```
[Backend] Saved transcript for session <session_id>: Hello everyone, I think AI...
```

**Database Check**:
```sql
SELECT * FROM transcripts WHERE session_id = '<session_id>';
```

---

### 9. User Disconnection

**Expected Flow**:
1. User closes browser or navigates away
2. Socket.io disconnect event triggers
3. Backend removes participant from room
4. Backend emits `participant-left` event
5. Backend emits `participants-update` with updated list
6. If room is empty, backend cleans up room

**Manual Testing Steps**:
```
1. Open 2 browser windows with different users
2. Close one browser window
3. Verify other window shows participant left notification
4. Verify participant count decreases
```

**Expected Console Logs (Remaining User)**:
```
[Roundtable] Participant left: {participantId: "...", anonymousName: "Blue Panda"}
[Roundtable] Participants updated: [remaining participants]
```

**Backend Logs to Check**:
```
👋 User disconnected: abc123
[Backend] Blue Panda disconnected from room general
➖ Removed user abc123 from room general. Remaining: 1
[Backend] Emitted participants-update
```

---

## Performance & Reliability Tests

### Test 10: Reconnection Handling
1. Disconnect/reconnect network during discussion
2. Verify socket reconnects automatically
3. Verify room state syncs correctly
4. Verify ongoing discussion continues

### Test 11: Concurrent Users (Stress Test)
1. Open 6 browser windows (max participants)
2. Join same room in all windows
3. All users mark ready
4. Verify discussion flows through all 6 participants
5. Verify timers work correctly for all

### Test 12: Error Handling
1. Try joining non-existent room
2. Try emitting events when not in room
3. Try joining room when disconnected
4. Verify graceful error messages

---

## Automated Testing (Future)

### Socket.io Integration Tests
```javascript
// Example test structure
describe('Discussion Flow', () => {
  it('should start discussion when all participants are ready', async () => {
    const client1 = io('http://localhost:3003');
    const client2 = io('http://localhost:3003');
    
    // Join room
    client1.emit('join-room', 'test-room', userData1);
    client2.emit('join-room', 'test-room', userData2);
    
    // Mark ready
    client1.emit('user-ready', {userId: 'user1', isReady: true});
    client2.emit('user-ready', {userId: 'user2', isReady: true});
    
    // Wait for discussion-started event
    await new Promise(resolve => {
      client1.on('discussion-started', (data) => {
        expect(data).toHaveProperty('topic');
        expect(data).toHaveProperty('firstSpeaker');
        resolve();
      });
    });
  });
});
```

---

## Common Issues & Troubleshooting

### Issue 1: Socket doesn't connect
- **Check**: Backend server running on port 3003?
- **Check**: VITE_SOCKET_URL set correctly in client/.env?
- **Check**: CORS configured properly in backend?
- **Fix**: Verify `ALLOWED_ORIGINS` in server_py/.env

### Issue 2: Participants not updating
- **Check**: Console for "participants-update" events
- **Check**: Backend logs for "Emitted participants-update"
- **Fix**: Verify socket connection and room join logic

### Issue 3: Discussion doesn't start
- **Check**: MIN_PARTICIPANTS setting (default 1)
- **Check**: Both users marked ready?
- **Check**: Backend logs for "Starting discussion"
- **Fix**: Verify ready check logic in backend

### Issue 4: Timer doesn't advance
- **Check**: Backend logs for "Timer completed"
- **Check**: TimerManager creating tasks properly
- **Fix**: Verify asyncio loop is running

### Issue 5: WebRTC not connecting
- **Check**: Browser console for WebRTC errors
- **Check**: Microphone permission granted?
- **Check**: STUN server accessible?
- **Fix**: Verify AudioContext initialization

---

## Success Criteria

✅ All socket events emit and are received correctly  
✅ Turn-based discussion flows through all participants  
✅ Timer management works (countdown, warning, auto-advance)  
✅ Round progression works correctly (3 rounds)  
✅ Discussion ends after 3 rounds  
✅ WebRTC signaling relays properly  
✅ Speech transcripts save to database  
✅ Disconnection cleanup works  
✅ Multiple concurrent users supported  
✅ No memory leaks or stale timers

---

## Next Integration Steps

1. **LLM Integration**: Implement `english-feedback` and `session-summary` events
2. **End-to-End Tests**: Create automated Playwright tests
3. **Load Testing**: Test with 100+ concurrent rooms
4. **Analytics**: Verify all events logged to database
5. **Error Boundaries**: Add comprehensive error handling

---

**Last Updated**: 2025-10-16 17:40 UTC  
**Status**: Core integration complete, ready for manual testing  
**Blocked By**: None  
**Blockers For**: LLM feedback integration, E2E tests
