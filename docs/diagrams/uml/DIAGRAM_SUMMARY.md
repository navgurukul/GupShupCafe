# GupShup Cafe UML Diagrams - Summary

## Project Information
- **Project Name:** GupShup Cafe
- **Description:** AI-powered online roundtable discussion platform for educational purposes
- **Tech Stack:** React + Node.js + Socket.io + WebRTC + SQLite
- **PlantUML Version:** v1.2024.7 (Latest)
- **Diagrams Generated:** October 2024

## Diagram Verification Status

All diagrams have been validated using PlantUML v1.2024.7 and are **error-free**.

## Complete List of UML Diagrams

### 1. ✅ class-diagram.puml
- **Type:** Class Diagram
- **Purpose:** Shows the object-oriented design including all classes, their attributes, methods, and relationships
- **Coverage:** Backend classes (Server, RoomManager, SocketHandlers, Database, TopicGenerator), Frontend classes (Components, Context Providers, Pages), and data models
- **Status:** ✓ Validated

### 2. ✅ component-diagram.puml
- **Type:** Component Diagram
- **Purpose:** Illustrates the high-level system architecture and how components interact
- **Coverage:** Frontend (React, Router, Socket Client), Backend (Express, Socket.io, Business Logic), External Services (Hugging Face API, WebRTC), Deployment infrastructure
- **Status:** ✓ Validated

### 3. ✅ sequence-login-join.puml
- **Type:** Sequence Diagram
- **Purpose:** Details the user authentication and room joining workflow
- **Flow:** Login → Anonymous Name Generation → Socket Connection → Room Join → Audio Setup → Ready Signal
- **Status:** ✓ Validated

### 4. ✅ sequence-discussion.puml
- **Type:** Sequence Diagram
- **Purpose:** Shows the complete discussion lifecycle
- **Flow:** Discussion Start → Topic Generation → Session Creation → Speaking Timer → Speaker Rotation → Round Management → Discussion End
- **Status:** ✓ Validated

### 5. ✅ sequence-webrtc.puml
- **Type:** Sequence Diagram
- **Purpose:** Illustrates peer-to-peer audio connection setup
- **Flow:** Audio Init → RTCPeerConnection Creation → SDP Exchange → ICE Candidate Exchange → Audio Streaming → Connection Management
- **Status:** ✓ Validated

### 6. ✅ activity-diagram.puml
- **Type:** Activity Diagram
- **Purpose:** Shows the workflow and decision points throughout the system
- **Coverage:** User journey from login through discussion to logout, including all decision points and parallel activities
- **Status:** ✓ Validated

### 7. ✅ deployment-diagram.puml
- **Type:** Deployment Diagram
- **Purpose:** Documents the physical deployment architecture
- **Coverage:** Client Devices, Vercel CDN (Frontend), Render/Cloud (Backend), SQLite Database, External Services, Network protocols
- **Status:** ✓ Validated

### 8. ✅ use-case-diagram.puml
- **Type:** Use Case Diagram
- **Purpose:** Identifies all actors and their interactions with the system
- **Coverage:** 36 use cases across Authentication, Lobby Management, Discussion Management, Audio Communication, Role Management, Topic Management, Analytics, and Room Management
- **Status:** ✓ Validated

### 9. ✅ state-diagram.puml
- **Type:** State Diagram
- **Purpose:** Shows state transitions for rooms and discussions
- **Coverage:** Authentication states, Lobby states, Discussion states, WebRTC connection states, Audio states, and all transitions
- **Status:** ✓ Validated

### 10. ✅ package-diagram.puml
- **Type:** Package Diagram
- **Purpose:** Organizes the system into logical packages
- **Coverage:** Client Application packages, Server Application packages, Database Layer, External Services, Deployment Infrastructure, Development Tools
- **Status:** ✓ Validated

### 11. ✅ database-schema.puml
- **Type:** Entity-Relationship Diagram
- **Purpose:** Documents the database structure
- **Coverage:** 3 tables (sessions, participants, topics) with all fields, relationships, indexes, and sample queries
- **Status:** ✓ Validated

## Diagram Features

