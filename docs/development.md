# AI Roundtable Discussion Platform - Development Guide

## Project Overview

This is a full-stack web application that provides instant feedback to students participating in a gamified discussion experience with their peers on their English speaking skills for rapid growth in English. The LLM Agent provides corrective feedback to the participants for their English based on the CEFR standard.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Client  │    │  Python Backend │    │    Database     │
│                 │    │                 │    │                 │
│  - Login Page   │◄──►│  - Socket.io    │◄──►│  - Sessions     │
│  - Lobby Page   │    │  - FastAPI      │    │  - Participants │
│  - Roundtable   │    │  - LLM Agent    │    │  - Progress     │
│                 │    │  - STT/TTS      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  AI Services    │
                    │  AWS Strands/   │
                    │  Gemini/Bedrock │
                    └─────────────────┘
```

## Tech Stack

### Frontend (Client)
- **React 18** - Modern UI library
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Socket.io Client** - Real-time communication
- **Lucide React** - Beautiful icons

### Backend (Server)
- **Python** - Programming language
- **FastAPI** - Modern web framework
- **python-socketio** - Real-time WebSocket communication
- **Database** - Data persistence
- **AWS Strands/Gemini/Bedrock** - AI models for feedback
- **STT** - Speech-to-Text integration
- **TTS** - Text-to-Speech (used in Samyarth teams)

### AI & External Services
- **AWS Strands/Gemini** - AI services for development
- **Bedrock Models** - AI services for production
- **WebRTC** - Browser audio communication
- **AWS Deployment** - AWS AgentCore + EC2 (backend), AWS Amplify (frontend)

## Features

### 1. User Authentication
- Authentication to save user details and progress
- Anonymous display names for roundtable participation
- User progress tracking

### 2. Lobby System
- Wait for minimum participants (2+)
- Audio permission setup
- Real-time participant updates

### 3. Roundtable Interface
- Visual circular table with participant chairs
- Dynamic chair placement based on participant count
- Active speaker highlighting
- Turn-based speaking system

### 4. LLM Agent & Feedback
- LLM-agent to facilitate the conversation
- Corrective feedback based on CEFR standard
- STT to transcribe and send conversations to agent
- TTS for live conversations with agent
- Track student progress across English proficiency levels
- Save topics of interest for students

### 5. Speaking Management
- Timer-based turns (default 60 seconds)
- Automatic speaker rotation
- Audio level monitoring
- Mute/unmute controls

### 6. Real-time Communication
- Socket.io for instant updates
- WebRTC for voice communication
- Room-based session management

## Development Setup

### Prerequisites
- Node.js 18+ installed (for frontend)
- Python 3.11+ installed (for backend)
- Git for version control
- Modern web browser with WebRTC support

### Quick Start

1. **Install dependencies**:
   ```bash
   # Install frontend dependencies
   cd client && npm install
   
   # Install backend dependencies
   cd ../server_py
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   # Copy example files
   cp client/.env.example client/.env
   cp server_py/.env.example server_py/.env
   
   # Edit the .env files with your settings
   ```

3. **Start development servers**:
   ```bash
   # Start backend
   cd server_py
   python main.py
   
   # In another terminal, start frontend
   cd client
   npm run dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend: http://localhost:3003

### Environment Variables

#### Client (.env)
```env
VITE_API_URL=http://localhost:3003
VITE_SOCKET_URL=http://localhost:3003
```

#### Server (.env)
```env
PORT=3003
DATABASE_URL=./data/roundtable.db
MIN_PARTICIPANTS=2
DEFAULT_SPEAKING_TIME=60
```

## Project Structure

```
ai-roundtable-discussion/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── contexts/       # React contexts (Auth, Socket, Audio)
│   │   ├── pages/          # Main application pages
│   │   └── App.jsx         # Main app component
│   ├── public/             # Static assets
│   └── package.json
├── server_py/              # Python FastAPI backend
│   ├── src/
│   │   ├── ai/             # AI agent and feedback
│   │   ├── database/       # Database management
│   │   ├── routes/         # FastAPI routes
│   │   ├── socket/         # Socket.io handlers
│   │   └── main.py         # Main server file
│   └── requirements.txt
├── docs/                   # Documentation
└── README.md
```

## Core Components

### Client Components

#### `LoginPage.jsx`
- User authentication form
- Anonymous name generation
- Input validation

#### `LobbyPage.jsx`
- Waiting area for participants
- Audio setup and permissions
- Real-time participant list

#### `RoundtablePage.jsx`
- Main discussion interface
- Integrates all discussion components

#### `RoundtableView.jsx`
- Visual representation of the roundtable
- Dynamic chair positioning
- Active speaker highlighting

#### Context Providers

#### `AuthContext.jsx`
- User authentication state
- Login/logout functionality
- Local storage persistence

#### `SocketContext.jsx`
- WebSocket connection management
- Real-time event handling
- Room management

#### `AudioContext.jsx`
- WebRTC audio management
- Microphone permissions
- Audio level monitoring

### Server Modules

#### `socketHandlers.py`
- Real-time event management
- Room joining/leaving
- Speaking turn management
- Timer coordination

#### `roomManager.py`
- In-memory room state management
- Participant tracking
- Discussion state coordination

#### `llmAgent.py`
- LLM-based conversation facilitation
- CEFR-based corrective feedback
- Student progress tracking
- Topic interest management

#### `database.py`
- Database operations
- Session analytics
- Participant tracking
- Progress persistence

## Real-time Communication Flow

### 1. User Login & Join Lobby
```
Client                    Server
  │                        │
  │── login(userData) ────►│
  │◄── authenticated ──────│
  │                        │
  │── connect socket ─────►│
  │── join-room('general')►│
  │◄── participants-update─│
```

