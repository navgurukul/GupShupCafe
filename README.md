# 🎯 AI Gupshup Platform

An **innovative educational platform** that provides instant feedback to students participating in a gamified discussion experience with their peers on their English speaking skills for rapid growth in English. The LLM Agent provides corrective feedback to the participants for their English based on the CEFR standard.

## ✨ Features
- 🎤 **Real-time collaborative discussions** with voice controls
- 🤖 **LLM-agent to facilitate the conversation**
- 🔈 **TTS for live conversations** with agent
- 📝 **STT to transcribe and send conversations** to the agent
- 👥 **Turn-based speaking management** with visual feedback
- 📱 **Mobile-responsive design** for all devices
- 🔒 **WebRTC audio** with microphone controls
- 🎨 **Gamified UI** with animations, audio and visual effects
- 🔐 **Authentication to save user details and progress**
- 👤 **Anonymous participation** across the roundtable
- 📊 **CEFR standard tracking** for English progress and topics of interest

## 🚀 Tech Stack
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: Python: FastAPI + python-socketio
- **Database**: Database (Let's rethink on this)
- **Real-time Voice of participants**: Socket.io + WebRTC
- **AI**: AWS Strands + Gemini (for development) / Bedrock Models (for production)
- **STT**: Speech-to-Text integration
- **TTS**: TTS used in Samyarth teams
- **Backend Deployment**: AWS AgentCore + EC2 (backend)
- **Frontend Deployment**: AWS Amplify accessing backend using APIs

## 📦 Quick Start

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- npm or yarn

### Installation

```bash
# Install frontend dependencies
cd client && npm install

# Install Python backend dependencies
cd ../server_py
pip install -r requirements.txt

# Start Python backend
python main.py

# In another terminal, start frontend
cd ../client
npm run dev
```

### Access
- **Frontend**: http://localhost:5173
- **Backend (Python)**: http://localhost:3003

## 🌐 Deployment
- **Python Backend**: See [server_py/DEPLOYMENT.md](./server_py/DEPLOYMENT.md) for AWS EC2 deployment instructions
- **Frontend**: AWS Amplify deployment accessing backend using APIs

## 📁 Project Structure
```
├── client/          # React frontend
├── server_py/       # Python FastAPI backend
├── docs/            # Documentation
└── README.md        # This file
```

## 🎓 Educational Use Cases
- **English Speaking Skills**: Instant feedback based on CEFR standards
- **Language Learning**: Gamified conversation practice with peers
- **Progress Tracking**: Save student progress and topics of interest
- **Virtual Classrooms**: Structured online discussions
- **Debate Practice**: Turn-based speaking with timers

## 📄 License
Open source - see individual files for specific licensing.