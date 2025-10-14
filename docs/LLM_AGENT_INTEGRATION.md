# LLM Agent Integration Guide

## Overview

The GupShup Cafe platform now includes an **LLM Agent** (AI Tutor) that can participate as a default participant in roundtable discussions. The agent provides:

- 🤖 **Automated Participation**: Joins discussions automatically when enabled
- 📚 **Discussion Facilitation**: Provides thoughtful feedback and guidance
- 🗣️ **English Language Feedback**: Offers constructive feedback on language usage
- 🔍 **Fact-Checking**: Helps verify claims and observations
- 💡 **Engagement**: Asks thought-provoking questions to deepen discussions

## Architecture

### Components

1. **LLM Agent Service** (`src/ai/llm_agent_service.py`)
   - Core service managing agent behavior
   - Conversation history tracking
   - Response generation

2. **Socket Integration** (`src/socket/socket_handlers.py`)
   - Automatic agent addition to rooms
   - Agent response triggers
   - Turn management

3. **API Endpoints** (`src/api/routes.py`)
   - `/api/llm-agent/status` - Check agent status
   - `/api/llm-agent/response/{room_id}` - Manually trigger responses

## Configuration

### Enable the LLM Agent

Set the environment variable in your `.env` file:

```env
ENABLE_LLM_AGENT=true
```

By default, the agent is **disabled** (`false`) to ensure backward compatibility.

### Agent Parameters

The agent automatically:
- Joins as a participant named "AI Tutor"
- Takes speaker role (can speak in discussions)
- Is always ready when added
- Has participant ID: `llm-agent`

## Usage

### Automatic Integration

When a discussion starts and the agent is enabled:

1. **Agent Auto-Joins**: The agent is automatically added to the room as a participant
2. **Appears in Participant List**: Shows up alongside human participants with `isAgent: true` flag
3. **Takes Turns**: Participates in the speaking rotation
4. **Provides Feedback**: Offers discussion insights and language feedback

### Socket Events

#### Client → Server

```javascript
// Request agent response manually
socket.emit('request_agent_response', {});

// Notify when speaker turn changes
socket.emit('speaker_turn_changed', {
  currentSpeaker: participantObject
});
```

#### Server → Client

```javascript
// Agent provides a response
socket.on('agent-response', (response) => {
  // response = {
  //   speaker: "AI Tutor",
  //   content: "...",
  //   timestamp: "...",
  //   isAgent: true
  // }
});

// Participants list includes agent
socket.on('participants-update', (participants) => {
  // One participant will have isAgent: true
});
```

### API Endpoints

#### Check Agent Status

```bash
GET /api/llm-agent/status

Response:
{
  "success": true,
  "data": {
    "enabled": true,
    "agentName": "AI Tutor",
    "agentId": "llm-agent"
  }
}
```

#### Trigger Agent Response

```bash
POST /api/llm-agent/response/{room_id}

Response:
{
  "success": true,
  "data": {
    "speaker": "AI Tutor",
    "content": "Discussion feedback here...",
    "timestamp": "2024-01-15T10:30:00Z",
    "isAgent": true
  }
}
```

## Agent Behavior

### Opening Statement

When a discussion starts with no prior conversation, the agent provides a welcoming opening statement that:
- Introduces itself
- References the discussion topic
- Sets a positive, collaborative tone

Example:
```
"Welcome everyone! I'm excited to discuss The Future of Education with you today. 
How will technology reshape learning in the next decade? Let's explore different 
perspectives together."
```

### Discussion Feedback

After participants have spoken, the agent provides:

1. **Discussion Observations**
   - Summary of key points raised
   - Common ground identified
   - Areas of divergence noted

2. **English Language Feedback**
   - Constructive feedback on language usage
   - Grammar suggestions
   - Vocabulary enhancement tips
   - Sentence structure improvements

Example Response Format:
```
**Discussion Feedback:**
I appreciate everyone's contributions so far. You're exploring The Future of 
Education from multiple angles.

Consider this: What role should AI play in personalized learning?

**English Language Tips:**
• **Alice**: Good use of descriptive language! Try varying your sentence 
  structure for even more engaging expression.
• **Bob**: Good use of descriptive language! Try varying your sentence 
  structure for even more engaging expression.
```

## Frontend Integration

### Identifying Agent Participants

Check the `isAgent` flag in participant objects:

