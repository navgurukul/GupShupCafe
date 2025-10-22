#!/usr/bin/env python3
"""
Simple Socket.io test server to verify the setup
"""

import socketio
import uvicorn
from fastapi import FastAPI

# Create FastAPI app
app = FastAPI()

# Create Socket.io server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

# Simple test endpoint


@app.get("/")
async def root():
    return {"message": "Socket.io test server"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

# Socket.io event handlers


@sio.event
async def connect(sid, environ, auth):
    print(f"Client connected: {sid}")
    await sio.emit("welcome", {"message": "Connected successfully!"}, room=sid)


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


@sio.event
async def test_message(sid, data):
    print(f"Received test message from {sid}: {data}")
    await sio.emit("test_response", {"echo": data}, room=sid)

# Create ASGI app
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

if __name__ == "__main__":
    print("Starting Socket.io test server on port 3004...")
    uvicorn.run(socket_app, host="0.0.0.0", port=3004)
