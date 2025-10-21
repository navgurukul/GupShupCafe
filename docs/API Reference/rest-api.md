# REST API Reference

## Overview

The GupShup Cafe REST API provides endpoints for health checks, topic management, room management, participant management, user authentication, feedback, transcripts, and AI agents. All endpoints follow RESTful conventions and return JSON responses.

## Base URL

- **Development:** `http://localhost:3003`
- **Production:** `https://your-backend-domain.com`

## API Prefix

All API routes are prefixed with their respective paths:
- General API: `/api`
- Users: `/users`
- Rooms: `/rooms`
- Participants: `/participants`
- Transcripts: `/transcripts`
- Feedback: `/feedback`
- Agents: `/agents`

## Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "success": true,
  "data": { /* response data */ },
  "count": 0  // Optional: for list responses
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "message": "Detailed error (development only)"
}
```

## Authentication

User authentication is handled through the `/users/login` and `/users/signup` endpoints. The API currently uses session-based authentication. For Socket.io connections, user identification is handled through auth tokens passed during connection.

---

## Endpoints

### Health & Status

#### `GET /health`

Health check endpoint to verify server status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "uptime": 1234.56,
  "environment": "development"
}
```

**Status Codes:**
- `200 OK` - Server is healthy

**Example:**
```bash
curl http://localhost:3003/health
```

---

#### `GET /`

Root endpoint with API information.

**Response:**
```json
{
  "name": "AI Roundtable Discussion Server",
  "version": "1.0.0",
  "description": "Backend server for AI-powered educational discussions",
  "endpoints": {
    "health": "/health",
    "api": "/api",
    "socket": "ws://localhost:3003"
  }
}
```

---

### Topics

#### `GET /api/topics`

Get all available fallback topics.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "title": "The Future of Education",
      "description": "How will technology reshape learning in the next decade?",
      "category": "Education",
      "questions": [
        "What role should AI play in personalized learning?",
        "How can we maintain human connection in digital education?",
        "What skills will be most important for future students?"
      ]
    }
  ],
  "count": 10
}
```

**Status Codes:**
- `200 OK` - Topics retrieved successfully
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:3003/api/topics
```

---

#### `GET /api/topics/generate`

Generate a new discussion topic using AI.

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "The Role of AI in Modern Education",
    "description": "Exploring how artificial intelligence is transforming learning experiences",
    "category": "Technology",
    "source": "ai",
    "questions": [
      "How can AI personalize learning for students?",
      "What are the ethical implications of AI in education?",
      "How do we balance AI tools with human teaching?"
    ]
  }
}
```

**Status Codes:**
- `200 OK` - Topic generated successfully
- `500 Internal Server Error` - Generation failed (fallback topic returned)

**Example:**
```bash
curl http://localhost:3003/api/topics/generate
```

**Notes:**
- If AI generation fails, a fallback topic will be returned
- Requires `HUGGINGFACE_API_KEY` environment variable
- Rate limited by Hugging Face API

---

#### `GET /api/topics/category/:category`

Get a topic by category.

**Parameters:**
- `category` (string) - Topic category (Education, Technology, Health, Environment, etc.)

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "Sustainable Living in Urban Areas",
    "description": "Exploring practical ways to live more sustainably in cities",
    "category": "Environment",
    "questions": [
      "What small changes can make the biggest environmental impact?",
      "How can cities be redesigned for sustainability?",
      "What role does individual responsibility play in climate change?"
    ]
  }
}
```

**Status Codes:**
- `200 OK` - Topic found
- `404 Not Found` - No topic for category
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:3003/api/topics/category/Environment
```

---

### Configuration

#### `GET /api/config`

Get public server configuration.

**Response:**
```json
{
  "success": true,
  "data": {
    "minParticipants": 1,
    "maxParticipants": 6,
    "defaultSpeakingTime": 60,
    "features": {
      "aiTopics": true,
      "analytics": true,
      "feedback": true
    }
  }
}
```

**Status Codes:**
- `200 OK` - Configuration retrieved successfully
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:3003/api/config
```

**Configuration Options:**
- `minParticipants` - Minimum participants to start discussion
- `maxParticipants` - Maximum participants allowed
- `defaultSpeakingTime` - Default speaking time in seconds
- `features.aiTopics` - Whether AI topic generation is enabled
- `features.analytics` - Whether analytics are enabled
- `features.feedback` - Whether feedback submission is enabled

---

### User Management

#### `POST /users/signup`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "userId": "user-uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Status Codes:**
- `200 OK` - User created successfully
- `400 Bad Request` - Invalid input
- `500 Internal Server Error` - Server error

---

