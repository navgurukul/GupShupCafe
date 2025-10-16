# GupShup Cafe - UML Diagrams Quick Reference

This is a quick reference guide to all UML diagrams in the project.

## 📊 Diagrams at a Glance

| # | Diagram Name | File | Type | Lines | Status |
|---|--------------|------|------|-------|--------|
| 1 | Class Diagram | `class-diagram.puml` | Class | 328 | ✅ |
| 2 | Component Diagram | `component-diagram.puml` | Component | 199 | ✅ |
| 3 | Login & Join Sequence | `sequence-login-join.puml` | Sequence | 160 | ✅ |
| 4 | Discussion Management Sequence | `sequence-discussion.puml` | Sequence | 207 | ✅ |
| 5 | WebRTC Audio Sequence | `sequence-webrtc.puml` | Sequence | 243 | ✅ |
| 6 | Activity Diagram | `activity-diagram.puml` | Activity | 205 | ✅ |
| 7 | Deployment Diagram | `deployment-diagram.puml` | Deployment | 206 | ✅ |
| 8 | Use Case Diagram | `use-case-diagram.puml` | Use Case | 229 | ✅ |
| 9 | State Diagram | `state-diagram.puml` | State | 210 | ✅ |
| 10 | Package Diagram | `package-diagram.puml` | Package | 274 | ✅ |
| 11 | Database Schema | `database-schema.puml` | ER Diagram | 208 | ✅ |

**Total:** 2,469 lines of PlantUML code

## 🎯 When to Use Each Diagram

### Understanding Structure
- **Class Diagram** → See all classes, their properties, methods, and relationships
- **Package Diagram** → Understand code organization and module dependencies
- **Database Schema** → View data model and table relationships

### Understanding Architecture
- **Component Diagram** → See high-level system architecture and deployment
- **Deployment Diagram** → Understand physical deployment and infrastructure

### Understanding Behavior
- **Sequence Diagrams** (3 total):
  - Login & Join → User authentication and room joining
  - Discussion Management → Discussion lifecycle and speaker rotation
  - WebRTC Audio → Peer-to-peer audio connection setup
- **Activity Diagram** → Complete user journey from login to logout
- **State Diagram** → Room and discussion state transitions

### Understanding Interactions
- **Use Case Diagram** → All user roles and their interactions (36 use cases)

## 🚀 Quick Start

### View Online
```
1. Go to: http://www.plantuml.com/plantuml/uml/
2. Open any .puml file from docs/diagrams/uml/
3. Copy and paste the content
4. View the rendered diagram
```

### Generate Images Locally
```bash
# Install PlantUML (one-time)
brew install plantuml  # macOS
sudo apt-get install plantuml  # Ubuntu/Debian

# Navigate to diagrams directory
cd docs/diagrams/uml

# Generate all diagrams as PNG
plantuml *.puml

# Generate all diagrams as SVG (scalable)
plantuml -tsvg *.puml

# Generate specific diagram
plantuml class-diagram.puml
```

### View in VS Code
```
1. Install "PlantUML" extension by jebbs
2. Open any .puml file
3. Press Alt+D (Windows/Linux) or Option+D (macOS)
4. Preview pane will show the diagram
```

## 📖 Key Concepts Explained

### Backend (Server)
```
Server → Express + Socket.io + SQLite
├── Socket Handlers → Real-time event management
├── Room Manager → In-memory room state (singleton)
├── Topic Generator → AI + fallback topics
└── Database → Session analytics and persistence
```

### Frontend (Client)
```
React App → Pages + Components + Contexts
├── Auth Context → User authentication state
├── Socket Context → Real-time WebSocket connection
└── Audio Context → WebRTC peer connections
```

### Communication Flow
```
User → Browser → Socket.io → Server → Room Manager
                      ↓
                  WebRTC (P2P Audio)
                      ↓
                  Other Users
```

### Discussion Flow
```
Login → Lobby → Audio Setup → Ready
  → Discussion Start → Topic Generation
  → Speaking Turns (60s each)
  → 3 Rounds
  → Discussion End → Back to Lobby
```

## 🔍 Finding Specific Information

| Want to know... | See diagram... |
|----------------|----------------|
| How classes are organized | Class Diagram |
| How components interact | Component Diagram |
| How user logs in and joins | Login & Join Sequence |
| How discussions work | Discussion Management Sequence |
| How audio works | WebRTC Audio Sequence |
| What users can do | Use Case Diagram |
| Where code is deployed | Deployment Diagram |
| How data is stored | Database Schema |
| What states exist | State Diagram |
| Complete user journey | Activity Diagram |
| Code structure | Package Diagram |

## 🎨 Diagram Features

All diagrams include:
- ✅ Latest PlantUML syntax (v1.2024.7)
- ✅ Cerulean theme (professional blue color scheme)
- ✅ Comprehensive notes and explanations
- ✅ Clear relationships and connections
- ✅ Consistent naming conventions
- ✅ Error-free validated syntax
- ✅ Production-ready documentation

## 📚 Additional Resources

- **README.md** - Complete documentation with detailed descriptions
- **DIAGRAM_SUMMARY.md** - Comprehensive overview and validation details
- **PlantUML Documentation** - https://plantuml.com/
- **Project README** - ../../README.md

## ✨ Tips

1. **Start with Component Diagram** for overall architecture
2. **Use Sequence Diagrams** to understand specific workflows
3. **Check State Diagram** to understand system behavior
4. **Reference Class Diagram** when coding
5. **Consult Database Schema** for data queries

## 🔧 Maintenance

To update diagrams:
```bash
# 1. Edit the .puml file
vim class-diagram.puml

# 2. Validate syntax
java -jar plantuml.jar -syntax class-diagram.puml

# 3. Regenerate image
plantuml -tsvg class-diagram.puml

# 4. Commit changes
git add class-diagram.puml class-diagram.svg
git commit -m "Update class diagram"
```

## 📊 Statistics

- **Total Diagrams:** 11
- **Total Lines of Code:** 2,469
- **Documentation Lines:** 533
- **Grand Total:** 3,002 lines
- **Validation:** All passed ✅
- **PlantUML Version:** v1.2024.7
- **Theme:** Cerulean
- **Status:** Complete and Production-Ready

---

**Created:** October 2024  
**Validated:** PlantUML v1.2024.7  
**Status:** Complete ✅
