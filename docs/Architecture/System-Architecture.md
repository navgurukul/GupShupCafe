# System Architecture

## Overview

GupShup Cafe is a full-stack web application built with a modern, scalable architecture. It follows a client-server model with real-time communication using WebSocket and WebRTC protocols.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │   React    │  │ TailwindCSS│  │   React Router     │    │
│  │   + Vite   │  │            │  │   (Navigation)     │    │
│  └────────────┘  └────────────┘  └────────────────────┘    │
│                                                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │  Context   │  │  WebRTC    │  │   Socket.io        │    │
│  │  Providers │  │  Client    │  │   Client           │    │
│  └────────────┘  └────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
              HTTP/REST         WebSocket
                    │               │
┌───────────────────┴───────────────┴─────────────────────────┐
│                      Server Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Express.js + Node.js                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │   REST API │  │ Socket.io  │  │  Room Manager      │    │
│  │  Endpoints │  │  Server    │  │  (State Mgmt)      │    │
│  └────────────┘  └────────────┘  └────────────────────┘    │
│                                                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐    │
│  │  Database  │  │    AI      │  │  WebRTC Signaling  │    │
│  │  Manager   │  │ Generator  │  │  Server            │    │
│  └────────────┘  └────────────┘  └────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                 SQLite      Hugging Face API
                    │               │
┌───────────────────┴───────────────┴─────────────────────────┐
│                     Data/External Layer                      │
│  ┌────────────┐                    ┌────────────────────┐   │
│  │   SQLite   │                    │  Hugging Face      │   │
│  │  Database  │                    │  API (AI Topics)   │   │
│  │  (Local)   │                    │  (External)        │   │
│  └────────────┘                    └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Client Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        App.jsx                               │
│                  (Main Application)                          │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼───────┐  ┌───────▼────────┐
│  AuthProvider  │  │SocketProvider│  │ AudioProvider  │
│  (Auth State)  │  │ (WebSocket)  │  │ (WebRTC/Audio) │
└───────┬────────┘  └──────┬───────┘  └───────┬────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼─────┐   ┌────────▼────────┐   ┌─────▼────────┐
│  LoginPage  │   │   LobbyPage     │   │ Roundtable   │
│             │   │                 │   │    Page      │
└─────────────┘   └─────────────────┘   └──────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼───────┐  ┌───────▼────────┐
│  Participant   │  │    Topic     │  │   Speaker      │
│   Controls     │  │   Display    │  │    Timer       │
└────────────────┘  └──────────────┘  └────────────────┘
```

### Server Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       server.js                              │
│               (Express + Socket.io Setup)                    │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼───────┐  ┌───────▼────────┐
│   API Routes   │  │   Socket     │  │  Middleware    │
│   (REST)       │  │   Handlers   │  │  (CORS, etc)   │
└───────┬────────┘  └──────┬───────┘  └────────────────┘
        │                   │
        └───────────────────┼────────────────────┐
                            │                    │
        ┌───────────────────┼───────┐            │
        │                   │       │            │
┌───────▼────────┐  ┌──────▼───┐  ┌▼────────┐  ┌▼────────────┐
│  Room Manager  │  │ Database │  │   AI    │  │   WebRTC    │
│  (State)       │  │ Manager  │  │ Topics  │  │  Signaling  │
└────────────────┘  └──────────┘  └─────────┘  └─────────────┘
```

---

## Technology Stack

### Frontend
- **Framework**: React 18.x
- **Build Tool**: Vite 5.x
- **Styling**: Tailwind CSS 3.x
- **Routing**: React Router v6
- **Real-time**: Socket.IO Client
- **Audio**: WebRTC API
- **State Management**: React Context API

### Backend
- **Runtime**: Node.js 18+
- **Framework**: Express.js 4.x
- **Real-time**: Socket.IO Server
- **Database**: SQLite 3.x
- **AI Integration**: Hugging Face API
- **Utilities**: UUID, dotenv, cors, helmet

### Development Tools
- **Package Manager**: npm
- **Concurrency**: Concurrently
- **Environment**: dotenv

---

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Production Setup                         │
└─────────────────────────────────────────────────────────────┘

┌──────────────────┐                        ┌─────────────────┐
│     Vercel       │                        │     Render      │
│   (Frontend)     │                        │   (Backend)     │
│                  │                        │                 │
│  - React Build   │──────HTTP/WS───────────│  - Node.js      │
│  - Static CDN    │                        │  - Socket.io    │
│  - HTTPS         │                        │  - SQLite       │
└──────────────────┘                        └─────────────────┘
                                                     │
                                                     │
                                            ┌────────▼─────────┐
                                            │  Hugging Face    │
                                            │  Inference API   │
                                            └──────────────────┘
