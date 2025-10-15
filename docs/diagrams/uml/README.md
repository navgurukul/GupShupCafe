# UML Diagrams - GupShup Cafe

This directory contains comprehensive UML diagrams for the GupShup Cafe (AI Roundtable Discussion Platform) created using PlantUML. These diagrams document the system architecture, focusing on the **server_py (Python FastAPI backend)** which is the target backend going forward, with LLM Agent integration.

**Note:** All diagrams use the `.wsd` (WebSequence Diagram) file format, which is compatible with PlantUML 1.2024.8 and later versions.

## 📋 Diagram Index

### 1. Component Diagram
**File:** `01-component-diagram.wsd`

**Purpose:** Shows the overall system architecture with all major components and their interactions.

**Highlights:**
- Client Layer (React Application with contexts)
- Communication Layer (REST, WebSocket, WebRTC)
- Server Layer (FastAPI, Socket.io, Room Manager, LLM Tutor Service)
- Data Layer (SQLite Database, External AI Services, MCP Server)

**Key Focus:** server_py backend architecture with LLM Agent facilitation

---

### 2. Deployment Diagram
**File:** `02-deployment-diagram.wsd`

**Purpose:** Illustrates deployment architecture for both development and production environments.

**Environments:**
- **Development:** Local machine with Vite + FastAPI + SQLite
- **Production:** AWS Amplify (frontend) + AWS EC2 (backend) + AI Services

**Deployment Commands:**
- Development: `npm run dev`
- Production: systemd service on EC2, Amplify auto-deploy

---

### 3. Class Diagram - Backend (server_py)
**File:** `03-class-diagram-backend.wsd`

**Purpose:** Detailed class structure of the Python FastAPI backend (server_py).

**Key Classes:**
- `FastAPIApplication` - Main application entry
- `SocketHandlers` - Real-time event management
- `RoomManager` - In-memory state management
- `Database` - SQLite persistence layer
- `DebateRoomFacilitator` - LLM agent for discussions
- `GeminiAgent` - AI-powered feedback
- `MCPClient` - Model Context Protocol client
- `TopicGenerator` - AI topic generation

**Relationships:** Shows dependencies, compositions, and associations between backend modules.

---

### 4. Sequence Diagram - User Join and Discussion Start
**File:** `04-sequence-user-join-discussion.wsd`

**Purpose:** Shows the complete flow from user login to discussion start.

**Flow Steps:**
1. User Login & Authentication
2. Join Lobby & Socket Connection
3. Request Audio Permissions
4. Mark Ready
5. Start Discussion (when all ready)
6. Initialize WebRTC

**Participants:** User, Browser, Auth Context, Socket Context, Audio Context, FastAPI Server, Socket Handlers, Room Manager, LLM Agent, Database

---

### 5. Sequence Diagram - WebRTC Audio Connection
**File:** `05-sequence-webrtc-audio.wsd`

**Purpose:** Detailed WebRTC peer-to-peer audio connection flow.

**Flow Steps:**
1. Audio Permission & Local Stream
2. WebRTC Initialization
3. Ready Signal
4. Offer/Answer Exchange
5. ICE Candidate Exchange
6. Connection Established

**Key Points:**
- Signaling via Socket.io
- P2P audio streaming
- STUN server usage for NAT traversal
- Opus codec prioritization

---

### 6. Sequence Diagram - LLM Agent Interaction
**File:** `06-sequence-llm-agent-interaction.wsd`

**Purpose:** Shows how the LLM Agent interacts with the discussion system.

**Flow Steps:**
1. Setup Room & Initialize Agent
2. Discussion - Participant Statement
3. Agent Turn - Provide Feedback
4. Discussion End - Final Summary

**Key Components:**
- Debate Room Facilitator
- Gemini Agent
- MCP Client & Server
- CEFR-based feedback generation

**AI Services:** AWS Strands, Gemini, Bedrock

---

### 7. Activity Diagram - Complete Discussion Lifecycle
**File:** `07-activity-discussion-lifecycle.wsd`

**Purpose:** Shows the complete end-to-end flow of a discussion session.

**Lifecycle:**
1. Login & Authentication
2. Join Lobby
3. Ready Check
4. Start Discussion
5. Turn-based Speaking
6. LLM Agent Feedback
7. Discussion End
8. Final Summary