```javascript
const participants = [
  {
    id: "user-123",
    anonymousName: "Friendly Fox",
    isAgent: false,
    // ... other fields
  },
  {
    id: "llm-agent",
    anonymousName: "AI Tutor",
    isAgent: true,
    role: "speaker",
    isReady: true,
    // ... other fields
  }
];

// Filter human participants
const humanParticipants = participants.filter(p => !p.isAgent);

// Get agent
const agent = participants.find(p => p.isAgent);
```

### Displaying Agent Responses

```javascript
socket.on('agent-response', (response) => {
  if (response.isAgent) {
    // Display agent response differently
    displayAgentMessage(response.content);
  }
});
```

### Handling Agent in UI

- Display agent with special icon (🤖 or robot avatar)
- Differentiate agent messages with distinct styling
- Don't show audio controls for agent
- Agent doesn't need camera/microphone permissions

## Testing

### Running Tests

```bash
cd server_py
python -m pytest tests/test_llm_agent.py -v
```

All 15 LLM Agent tests cover:
- Service initialization
- Agent participant creation
- Room initialization
- Statement recording
- Response generation
- Conversation history
- Error handling
- Cleanup operations

### Manual Testing

1. **Enable the agent**:
   ```bash
   echo "ENABLE_LLM_AGENT=true" >> server_py/.env
   ```

2. **Start the server**:
   ```bash
   cd server_py
   python main.py
   ```

3. **Check agent status**:
   ```bash
   curl http://localhost:3003/api/llm-agent/status
   ```

4. **Join a room and start discussion** - agent should auto-join

5. **Manually trigger response**:
   ```bash
   curl -X POST http://localhost:3003/api/llm-agent/response/general
   ```

## Troubleshooting

### Agent Not Appearing

**Problem**: Agent doesn't join discussions

**Solutions**:
1. Check `ENABLE_LLM_AGENT=true` in `.env`
2. Restart the server after changing environment
3. Check server logs for initialization messages:
   ```
   ✅ LLM Agent service enabled
   🤖 Added LLM Agent to room general
   ```

### Agent Not Responding

**Problem**: Agent joins but doesn't provide responses

**Solutions**:
1. Ensure discussion is active (topic set)
2. Check if participants have spoken (agent needs context)
3. Manually trigger via API endpoint for testing
4. Check server logs for errors

### Agent Responses Generic

**Problem**: Agent provides basic, repetitive responses

**Note**: The current implementation uses a simplified response generator. To get more sophisticated responses:

1. **Integrate with Gemini API**: Uncomment Gemini integration code
2. **Set API Key**: Add `GEMINI_API_KEY` to `.env`
3. **Install dependencies**: 
   ```bash
   pip install google-genai strands-agents bedrock-agentcore
   ```

## Future Enhancements

Potential improvements for the LLM Agent:

1. **Full Gemini Integration**: Use actual LLM for dynamic responses
2. **Bedrock AgentCore**: Integrate AWS Bedrock for advanced capabilities
3. **Memory System**: Agent remembers past discussions
4. **Personality Customization**: Different agent personalities
5. **Multi-Language Support**: Support for multiple languages
6. **Voice Synthesis**: Text-to-speech for agent responses
7. **Advanced Fact-Checking**: Real-time information verification
8. **Debate Strategies**: Specialized modes for debates vs. discussions

## API Reference

### LLMAgentService

```python
from src.ai.llm_agent_service import llm_agent_service

# Check if enabled
is_enabled = llm_agent_service.is_enabled()

# Get agent participant object
agent = llm_agent_service.get_agent_participant()

# Initialize for a room
llm_agent_service.initialize_room(room_id, topic, participants)

# Record a statement
llm_agent_service.add_statement(room_id, speaker_name, content)

# Generate response
response = await llm_agent_service.generate_response(room_id, topic)

# Cleanup
llm_agent_service.cleanup_room(room_id)
```

## Security Considerations

1. **Rate Limiting**: Consider adding rate limits to prevent abuse
2. **Content Filtering**: Agent responses should be monitored
3. **Privacy**: Agent doesn't store personal information
4. **Authentication**: API endpoints are currently open - add auth if needed

## Performance

- **Minimal Overhead**: Service adds ~5-10ms per request
- **Memory Usage**: Stores conversation history per room (auto-cleaned)
- **Scalability**: Handles multiple concurrent rooms
- **No External Dependencies**: Works without API keys (basic mode)

## License

This LLM Agent integration is part of the GupShup Cafe platform and follows the same license terms.

## Support

For issues or questions:
1. Check server logs for error messages
2. Run test suite to verify installation
3. Review this documentation
4. Create an issue on GitHub repository

---

**Version**: 1.0.0  
**Last Updated**: October 2024
