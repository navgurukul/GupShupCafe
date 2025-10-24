# GupShup Cafe - MVP Plan UML Diagrams

**Comprehensive UML Diagrams for MVP Architecture**

This directory contains 14 detailed PlantUML diagrams (`.wsd` format) documenting the complete architecture of GupShup Cafe's MVP (Minimum Viable Product) as planned for the AWS AI Agent Hackathon 2025. All diagrams use PlantUML version 1.2025.3.

---

## 📋 Overview

These diagrams focus on the **planned MVP architecture** with:
- **AWS Fargate** for serverless container deployment (replacing EC2)
- **server_py** (Python FastAPI backend) as the primary backend
- **AWS Strands Multi-Agent System** for LLM-powered English feedback
- **WebRTC** for peer-to-peer audio communication
- **React 18 + Vite** frontend

**PlantUML Version**: 1.2025.3 (uses modern `!theme` directive, updated color schemes, and enhanced styling)

---

## 📁 Diagram Index

### 1. **Component Diagram** (`01-component-diagram.wsd`)
**Purpose**: Shows the high-level system architecture and component relationships

**Key Components**:
- React frontend with Contexts (Auth, Socket, Audio)
- FastAPI backend (server_py)
- Room Manager service
- AWS Strands Multi-Agent Orchestrator
- EnglishFeedbackAgent and DebateFacilitatorAgent
- AWS infrastructure (Amplify, Fargate, Bedrock, EFS)

**Use When**: Understanding overall system structure and component dependencies

---

### 2. **Deployment Diagram** (`02-deployment-diagram.wsd`)
**Purpose**: Illustrates AWS infrastructure and deployment architecture

**Key Elements**:
- AWS Amplify for frontend hosting (CloudFront CDN)
- AWS Fargate/ECS for containerized backend
- Application Load Balancer (ALB)
- EFS for persistent storage (SQLite database)
- Security groups and VPC configuration
- AWS Strands + AgentCore integration
- AWS Bedrock for LLM inference

**Use When**: Planning deployment, infrastructure setup, or understanding cloud architecture

---

### 3. **Class Diagram - Backend** (`03-class-diagram-backend.wsd`)
**Purpose**: Details server_py backend classes and their relationships

**Key Classes**:
- `FastAPIApp`: Main application entry point
- `SocketHandlers`: Socket.io event handlers
- `RoomManager`: Room state management
- `Room` & `Participant`: Core data models
- `DatabaseService`: SQLite persistence layer
- `AWSStrandsOrchestrator`: Multi-agent coordinator
- `EnglishFeedbackAgent` & `DebateFacilitatorAgent`: AI agents
- `LLMInterface`: Pluggable LLM provider interface
- `GeminiLLM` & `BedrockLLM`: Concrete LLM implementations

**Use When**: Implementing backend features, understanding data flow, or refactoring code

---

### 4. **Class Diagram - Frontend** (`04-class-diagram-frontend.wsd`)
**Purpose**: Documents React component architecture and relationships

**Key Components**:
- Context Providers (Auth, Socket, Audio)
- Page Components (Login, Lobby, Roundtable)
- UI Components (RoundtableView, ParticipantCard, Timer, FeedbackModal)
- Custom Hooks (useAuth, useSocket, useAudio, useRoomState)
- Data Models (User, Participant, RoomState, Feedback)

**Use When**: Developing frontend features, understanding state management, or component composition

---

### 5. **Sequence Diagram - User Join & Discussion** (`05-sequence-user-join-discussion.wsd`)
**Purpose**: Shows complete user flow from login to discussion completion

**Flow**:
1. Google OAuth authentication
2. Join room and ready check
3. Start discussion
4. Speaking turns with timer management
5. WebRTC audio streaming
6. Speech transcription
7. Round progression
8. Discussion end and summary

**Use When**: Understanding user journey, implementing features, or debugging issues

---

### 6. **Sequence Diagram - WebRTC Audio** (`06-sequence-webrtc-audio.wsd`)
**Purpose**: Details WebRTC peer-to-peer audio connection setup

