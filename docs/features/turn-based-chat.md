# Turn-Based Chat Discussion System

## Overview

The turn-based chat system enables participants in roundtable discussions to send text messages during their speaking turns. After each round, all messages are analyzed by AI to provide insights and thematic analysis.

## Features

### 1. Turn-Based Messaging
- Only the current speaker can send messages
- Messages are displayed in real-time to all participants
- Clear visual indicators show whose turn it is to speak
- Messages are organized by rounds

### 2. AI Analysis
- After each round completion, AI analyzes all messages
- Identifies key themes and discussion patterns
- Provides insights on participant engagement
- Analysis displayed temporarily to all participants

### 3. User Interface
- **Full View**: Complete chat interface in right sidebar
- **Compact View**: Condensed chat in participants section
- Real-time message updates
- Auto-scroll to latest messages
- Round-based message clearing

## Technical Implementation

### Backend Components

#### Socket Handlers (`server_py/src/socket/socket_handlers.py`)
```python
@sio.event
async def message(sid, message_data):
    # Validates turn-based speaking
    # Stores messages in transcripts table
    # Broadcasts to all participants

@sio.event
async def send_round_messages_to_ai(sid, data):
    # Retrieves round messages
    # Sends to AI for analysis
    # Broadcasts analysis results
```

#### Database Integration
- Uses existing `transcripts` table for message storage
- `stt_confidence: 1.0` distinguishes chat from speech
- `round_number` and `turn_order` for sequencing
- `duration_seconds: 0` for instant messages

#### AI Agent Service
```python
async def analyze_round_messages(agent_id, round_messages, round_number):
    # Analyzes message themes
    # Provides participant insights
    # Returns structured analysis
```

### Frontend Components

#### ChatPanel Component (`client/src/components/chat/ChatPanel.jsx`)
- Turn validation and message sending
- Real-time message display
- AI analysis presentation
- Both full and compact modes
- Socket event handling

#### Integration Points
- Integrated into `RoundtablePage.jsx`
- Uses existing socket and auth contexts
- Responsive design for different screen sizes

## Usage Flow

1. **Discussion Start**: Chat panel becomes available
2. **Turn Management**: Only current speaker can send messages
3. **Message Broadcasting**: Messages appear for all participants
4. **Round Completion**: Triggers AI analysis
5. **AI Insights**: Analysis displayed to all participants
6. **New Round**: Previous messages cleared, cycle repeats

## Socket Events

### Client to Server
- `message`: Send chat message (turn-validated)
- `send-round-messages-to-ai`: Request AI analysis

### Server to Client
- `message`: Broadcast message to all participants
- `message-error`: Error feedback for invalid messages
- `ai-round-analysis`: AI insights after round completion

## Database Schema

Messages stored in existing `transcripts` table:
```sql
transcript_id: UUID (message ID)
room_id: Room identifier
participant_id: Sender ID
transcript_text: Message content
round_number: Discussion round
turn_order: Speaker position
stt_confidence: 1.0 (chat marker)
duration_seconds: 0 (instant)
```

## Error Handling

- Turn validation prevents out-of-turn messages
- Fallback AI responses for analysis failures
- Optimistic UI updates with error recovery
- Socket reconnection handling

## Testing

Basic test coverage includes:
- Turn-based message validation
- UI state management
- Socket event handling
- Compact vs full view rendering

## Future Enhancements

- Message reactions/emoji responses
- Private messaging between participants
- Message search and filtering
- Export chat transcripts
- Enhanced AI analysis with sentiment detection