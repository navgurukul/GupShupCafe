# Agent Socket Handlers Testing Guide

## Overview

This document explains the agent-related functions in `socket_handlers.py` and how to test them effectively.

## Agent-Related Functions in Socket Handlers

### 1. `process_transcript_for_english_feedback(room_id, transcript_id)`

**Purpose**: Background async task that processes transcripts with the English feedback agent.

**Flow**:
1. Gets English feedback agent for the room
2. Calls `agent_service.process_transcript_for_feedback()` with "instant" feedback type
3. Runs asynchronously in the background

**Testing**: 
- Mock `agent_service.get_agents_by_room()` and `agent_service.process_transcript_for_feedback()`
- Test both success case and when no English agent exists

### 2. `transcript_received` Socket Event Handler

**Purpose**: Handles speech transcripts from participants and triggers agent processing.

**Flow**:
1. Receives transcript data from client
2. Finds the room and user for the socket
3. Saves transcript to database with metadata (word count, speech rate, etc.)
4. Creates background task to process transcript for English feedback
5. Emits `transcript-saved` confirmation

**Data Structure**:
```python
{
    "text": "The actual transcript text",
    "participantId": "user-id",
    "round": 1,
    "turnOrder": 0,
    "confidence": 0.95,
    "startedAt": "2024-01-01T10:00:00Z",
    "endedAt": "2024-01-01T10:00:05Z",
    "duration": 5.0
}
```

**Testing**:
- Mock database `save_transcript()` method
- Mock `asyncio.create_task()` to verify background processing
- Verify correct transcript data structure is saved
- Test error handling for invalid room/user

### 3. `request_facilitator_response` Socket Event Handler

**Purpose**: Handles requests for the facilitator agent to provide a spoken response (TTS).

**Flow**:
1. Gets recent transcripts from the room (last 5)
2. Gets feedback summaries for context
3. Calls `agent_service.generate_facilitator_turn_response()`
4. Emits `facilitator-speaking` event with generated text

**Testing**:
- Mock database methods: `get_recent_transcripts()`, `get_feedback_by_room()`
- Mock `agent_service.generate_facilitator_turn_response()`
- Verify correct data is passed to agent service
- Test `facilitator-speaking` event emission

### 4. `get_instant_feedback` Socket Event Handler

**Purpose**: Handles requests for instant feedback for a specific participant.

**Flow**:
1. Gets participant ID from request data
2. Queries database for recent feedback for that participant
3. Returns the most recent feedback or fallback message
4. Emits `instant-feedback` event

**Testing**:
- Mock `db.get_feedback_by_room()` with participant-specific feedback
- Test filtering by participant ID
- Test fallback message when no feedback exists
- Verify correct event emission structure

### 5. Agent Creation in `check_and_start_discussion`

**Purpose**: Creates facilitator and English feedback agents when a discussion starts.

**Flow**:
1. Calls `agent_service.create_room_agents(room_id, topic)`
2. Updates room record with facilitator agent ID
3. Continues discussion start even if agent creation fails

**Testing**:
- Mock `agent_service.create_room_agents()`
- Verify agents are created with correct room_id and topic
- Test error handling when agent creation fails
- Ensure discussion continues despite agent failures

## Test File Structure

The test file `test_agent_socket_handlers.py` includes:

### Fixtures
- `mock_sio()`: Mock Socket.io server with all required methods
- `setup_test_room_with_agents()`: Creates test room with participants and mock agent data

### Test Categories

#### 1. Background Processing Tests
- `test_process_transcript_for_english_feedback()`
- `test_process_transcript_for_english_feedback_no_agent()`

#### 2. Socket Event Handler Tests
- `test_transcript_received_handler()`
- `test_request_facilitator_response_handler()`
- `test_get_instant_feedback_handler()`
- `test_get_instant_feedback_no_feedback_available()`

#### 3. Integration Tests
- `test_agent_creation_in_discussion_start()`
- `test_agent_creation_failure_handling()`

#### 4. Error Handling Tests
- `test_transcript_received_error_handling()`
- `test_facilitator_response_error_handling()`
- `test_get_instant_feedback_error_handling()`

## Running the Tests

### Option 1: Using pytest directly
```bash
cd server_py
python -m pytest tests/test_agent_socket_handlers.py -v
```

### Option 2: Using the test runner script
```bash
cd server_py
python run_agent_tests.py
```

### Option 3: Run specific test
```bash
cd server_py
python -m pytest tests/test_agent_socket_handlers.py::test_transcript_received_handler -v
```

## Key Testing Patterns

### 1. Socket Handler Testing Pattern
```python
# Get the handler from registered events
handler = None
for call in mock_sio.event.call_args_list:
    if call[0] and hasattr(call[0][0], '__name__'):
        if call[0][0].__name__ == 'handler_name':
            handler = call[0][0]
            break

assert handler is not None, "handler not found"
await handler(socket_id, test_data)
```

### 2. Database Mocking Pattern
```python
with patch('src.socket.socket_handlers.db.method_name', new_callable=AsyncMock) as mock_method:
    mock_method.return_value = expected_data
    # Test code here
    mock_method.assert_called_once_with(expected_args)
```

### 3. Agent Service Mocking Pattern
```python
with patch.object(agent_service, 'method_name', new_callable=AsyncMock) as mock_method:
    mock_method.return_value = expected_result
    # Test code here
    mock_method.assert_called_once()
```

## Mock Data Examples

### Mock Agent Data
```python
mock_english_agent = {
    "agent_id": "english-agent-123",
    "room_id": "test-room",
    "agent_type": "english",
    "status": "active",
    "agent_model": "gemini"
}
```

### Mock Transcript Data
```python
transcript_data = {
    "text": "This is a test transcript",
    "participantId": "user-123",
    "round": 1,
    "turnOrder": 0,
    "confidence": 0.95,
    "duration": 5.0
}
```

### Mock Feedback Data
```python
feedback_data = {
    "participant_id": "user-123",
    "display_message": "Great use of vocabulary!",
    "created_at": "2024-01-01T10:00:00Z"
}
```

## Common Test Assertions

### Verify Database Calls
```python
mock_save.assert_called_once()
saved_data = mock_save.call_args[0][0]
assert saved_data["room_id"] == expected_room_id
```

### Verify Socket Emissions
```python
emit_calls = [call for call in mock_sio.emit.call_args_list 
              if call[0][0] == "event-name"]
assert len(emit_calls) > 0
emitted_data = emit_calls[0][0][1]
assert "expected_field" in emitted_data
```

### Verify Agent Service Calls
```python
mock_agent_method.assert_called_once_with(
    expected_agent_id,
    expected_transcript_id,
    "instant"
)
```

## Error Handling Testing

All agent-related handlers should gracefully handle:
- Missing room/user data
- Database connection errors
- Agent service failures
- Invalid input data

Test these scenarios by:
- Mocking methods to raise exceptions
- Providing invalid socket/room configurations
- Testing with missing required data fields

## Integration with Existing Tests

The agent tests complement the existing socket handler tests in `test_socket_handlers.py`. They focus specifically on:
- Agent interactions
- Background processing
- AI-related functionality
- Transcript and feedback handling

Run both test files together for comprehensive coverage:
```bash
python -m pytest tests/test_socket_handlers.py tests/test_agent_socket_handlers.py -v
```