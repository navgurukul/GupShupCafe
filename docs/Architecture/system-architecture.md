# System Architecture

## Overview

GupShup Cafe (AI Roundtable Discussion Platform) is a full-stack web application designed for real-time, AI-powered educational discussions. The platform follows a modern client-server architecture with real-time communication capabilities.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  React App   │  │   Vite Dev   │  │  Tailwind    │          │
│  │   (UI/UX)    │  │    Server    │  │     CSS      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│           │                  │                │                  │
│           └──────────────────┴────────────────┘                  │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │
                ┌──────────▼──────────┐
                │   HTTPS / WSS       │
                │  (Socket.io + REST) │
                └──────────┬──────────┘
                           │
┌──────────────────────────▼───────────────────────────────────────┐
│                      SERVER LAYER                                │
│  ┌────────────────────────────────────────────────────┐         │
│  │              FastAPI Application                   │         │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────┐ │         │
│  │  │   REST API  │  │  Socket.io  │  │  Middleware│ │         │
│  │  │  Endpoints  │  │  Handlers   │  │   (CORS)   │ │         │
│  │  └─────────────┘  └─────────────┘  └───────────┘ │         │
│  └────────────────────────────────────────────────────┘         │
│           │                  │                │                  │
│  ┌────────▼─────┐   ┌────────▼─────┐  ┌──────▼─────┐          │
│  │ Room Manager │   │  LLM Agent   │  │  Database  │          │
│  │   Service    │   │   Service    │  │   Service  │          │
│  └──────────────┘   └──────┬───────┘  └─────┬──────┘          │
└────────────────────────────┼────────────────┼──────────────────┘
                             │                │
                    ┌────────▼─────┐   ┌──────▼──────┐
                    │ AI Services  │   │   Database  │
                    │ AWS Strands/ │   │             │
                    │ Gemini/      │   │             │
                    │ Bedrock      │   │             │
                    └──────────────┘   └─────────────┘
```

## Architecture Layers

### 1. Client Layer (Frontend)

**Technology Stack:**
- React 18 with Hooks
- Vite for build and development
- Tailwind CSS for styling
- Socket.io-client for real-time communication
- React Router for navigation

**Key Responsibilities:**
- User interface rendering
- State management (Context API)
- WebRTC audio handling
- Real-time event handling
- Client-side routing

**Main Components:**
- Pages (Login, Lobby, Roundtable)
- UI Components (RoundtableView, TopicDisplay, etc.)
- Context Providers (Auth, Socket, Audio)

### 2. Communication Layer

**Protocols:**
- **HTTP/HTTPS:** RESTful API endpoints
- **WebSocket (WSS):** Real-time bidirectional communication via Socket.io
- **WebRTC:** Peer-to-peer audio streaming

**Data Flow:**
```
Client Request → Socket.io/REST → Server Handler → Service Layer → Database/External API
     ↓                                                                      ↓
Client Response ← Socket.io/REST ← Server Response ← Service Logic ← Data/Response
```

### 3. Server Layer (Backend)

**Technology Stack:**
- Python runtime
- FastAPI framework
- python-socketio for WebSocket management
- Database for data persistence
- CORS middleware for cross-origin requests

**Key Responsibilities:**
- Request routing and handling
- Real-time event management
- Business logic execution
- Database operations
- AI service integration
- Authentication and authorization
- Room and session management

**Module Organization:**
```
server_py/src/
├── main.py             # Main application entry
├── routes/
│   └── api.py         # REST API endpoints
├── socket/
│   ├── socketHandlers.py  # Socket.io event handlers
│   └── roomManager.py     # Room state management
├── ai/
│   └── llmAgent.py        # LLM agent for feedback
└── database/
    └── database.py        # Database operations
