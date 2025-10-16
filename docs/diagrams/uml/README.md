# GupShup Cafe - UML Diagrams

This directory contains comprehensive UML diagrams for the GupShup Cafe project, an AI-powered online roundtable discussion platform for educational purposes.

## Overview

These diagrams document the complete system architecture, design, and workflows of the application using PlantUML (`.puml` format). They provide visual documentation for developers, educators, and stakeholders to understand the system.

## Diagrams

### 1. Class Diagram (`class-diagram.puml`)
**Purpose:** Shows the static structure of the system including classes, attributes, methods, and relationships.

**Contents:**
- Backend classes (Server, SocketHandlers, RoomManager, Database, etc.)
- Frontend classes (Components, Context Providers, Pages)
- Data models (Room, Participant, Discussion, Topic, User)
- Relationships and dependencies between classes

**Use Case:** Understanding the object-oriented design and class relationships.

---

### 2. Component Diagram (`component-diagram.puml`)
**Purpose:** Illustrates the high-level system architecture and component interactions.

**Contents:**
- Frontend components (React Router, Authentication, Socket.io Client, WebRTC)
- Backend components (Express Server, Socket.io Server, API Routes, Business Logic)
- External systems (Hugging Face API, SQLite Database)
- Deployment infrastructure (Vercel, Render)
- Communication protocols and data flow

**Use Case:** Understanding system architecture and deployment structure.

---

### 3. Sequence Diagrams

#### a. Login and Join Room (`sequence-login-join.puml`)
**Purpose:** Details the user authentication and room joining workflow.

**Flow:**
1. User login with credentials
2. Anonymous name generation
3. Socket connection establishment
4. Room joining process
5. Audio setup
6. Ready signal and discussion start check

**Use Case:** Understanding user onboarding and initial setup.

#### b. Discussion Management (`sequence-discussion.puml`)
**Purpose:** Shows the complete discussion lifecycle including start, speaker rotation, and end.

**Flow:**
1. Discussion initialization
2. Topic generation (AI or fallback)
3. Session creation in database
4. Speaking timer management
5. Speaker advancement logic
6. Round completion
7. Discussion end and cleanup
8. User disconnection handling

**Use Case:** Understanding the core discussion mechanics.

#### c. WebRTC Audio Communication (`sequence-webrtc.puml`)
**Purpose:** Illustrates peer-to-peer audio connection setup and streaming.

**Flow:**
1. Audio initialization and microphone access
2. RTCPeerConnection creation
3. SDP offer/answer exchange
4. ICE candidate gathering and exchange
5. Connection establishment
6. Audio streaming (bidirectional)
7. Mute/unmute controls
8. Audio level monitoring
9. Connection cleanup

**Use Case:** Understanding WebRTC implementation and audio features.

---

### 4. Activity Diagram (`activity-diagram.puml`)
**Purpose:** Shows the workflow and decision points in the discussion lifecycle.

**Contents:**
- User authentication flow
- Lobby waiting and audio setup
- Discussion start conditions
- WebRTC connection setup
- Discussion loop with timer and speaker rotation
- Round management
- Disconnection handling
- Discussion end scenarios

**Use Case:** Understanding business logic and user journey.

---

### 5. Deployment Diagram (`deployment-diagram.puml`)
**Purpose:** Documents the physical deployment architecture and infrastructure.

**Contents:**
- Client devices and web browsers
- Frontend hosting on Vercel CDN
- Backend hosting on Render/Cloud platform
- SQLite database storage
- External services (Hugging Face API, STUN/TURN servers)
- Network protocols (HTTPS, WebSocket, WebRTC)
- Environment configuration
- Deployment notes and requirements

**Use Case:** Understanding production deployment and infrastructure.

---

### 6. Use Case Diagram (`use-case-diagram.puml`)
**Purpose:** Identifies all system actors and their interactions with the platform.

**Actors:**
- Student, Educator, Participant, Speaker, Listener, Administrator
- External systems (Hugging Face API, WebRTC STUN/TURN)

**Use Cases (36 total):**
- Authentication (UC1-UC3)
- Lobby Management (UC4-UC8)
- Discussion Management (UC9-UC15)
- Audio Communication (UC16-UC21)
- Role Management (UC22-UC24)
- Topic Management (UC25-UC28)
- Analytics & Monitoring (UC29-UC32)
- Room Management (UC33-UC36)

**Use Case:** Understanding user roles and system functionality.

---

