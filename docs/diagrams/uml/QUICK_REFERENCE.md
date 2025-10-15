# Quick Reference Guide - UML Diagrams

**Location:** `/docs/diagrams/uml/`
**Total Diagrams:** 13 PlantUML diagrams
**Total Lines:** ~2,700 lines of PlantUML code

---

## 🚀 Quick Start

### View Diagrams Online (Easiest)
1. Go to http://www.plantuml.com/plantuml/uml/
2. Copy the content of any `.puml` file
3. Paste and view instantly

### View in VS Code (Recommended for Development)
1. Install the **PlantUML** extension by jebbs
2. Open any `.puml` file
3. Press `Alt+D` to open preview
4. Press `Ctrl+Shift+P` and search "PlantUML: Preview Current Diagram"

### Generate PNG Images
```bash
# Install PlantUML (one-time setup)
sudo apt-get update
sudo apt-get install plantuml

# Navigate to diagrams directory
cd /home/runner/work/GupShupCafe/GupShupCafe/docs/diagrams/uml/

# Generate all PNG images
plantuml *.puml

# Generate specific diagram
plantuml 01-component-diagram.puml

# Generate as SVG (scalable)
plantuml -tsvg 01-component-diagram.puml
```

---

## 📊 Diagram Quick Reference

### 1️⃣ Component Diagram
**File:** `01-component-diagram.puml`
**Best For:** Understanding overall system architecture
**Shows:** All layers (Client, Communication, Server, Data)

### 2️⃣ Deployment Diagram
**File:** `02-deployment-diagram.puml`
**Best For:** Setting up environments
**Shows:** Dev setup (local) and Prod setup (AWS)

### 3️⃣ Class Diagram - Backend
**File:** `03-class-diagram-backend.puml`
**Best For:** Backend development in server_py
**Shows:** Python classes, relationships, methods

### 4️⃣ Sequence - User Join
**File:** `04-sequence-user-join-discussion.puml`
**Best For:** Understanding user onboarding flow
**Shows:** Login → Lobby → Discussion Start

### 5️⃣ Sequence - WebRTC
**File:** `05-sequence-webrtc-audio.puml`
**Best For:** Debugging audio issues
**Shows:** P2P audio connection setup

### 6️⃣ Sequence - LLM Agent
**File:** `06-sequence-llm-agent-interaction.puml`
**Best For:** Understanding AI integration
**Shows:** Agent initialization, feedback, MCP

### 7️⃣ Activity Diagram
**File:** `07-activity-discussion-lifecycle.puml`
**Best For:** Complete flow understanding
**Shows:** End-to-end discussion lifecycle

### 8️⃣ State Diagram
**File:** `08-state-room-management.puml`
**Best For:** Room state debugging
**Shows:** All room states and transitions

### 9️⃣ Use Case Diagram
**File:** `09-usecase-diagram.puml`
**Best For:** Feature planning
**Shows:** 33 use cases across 7 packages

### 🔟 ER Diagram
**File:** `10-er-diagram-database.puml`
**Best For:** Database development
**Shows:** Tables, relationships, constraints

### 1️⃣1️⃣ Package Diagram - Frontend
**File:** `11-package-diagram-frontend.puml`
**Best For:** Frontend architecture
**Shows:** React app structure and organization

### 1️⃣2️⃣ Class Diagram - Frontend
**File:** `12-class-diagram-frontend.puml`
**Best For:** Frontend development
**Shows:** React components, contexts, hooks

### 1️⃣3️⃣ Sequence - Turn Management
**File:** `13-sequence-speaker-turn-management.puml`
**Best For:** Understanding speaking turns
**Shows:** Timer, turn rotation, agent turns

---

## 🎯 Common Use Cases

### I want to understand the overall architecture
→ Start with **01-component-diagram.puml**

### I'm setting up the project
→ Check **02-deployment-diagram.puml**

### I'm developing backend features
→ Reference **03-class-diagram-backend.puml**

### I'm implementing user flow
→ Use **04-sequence-user-join-discussion.puml**

### Audio isn't working
→ Debug with **05-sequence-webrtc-audio.puml**

### I'm integrating LLM features
→ Follow **06-sequence-llm-agent-interaction.puml**

### I need to understand the full flow
→ Study **07-activity-discussion-lifecycle.puml**

### Room state is confusing
→ Refer to **08-state-room-management.puml**

