# FastAPI Backend Server

Python FastAPI backend for AI Roundtable Discussion Platform with WebSocket support via Socket.io.

## Features

- ✅ RESTful API with FastAPI
- ✅ Real-time WebSocket communication (Socket.io)
- ✅ SQLite database with async support
- ✅ AI topic generation (Hugging Face)
- ✅ **LLM Agent Integration** - AI Tutor as default participant
- ✅ Room management system
- ✅ AWS EC2 deployment ready
- ✅ Docker support

## Tech Stack

- **FastAPI** - Modern Python web framework
- **python-socketio** - WebSocket support compatible with Socket.io clients
- **aiosqlite** - Async SQLite database
- **httpx** - Async HTTP client for AI API
- **uvicorn** - ASGI server

## Requirements

- Python 3.11+
- pip

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

### Run Development Server

```bash
# Start server with hot reload
python -m uvicorn main:socket_app --reload --port 3003

# Or run directly
python main.py
```

The server will start on http://localhost:3003

## API Endpoints

### Health Check
- `GET /health` - Server health status
- `GET /` - Server information

### Topics
- `GET /api/topics` - Get all fallback topics
- `GET /api/topics/generate` - Generate new AI topic
- `GET /api/topics/category/{category}` - Get topic by category

### Analytics
- `GET /api/analytics/sessions` - Get session analytics
- `GET /api/analytics/topics` - Get topic usage statistics
- `GET /api/analytics/stats` - Get server statistics

### Room
- `GET /api/room/{roomId}/state` - Get room state

### Configuration
- `GET /api/config` - Get public configuration

### Feedback
- `POST /api/feedback` - Submit user feedback

## WebSocket Events

### Client → Server
- `join-room` - Join a discussion room
- `user-ready` - Mark user as ready
- `change-role` - Change between speaker/listener
- `message` - Send chat message

### Server → Client
- `participants-update` - Updated participant list
- `discussion-started` - Discussion has started
- `role-changed` - Role change confirmation
- `user-left` - User disconnected

## Project Structure

```
server_py/
├── src/
│   ├── api/
│   │   └── routes.py          # FastAPI routes
│   ├── database/
│   │   └── database.py        # Database operations
│   ├── socket/
│   │   ├── socket_handlers.py # Socket.io event handlers
│   │   └── room_manager.py    # Room state management
│   └── ai/
│       └── topic_generator.py # AI topic generation
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── gupshup-api.service       # Systemd service file
└── DEPLOYMENT.md             # Deployment guide
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| PORT | Server port | 3003 |
| PYTHON_ENV | Environment (development/production) | development |
| ALLOWED_ORIGINS | Comma-separated CORS origins | localhost:5173,localhost:5174 |
| DATABASE_URL | SQLite database path | ./data/roundtable.db |
| HUGGINGFACE_API_KEY | Hugging Face API key | - |
| **ENABLE_LLM_AGENT** | Enable AI Tutor as participant | false |
| DEFAULT_SPEAKING_TIME | Speaking time in seconds | 60 |
| MIN_PARTICIPANTS | Minimum participants to start | 1 |
| MAX_PARTICIPANTS | Maximum participants per room | 8 |

## LLM Agent Integration

The platform includes an **AI Tutor** that can participate in discussions as a default participant:

### Features
- 🤖 Automatic participation in discussions
- 📚 Discussion facilitation and guidance
- 🗣️ English language feedback
- 💡 Thought-provoking questions
- 🔍 Fact-checking and observations

### Quick Start

Enable the LLM Agent:
```bash
echo "ENABLE_LLM_AGENT=true" >> .env
python main.py
```

### API Endpoints

Check agent status:
```bash
GET /api/llm-agent/status
```

Trigger agent response:
```bash
POST /api/llm-agent/response/{room_id}
```

For complete documentation, see [LLM Agent Integration Guide](../docs/LLM_AGENT_INTEGRATION.md).

## Development

### Code Style

The codebase follows Python best practices:
- Type hints where applicable
- Docstrings for functions and classes
- Async/await for I/O operations

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_llm_agent.py

# Run with coverage
pytest --cov=src
```

Current test coverage: **56 tests** including:
- 15 LLM Agent service tests
- 7 AI/topic generation tests
- 17 API endpoint tests
- 7 Database tests
- 10 Room manager tests

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions for:
- AWS EC2 (with systemd)
- Docker
- Nginx reverse proxy
- SSL/HTTPS setup

### Quick Deploy to EC2

```bash
# 1. SSH to EC2
ssh -i key.pem ubuntu@your-ec2-ip

# 2. Install dependencies
sudo apt update && sudo apt install -y python3.11 python3-pip git

# 3. Clone and setup
git clone https://github.com/navgurukul/GupShupCafe.git
cd GupShupCafe/server_py
pip install -r requirements.txt

# 4. Configure .env

# 5. Run with systemd
sudo cp gupshup-api.service /etc/systemd/system/
sudo systemctl enable gupshup-api
sudo systemctl start gupshup-api
```

## Migration from Node.js

This Python backend is a complete rewrite of the Node.js Express backend with the following benefits:

1. **Type Safety** - Better type hints with Python
2. **Async Performance** - Native async/await support
3. **Easier Deployment** - Simpler dependency management
4. **AWS EC2 Ready** - Includes systemd service and deployment guides

The API contract remains the same, so no frontend changes are required.

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 3003
lsof -i :3003

# Kill the process
kill -9 <PID>
```

### Database Locked
```bash
# Ensure data directory has proper permissions
chmod 755 data/
chmod 644 data/roundtable.db
```

### Socket.io Connection Issues
- Check CORS settings in .env
- Verify frontend is connecting to correct URL
- Check firewall rules

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

See main repository LICENSE file.