```

### 4. Data Layer

**Database Schema:**
- **sessions:** Discussion session records
- **participants:** User participation data
- **progress:** CEFR progress tracking

**External Services:**
- **AI Services:** AWS Strands/Gemini (dev) or Bedrock (prod) for LLM-based feedback

## Communication Patterns

### 1. WebSocket Events (Socket.io)

**Client → Server Events:**
```
join-room          → User joins discussion room
leave-room         → User leaves discussion room
user-ready         → User marks themselves as ready
next-speaker       → Request to advance to next speaker
mute-toggle        → Toggle microphone mute status
webrtc-offer       → WebRTC connection offer
webrtc-answer      → WebRTC connection answer
webrtc-ice-candidate → WebRTC ICE candidate exchange
message            → Chat message (future feature)
```

**Server → Client Events:**
```
participants-update    → Updated list of participants
discussion-start       → Discussion has begun
discussion-end         → Discussion has ended
next-turn             → Next speaker's turn
timer-update          → Speaking time update
user-joined           → User joined notification
user-left             → User left notification
webrtc-offer          → WebRTC offer forwarding
webrtc-answer         → WebRTC answer forwarding
webrtc-ice-candidate  → ICE candidate forwarding
error                 → Error notification
```

### 2. REST API Endpoints

```
GET  /api/health                  → Server health check
GET  /api/topics                  → Get fallback topics
POST /api/topics/generate         → Generate AI topic
GET  /api/topics/category/:cat    → Get topic by category
GET  /api/analytics/sessions      → Session analytics
GET  /api/analytics/topics        → Topic usage analytics
GET  /api/analytics/stats         → Server statistics
POST /api/feedback                → Submit user feedback
GET  /api/config                  → Get server configuration
GET  /api/room/:roomId/state      → Get room state
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION DEPLOYMENT                     │
│                                                              │
│  ┌────────────────┐              ┌────────────────┐        │
│  │  AWS Amplify   │              │    AWS EC2     │        │
│  │   (Frontend)   │              │   (Backend)    │        │
│  │                │              │                │        │
│  │  - React App   │──── HTTPS ──▶│  - FastAPI     │        │
│  │  - Static CDN  │              │  - Socket.io   │        │
│  │  - Auto SSL    │              │  - Database    │        │
│  └────────────────┘              └────────┬───────┘        │
│                                            │                │
│                                   ┌────────▼───────┐       │
│                                   │  AI Services   │       │
│                                   │  AWS Strands/  │       │
│                                   │  Gemini/       │       │
│                                   │  Bedrock       │       │
│                                   └────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Characteristics

**Frontend (AWS Amplify):**
- Automatic HTTPS
- Global CDN distribution
- Serverless architecture
- Automatic builds from Git
- Environment variable management

**Backend (AWS EC2 + AgentCore):**
- Persistent instances
- WebSocket support
- Scalable architecture
- Auto-deploy capabilities
- Built-in SSL/TLS

## Security Architecture

### Security Layers