**Decision Points:**
- All participants ready?
- Permission granted?
- Current speaker?
- Timer expired?
- Agent's turn?
- Discussion active?

---

### 8. State Diagram - Room State Management
**File:** `08-state-room-management.wsd`

**Purpose:** Shows the state transitions of a discussion room.

**States:**
- Room Not Exists
- Room Created
- Waiting for Participants
- Participants Joining
- Ready Check
- Discussion Active (with sub-states)
  - Speaking Turn
  - Timer Running
  - Waiting for Next
  - Agent Feedback
- Discussion Ended
- Room Cleanup

**Transitions:** Clear transitions between states with triggering events.

---

### 9. Use Case Diagram
**File:** `09-usecase-diagram.wsd`

**Purpose:** Shows all user interactions and system capabilities.

**Actors:**
- Student (Participant)
- Facilitator (LLM Agent)
- System Admin

**Use Case Packages:**
1. Authentication
2. Lobby Management
3. Discussion Room
4. Audio Communication
5. LLM Agent Facilitation
6. Analytics & Progress
7. System Management

**Total Use Cases:** 33 documented interactions

---

### 10. Database ER Diagram
**File:** `10-er-diagram-database.wsd`

**Purpose:** Enhanced Entity-Relationship diagram for the database schema.

**Core Tables:**
- `sessions` - Discussion session records
- `participants` - Participant tracking
- `topics` - Topic management
- `progress` - User learning progress (future)
- `feedback` - LLM-generated feedback (future)
- `user_profiles` - User profiles (future)

**Relationships:**
- One-to-Many: sessions → participants
- One-to-Many: sessions → feedback
- Many-to-One: sessions → topics

**Indexes:** Documented for optimization

---

### 11. Package Diagram - Frontend React
**File:** `11-package-diagram-frontend.wsd`

**Purpose:** Shows the organization of the React frontend (client/).

**Packages:**
- `pages/` - Route components (Login, Lobby, Roundtable, AudioTest)
- `components/` - UI components (organized by feature)
- `contexts/` - Context Providers (Auth, Socket, Audio)
- `hooks/` - Custom React hooks
- `utils/` - Utility functions

**Configuration Files:**
- package.json
- vite.config.js
- tailwind.config.js
- .env

---

### 12. Class Diagram - Frontend React Components
**File:** `12-class-diagram-frontend.wsd`

**Purpose:** Detailed class structure of React components and contexts.

**Key Components:**
- Context Layer (AuthContext, SocketContext, AudioContext)
- Page Components (LoginPage, LobbyPage, RoundtablePage)
- Roundtable Components (RoundtableView, ParticipantChair, TopicDisplay)
- Audio Components (AudioControls, AudioLevelMeter)
- Feedback Components (FeedbackDisplay, SummaryCard)
- Custom Hooks (useAudioPermission, useWebRTC, useTimer)

**Type Definitions:** User, Participant, Topic, Discussion, Feedback

---

### 13. Sequence Diagram - Speaker Turn Management
**File:** `13-sequence-speaker-turn-management.wsd`

**Purpose:** Shows the detailed flow of speaker turn management during a discussion.

**Flow Steps:**
1. Timer countdown and turn management
2. Speaker transitions
3. Mute/unmute management
4. Turn completion and next speaker selection

**Key Components:**
- Room Manager
- Audio Context
- Timer Management
- Participant State Tracking

---

## 🚀 How to Use These Diagrams

### Viewing PlantUML Diagrams

#### Option 1: PlantUML Online Server
Visit [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/) and paste the content of any `.wsd` file.

#### Option 2: VS Code Extension
1. Install the "PlantUML" extension in VS Code
2. Open any `.wsd` file
3. Press `Alt+D` to preview

#### Option 3: Command Line (Latest PlantUML)
```bash
# Download latest PlantUML (v1.2024.8 or later)
wget https://github.com/plantuml/plantuml/releases/download/v1.2024.8/plantuml-1.2024.8.jar

# Generate PNG
java -jar plantuml-1.2024.8.jar 01-component-diagram.wsd

# Generate SVG
java -jar plantuml-1.2024.8.jar -tsvg 01-component-diagram.wsd
```

#### Option 4: Generate All Diagrams
```bash
# From this directory
java -jar plantuml-1.2024.8.jar *.wsd
```

This will generate PNG images for all diagrams in the `uml/` directory.