#### `POST /users/login`

User login.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "userId": "user-uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "cefrLevel": 3
  }
}
```

**Status Codes:**
- `200 OK` - Login successful
- `401 Unauthorized` - Invalid credentials
- `500 Internal Server Error` - Server error

---

#### `GET /users/:userId`

Get user details by ID.

**Parameters:**
- `userId` (string) - User identifier

**Response:**
```json
{
  "status": "success",
  "data": {
    "userId": "user-uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "cefrLevel": 3,
    "lastActive": "2024-01-15T10:00:00.000Z"
  }
}
```

**Status Codes:**
- `200 OK` - User found
- `404 Not Found` - User not found
- `500 Internal Server Error` - Server error

---

#### `GET /users`

List all users.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "userId": "user-uuid",
      "email": "user@example.com",
      "name": "John Doe"
    }
  ]
}
```

---

#### `PATCH /users/cefr-level`

Update user's CEFR level.

**Request Body:**
```json
{
  "userId": "user-uuid",
  "cefrLevel": 4
}
```

**Response:**
```json
{
  "status": "success",
  "message": "CEFR level updated"
}
```

---

#### `PATCH /users/last-active`

Update user's last active timestamp.

**Request Body:**
```json
{
  "userId": "user-uuid"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Last active updated"
}
```

---

#### `DELETE /users/:userId`

Delete a user.

**Parameters:**
- `userId` (string) - User identifier

**Response:**
```json
{
  "status": "success",
  "message": "User deleted"
}
```

---

### Room Management

#### `GET /api/room/:roomId/state`

Get the current state of a discussion room.

**Parameters:**
- `roomId` (string) - Room identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "room-123",
    "participants": [
      {
        "id": "user-1",
        "anonymousName": "Wise Owl",
        "campus": "Delhi",
        "location": "India",
        "isReady": true
      }
    ],
    "discussion": {
      "active": true,
      "topic": {
        "title": "The Future of Education",
        "category": "Education"
      },
      "currentSpeakerIndex": 0,
      "speakingTime": 60,
      "timeRemaining": 45,
      "round": 1
    },
    "createdAt": "2024-01-15T10:00:00.000Z"
  }
}
```

**Status Codes:**
- `200 OK` - Room state retrieved successfully
- `404 Not Found` - Room not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:3003/api/room/room-123/state
```

---

### Room Management

#### `POST /rooms`

Create a new room.

**Request Body:**
```json
{
  "roomName": "Discussion Room 1",
  "topicCategory": "Education",
  "cefrLevel": 3,
  "hostUserId": "user-uuid"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "roomId": "room-uuid",
    "roomName": "Discussion Room 1",
    "status": "waiting"
  }
}
```

**Status Codes:**
- `200 OK` - Room created successfully
- `400 Bad Request` - Invalid input
- `500 Internal Server Error` - Server error

---

#### `GET /rooms/:roomId`

Get room details by ID.

**Parameters:**
- `roomId` (string) - Room identifier

**Response:**
```json
{
  "status": "success",
  "data": {
    "roomId": "room-uuid",
    "roomName": "Discussion Room 1",
    "status": "waiting",
    "participantCount": 3,
    "createdAt": "2024-01-15T10:00:00.000Z"
  }
}
```

**Status Codes:**
- `200 OK` - Room found
- `404 Not Found` - Room not found
- `500 Internal Server Error` - Server error

---

#### `GET /rooms`

List all rooms.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "roomId": "room-uuid",
      "roomName": "Discussion Room 1",
      "status": "waiting",
      "participantCount": 3
    }
  ]
}
```

---

#### `GET /rooms/waiting`

List rooms with status 'waiting'.

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "roomId": "room-uuid",
      "roomName": "Discussion Room 1",
      "status": "waiting",
      "participantCount": 2
    }
  ]
}
```

---

#### `GET /rooms/:roomId/state`

Get current room state including discussion status.

**Parameters:**
- `roomId` (string) - Room identifier

**Response:**
```json
{
  "participants": [
    {
      "id": "user-123",
      "anonymousName": "Wise Owl",
      "role": "speaker",
      "isReady": true
    }
  ],
  "discussion": {
    "active": true,
    "topic": {
      "title": "The Future of Education",
      "category": "Education"
    },
    "currentSpeakerIndex": 0,
    "speakingTime": 60,
    "timeRemaining": 45,
    "round": 1,
    "startedAt": "2024-01-15T10:00:00.000Z",
    "endedAt": null
  }
}
```