```
┌─────────────────────────────────────────┐
│         Application Security            │
│  ┌───────────────────────────────────┐ │
│  │  1. Helmet.js Security Headers    │ │
│  │  2. CORS Origin Validation        │ │
│  │  3. Input Validation              │ │
│  │  4. Rate Limiting (Future)        │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
              ▲
              │
┌─────────────┴───────────────────────────┐
│       Transport Security                │
│  ┌───────────────────────────────────┐ │
│  │  1. HTTPS/WSS Encryption          │ │
│  │  2. WebRTC DTLS-SRTP              │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Security Measures

1. **Transport Layer Security:**
   - All communication over HTTPS/WSS
   - TLS 1.2+ encryption
   - Secure WebSocket connections

2. **Application Security:**
   - Helmet.js security headers
   - CORS policy enforcement
   - XSS protection
   - Content Security Policy

3. **WebRTC Security:**
   - DTLS-SRTP encryption
   - ICE candidate validation
   - Peer connection security

4. **Data Security:**
   - No sensitive data storage
   - Anonymous user identification
   - Session-based data management

## Scalability Considerations

### Current Architecture (Free Tier)

**Limitations:**
- Single server instance
- In-memory room management
- Database (single instance)
- No horizontal scaling

**Capacity:**
- ~50-100 concurrent users
- Multiple discussion rooms
- Limited by server memory

### Future Scalability Path

```
┌────────────────────────────────────────────────────┐
│            SCALED ARCHITECTURE (Future)            │
│                                                     │
│  Load Balancer → [Server 1, Server 2, Server N]   │
│         ↓                    ↓                     │
│     Redis (Session Store + Pub/Sub)                │
│         ↓                                          │
│     PostgreSQL (Persistent Data)                   │
└────────────────────────────────────────────────────┘
```

**Scaling Strategies:**
1. **Horizontal Scaling:** Multiple server instances
2. **State Management:** Redis for shared state
3. **Database:** PostgreSQL for better concurrency
4. **CDN:** Static asset distribution
5. **Microservices:** Separate AI service

## Technology Decisions

### Why These Technologies?

1. **React:** 
   - Component-based architecture
   - Rich ecosystem
   - Excellent developer experience

2. **python-socketio:**
   - Real-time bidirectional communication
   - Automatic reconnection
   - Fallback transports

3. **FastAPI:**
   - High performance async framework
   - Automatic API documentation
   - Type safety with Python type hints

4. **Database:**
   - Flexible data persistence
   - Easy backup and migration
   - Scalable architecture

5. **Vite:**
   - Fast development server
   - Optimized production builds
   - Modern JavaScript support

6. **Tailwind CSS:**
   - Utility-first approach
   - Rapid development
   - Consistent design system
   - Small production bundle

## Performance Optimization

### Client-Side Optimizations

1. **Code Splitting:** React.lazy for route-based splitting
2. **Asset Optimization:** Vite's automatic optimization
3. **State Management:** Context API for minimal re-renders
4. **Memoization:** React.memo for expensive components

### Server-Side Optimizations

1. **Connection Pooling:** Socket.io connection management
2. **Event Debouncing:** Reduced event frequency
3. **Efficient Queries:** Optimized database queries
4. **Caching:** In-memory caching for frequently accessed data

## System Resilience

### Error Handling Strategy

```
┌─────────────────────────────────────────┐
│         Error Handling Layers           │
│                                          │
│  1. Client Error Boundary               │
│     └→ Graceful UI degradation          │
│                                          │
│  2. Network Error Recovery              │
│     └→ Automatic reconnection           │
│                                          │
│  3. Server Error Middleware             │
│     └→ Error logging & response         │
│                                          │
│  4. Database Error Handling             │
│     └→ Fallback mechanisms              │
└─────────────────────────────────────────┘
```

### Fault Tolerance

1. **Socket Reconnection:** Automatic with exponential backoff
2. **Fallback Topics:** When AI generation fails
3. **Graceful Degradation:** Core features always available
4. **Error Boundaries:** Prevent full app crashes

## Development vs Production

### Development Environment

```
Local Machine
├── Vite Dev Server (Port 5173)
│   └── Hot Module Replacement
├── FastAPI Server (Port 3003)
│   └── Development logging
└── Database (./data/roundtable.db)
```

### Production Environment

```
Cloud Infrastructure
├── AWS Amplify (Frontend)
│   └── Global CDN
├── AWS EC2 + AgentCore (Backend)
│   └── Persistent instance
└── Database (Managed service)
```

## Monitoring and Observability

### Current Monitoring

1. **Server Logs:** Console-based logging
2. **Health Endpoints:** `/health` endpoint
3. **Analytics:** Built-in session/topic analytics
4. **Error Tracking:** Console error logs

### Future Monitoring (Recommended)

1. **Application Monitoring:** Sentry/New Relic
2. **Log Aggregation:** LogRocket/Papertrail
3. **Performance Monitoring:** Web Vitals tracking
4. **Uptime Monitoring:** UptimeRobot/Pingdom

## Conclusion

The GupShup Cafe architecture is designed for:
- **Simplicity:** Easy to understand and maintain
- **Scalability:** Clear path for future growth
- **Reliability:** Robust error handling
- **Performance:** Optimized for real-time interaction
- **Cost-Effective:** Free tier deployment options

The architecture balances educational goals with production-ready practices, making it ideal for learning and real-world use.