```

### Deployment Flow

1. **Frontend (Vercel)**:
   - Build: `npm run build` (Vite creates optimized bundle)
   - Deploy: Static files served via Vercel CDN
   - Environment: `VITE_API_URL` points to backend

2. **Backend (Render)**:
   - Deploy: Direct from GitHub repository
   - Start: `npm start` (runs Node.js server)
   - Persistent: Uses Render's persistent disk for SQLite

3. **External Services**:
   - Hugging Face API for AI topic generation
   - STUN servers for WebRTC connections

---

## Data Flow Architecture

### Authentication Flow

```
User → LoginPage → AuthContext → localStorage
                       ↓
            SocketContext (auth handshake)
                       ↓
                   Server validates
                       ↓
              User joins room (Socket)
```

### Discussion Flow

```
Participants Ready → Socket: user-ready
                          ↓
              Server: Check min participants
                          ↓
           Generate Topic (AI/Fallback)
                          ↓
            Save Session to Database
                          ↓
     Emit: discussion-started (to all)
                          ↓
           Start Speaking Timer
                          ↓
        Emit: timer-update (every 1s)
                          ↓
    Timer expires → Advance Speaker
                          ↓
      Emit: speaker-changed (to all)
                          ↓
        Repeat for 3 rounds
                          ↓
      Emit: discussion-ended
                          ↓
       Update Session in Database
```

### Audio/WebRTC Flow

```
Speaker Requests Mic → Browser Permission
                            ↓
                   Get MediaStream
                            ↓
              Emit: ready-for-webrtc
                            ↓
         Server: participants-update
                            ↓
    Create RTCPeerConnection (mesh)
                            ↓
         Exchange SDP Offers/Answers
                   (via Socket.io)
                            ↓
         Exchange ICE Candidates
                            ↓
           P2P Audio Streaming
```

---

## Security Architecture

### Authentication
- User data stored in localStorage
- Socket authentication via handshake
- No passwords (anonymous/identity-based)

### Network Security
- CORS configured for allowed origins
- Helmet.js for HTTP headers
- HTTPS enforced in production
- Input validation on all endpoints

### WebRTC Security
- ICE candidates filtered
- STUN servers only (no TURN for privacy)
- Peer-to-peer connections (no server relay)

---

## Scalability Considerations

### Current Architecture
- **Single Server**: All state in memory
- **No Database Clustering**: SQLite file-based
- **Mesh Network**: P2P WebRTC (scales poorly beyond 6-8 peers)

### Scaling Strategy (Future)

```
┌────────────────────────────────────────┐
│      Load Balancer (Nginx)             │
└────────────────────────────────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
┌───▼────┐          ┌────▼───┐
│Server 1│          │Server 2│
└───┬────┘          └────┬───┘
    │                    │
    └─────────┬──────────┘
              │
     ┌────────▼─────────┐
     │   Redis (State)  │
     └──────────────────┘
              │
     ┌────────▼─────────┐
     │ PostgreSQL (DB)  │
     └──────────────────┘
```

**Improvements Needed**:
1. Redis for shared state across servers
2. PostgreSQL for scalable database
3. SFU (Selective Forwarding Unit) for audio routing
4. Session affinity in load balancer

---

## Performance Optimization

### Frontend
- Code splitting via React.lazy()
- Vite's fast HMR for development
- Production builds with tree-shaking
- CSS purging with Tailwind

### Backend
- Connection pooling for database
- Event-driven architecture (Socket.io)
- Efficient room state management
- Minimal data in Socket events

### Network
- WebSocket for reduced overhead
- WebRTC for P2P audio (no server relay)
- Compressed JSON responses
- CDN for static assets (Vercel)

---

## Monitoring & Observability

### Current Implementation
- Console logging for debugging
- Session analytics in database
- Server statistics endpoint

### Recommended Additions
- Error tracking (Sentry)
- Performance monitoring (New Relic)
- Real-time dashboards (Grafana)
- Structured logging (Winston)

---

## Disaster Recovery

### Database Backup
- SQLite file-based (easy to backup)
- Periodic snapshots recommended
- Version control for migrations

### Server Recovery
- Stateless design (memory-only state)
- Quick redeployment via Git
- Environment variables in Render

### Client Recovery
- PWA capabilities (future)
- Offline fallback page
- Auto-reconnection logic