**Status Codes:**
- `200 OK` - Room state retrieved successfully
- `404 Not Found` - Room not found
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl http://localhost:3003/rooms/room-123/state
```

---

#### `PATCH /rooms/:roomId/status`

Update room status.

**Parameters:**
- `roomId` (string) - Room identifier

**Request Body:**
```json
{
  "status": "active"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Room status updated"
}
```

---

#### `PATCH /rooms/:roomId/state`

Update room discussion state.

**Parameters:**
- `roomId` (string) - Room identifier

**Request Body:**
```json
{
  "currentSpeakerIndex": 1,
  "round": 2
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Room state updated"
}
```

---

#### `PATCH /rooms/:roomId/end`

End room and mark as finished.

**Parameters:**
- `roomId` (string) - Room identifier

**Request Body:**
```json
{
  "roundsCompleted": 3
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Room ended"
}
```

---

#### `DELETE /rooms/:roomId`

Delete a room.

**Parameters:**
- `roomId` (string) - Room identifier

**Response:**
```json
{
  "status": "success",
  "message": "Room deleted"
}
```

---

### Participant Management

#### `POST /participants`

Create a new participant.

**Request Body:**
```json
{
  "userId": "user-uuid",
  "roomId": "room-uuid",
  "anonymousName": "Wise Owl",
  "role": "speaker"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "participantId": "participant-uuid",
    "userId": "user-uuid",
    "roomId": "room-uuid",
    "role": "speaker"
  }
}
```

---

#### `GET /participants/:userId/:roomId`

Get participant details.

**Parameters:**
- `userId` (string) - User identifier
- `roomId` (string) - Room identifier

**Response:**
```json
{
  "status": "success",
  "data": {
    "participantId": "participant-uuid",
    "userId": "user-uuid",
    "roomId": "room-uuid",
    "anonymousName": "Wise Owl",
    "role": "speaker",
    "isReady": true
  }
}
```

---

#### `GET /participants/room/:roomId`

List participants for a room.

**Parameters:**
- `roomId` (string) - Room identifier

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "participantId": "participant-uuid",
      "userId": "user-uuid",
      "anonymousName": "Wise Owl",
      "role": "speaker"
    }
  ]
}
```

---

#### `PATCH /participants/:participantId`

Update participant.

**Parameters:**
- `participantId` (string) - Participant identifier

**Request Body:**
```json
{
  "role": "listener"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Participant updated"
}
```

---

#### `PATCH /participants/ready`

Update participant ready status.

**Request Body:**
```json
{
  "userId": "user-uuid",
  "roomId": "room-uuid",
  "isReady": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Participant ready status updated"
}
```

---

#### `PATCH /participants/muted`

Update participant muted status.

**Request Body:**
```json
{
  "userId": "user-uuid",
  "roomId": "room-uuid",
  "isMuted": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Participant muted status updated"
}
```

---

#### `PATCH /participants/speaking`

Update participant speaking status.

**Request Body:**
```json
{
  "userId": "user-uuid",
  "roomId": "room-uuid",
  "isSpeaking": true
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Participant speaking status updated"
}
```

---

#### `PATCH /participants/left`

Mark participant as left.

**Request Body:**
```json
{
  "userId": "user-uuid",
  "roomId": "room-uuid",
  "leftAt": "2024-01-15T10:30:00.000Z"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Participant marked as left"
}
```

---

#### `DELETE /participants/:participantId`

Delete a participant.

**Parameters:**
- `participantId` (string) - Participant identifier

**Response:**
```json
{
  "status": "success",
  "message": "Participant deleted"
}
```

---

### Transcript Management

#### `POST /transcripts`

Create a new transcript.

**Request Body:**
```json
{
  "roomId": "room-uuid",
  "participantId": "participant-uuid",
  "transcriptText": "This is what was said...",
  "roundNumber": 1,
  "turnOrder": 0,
  "language": "en",
  "sttConfidence": 0.95,
  "durationSeconds": 60
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transcriptId": "transcript-uuid"
  }
}
```

---

#### `GET /transcripts/:transcriptId`

Get transcript by ID.

**Parameters:**
- `transcriptId` (string) - Transcript identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "transcriptId": "transcript-uuid",
    "roomId": "room-uuid",
    "participantId": "participant-uuid",
    "transcriptText": "This is what was said...",
    "roundNumber": 1,
    "createdAt": "2024-01-15T10:00:00.000Z"
  }
}
```

---

#### `GET /transcripts/room/:roomId`

List transcripts for a room.

**Parameters:**
- `roomId` (string) - Room identifier

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "transcriptId": "transcript-uuid",
      "participantId": "participant-uuid",
      "transcriptText": "This is what was said...",
      "roundNumber": 1
    }
  ]
}
```

---

#### `PATCH /transcripts/processing`

