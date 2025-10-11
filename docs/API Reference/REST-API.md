# REST API Reference

## Overview

The GupShup Cafe backend provides a RESTful API for managing discussion topics, room state, analytics, and configuration. All endpoints return JSON responses.

**Base URL**: `http://localhost:3003/api` (development) or your deployed backend URL

---

## Endpoints

### Health Check

#### `GET /api/health`

Check if the API server is running and healthy.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-11T09:10:36.664Z",
  "service": "AI Roundtable API"
}
```

**Status Codes**:
- `200 OK`: Server is healthy

---

### Topics

#### `GET /api/topics`

Retrieve all available fallback discussion topics.

**Response**:
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
  "count": 8
}
```

**Status Codes**:
- `200 OK`: Topics retrieved successfully
- `500 Internal Server Error`: Failed to retrieve topics

---

#### `POST /api/topics/generate`

Generate a new discussion topic using AI or fallback topics.

**Request Body** (optional):
```json
{
  "category": "Technology"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "title": "The Impact of Social Media on Society",
    "description": "Examining both positive and negative effects of social media platforms.",
    "category": "Technology",
    "questions": [
      "How has social media changed human relationships?",
      "What are the benefits and drawbacks of constant connectivity?",
      "How can we use social media more mindfully?"
    ],
    "source": "fallback"
  }
}
```

**Status Codes**:
- `200 OK`: Topic generated successfully
- `500 Internal Server Error`: Failed to generate topic

---

#### `GET /api/topics/category/:category`

Get a specific topic by category.

**Parameters**:
- `category` (string): Topic category (e.g., "Education", "Technology")

**Response**:
```json
{
  "success": true,
  "data": {
    "title": "The Future of Education",
    "description": "How will technology reshape learning in the next decade?",
    "category": "Education",
    "questions": [...]
  }
}
```

**Status Codes**:
- `200 OK`: Topic found
- `404 Not Found`: No topic found for category
- `500 Internal Server Error`: Server error

---

### Room State

#### `GET /api/room/:roomId/state`

Get the current state of a discussion room including participants and discussion status.

**Parameters**:
- `roomId` (string): Room identifier

**Response**:
```json
{
  "participants": [
    {
      "id": "user-123",
      "anonymousName": "Brave Lion",
      "isReady": true,
      "joinedAt": "2025-10-11T09:00:00.000Z",
      "socketId": "socket-abc-123",
      "role": "speaker"
    }
  ],
  "discussion": {
    "active": true,
    "topic": {
      "title": "The Future of Education",
      "description": "...",
      "category": "Education"
    },
    "currentSpeakerIndex": 0,
    "speakingTime": 60,
    "timeRemaining": 45,
    "round": 1,
    "startedAt": "2025-10-11T09:05:00.000Z",
    "endedAt": null
  }
}
```

**Status Codes**:
- `200 OK`: Room state retrieved
- `404 Not Found`: Room not found
- `500 Internal Server Error`: Failed to get room state

---

### Analytics

#### `GET /api/analytics/sessions`

Get analytics for recent discussion sessions.

**Query Parameters** (optional):
- `limit` (number): Number of sessions to retrieve (default: 10)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "session-123",
      "roomId": "general",
      "topic": "The Future of Education",
      "participantCount": 4,
      "startedAt": "2025-10-11T09:00:00.000Z",
      "endedAt": "2025-10-11T09:15:00.000Z",
      "durationSeconds": 900,
      "roundsCompleted": 3
    }
  ],
  "count": 10
}
```

**Status Codes**:
- `200 OK`: Analytics retrieved
- `500 Internal Server Error`: Failed to retrieve analytics

---

#### `GET /api/analytics/topics`

Get analytics for topic usage.

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "The Future of Education",
      "category": "Education",
      "used_count": 15,
      "created_at": "2025-10-01T00:00:00.000Z"
    }
  ],
  "count": 8
}
```

**Status Codes**:
- `200 OK`: Topic analytics retrieved
- `500 Internal Server Error`: Failed to retrieve analytics

---

#### `GET /api/analytics/stats`

Get server-wide statistics.

**Response**:
```json
{
  "success": true,
  "data": {
    "totalSessions": 150,
    "totalParticipants": 45,
    "avgSessionDuration": 850.5,
    "avgParticipantsPerSession": 3.2,
    "topCategories": [
      {
        "category": "Education",
        "count": 30
      },
      {
        "category": "Technology",
        "count": 25
      }
    ]
  }
}
```

**Status Codes**:
- `200 OK`: Stats retrieved
- `500 Internal Server Error`: Failed to retrieve stats

---

### Feedback

#### `POST /api/feedback`

Submit user feedback about a discussion session.

**Request Body**:
```json
{
  "rating": 5,
  "comment": "Great discussion platform!",
  "session_id": "session-123"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Feedback received successfully"
}
```

**Status Codes**:
- `200 OK`: Feedback submitted
- `400 Bad Request`: Invalid feedback data
- `500 Internal Server Error`: Failed to submit feedback

---

### Configuration

#### `GET /api/config`

Get public configuration settings for the application.

**Response**:
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

**Status Codes**:
- `200 OK`: Configuration retrieved
- `500 Internal Server Error`: Failed to retrieve configuration

---

## Error Handling

All endpoints follow a consistent error response format:

```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "details": "Additional error details (in development mode only)"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently, no rate limiting is implemented. This may be added in future versions.

---

## CORS

The API supports CORS for the following origins (configurable via environment variables):
- Development: `http://localhost:5173`, `http://localhost:5174`
- Production: Configured via `ALLOWED_ORIGINS` or `CORS_ORIGIN` environment variable

---

## Authentication

Currently, no authentication is required for API endpoints. Authentication is handled via Socket.io handshake for real-time connections.