### I'm planning new features
→ Check **09-usecase-diagram.puml**

### I'm working with the database
→ Use **10-er-diagram-database.puml**

### I'm developing React components
→ Reference **11-package-diagram-frontend.puml** and **12-class-diagram-frontend.puml**

### Turn management is unclear
→ Follow **13-sequence-speaker-turn-management.puml**

---

## 🔍 Finding Specific Information

### Architecture Questions
- **What components exist?** → Component Diagram
- **How are they connected?** → Component Diagram
- **Where is it deployed?** → Deployment Diagram

### Development Questions
- **What classes exist?** → Class Diagrams (03, 12)
- **What methods are available?** → Class Diagrams (03, 12)
- **How do components interact?** → Sequence Diagrams (04-06, 13)

### Database Questions
- **What tables exist?** → ER Diagram (10)
- **What are the relationships?** → ER Diagram (10)
- **What are the fields?** → ER Diagram (10)

### Flow Questions
- **How does a user join?** → Sequence Diagram (04)
- **How does audio work?** → Sequence Diagram (05)
- **How does the agent work?** → Sequence Diagram (06)
- **How do turns work?** → Sequence Diagram (13)
- **What's the complete flow?** → Activity Diagram (07)

### State Questions
- **What states exist?** → State Diagram (08)
- **How do states transition?** → State Diagram (08)
- **What triggers transitions?** → State Diagram (08)

---

## 💡 Tips for Using Diagrams

### For New Team Members
1. Start with **Component Diagram** (01) for big picture
2. Review **Deployment Diagram** (02) for setup
3. Study **Use Case Diagram** (09) for features
4. Deep dive into specific areas as needed

### For Backend Developers
1. **Class Diagram - Backend** (03) is your main reference
2. Use **Sequence - LLM Agent** (06) for AI features
3. Refer to **ER Diagram** (10) for database work

### For Frontend Developers
1. **Package Diagram** (11) shows structure
2. **Class Diagram - Frontend** (12) shows components
3. **Sequence Diagrams** show interaction patterns

### For QA/Testing
1. **Use Case Diagram** (09) lists all scenarios
2. **Sequence Diagrams** show expected flows
3. **State Diagram** (08) shows all possible states
4. **Activity Diagram** (07) shows complete lifecycle

---

## 📚 Documentation Links

- **Full Documentation:** [/docs/diagrams/uml/README.md](README.md)
- **Summary:** [/docs/Miscellaneous/UML_DIAGRAMS_SUMMARY.md](../Miscellaneous/UML_DIAGRAMS_SUMMARY.md)
- **Main Docs:** [/docs/README.md](../README.md)
- **Architecture:** [/docs/Architecture/system-architecture.md](../Architecture/system-architecture.md)

---

## 🛠️ Tools & Resources

### PlantUML Resources
- Official Site: https://plantuml.com/
- Online Editor: http://www.plantuml.com/plantuml/uml/
- Documentation: https://plantuml.com/guide
- Syntax Guide: https://plantuml.com/sitemap-language-specification

### VS Code Extensions
- **PlantUML** by jebbs (recommended)
- **PlantUML Syntax** for syntax highlighting
- **Markdown Preview Enhanced** for inline diagrams

### Command Line Tools
```bash
# PlantUML CLI
sudo apt-get install plantuml

# GraphViz (required by PlantUML)
sudo apt-get install graphviz

# View generated images
eog diagram.png  # Ubuntu
open diagram.png # macOS
```

---

## 🔄 Keeping Diagrams Updated

### When to Update
- New feature added → Update relevant diagrams
- API changed → Update sequence/class diagrams
- Database schema changed → Update ER diagram
- Architecture changed → Update component/deployment diagrams

### How to Update
1. Edit the `.puml` file
2. Regenerate images: `plantuml filename.puml`
3. Review in preview
4. Commit to Git
5. Update documentation if needed

---

## ✅ Checklist for Using Diagrams

- [ ] I know where the diagrams are located (`/docs/diagrams/uml/`)
- [ ] I can view diagrams (online or VS Code)
- [ ] I know which diagram to use for my task
- [ ] I understand the diagram conventions
- [ ] I can generate PNG images if needed
- [ ] I know how to update diagrams

---

**Happy Diagramming! 🎨**

For questions or issues, refer to the [full README](README.md) or open an issue on GitHub.