Update transcript processing status.

**Request Body:**
```json
{
  "transcriptId": "transcript-uuid",
  "isProcessed": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Transcript processing status updated"
}
```

---

#### `PATCH /transcripts/audio-url`

Update transcript audio file URL.

**Request Body:**
```json
{
  "transcriptId": "transcript-uuid",
  "audioFileUrl": "https://example.com/audio.mp3"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Transcript audio URL updated"
}
```

---

#### `DELETE /transcripts/:transcriptId`

Delete a transcript.

**Parameters:**
- `transcriptId` (string) - Transcript identifier

**Response:**
```json
{
  "success": true,
  "message": "Transcript deleted"
}
```

---

### Feedback Management

#### `POST /feedback/instant`

Create instant feedback.

**Request Body:**
```json
{
  "participantId": "participant-uuid",
  "feedbackType": "instant",
  "displayMessage": "Great use of vocabulary!"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "feedbackId": "feedback-uuid"
  }
}
```

---

#### `POST /feedback/comprehensive`

Create comprehensive feedback.

**Request Body:**
```json
{
  "participantId": "participant-uuid",
  "feedbackType": "comprehensive",
  "displayMessage": "Overall excellent performance...",
  "detailedAnalysis": "Strengths: ..., Areas for improvement: ..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "feedbackId": "feedback-uuid"
  }
}
```

---

#### `GET /feedback/:feedbackId`

Get feedback by ID.

**Parameters:**
- `feedbackId` (string) - Feedback identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "feedbackId": "feedback-uuid",
    "participantId": "participant-uuid",
    "feedbackType": "instant",
    "displayMessage": "Great use of vocabulary!",
    "createdAt": "2024-01-15T10:00:00.000Z"
  }
}
```

---

#### `GET /feedback/participant/:participantId`

List feedback for a participant.

**Parameters:**
- `participantId` (string) - Participant identifier

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "feedbackId": "feedback-uuid",
      "feedbackType": "instant",
      "displayMessage": "Great use of vocabulary!"
    }
  ]
}
```

---

#### `GET /feedback/room/:roomId`

List feedback for a room.

**Parameters:**
- `roomId` (string) - Room identifier

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "feedbackId": "feedback-uuid",
      "participantId": "participant-uuid",
      "feedbackType": "instant",
      "displayMessage": "Great use of vocabulary!"
    }
  ]
}
```

---

#### `DELETE /feedback/:feedbackId`

Delete feedback.

**Parameters:**
- `feedbackId` (string) - Feedback identifier

**Response:**
```json
{
  "success": true,
  "message": "Feedback deleted"
}
```

---

### AI Agent Management

#### `POST /agents`

Create a new AI agent.

**Request Body:**
```json
{
  "roomId": "room-uuid",
  "agentType": "english",
  "agentName": "English Coach",
  "isActive": true
}
```

**Response:**
```json
{
  "success": true,
  "data": "agent-uuid",
  "message": "Agent created successfully"
}
```

---

#### `GET /agents/:agentId`

Get agent by ID.

**Parameters:**
- `agentId` (string) - Agent identifier

**Response:**
```json
{
  "agentId": "agent-uuid",
  "roomId": "room-uuid",
  "agentType": "english",
  "agentName": "English Coach",
  "isActive": true,
  "createdAt": "2024-01-15T10:00:00.000Z"
}
```

---

#### `GET /agents/room/:roomId`

Get all agents for a room.

**Parameters:**
- `roomId` (string) - Room identifier

**Response:**
```json
[
  {
    "agentId": "agent-uuid",
    "agentType": "english",
    "agentName": "English Coach",
    "isActive": true
  }
]
```

---

#### `GET /agents/room/:roomId/type/:agentType`

Get agents by type for a room.

**Parameters:**
- `roomId` (string) - Room identifier
- `agentType` (string) - Agent type (english, facilitator, etc.)

**Response:**
```json
[
  {
    "agentId": "agent-uuid",
    "agentType": "english",
    "agentName": "English Coach",
    "isActive": true
  }
]
```

---

#### `GET /agents/room/:roomId/active`

Get all active agents for a room.

**Parameters:**
- `roomId` (string) - Room identifier

**Response:**
```json
[
  {
    "agentId": "agent-uuid",
    "agentType": "english",
    "isActive": true
  }
]
```

---

#### `PATCH /agents/:agentId`

Update agent properties.

**Parameters:**
- `agentId` (string) - Agent identifier

**Request Body:**
```json
{
  "isActive": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Agent updated successfully"
}
```

---

#### `DELETE /agents/:agentId`

Delete an agent.

**Parameters:**
- `agentId` (string) - Agent identifier

**Response:**
```json
{
  "success": true,
  "message": "Agent deleted successfully"
}
```

---

#### `POST /agents/:agentId/process-transcript`

Process a transcript with an agent.

**Parameters:**
- `agentId` (string) - Agent identifier

**Request Body:**
```json
{
  "transcriptId": "transcript-uuid",
  "feedbackType": "instant"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "feedback": "Great use of vocabulary!",
    "processingTime": 1.23
  }
}
```

---

### Feedback (Legacy)

#### `POST /api/feedback`

Submit user feedback (placeholder for future enhancement).

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Great platform for discussions!",
  "session_id": "session-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Feedback received successfully"
}
```