All diagrams include:
- ✓ Latest PlantUML syntax (v1.2024.7)
- ✓ Cerulean theme for professional styling
- ✓ Comprehensive notes and documentation
- ✓ Clear relationships and dependencies
- ✓ Proper naming conventions
- ✓ Error-free rendering
- ✓ Consistent formatting

## Directory Structure

```
docs/diagrams/uml/
├── README.md                      # Comprehensive documentation
├── DIAGRAM_SUMMARY.md            # This file
├── class-diagram.puml            # Class diagram
├── component-diagram.puml        # Component/Architecture diagram
├── sequence-login-join.puml      # Login & join sequence
├── sequence-discussion.puml      # Discussion flow sequence
├── sequence-webrtc.puml          # WebRTC audio sequence
├── activity-diagram.puml         # Activity/workflow diagram
├── deployment-diagram.puml       # Deployment architecture
├── use-case-diagram.puml         # Use cases and actors
├── state-diagram.puml            # State transitions
├── package-diagram.puml          # Package organization
└── database-schema.puml          # Database ER diagram
```

## Usage

### Viewing Diagrams

**Option 1: PlantUML Online**
```
Visit: http://www.plantuml.com/plantuml/uml/
Copy & paste .puml file content
```

**Option 2: Local PlantUML**
```bash
# Install PlantUML (requires Java)
brew install plantuml  # macOS
sudo apt-get install plantuml  # Linux

# Generate images
cd docs/diagrams/uml
plantuml *.puml          # PNG
plantuml -tsvg *.puml    # SVG
```

**Option 3: VS Code Extension**
```
Install "PlantUML" extension by jebbs
Open .puml file → Alt+D (Windows/Linux) or Option+D (macOS)
```

### Embedding in Documentation

```markdown
![Class Diagram](docs/diagrams/uml/class-diagram.png)
![Component Diagram](docs/diagrams/uml/component-diagram.png)
```

## Key System Components Documented

### Backend Architecture
- Express Server with Socket.io
- Real-time room and participant management
- WebRTC signaling relay
- AI topic generation with fallback
- SQLite database for analytics
- RESTful API routes

### Frontend Architecture
- React 18 with Vite
- Context-based state management
- Socket.io client for real-time updates
- WebRTC for peer-to-peer audio
- Responsive UI components
- Protected routing

### Key Workflows
1. User authentication and lobby joining
2. Audio setup and WebRTC connection
3. Discussion start with AI/fallback topics
4. Speaking timer and turn rotation
5. Round management (3 rounds)
6. Graceful disconnection handling
7. Session analytics recording

### External Integrations
- Hugging Face API (optional, for AI topics)
- WebRTC STUN/TURN servers
- Vercel deployment (frontend)
- Render/Cloud deployment (backend)

## Technical Specifications

### Database Schema
- **sessions:** Discussion session metadata and analytics
- **participants:** Participant tracking within sessions
- **topics:** Topic library and usage statistics

### Communication Protocols
- **HTTP/HTTPS:** REST API calls
- **WebSocket (WSS):** Real-time Socket.io events
- **WebRTC:** Peer-to-peer audio streaming
- **SQLite:** Local database operations

### Deployment
- **Frontend:** Vercel CDN with automatic builds
- **Backend:** Render/Cloud with Node.js runtime
- **Database:** File-based SQLite (can scale to PostgreSQL)

## Validation Details

All diagrams have been tested and validated using:
- **Tool:** PlantUML JAR v1.2024.7
- **Graphviz:** Required for rendering (installed)
- **Test Command:** `java -jar plantuml.jar -tsvg -o /tmp *.puml`
- **Result:** All 11 diagrams passed validation with no syntax errors

## Maintenance

When updating the system:
1. Update relevant .puml files to reflect code changes
2. Run validation: `java -jar plantuml.jar -syntax filename.puml`
3. Regenerate images if needed for documentation
4. Commit both .puml source and generated images
5. Update this summary if adding new diagrams

## References

- **PlantUML Official:** https://plantuml.com/
- **Project Repository:** https://github.com/navgurukul/GupShupCafe
- **Documentation:** ../../../README.md

---

**Last Updated:** October 2024  
**Status:** Complete ✓  
**Total Diagrams:** 11  
**All Validated:** Yes ✓