**Flow**:
1. Microphone permission request
2. Initialize AudioContext
3. Create RTCPeerConnection
4. SDP offer/answer exchange
5. ICE candidate gathering
6. Connection establishment
7. Audio streaming
8. Mute/unmute control
9. Cleanup on disconnect

**Use When**: Implementing or debugging WebRTC audio, optimizing audio quality

---

### 7. **Sequence Diagram - LLM Agent Interaction** (`07-sequence-llm-agent-interaction.wsd`)
**Purpose**: Shows AWS Strands multi-agent system in action

**Flow**:
1. User speaks and transcript is captured
2. Request instant feedback (2-3 second target)
3. EnglishFeedbackAgent analyzes grammar, vocabulary, fluency
4. CEFR level determination
5. Feedback formatting for UI
6. Private feedback display in modal
7. Optional agent gentle mention
8. Comprehensive analysis after discussion ends

**Use When**: Implementing AI feedback, optimizing LLM prompts, understanding agent coordination

---

### 8. **Sequence Diagram - English Feedback Flow** (`08-sequence-english-feedback-flow.wsd`)
**Purpose**: Detailed flow of real-time English feedback modal

**Flow**:
1. Speech transcription (Web Speech API)
2. Send transcript to backend
3. LLM analysis (2-3 seconds)
4. Grammar/vocabulary/fluency scoring
5. CEFR leveling
6. Display in EnglishFeedbackModal (private)
7. Auto-dismiss after 10 seconds

**Use When**: Implementing feedback UI, optimizing response time, debugging feedback issues

---

### 9. **Activity Diagram - Discussion Lifecycle** (`09-activity-discussion-lifecycle.wsd`)
**Purpose**: Complete activity flow from login to session summary

**Activities**:
- User authentication
- Room creation/joining
- Microphone setup
- Ready check mechanism
- 3 rounds of turn-based speaking
- Real-time feedback per turn
- Comprehensive post-discussion analysis
- Session summary display

**Use When**: Understanding business logic, implementing features, planning user experience

---

### 10. **State Diagram - Room Management** (`10-state-room-management.wsd`)
**Purpose**: Room state machine and transitions

**States**:
- `WAITING`: Lobby phase, ready check
- `IN_PROGRESS`: Active discussion with rounds and turns
- `COMPLETED`: Post-discussion summary
- `CANCELLED`: Emergency cleanup

**Transitions**:
- WAITING → IN_PROGRESS (all ready, start discussion)
- IN_PROGRESS → COMPLETED (3 rounds done)
- Any → CANCELLED (timeout, all left, host cancels)

**Use When**: Implementing room state logic, handling edge cases, debugging state issues

---

### 11. **Use Case Diagram** (`11-usecase-diagram.wsd`)
**Purpose**: All MVP features and actor interactions

**Actors**:
- Guest User
- Authenticated User
- Room Host
- Room Participant
- AI Agent System

**Use Cases** (60+ documented):
- Authentication (Google OAuth)
- Lobby operations (create, join, filter rooms)
- Room preparation (mic setup, ready check)
- Discussion management (turns, timer, rounds)
- Speech transcription
- AI feedback (instant & comprehensive)
- Post-discussion actions
- Analytics and progress tracking

**Use When**: Feature planning, understanding scope, requirements documentation

---

### 12. **ER Diagram - Database Schema** (`12-er-diagram-database.wsd`)
**Purpose**: Complete database schema for SQLite on EFS

**Tables**:
- `users`: User profiles, CEFR levels, topic interests
- `sessions`: Discussion sessions, room state
- `participants`: Per-session participant data
- `transcripts`: Speech-to-text output
- `feedback`: AI-generated feedback (instant & comprehensive)
- `topics`: AI-generated topics tracking
- `analytics`: Aggregated statistics

**Relationships**:
- users → sessions (1:N, creator)
- users → participants (1:N)
- sessions → participants (1:N)
- sessions → transcripts (1:N)
- participants → transcripts (1:N)
- participants → feedback (1:N)
- transcripts → feedback (1:1)

**Use When**: Implementing data layer, writing queries, planning migrations

---

### 13. **Package Diagram - Frontend** (`13-package-diagram-frontend.wsd`)
**Purpose**: Frontend code organization and module structure