**Status Codes:**
- `200 OK` - Feedback submitted successfully
- `400 Bad Request` - Invalid feedback data
- `500 Internal Server Error` - Server error

**Example:**
```bash
curl -X POST http://localhost:3003/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Excellent platform!",
    "session_id": "session-123"
  }'
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "success": false,
  "error": "User-friendly error message",
  "message": "Detailed technical error (development only)"
}
```

### Common Error Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable

### Error Examples

**Missing Resource:**
```json
{
  "success": false,
  "error": "Topic not found for this category"
}
```

**Server Error:**
```json
{
  "success": false,
  "error": "Failed to retrieve topic analytics"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented on the REST API. However, external API calls (Hugging Face) are subject to their rate limits.

**Recommended Client Behavior:**
- Implement exponential backoff for retries
- Cache topic data when possible
- Use WebSocket events for real-time updates instead of polling

---

## CORS Configuration

The API supports CORS with the following configuration:

**Allowed Origins:**
- Configured via `ALLOWED_ORIGINS` environment variable
- Development: `http://localhost:5173`
- Production: Your frontend domain

**Allowed Methods:**
- GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers:**
- Content-Type, Authorization

---

## Best Practices

### 1. Error Handling

Always check the `success` field in responses:

```javascript
const response = await fetch('/api/topics');
const data = await response.json();

if (data.success) {
  // Handle success
  console.log(data.data);
} else {
  // Handle error
  console.error(data.error);
}
```

### 2. Topic Generation

Use fallback topics when AI generation fails:

```javascript
try {
  const response = await fetch('/api/topics/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category: 'Technology' })
  });
  const data = await response.json();
  
  if (data.success) {
    return data.data;
  } else {
    // Fallback to static topics
    const fallback = await fetch('/api/topics');
    return (await fallback.json()).data[0];
  }
} catch (error) {
  console.error('Topic generation failed:', error);
}
```

### 3. Analytics Queries

Use pagination for large datasets:

```javascript
const limit = 50;
const response = await fetch(`/api/analytics/sessions?limit=${limit}`);
const data = await response.json();

console.log(`Retrieved ${data.count} sessions`);
```

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:3003/health

# Get topics
curl http://localhost:3003/api/topics

# Generate topic
curl http://localhost:3003/api/topics/generate

# Get config
curl http://localhost:3003/api/config

# Create a user
curl -X POST http://localhost:3003/users/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "pass123", "name": "Test User"}'

# Create a room
curl -X POST http://localhost:3003/rooms \
  -H "Content-Type: application/json" \
  -d '{"roomName": "Test Room", "topicCategory": "Education", "cefrLevel": 3}'

# Get room state
curl http://localhost:3003/rooms/room-123/state
```

### Using JavaScript Fetch

```javascript
// Health check
fetch('http://localhost:3003/health')
  .then(res => res.json())
  .then(data => console.log(data));

// Generate topic
fetch('http://localhost:3003/api/topics/generate')
  .then(res => res.json())
  .then(data => console.log(data));

// Create a room
fetch('http://localhost:3003/rooms', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    roomName: 'Test Room',
    topicCategory: 'Education',
    cefrLevel: 3
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Migration Notes

### API Version 1.0

Current implementation uses FastAPI with the following architecture:
- `/api/*` - General API endpoints (topics, config)
- `/users/*` - User management
- `/rooms/*` - Room management
- `/participants/*` - Participant management
- `/transcripts/*` - Transcript management
- `/feedback/*` - Feedback management
- `/agents/*` - AI agent management

### Future Breaking Changes

When breaking changes are introduced, version-specific endpoints will be provided:
- `/api/v1/*` - Legacy endpoints
- `/api/v2/*` - New endpoints with additional features

---

## Support

For API issues or questions:
- GitHub Issues: [navgurukul/GupShupCafe](https://github.com/navgurukul/GupShupCafe/issues)
- Documentation: See `/docs` directory
