# 🎯 AI Gupshup Platform

A **full-stack educational web application** for AI-powered roundtable discussions.

## ✨ Features
- 🎤 **Real-time collaborative discussions** with voice controls
- 🤖 **AI-generated topics** using Hugging Face API
- 👥 **Turn-based speaking management** with visual feedback
- 📱 **Mobile-responsive design** for all devices
- 🔒 **WebRTC audio** with microphone controls
- 🎨 **Professional UI** with animations and visual effects
- 💯 **100% free and open source**

## 🚀 Tech Stack
- **Frontend**: React 18 + Vite + Tailwind CSS
- **Backend**: 
  - **Node.js** (original): Express + Socket.io
  - **Python** (new): FastAPI + python-socketio
- **Database**: SQLite
- **Real-time**: Socket.io + WebRTC
- **AI**: Hugging Face Inference API
- **Deployment**: Vercel (frontend) + Render/AWS EC2 (backend)

## 📦 Quick Start

### Prerequisites
- Node.js 18+ (for Node.js backend or frontend)
- Python 3.11+ (for Python backend)
- npm or yarn

### Installation

#### Option 1: Node.js Backend (Original)
```bash
# Install dependencies
npm run install:all

# Start development servers
npm run dev
```

#### Option 2: Python FastAPI Backend (New - AWS EC2 Ready)
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
- **Backend (Node.js)**: http://localhost:3003
- **Backend (Python)**: http://localhost:3003

## 🌐 Deployment
- **Node.js Backend**: See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for Vercel + Render deployment
- **Python Backend**: See [server_py/DEPLOYMENT.md](./server_py/DEPLOYMENT.md) for AWS EC2 deployment instructions

## 📁 Project Structure
```
├── client/          # React frontend
├── server/          # Node.js backend (original)
├── server_py/       # Python FastAPI backend (new - AWS EC2 ready)
├── docs/            # Documentation
└── README.md        # This file
```

## 🎓 Educational Use Cases
- **Virtual Classrooms**: Structured online discussions
- **Debate Practice**: Turn-based speaking with timers
- **Language Learning**: Conversation practice with AI topics
- **Workshop Facilitation**: Guided group discussions
- **Student Presentations**: Organized speaking turns

## 📄 License
Open source - see individual files for specific licensing.

## 🌍 Live Repository
This platform is available as a dedicated repository at:
**https://github.com/theemubin/GupShup-Cafe**
