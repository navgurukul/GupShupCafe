# Agent System Implementation Plan

## Overview
This document outlines the backend implementation for the AI agent system in GupShup Cafe, supporting facilitator and English feedback agents for each room.

## Architecture

### 1. Database Schema
The `agents` table stores agent instances:
```sql
CREATE TABLE agents (
    agent_id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    agent_model TEXT NOT NULL, -- Gemini or Bedrock
    agent_type TEXT DEFAULT 'english', -- facilitator, english, tutor, moderator
    status TEXT DEFAULT 'active', -- active, inactive, error, processing
    system_prompt TEXT,
    total_interactions INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms (room_id)
);
```

### 2. Agent Types

#### Facilitator Agent
- **Purpose**: Guides conversation flow, provides vocal responses via TTS
- **Triggers**: 
  - At designated speaking turns (every 15 seconds before turn)
  - Manual requests from participants
- **Capabilities**:
  - Analyzes recent conversation context
  - Incorporates feedback insights from English agent
  - Generates natural, conversational responses
  - Acknowledges participant contributions
  - Asks follow-up questions to deepen discussion

#### English Feedback Agent
- **Purpose**: Provides instant language learning feedback
- **Triggers**: After each participant's speaking turn
- **Capabilities**:
  - Analyzes speech transcripts for grammar, vocabulary, fluency
  - Generates instant feedback (private modal)
  - Creates comprehensive feedback summaries
  - Tracks participant progress over time

### 3. API Endpoints

#### Agent Management
- `POST /agents/` - Create individual agent
- `GET /agents/{agent_id}` - Get agent details
- `GET /agents/room/{room_id}` - Get all agents for room
- `GET /agents/room/{room_id}/type/{agent_type}` - Get agents by type
- `PATCH /agents/{agent_id}` - Update agent properties
- `DELETE /agents/{agent_id}` - Delete agent

#### Room Agent Operations
- `POST /agents/room/{room_id}/create-agents` - Auto-create facilitator + English agents
- `POST /agents/{agent_id}/process-transcript` - Process transcript for feedback
- `POST /agents/{agent_id}/generate-facilitator-response` - Generate TTS response

#### Agent Analytics
- `GET /agents/{agent_id}/stats` - Interaction statistics
- `GET /agents/{agent_id}/health` - Health status

### 4. Socket.io Events

#### Transcript Processing
- **Event**: `transcript_received`
- **Data**: `{text, participantId, round, turnOrder, confidence, duration}`
- **Flow**:
  1. Save transcript to database
  2. Trigger English agent processing (async)
  3. Generate instant feedback
  4. Emit `transcript-saved` confirmation

#### Facilitator Interactions
- **Event**: `request_facilitator_response`
- **Flow**:
  1. Gather recent transcripts and feedback
  2. Generate contextual response
  3. Emit `facilitator-speaking` with TTS text

#### Feedback Delivery
- **Event**: `get_instant_feedback`
- **Data**: `{participantId}`
- **Response**: `instant-feedback` with feedback text

### 5. Agent Service Methods

#### Core Operations
```python
async def create_room_agents(room_id: str, room_topic: Dict) -> Dict[str, str]
async def process_transcript_for_feedback(agent_id: str, transcript_id: str, feedback_type: str) -> AgentResponseModel
async def generate_facilitator_turn_response(room_id: str, recent_transcripts: List, feedback_summaries: List) -> str
```

#### Feedback Generation
```python
async def _generate_english_feedback(agent: AgentModel, transcript_data: Dict, feedback_type: str) -> str
async def _generate_facilitator_response(agent: AgentModel, transcript_data: Dict) -> str
```

### 6. Integration Points

#### Room Creation
- Agents are automatically created when a room discussion starts
- `check_and_start_discussion()` calls `create_room_agents()`
- Both facilitator and English agents are initialized with room-specific prompts

#### Turn-Based Processing
- English feedback processing starts immediately after participant turn ends
- Facilitator processing begins 15 seconds before facilitator's turn
- Async processing prevents blocking the conversation flow

#### Database Integration
- Transcripts stored with metadata (word count, speech rate, confidence)
- Feedback linked to transcripts and participants
- Agent interaction counters track usage

### 7. LLM Integration (Future)
The current implementation includes placeholders for LLM calls:
- `_generate_english_feedback()` - Will call Gemini/Bedrock for analysis
- `_generate_facilitator_response()` - Will call LLM for contextual responses
- System prompts are stored per agent for consistent behavior

### 8. Error Handling
- Agent status tracking (active, processing, error, inactive)
- Graceful fallbacks when agents are unavailable
- Comprehensive logging for debugging

### 9. Performance Considerations
- Async processing for non-blocking feedback generation
- Database indexing on room_id and agent_type
- Connection pooling for LLM services
- Caching for frequently accessed agent data

## Implementation Status

### ✅ Completed
- Database schema and migrations
- Agent Pydantic models and enums
- Agent service with CRUD operations
- API routes for agent management
- Socket.io event handlers for real-time communication
- Auto-creation of room agents
- Transcript processing pipeline
- Basic feedback generation (placeholder)

### 🔄 In Progress
- LLM service integration (Gemini/Bedrock)
- Advanced feedback analysis algorithms
- TTS integration for facilitator responses

### 📋 TODO
- Frontend integration for agent interactions
- Speech-to-text integration
- Comprehensive testing suite
- Performance optimization
- Production deployment configuration

## Testing Strategy

### Unit Tests
- Agent model validation
- Service method functionality
- Database operations
- Error handling scenarios

### Integration Tests
- Socket.io event flow
- Agent creation and processing
- Database transactions
- API endpoint responses

### End-to-End Tests
- Complete conversation flow with agents
- Feedback generation and delivery
- Facilitator TTS responses
- Multi-participant scenarios

## Deployment Notes

### Environment Variables
```bash
# Agent Configuration
AGENT_MODEL_DEFAULT=Gemini
AGENT_PROCESSING_TIMEOUT=30
FACILITATOR_RESPONSE_DELAY=15

# LLM Service Configuration
GEMINI_API_KEY=your_key_here
BEDROCK_REGION=us-east-1
BEDROCK_ACCESS_KEY=your_key_here
```

### Database Migrations
The agent table is created automatically on server startup. For production deployments, consider running migrations separately.

### Monitoring
- Agent interaction metrics
- Processing time tracking
- Error rate monitoring
- LLM service health checks

This implementation provides a solid foundation for the AI agent system while maintaining flexibility for future enhancements and LLM integrations.