# UML Diagrams Documentation Summary

**Date Created:** October 15, 2025
**Created For:** GupShup Cafe - AI Roundtable Discussion Platform
**Backend Focus:** server_py (Python FastAPI) with LLM Agent Integration

---

## Overview

This documentation provides comprehensive UML diagrams for the GupShup Cafe platform, focusing on the **server_py (Python FastAPI backend)** which is the target backend architecture going forward. The diagrams emphasize the integration of the LLM Agent as a facilitator for roundtable discussions.

## What Was Created

### 13 Comprehensive UML Diagrams

All diagrams are created using **PlantUML** format (`.puml` files) and are located in `/docs/diagrams/uml/`.

#### 1. **Component Diagram** (`01-component-diagram.puml`)
- Shows complete system architecture
- Client Layer: React Application with Context Providers
- Communication Layer: REST, WebSocket, WebRTC
- Server Layer: FastAPI, Socket.io, Room Manager, LLM Tutor Service
- Data Layer: SQLite, External AI Services, MCP Server
- **Highlights:** server_py backend components and LLM Agent integration

#### 2. **Deployment Diagram** (`02-deployment-diagram.puml`)
- Development environment: Local machine setup
- Production environment: AWS infrastructure
- Frontend: AWS Amplify with CDN
- Backend: AWS EC2 with systemd service
- Database: SQLite with persistent storage
- AI Services: AWS Strands, Gemini, Bedrock integration

#### 3. **Class Diagram - Backend** (`03-class-diagram-backend.puml`)
- Complete Python class structure for server_py
- Main classes: FastAPIApplication, SocketHandlers, RoomManager, Database
- LLM components: DebateRoomFacilitator, GeminiAgent, MCPClient
- AI integration: TopicGenerator with Hugging Face
- Shows all relationships, dependencies, and compositions

#### 4. **Sequence Diagram - User Join & Discussion Start** (`04-sequence-user-join-discussion.puml`)
- User login and authentication flow
- Joining lobby and socket connection
- Audio permission requests
- Ready check mechanism
- Discussion start trigger
- WebRTC initialization

#### 5. **Sequence Diagram - WebRTC Audio** (`05-sequence-webrtc-audio.puml`)
- Peer-to-peer audio connection establishment
- WebRTC offer/answer exchange
- ICE candidate discovery and exchange
- Audio stream setup and playback
- STUN server integration
- Socket.io signaling relay

#### 6. **Sequence Diagram - LLM Agent Interaction** (`06-sequence-llm-agent-interaction.puml`)
- Room setup and agent initialization
- Participant statement processing
- Agent feedback generation via Gemini/Bedrock
- MCP Server tool execution
- CEFR-based English feedback
- Final summary generation

#### 7. **Activity Diagram - Discussion Lifecycle** (`07-activity-discussion-lifecycle.puml`)
- Complete end-to-end discussion flow
- Decision points and branches
- Turn-based speaking management
- LLM agent feedback loops
- Timer management
- Discussion end conditions

#### 8. **State Diagram - Room Management** (`08-state-room-management.puml`)
- Room lifecycle states
- State transitions and triggers
- Sub-states during active discussion
- Timer and turn management states
- Cleanup and resource management

#### 9. **Use Case Diagram** (`09-usecase-diagram.puml`)
- 33 documented use cases
- Three actors: Student, LLM Agent, System Admin
- Seven use case packages
- Include/extend relationships
- System capabilities overview

#### 10. **Database ER Diagram** (`10-er-diagram-database.puml`)
- Enhanced entity-relationship model
- Core tables: sessions, participants, topics
- Future tables: progress, feedback, user_profiles
- Relationships and cardinality
- Indexes and constraints
- Field descriptions and types

#### 11. **Package Diagram - Frontend** (`11-package-diagram-frontend.puml`)
- React application structure
- Pages, components, contexts, hooks, utils organization
- Configuration files
- Dependencies and relationships
- Component hierarchy