**Packages**:
- `contexts/`: React Context providers
- `pages/`: Page-level components
- `components/`: Reusable UI components
- `hooks/`: Custom React hooks
- `services/`: API and service abstractions
- `types/`: TypeScript definitions
- `utils/`: Helper functions
- `styles/`: Tailwind CSS configuration

**Use When**: Organizing code, refactoring, understanding dependencies

---

### 14. **Communication Diagram - Real-time Events** (`14-communication-diagram-events.wsd`)
**Purpose**: Socket.io event flow between clients and server

**Event Categories**:
- Connection management (connect, disconnect)
- Room operations (create, join, leave)
- Discussion control (ready, start, turn management)
- WebRTC signaling (offer, answer, ICE candidates)
- Speech & feedback (transcript, english-feedback, session-summary)

**Broadcasting Patterns**:
- To all in room (broadcast)
- To specific user (private)
- To all except sender
- To specific peer (WebRTC)

**Use When**: Implementing real-time features, debugging Socket.io events, optimizing performance

---

## 🚀 How to Use These Diagrams

### Viewing Diagrams

**Option 1: PlantUML Online Server (Latest Version)**
```
http://www.plantuml.com/plantuml/uml/
```
Copy and paste the content of any `.wsd` file to view the diagram. The online server uses PlantUML version 1.2025.3 or later.

**Option 2: VS Code Extension**
Install the PlantUML extension:
```bash
# Install PlantUML extension in VS Code
# Extension ID: jebbs.plantuml
# Ensure you have the latest version for best rendering
```

**Option 3: Command Line (PlantUML 1.2025.3)**
```bash
# Install PlantUML (requires Java)
brew install plantuml  # macOS
apt-get install plantuml  # Ubuntu

# For PlantUML 1.2025.3, download JAR directly:
# wget https://github.com/plantuml/plantuml/releases/download/v1.2025.3/plantuml-1.2025.3.jar
# java -jar plantuml-1.2025.3.jar *.wsd

# Generate PNG images
plantuml docs/diagrams/plan/uml/*.wsd

# Generate SVG images (vector, better for docs)
plantuml -tsvg docs/diagrams/plan/uml/*.wsd
```

### Modern PlantUML Features Used

All diagrams have been updated to use the latest PlantUML syntax:

