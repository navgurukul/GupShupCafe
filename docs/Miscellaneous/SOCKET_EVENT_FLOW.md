# Socket.io Event Flow Summary

## Connection & Room Management

```
Client                          Backend                         Room Manager
  |                               |                                  |
  |--connect()------------------>|                                  |
  |<--connected(socket_id)--------|                                  |
  |                               |                                  |
  |--join-room(roomId, userData)->|                                  |
  |                               |--add_user_to_room()------------>|
  |                               |<--room with participants---------|
  |<--participant-joined()--------|                                  |
  |<--participants-update()-------|                                  |
```

## Ready Check & Discussion Start

```
Client A                        Backend                         Timer Manager
  |                               |                                  |
  |--user-ready()---------------->|                                  |
  |                               |--check_all_ready()------------->|
  |                               |  (min_participants met)         |
  |                               |                                  |
  |<--discussion-started()--------|                                  |
  |<--turn-started(speaker_0)-----|                                  |
  |                               |--start_timer(60s)-------------->|
```

## Turn Progression (Automatic)

```
Timer Manager                   Backend                         Client A (Speaker)
  |                               |                                  |
  | (59s...)                      |                                  |
  | (10s remaining)               |                                  |
  |--on_warning()---------------->|                                  |
  |                               |--timer-warning()--------------->|
  |                               |                                  |
  | (0s - timer complete)         |                                  |
  |--on_complete()--------------->|                                  |
  |                               |--turn-ended()------------------>|
  |                               |--advance_turn()              Room Manager
  |                               |<--next_speaker--------------------|
  |                               |--turn-started(speaker_1)------->|
  |<--start_timer(60s)------------|                                  |
```

## Turn Progression (Manual)

```
Client A (Speaker)              Backend                         Timer Manager
  |                               |                                  |
  |--end-turn()------------------>|                                  |
  |                               |--cancel_timer()---------------->|
  |                               |--advance_turn()              Room Manager
  |                               |<--next_speaker--------------------|
  |<--turn-ended()----------------|                                  |
  |<--turn-started(speaker_1)-----|                                  |
  |                               |--start_timer(60s)-------------->|
```

## Round Completion

```
Timer Manager                   Backend                         All Clients
  |                               |                                  |
  |--on_complete()--------------->|                                  |
  | (last speaker of round)       |                                  |
  |                               |--advance_turn()              Room Manager
  |                               |  (speaker_index wraps to 0)     |
  |                               |  (current_round++)              |
  |                               |                                  |
  |                               |--round-complete()-------------->|
  |                               |--turn-started(speaker_0)------->|
  |<--start_timer(60s)------------|                                  |
```

## Discussion End

```
Timer Manager                   Backend                         All Clients
  |                               |                                  |
  |--on_complete()--------------->|                                  |
  | (last speaker of round 3)     |                                  |
  |                               |--advance_turn()              Room Manager
  |                               |  (current_round > max_rounds)   |
  |                               |  (status = COMPLETED)           |
  |                               |                                  |
  |                               |--update_session()            Database
  |                               |  (save endedAt, roundsCompleted)|
  |                               |                                  |
  |                               |--discussion-ended()------------>|
  |                               |  (sessionId, roundsCompleted)   |
```

## WebRTC Signaling

```
Client A                        Backend                         Client B
  |                               |                                  |
  |--ready-for-webrtc()---------->|                                  |
  |                               |--peer-ready()------------------>|
  |                               |                                  |
  |--webrtc-offer(to: B, offer)-->|                                  |
  |                               |--webrtc-offer(from: A)--------->|
  |                               |                                  |
  |                               |<--webrtc-answer(to: A, answer)---|
  |<--webrtc-answer(from: B)------|                                  |
  |                               |                                  |
  |--webrtc-ice-candidate()------>|                                  |
  |                               |--webrtc-ice-candidate()-------->|
  |                               |                                  |
  | (P2P audio connection established)                              |
```

## Speech Transcription

```
Client (Speaker)                Backend                         Database
  |                               |                                  |
  | (Web Speech API)              |                                  |
  |--speech-transcript()--------->|                                  |
  |  (text, speakerId)            |                                  |
  |                               |--save_transcript()------------->|
  |                               |  (sessionId, participantId,     |
  |                               |   text, timestamp)              |
  |                               |                                  |
  |                               | (Future: trigger LLM analysis)  |
```

## Disconnection

```
Client A                        Backend                         Room Manager
  |                               |                                  |
  | (closes browser)              |                                  |
  |--disconnect()---------------->|                                  |
  |                               |--remove_participant()---------->|
  |                               |<--room updated-------------------|
  |                               |                                  |
  |                               |--participant-left()------------>| (to others)
  |                               |--participants-update()--------->| (to others)
  |                               |                                  |
  |                               |--cleanup_room()              (if empty)
```

## Event Summary Table

| Event | Direction | Emitted By | Received By | Payload | Purpose |
|-------|-----------|------------|-------------|---------|---------|
| `connect` | → | Client | Backend | auth data | Establish socket connection |
| `connected` | ← | Backend | Client | socket_id | Confirm connection |
| `join-room` | → | Client | Backend | roomId, userData | Join a discussion room |
| `participant-joined` | ← | Backend | All in room | participant | Notify of new participant |
| `participants-update` | ← | Backend | All in room | participants[] | Full participant list |
| `user-ready` | → | Client | Backend | userId, isReady | Signal ready status |
| `discussion-started` | ← | Backend | All in room | topic, firstSpeaker, duration | Discussion begins |
| `turn-started` | ← | Backend | All in room | speaker_index, speaker, timer | New speaker's turn |
| `turn-ended` | ← | Backend | All in room | speaker | Turn completed |
| `timer-warning` | ← | Backend | All in room | remaining | 10s warning |
| `round-complete` | ← | Backend | All in room | round, next | Round transition |
| `discussion-ended` | ← | Backend | All in room | sessionId, roundsCompleted | Discussion complete |
| `end-turn` | → | Client | Backend | - | Manually end turn |
| `next-speaker` | → | Client | Backend | - | Request next speaker |
| `leave-room` | → | Client | Backend | - | Leave room |
| `participant-left` | ← | Backend | All in room | participantId, anonymousName | Participant left |
| `webrtc-offer` | ↔ | Both | Both | to, from, offer | WebRTC offer |
| `webrtc-answer` | ↔ | Both | Both | to, from, answer | WebRTC answer |
| `webrtc-ice-candidate` | ↔ | Both | Both | to, from, candidate | ICE candidate |
| `ready-for-webrtc` | → | Client | Backend | - | Ready for connections |
| `peer-ready` | ← | Backend | Others | socketId | Peer is ready |
| `speech-transcript` | → | Client | Backend | text, speakerId | Speech text |

## Notes

- **Direction**: → (client to backend), ← (backend to client), ↔ (bidirectional)
- **Broadcasting**: Most backend emissions go to entire room via `room=room_id`
- **Private events**: `english-feedback`, `session-summary` will be private (per UML)
- **Timer**: Fully server-managed, clients just display countdown
- **WebRTC**: Backend acts as signaling server only, audio is P2P