**Note:** These diagrams require PlantUML version 1.2024.8 or later for proper rendering.

---

## 📐 Diagram Conventions

### Color Coding
- **Blue tones (#E8F4F8, #4A90E2):** System components, states
- **Orange tones (#FFE6CC, #FF9933):** Decision points, actions
- **Default:** Entities, relationships

### Stereotypes Used
- `<<PK>>` - Primary Key
- `<<FK>>` - Foreign Key
- `<<NOT NULL>>` - Required field
- `<<DEFAULT>>` - Default value
- `<<UNIQUE>>` - Unique constraint
- `<<AUTO>>` - Auto-increment
- `<<JSON>>` - JSON data type
- `<<include>>` - Include relationship
- `<<extend>>` - Extend relationship
- `<<React Pages>>` - React page components
- `<<UI Components>>` - React UI components
- `<<Context Providers>>` - React contexts
- `<<Custom Hooks>>` - React hooks
- `<<Utilities>>` - Utility functions

### Relationship Types
- `-->` - Dependency/Association
- `*--` - Composition
- `o--` - Aggregation
- `--|>` - Inheritance
- `.>` - Dashed dependency
- `||--o{` - One-to-Many (ER)
- `||--||` - One-to-One (ER)

---

## 🎯 Architecture Focus

These diagrams focus on the **server_py (Python FastAPI) backend** as it is the target backend going forward. Key architectural decisions:

### Why server_py?
1. **Modern Python Stack:** FastAPI + async/await
2. **LLM Integration:** Native Python support for AI libraries
3. **MCP Support:** Model Context Protocol for tool execution
4. **Async I/O:** Better performance for real-time operations
5. **Type Safety:** Pydantic models and type hints
6. **Auto Documentation:** Built-in OpenAPI/Swagger docs

### LLM Agent Integration
The diagrams highlight the **LLM Agent as the facilitator** for discussions:
- **Debate Room Facilitator:** Manages turn-taking and feedback
- **Gemini Agent:** Provides AI-powered responses
- **MCP Client:** Connects to MCP Server for tool execution
- **CEFR Standards:** English language feedback based on Common European Framework

### Migration from Node.js (server/)
While the Node.js backend (server/) is currently working, we are transitioning to server_py. The diagrams reflect the target architecture.

---

## 📚 Related Documentation

For more details, refer to:
- `/docs/Architecture/system-architecture.md` - System architecture overview
- `/docs/development.md` - Development guide
- `/docs/Services/backend-services.md` - Backend services documentation
- `/docs/API Reference/` - API documentation
- `/docs/Miscellaneous/MIGRATION_GUIDE.md` - Migration from Node.js to Python

---

## 🔄 Keeping Diagrams Updated

These diagrams should be updated when:
1. New features are added
2. Architecture changes
3. Database schema evolves
4. API endpoints change
5. Component structure changes

### Update Process
1. Modify the relevant `.wsd` file
2. Regenerate images: `java -jar plantuml-1.2024.8.jar filename.wsd`
3. Update this README if needed
4. Commit changes to Git

---

## 📝 Notes

- **Current Status:** All diagrams reflect the server_py backend architecture
- **LLM Focus:** Diagrams emphasize the LLM Agent facilitation feature
- **Migration:** Node.js backend (server/) is being phased out
- **Future Enhancements:** Some features (like `feedback` table) are marked as future enhancements
- **File Format:** All diagrams now use `.wsd` format for better compatibility with latest PlantUML
- **PlantUML Version:** Requires version 1.2024.8 or later for proper rendering

---

## 🤝 Contributing

When adding new diagrams:
1. Use consistent naming: `##-descriptive-name.wsd`
2. Follow PlantUML best practices for latest version (1.2024.8+)
3. Add comprehensive notes and documentation
4. Update this README with the new diagram
5. Generate PNG/SVG for easy viewing using the latest PlantUML JAR
6. Test diagram rendering before committing

---

## 📞 Support

For questions about these diagrams:
1. Review the related documentation
2. Check PlantUML syntax guide: https://plantuml.com/
3. Open an issue on GitHub

---

**Last Updated:** 2025-10-15
**PlantUML Version:** 1.2024.8 (Latest)
**File Format:** .wsd (WebSequence Diagrams)
**Total Diagrams:** 13
**Migration Status:** Successfully migrated from .puml to .wsd format