- **`!theme plain`**: Modern theming system for consistent styling
- **Enhanced Color Schemes**: Material Design-inspired colors with better contrast
  - Frontend: Blue tones (#E3F2FD, #1976D2)
  - Backend: Green tones (#E8F5E9, #388E3C)
  - AI/LLM: Yellow tones (#FFF9C4, #F57C00)
  - Infrastructure: Grey tones (#ECEFF1, #546E7A)
- **Shadowing Disabled**: Cleaner, modern look (`skinparam shadowing false`)
- **Custom Fonts**: Arial for better readability (`skinparam defaultFontName Arial`)
- **Improved Arrows**: Better visibility with color and thickness settings
- **Stereotype-based Styling**: Clean component categorization using `<<frontend>>`, `<<backend>>`, etc.
- **No Deprecated Syntax**: Removed `!define` macros in favor of modern alternatives

### Generating Images

To generate all diagrams as images:

```bash
# From repository root
cd docs/diagrams/plan/uml

# Generate PNG images
plantuml *.wsd

# Generate SVG images (vector, better for docs)
plantuml -tsvg *.wsd

# Generate all with custom output directory
plantuml -o ../svg *.wsd
```

---

## 🎯 MVP Focus Areas

These diagrams emphasize the **core MVP features**:

✅ **Must-Have for Hackathon**:
- Google OAuth authentication
- Create/join rooms (max 3 participants)
- WebRTC peer-to-peer audio
- Turn-based speaking (60 seconds)
- Real-time speech transcription
- Instant AI feedback (2-3 seconds)
- CEFR level determination
- Private English Feedback Modal
- Session summary with recommendations
- SQLite persistence

⚠️ **Nice-to-Have (Post-MVP)**:
- Room filtering by CEFR/topic
- Pronunciation scoring
- Video support
- Mobile app
- Advanced analytics
- Gamification

---

## 🏗️ Architecture Highlights

### AWS Fargate Deployment
- **Serverless containers**: No EC2 management
- **Auto-scaling**: Based on CPU/memory metrics
- **Application Load Balancer**: HTTPS/WSS termination
- **EFS**: Shared storage for SQLite across tasks
- **Cost-effective**: Pay only for resources used

### AWS Strands Multi-Agent System
- **Orchestrator**: Coordinates multiple AI agents
- **EnglishFeedbackAgent**: Grammar, vocabulary, fluency analysis
- **DebateFacilitatorAgent**: Discussion flow management
- **Pluggable LLMs**: Switch between Gemini (dev) and Bedrock (prod)
- **AWS AgentCore**: Wrapper for runtime, identity, internet access

### Real-time Architecture
- **WebRTC**: P2P audio (no server relay)
- **Socket.io**: Real-time event messaging
- **React Context**: Global state management
- **Custom Hooks**: Reusable business logic

---

## 📊 Diagram Statistics

- **Total Diagrams**: 14
- **Total Lines of Code**: ~90,000+ characters
- **Diagram Types**:
  - Component: 1
  - Deployment: 1
  - Class: 2 (Backend, Frontend)
  - Sequence: 4 (User flow, WebRTC, LLM, Feedback)
  - Activity: 1
  - State: 1
  - Use Case: 1
  - ER: 1
  - Package: 1
  - Communication: 1

---

## 🔗 Related Documentation

- **System Architecture**: `docs/Architecture/system-architecture.md`
- **Product Design**: `docs/Architectural Conversations/product_system_design.md`
- **API Reference**: `docs/API Reference/`
- **Component Reference**: `docs/Component Reference/`
- **Initial UML Diagrams**: `docs/diagrams/initial/uml/` (Node.js backend version)

---

## 🛠️ Maintenance

These diagrams should be updated when:
- Architecture changes (e.g., new services, infrastructure changes)
- API contracts change (e.g., new Socket.io events)
- Database schema evolves (e.g., new tables, columns)
- UI components are added/modified
- LLM agent behavior changes

**Update Process**:
1. Edit the `.wsd` file
2. Regenerate images: `plantuml filename.wsd`
3. Verify diagram correctness
4. Commit both `.wsd` and generated images
5. Update this README if diagram purpose changes

---

## 📝 Conventions

### Naming Convention
```
<number>-<type>-<description>.wsd

Examples:
01-component-diagram.wsd
05-sequence-user-join-discussion.wsd
12-er-diagram-database.wsd
```

### Color Coding
- **LightBlue**: Frontend components
- **LightGreen**: Backend components
- **LightYellow**: AI/LLM components
- **LightGray**: Infrastructure components

### Notes
- Include detailed notes in each diagram
- Explain key design decisions
- Provide code examples where helpful
- Reference related diagrams

---

## 🎓 Learning Resources

**PlantUML Documentation**:
- Official Guide: https://plantuml.com/
- Sequence Diagrams: https://plantuml.com/sequence-diagram
- Class Diagrams: https://plantuml.com/class-diagram
- Component Diagrams: https://plantuml.com/component-diagram

**UML Best Practices**:
- Keep diagrams focused (one purpose per diagram)
- Use consistent notation
- Add descriptive notes
- Maintain up-to-date with code

---

## 🤝 Contributing

When adding new diagrams:
1. Follow naming convention
2. Use consistent color scheme
3. Add comprehensive notes
4. Generate images in multiple formats
5. Update this README
6. Link from related documentation

---

## ✅ Validation Checklist

Before committing diagram changes:
- [ ] PlantUML syntax is valid (no errors)
- [ ] Generated images display correctly
- [ ] Diagram reflects current architecture
- [ ] Notes are clear and comprehensive
- [ ] Related diagrams are updated
- [ ] README is updated
- [ ] Cross-references are correct

---

**Last Updated**: October 2025  
**Version**: 1.0 (MVP Plan)  
**Authors**: Product Team - AWS AI Agent Hackathon 2025  
**Status**: ✅ Ready for Implementation

---

**Need Help?**
- Open an issue on GitHub
- Check related documentation in `docs/`
- Review existing diagrams for examples
- Consult PlantUML documentation

**Happy Diagramming! 📊**
