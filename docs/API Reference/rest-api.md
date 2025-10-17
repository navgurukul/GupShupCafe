# REST API Reference

## Overview

The GupShup Cafe REST API provides endpoints for health checks, topic management, analytics, and configuration. All endpoints follow RESTful conventions and return JSON responses.

## Base URL

- **Development:** `http://localhost:3003/api`
- **Production:** `https://your-backend-domain.com/api`

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

Currently, the API does not require authentication for most endpoints. User identification is handled through Socket.io authentication tokens for real-time features.

---

## Endpoints

### Health & Status

#### `GET /api/health`

Health check endpoint to verify server status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "service": "AI Roundtable API"
}
```

**Status Codes:**
- `200 OK` - Server is healthy

**Example:**
```bash
curl http://localhost:3003/api/health
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

#### `POST /api/topics/generate`

Generate a new discussion topic using AI.

**Request Body:**
```json
{
  "category": "Technology",  // Optional
  "context": "Education"     // Optional
}
```

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
curl -X POST http://localhost:3003/api/topics/generate \
  -H "Content-Type: application/json" \
  -d '{"category": "Technology"}'
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

### Analytics

#### `GET /api/analytics/sessions`

Get session analytics data.

**Query Parameters:**
- `limit` (integer, optional) - Number of sessions to return (default: 10)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "session-uuid",
      "room_id": "room-123",
      "topic_title": "The Future of Education",
      "topic_category": "Education",
      "participant_count": 5,
      "started_at": "2024-01-15T10:00:00.000Z",
      "ended_at": "2024-01-15T10:30:00.000Z",
      "duration_seconds": 1800,
      "rounds_completed": 3,
      "created_at": "2024-01-15T10:00:00.000Z"
    }
  ],
  "count": 10
}
```

**Status Codes:**
- `200 OK` - Analytics retrieved successfully
- `500 Internal Server Error` - Database error

**Example:**
```bash
curl "http://localhost:3003/api/analytics/sessions?limit=20"
```

---

#### `GET /api/analytics/topics`

Get topic usage analytics.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "The Future of Education",
      "description": "How will technology reshape learning...",
      "category": "Education",
      "source": "fallback",
      "used_count": 15,
      "created_at": "2024-01-01T00:00:00.000Z"
    }
  ],
  "count": 10
}
```

**Status Codes:**
- `200 OK` - Analytics retrieved successfully
- `500 Internal Server Error` - Database error

**Example:**
```bash
curl http://localhost:3003/api/analytics/topics
```

---

#### `GET /api/analytics/stats`

Get server statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "totalSessions": 50,
    "totalParticipants": 250,
    "totalTopics": 10,
    "averageSessionDuration": 1500,
    "averageParticipantsPerSession": 5
  }
}
```

**Status Codes:**
- `200 OK` - Statistics retrieved successfully
- `500 Internal Server Error` - Database error

**Example:**
```bash
curl http://localhost:3003/api/analytics/stats
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
    "maxParticipants": 8,
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

### Feedback

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
curl http://localhost:3003/api/health

# Get topics
curl http://localhost:3003/api/topics

# Generate topic
curl -X POST http://localhost:3003/api/topics/generate \
  -H "Content-Type: application/json" \
  -d '{"category": "Technology"}'

# Get analytics
curl http://localhost:3003/api/analytics/stats
```

### Using JavaScript Fetch

```javascript
// Health check
fetch('http://localhost:3003/api/health')
  .then(res => res.json())
  .then(data => console.log(data));

// Generate topic
fetch('http://localhost:3003/api/topics/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ category: 'Education' })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Migration Notes

### From v1.0 to v2.0 (Future)

When breaking changes are introduced, version-specific endpoints will be provided:

- `/api/v1/topics` - Legacy endpoint
- `/api/v2/topics` - New endpoint with additional features

---

## Support

For API issues or questions:
- GitHub Issues: [navgurukul/GupShupCafe](https://github.com/navgurukul/GupShupCafe/issues)
- Documentation: See `/docs` directory
