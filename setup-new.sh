#!/bin/bash

echo "🚀 Setting up GupShup Cafe (New Implementation)..."

# Setup New Frontend (client-1)
echo "📦 Installing new frontend dependencies..."
cd client-1
npm install
cd ..

# Setup New Backend (server-ani) 
echo "🐍 Setting up Python backend..."
cd server-ani

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the NEW application:"
echo "1. Start backend: cd server-ani && source venv/bin/activate && python main.py"
echo "2. Start frontend: cd client-1 && npm run dev"
echo ""
echo "🌐 Frontend will be available at: http://localhost:3000"
echo "🔧 Backend API will be available at: http://localhost:8000"