### 2. Discussion Start
```
Client                    Server                   AI
  │                        │                       │
  │── user-ready ─────────►│                       │
  │                        │── get feedback ──────►│
  │                        │◄── CEFR feedback ────│
  │◄── discussion-started ─│                       │
  │◄── speaker-changed ────│                       │
```

### 3. Speaking Turn Management
```
Client                    Server
  │                        │
  │◄── timer-update ───────│ (every second)
  │                        │
  │                        │ (time expires)
  │◄── speaker-changed ────│
  │                        │
  │── next-speaker ───────►│ (manual advance)
```

## AI Integration

### LLM Agent Setup

1. **AI Services Configuration**:
   - Development: AWS Strands + Gemini
   - Production: Bedrock Models
   
2. **Configure Environment**:
   ```env
   AI_SERVICE=gemini  # or bedrock
   AI_API_KEY=your_api_key_here
   ```

3. **CEFR Standard Integration**:
   - Real-time feedback on English speaking
   - Progress tracking across proficiency levels
   - Topic interest tracking for personalization

### STT/TTS Integration

1. **Speech-to-Text**: Transcribe user conversations
2. **Text-to-Speech**: Agent responses using Samyarth TTS
3. **Real-time Processing**: Low-latency feedback loop

## Database Schema

### Sessions Table
```sql
sessions (
  id TEXT PRIMARY KEY,
  room_id TEXT,
  topic_title TEXT,
  participant_count INTEGER,
  started_at DATETIME,
  ended_at DATETIME,
  duration_seconds INTEGER,
  rounds_completed INTEGER
)
```

### Participants Table
```sql
participants (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  user_id TEXT,
  anonymous_name TEXT,
  campus TEXT,
  location TEXT,
  joined_at DATETIME,
  speaking_time_seconds INTEGER,
  cefr_level TEXT,
  progress_data TEXT
)
```

### Progress Table
```sql
progress (
  id TEXT PRIMARY KEY,
  user_id TEXT,
  cefr_level TEXT,
  topics_of_interest TEXT,
  last_updated DATETIME,
  feedback_history TEXT
)
```

## API Endpoints

### Public Endpoints
- `GET /health` - Health check
- `GET /api/config` - Public configuration

### LLM Agent Endpoints
- `POST /api/feedback` - Get CEFR-based feedback
- `GET /api/progress/:userId` - Get user progress
- `POST /api/topics/interest` - Update topics of interest

### Analytics Endpoints
- `GET /api/analytics/sessions` - Session analytics
- `GET /api/analytics/topics` - Topic usage stats
- `GET /api/analytics/stats` - Server statistics

## Security Considerations

### Client-side
- Input validation on all forms
- XSS prevention with React's built-in protection
- No sensitive data in localStorage

### Server-side
- Helmet.js for security headers
- CORS configuration
- Input sanitization
- Rate limiting (recommended for production)

### WebRTC
- Secure media streams
- No persistent audio recording
- User consent for microphone access

## Performance Optimizations

### Frontend
- Lazy loading of routes
- Memoized components where appropriate
- Efficient re-renders with proper dependency arrays

### Backend
- In-memory room management for speed
- Database for data persistence
- Efficient Socket.io event handling

### Network
- WebSocket for real-time updates
- RESTful API for stateless operations
- Minimal data transfer

## Testing Strategy

### Manual Testing Checklist

#### Authentication Flow
- [ ] Valid login with all fields
- [ ] Input validation errors
- [ ] Anonymous name suggestions
- [ ] Login persistence

#### Lobby Functionality
- [ ] Participant join/leave
- [ ] Audio permission handling
- [ ] Ready state management
- [ ] Discussion start trigger

#### Roundtable Discussion
- [ ] Visual chair positioning
- [ ] Speaker highlighting
- [ ] Timer functionality
- [ ] Turn advancement
- [ ] Audio controls

#### Cross-browser Testing
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (macOS)
- [ ] Edge

### Automated Testing (Future Enhancement)
- Unit tests for utility functions
- Integration tests for Socket.io events
- E2E tests for user flows

## Deployment Guide

See [server_py/DEPLOYMENT.md](../server_py/DEPLOYMENT.md) for detailed deployment instructions for AWS EC2 and AWS Amplify.

## Contributing

### Code Style
- Use ESLint configuration
- Follow React best practices
- Add comments for complex logic
- Keep functions small and focused

### Git Workflow
```bash
git checkout -b feature/your-feature
# Make changes
git commit -m "Add: your feature description"
git push origin feature/your-feature
# Create pull request
```

## Troubleshooting

### Common Issues

#### Socket Connection Failed
- Check if backend server is running
- Verify CORS configuration
- Check network connectivity

#### Audio Not Working
- Ensure HTTPS for WebRTC (in production)
- Check browser microphone permissions
- Test with different browsers

#### AI Topics Not Generating
- Verify AI service API key
- Check API rate limits
- Check service status

### Debug Mode
```bash
# Enable debug logging
DEBUG=socket.io* npm run dev
```

## Future Enhancements

### Phase 2 Features
- [ ] Breakout rooms
- [ ] Screen sharing
- [ ] Chat functionality
- [ ] Recording capabilities
- [ ] Mobile app

### Analytics & Insights
- [ ] Participation metrics
- [ ] Topic popularity
- [ ] User engagement
- [ ] Export capabilities

### AI Improvements
- [ ] Enhanced CEFR assessment accuracy
- [ ] Personalized learning paths
- [ ] Sentiment analysis
- [ ] Multi-language support

## Support

For questions or issues:
1. Check this documentation
2. Review the code comments
3. Test with the example configurations
4. Create an issue with detailed information

This platform is designed for educational use and continuous improvement. Contributions and feedback are welcome!
