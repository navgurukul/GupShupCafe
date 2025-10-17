# GupShup Cafe - New Implementation

This is the new implementation of GupShup Cafe with a modern React frontend and FastAPI backend.

## Features

### Frontend (client-1)
- **React 18** with modern hooks and context
- **Tailwind CSS** for responsive, beautiful UI
- **Socket.IO Client** for real-time communication
- **React Router** for navigation
- **React Hook Form** for form handling
- **Audio Context API** for microphone integration

### Backend (server-ani)
- **FastAPI** for high-performance API
- **Socket.IO** for real-time communication
- **JWT Authentication** with secure token handling
- **File-based storage** (JSON) for user data
- **WebRTC** support for audio streaming

### Audio Features
- **Web Audio API** for audio processing and level monitoring
- **Real-time audio level visualization**
- **Microphone mute/unmute controls**
- **Audio device selection**
- **Speaking timer** for fair discussion time

## Project Structure

```
client-1/                 # Frontend React application
├── src/
│   ├── components/       # Reusable React components
│   ├── contexts/         # React context providers
│   ├── pages/           # Main application pages
│   └── data/            # Static data and topics
│
server-ani/              # Backend FastAPI application
├── main.py             # Main server file
├── data/               # Data storage
│   ├── data.json       # User and room data
│   └── topics.json     # Discussion topics
└── requirements.txt    # Python dependencies
```

## Setup Instructions

1. **Run the setup script:**
   ```bash
   chmod +x setup-new.sh
   ./setup-new.sh
   ```

2. **Manual setup (alternative):**

   **Backend:**
   ```bash
   cd server-ani
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   **Frontend:**
   ```bash
   cd client-1
   npm install
   ```

## Running the Application

1. **Start the backend:**
   ```bash
   cd server-ani
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python main.py
   ```

2. **Start the frontend:**
   ```bash
   cd client-1
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## User Journey

### 1. Registration/Login
- Users can sign up with name, email, password, and interests
- Multiple interest categories can be selected:
  - Current Affairs
  - Science & Technology
  - Literature
  - Education
  - Generative AI

### 2. Dashboard
- View available discussion rooms
- See participant counts and room capacity
- Create new custom rooms
- Audio level indicator shows microphone status

### 3. Room Types
- **Education** - Educational topics and learning discussions
- **Science & Technology** - Latest innovations and tech trends
- **Literature** - Books, writing, and literary analysis
- **Generative AI** - AI ethics, innovations, and implications

### 4. Discussion Flow
1. Join a room (up to 8 participants)
2. Click "Ready" when prepared to start
3. System assigns a random topic from the room's category
4. Speaking order is randomized
5. Each person gets a turn to speak
6. Speaking timer ensures fair discussion time
7. Room resets after everyone has spoken

## Audio Technology

### Web Audio API Integration
- **AudioContext** for audio processing pipeline
- **AnalyserNode** for real-time audio level analysis
- **MediaStreamSource** for microphone input processing
- **Real-time visualization** of audio levels

### WebRTC Features
- **Peer-to-peer** audio communication
- **MediaStream API** for audio capture
- **Optimized for 4-8 participants** (small rooms)
- **Scalable to 15-25 participants** with proper infrastructure

### Room Capacity Limits
- **Small rooms**: 4-8 participants (optimal voice quality)
- **Medium rooms**: 8-15 participants 
- **Large rooms**: 15-25 participants (requires media server)

## Topic Categories

### Current Affairs (10 topics)
- Climate change initiatives
- AI impact on elections
- Global economy discussions
- Social media misinformation
- And more...

### Science & Technology (10 topics)
- Quantum computing breakthroughs
- 5G technology impact
- Gene editing ethics
- Renewable energy access
- And more...

### Literature (10 topics)
- Digital media's impact on reading
- Timeless storytelling
- AI in creative writing
- Literature's role in social change
- And more...

### Education (10 topics)
- Global education accessibility
- Technology in classrooms
- Adapting to job market changes
- Online learning benefits/challenges
- And more...

### Generative AI (10 topics)
- Impact on creative industries
- Ethical considerations
- Content detection challenges
- Journalism implications
- And more...

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/user/me` - Get current user info

### Rooms
- `GET /api/rooms` - List available rooms

### Socket.IO Events
- `join_room` - Join a discussion room
- `leave_room` - Leave current room
- `user_ready` - Mark user as ready
- `start_speaking` - Begin speaking session
- `next_speaker` - Move to next speaker
- `create_room` - Create custom room

## Security Features

- **JWT token authentication**
- **Password hashing** with bcrypt
- **CORS protection**
- **Socket.IO authentication**
- **Secure token validation**

## Development

### Frontend Development
```bash
cd client-1
npm run dev      # Start development server
npm run build    # Build for production
npm run lint     # Run ESLint
```

### Backend Development
```bash
cd server-ani
python main.py   # Start development server
```

### Key Dependencies

**Frontend:**
- React 18.2.0
- Vite 4.4.5
- Tailwind CSS 3.3.3
- Socket.IO Client 4.7.2
- React Router Dom 6.8.1

**Backend:**
- FastAPI 0.104.1
- Python-SocketIO 5.9.0
- Python-JOSE 3.3.0
- Passlib 1.7.4
- Uvicorn 0.24.0

## Future Enhancements

1. **Database Integration** (PostgreSQL/MongoDB)
2. **File Upload** for profile pictures
3. **Room Recording** capabilities
4. **Advanced Audio Processing** (noise cancellation)
5. **Mobile App** (React Native)
6. **Video Chat** integration
7. **Moderation Tools** for room management
8. **Analytics Dashboard** for usage insights

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in configuration files
2. **Audio not working**: Check browser permissions for microphone
3. **Connection issues**: Verify CORS settings
4. **Token errors**: Clear localStorage and re-login

### Browser Requirements
- Modern browsers with WebRTC support
- Microphone permissions required
- JavaScript enabled

This implementation provides a solid foundation for a modern voice-based discussion platform with room for scalability and additional features.