#### 12. **Class Diagram - Frontend** (`12-class-diagram-frontend.puml`)
- React components as classes
- Context providers: AuthContext, SocketContext, AudioContext
- Page components and UI components
- Custom hooks
- Type definitions
- Component relationships

#### 13. **Sequence Diagram - Speaker Turn Management** (`13-sequence-speaker-turn-management.puml`)
- Turn-based speaking flow
- Timer countdown (60 seconds default)
- Automatic and manual turn advancement
- LLM Agent turn integration
- Role change during discussion
- Discussion end conditions
- Visual UI cues

---

## Key Features Documented

### Architecture Focus
- **Backend:** server_py (Python FastAPI) as the target backend
- **Legacy:** server (Node.js) is being phased out but still functional
- **Database:** SQLite with async operations
- **Real-time:** Socket.io for WebSocket communication
- **Audio:** WebRTC for peer-to-peer audio streaming

### LLM Agent Integration
- **Facilitator Role:** DebateRoomFacilitator manages discussions
- **AI Provider:** Gemini Agent with AWS Strands/Bedrock support
- **MCP Integration:** Model Context Protocol for tool execution
- **CEFR Standards:** Common European Framework for language feedback
- **Feedback Types:** Grammar, vocabulary, sentence structure, pronunciation

### Real-time Features
- **Turn Management:** Timer-based speaking turns (60s default)
- **Audio Streaming:** WebRTC P2P with STUN servers
- **Live Updates:** Socket.io event broadcasting
- **State Sync:** Real-time participant and discussion state

### Data Persistence
- **Sessions:** Complete discussion records
- **Participants:** User participation tracking
- **Topics:** AI-generated and fallback topics
- **Analytics:** Usage statistics and trends
- **Progress:** User learning progress (future)

---

## PlantUML Features Used

### Diagram Types
- Component Diagrams
- Deployment Diagrams
- Class Diagrams
- Sequence Diagrams
- Activity Diagrams
- State Diagrams
- Use Case Diagrams
- ER Diagrams (using entity notation)
- Package Diagrams

### Styling & Conventions
- Consistent color schemes
- Clear relationships (dependency, composition, aggregation)
- Stereotypes for clarity (<<PK>>, <<FK>>, <<include>>, etc.)
- Comprehensive notes and annotations
- Hidden lines for layout optimization
- Actor-based sequence diagrams

---

## How to Use

### Viewing Diagrams

#### Option 1: PlantUML Online
Visit http://www.plantuml.com/plantuml/uml/ and paste diagram code

#### Option 2: VS Code Extension
1. Install "PlantUML" extension
2. Open `.puml` file
3. Press `Alt+D` to preview

#### Option 3: Generate Images
```bash
# Install PlantUML
sudo apt-get install plantuml

# Generate all diagrams
cd docs/diagrams/uml
plantuml *.puml

# This creates PNG images for all diagrams
```

### Integration with Documentation
All diagrams are referenced in:
- `/docs/README.md` - Main documentation index
- `/docs/Architecture/system-architecture.md` - Architecture documentation
- `/docs/diagrams/uml/README.md` - Diagram-specific documentation

---

## Documentation Structure

```
docs/
├── diagrams/
│   ├── uml/
│   │   ├── 01-component-diagram.puml
│   │   ├── 02-deployment-diagram.puml
│   │   ├── 03-class-diagram-backend.puml
│   │   ├── 04-sequence-user-join-discussion.puml
│   │   ├── 05-sequence-webrtc-audio.puml
│   │   ├── 06-sequence-llm-agent-interaction.puml
│   │   ├── 07-activity-discussion-lifecycle.puml
│   │   ├── 08-state-room-management.puml
│   │   ├── 09-usecase-diagram.puml
│   │   ├── 10-er-diagram-database.puml
│   │   ├── 11-package-diagram-frontend.puml
│   │   ├── 12-class-diagram-frontend.puml
│   │   ├── 13-sequence-speaker-turn-management.puml
│   │   ├── README.md (Comprehensive guide)
│   │   └── demo.wsd (Original demo)
│   └── png/ (Generated images)
└── Miscellaneous/
    └── UML_DIAGRAMS_SUMMARY.md (This file)
```