### 7. State Diagram (`state-diagram.puml`)
**Purpose:** Shows the different states of rooms and discussions throughout their lifecycle.

**States:**
- User Authentication states
- Lobby states (joining, waiting, audio setup, ready)
- Discussion states (initializing, active, ending)
- Topic generation states
- WebRTC connection states
- Speaking turn states
- Round management states
- Disconnection handling states
- Audio management states (muted/unmuted)

**Use Case:** Understanding state transitions and system behavior.

---

### 8. Package Diagram (`package-diagram.puml`)
**Purpose:** Organizes the system into logical packages and shows dependencies.

**Packages:**
- Client Application (React, Pages, Components, Context Providers, Build Tools)
- Server Application (Core Server, Middleware, API Routes, Socket Handlers, Business Logic)
- Database Layer (SQLite tables)
- External Services (Hugging Face, WebRTC Infrastructure)
- Deployment Infrastructure (Vercel, Render)
- Development Tools (Git, NPM, Configuration)

**Use Case:** Understanding code organization and module structure.

---

### 9. Database Schema (`database-schema.puml`)
**Purpose:** Entity-Relationship diagram showing database structure.

**Tables:**
- **sessions:** Stores discussion session metadata and analytics
- **participants:** Tracks individual participants within sessions
- **topics:** Stores discussion topics and usage statistics

**Features:**
- Primary keys and foreign keys
- Field descriptions and data types
- Relationships (one-to-many)
- Recommended indexes for performance
- Sample data examples
- Common analytics queries

**Use Case:** Understanding data model and persistence layer.

---

## Viewing the Diagrams

### Option 1: PlantUML Online Server
1. Visit http://www.plantuml.com/plantuml/uml/
2. Copy the content of any `.puml` file
3. Paste into the text area to render

### Option 2: PlantUML Local Installation
```bash
# Install PlantUML (requires Java)
# On macOS with Homebrew:
brew install plantuml

# On Ubuntu/Debian:
sudo apt-get install plantuml

# Generate PNG images:
plantuml *.puml

# Generate SVG images:
plantuml -tsvg *.puml
```

### Option 3: VS Code Extension
1. Install "PlantUML" extension by jebbs
2. Open any `.puml` file
3. Use `Alt+D` (Windows/Linux) or `Option+D` (macOS) to preview

### Option 4: IntelliJ/WebStorm Plugin
1. Install "PlantUML integration" plugin
2. Open any `.puml` file
3. Preview pane will show the rendered diagram

## Generating Images

To generate image files from all diagrams:

```bash
# Navigate to the diagrams directory
cd docs/diagrams/uml

# Generate PNG images
plantuml *.puml

# Generate SVG images (scalable)
plantuml -tsvg *.puml

# Generate both
plantuml *.puml && plantuml -tsvg *.puml
```

This will create image files alongside the `.puml` source files.

## Integration with Documentation

These diagrams can be embedded in Markdown documentation:

```markdown
## Architecture Overview
![Component Diagram](diagrams/uml/component-diagram.png)

## Database Schema
![Database Schema](diagrams/uml/database-schema.png)
```

## Maintenance

When updating the codebase:

1. **Review relevant diagrams** to understand current design
2. **Update diagrams** to reflect code changes
3. **Regenerate images** if needed for documentation
4. **Commit both `.puml` and generated images** for easy viewing

## PlantUML Syntax Reference

- Official documentation: https://plantuml.com/
- Class diagrams: https://plantuml.com/class-diagram
- Sequence diagrams: https://plantuml.com/sequence-diagram
- Activity diagrams: https://plantuml.com/activity-diagram-beta
- Component diagrams: https://plantuml.com/component-diagram
- State diagrams: https://plantuml.com/state-diagram
- Deployment diagrams: https://plantuml.com/deployment-diagram
- Use case diagrams: https://plantuml.com/use-case-diagram

## Theme

All diagrams use the `cerulean` theme for consistent, professional styling:
```
!theme cerulean
```

## Contributing

When creating or updating diagrams:

1. Use consistent naming conventions
2. Add descriptive notes and comments
3. Keep diagrams focused and not overly complex
4. Use PlantUML best practices
5. Test rendering before committing
6. Update this README if adding new diagrams

## Questions or Issues

For questions about the diagrams or suggestions for improvements:
1. Review the existing diagrams thoroughly
2. Check PlantUML documentation
3. Open an issue in the repository
4. Discuss with the development team

---

**Generated with PlantUML** | **Project:** GupShup Cafe | **Date:** October 2024