---

## Benefits

### For Developers
- **Quick Understanding:** Visual representation of complex systems
- **Onboarding:** New developers can quickly grasp architecture
- **Reference:** Easy to reference during development
- **Consistency:** Ensures implementation follows design

### For Architects
- **Design Documentation:** Complete system design in visual form
- **Decision Making:** Helps evaluate architectural choices
- **Communication:** Clear communication with stakeholders
- **Migration Planning:** Documents transition from Node.js to Python

### For QA/Testing
- **Test Planning:** Understanding flows for test case creation
- **Integration Testing:** Clear interaction patterns
- **Edge Cases:** State diagrams show all possible states
- **Coverage:** Comprehensive view of system capabilities

### For Documentation
- **Visual Learning:** Diagrams complement text documentation
- **Up-to-date:** Source-controlled diagrams stay current
- **Versioning:** Git tracks diagram changes
- **Searchable:** PlantUML text format is searchable

---

## Maintenance

### When to Update
- New features added
- Architecture changes
- API modifications
- Database schema updates
- Component refactoring

### Update Process
1. Edit relevant `.puml` file
2. Regenerate images: `plantuml filename.puml`
3. Update README if needed
4. Commit to Git
5. Review in PR

---

## Related Documentation

### Architecture Documentation
- `/docs/Architecture/system-architecture.md`
- `/docs/development.md`
- `/docs/Services/backend-services.md`

### API Documentation
- `/docs/API Reference/rest-api.md`
- `/docs/API Reference/websocket-api.md`

### Component Documentation
- `/docs/Component Reference/react-components.md`
- `/docs/Hooks API Reference/react-hooks.md`

### Migration Documentation
- `/docs/Miscellaneous/MIGRATION_GUIDE.md`
- `/docs/Miscellaneous/PYTHON_BACKEND_README.md`

---

## Technical Details

### PlantUML Version
- Version: 1.2024.x
- Format: `.puml` (PlantUML source files)
- Output: PNG, SVG, or other formats supported by PlantUML

### Diagram Standards
- **Naming Convention:** `##-descriptive-name.puml`
- **Colors:** Consistent color schemes across diagrams
- **Notes:** Comprehensive annotations
- **Layout:** Optimized for readability

### Dependencies
- **PlantUML:** For diagram generation
- **Graphviz:** Required by PlantUML (automatically installed)
- **Java:** PlantUML runs on JVM

---

## Future Enhancements

### Potential Additions
1. **Timing Diagrams:** For performance analysis
2. **Network Diagrams:** Detailed network architecture
3. **Security Diagrams:** Security architecture and flows
4. **Integration Diagrams:** Third-party service integrations
5. **Monitoring Diagrams:** Observability architecture

### Diagram Improvements
1. Add more detailed error handling flows
2. Document edge cases in sequence diagrams
3. Add performance considerations
4. Include security checkpoints
5. Document rollback procedures

---

## Conclusion

This comprehensive set of UML diagrams provides a complete visual documentation of the GupShup Cafe platform, with a focus on the **server_py (Python FastAPI backend)** and **LLM Agent integration**. The diagrams serve as a reference for development, testing, documentation, and future enhancements.

**Total Diagrams:** 13
**Total Use Cases:** 33
**Backend Focus:** server_py (Python FastAPI)
**Key Feature:** LLM Agent Facilitation with CEFR-based Feedback

---

**Maintained by:** Development Team
**Last Updated:** October 15, 2025
**Status:** Complete and Ready for Use
