import os
import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
import socketio
import uvicorn

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI
app = FastAPI(title="GupShup Cafe API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins=["http://localhost:3000"],
    logger=True,
    engineio_logger=True
)

# Attach Socket.IO to FastAPI
socket_app = socketio.ASGIApp(sio, app)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Data storage (in production, use a proper database)
DATA_FILE = "data/data.json"
TOPICS_FILE = "data/topics.json"

# Initialize data storage
os.makedirs("data", exist_ok=True)

# Models
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    interests: List[str]

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: str
    name: str
    email: str
    interests: List[str]
    created_at: str

class Room(BaseModel):
    id: str
    name: str
    category: str
    description: str
    max_participants: int
    participants: List[Dict]
    created_by: str
    created_at: str
    is_active: bool

# Utility functions
def load_data() -> Dict[str, Any]:
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}, "rooms": {}}

def save_data(data: Dict[str, Any]):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_topics() -> Dict[str, List[str]]:
    try:
        with open(TOPICS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Default topics
        return {
            "currentAffairs": [
                "What are your thoughts on the latest climate change initiatives?",
                "How do you think artificial intelligence will impact future elections?"
            ],
            "scienceAndTechnology": [
                "What breakthrough in quantum computing excites you the most?",
                "How will 5G technology change our daily lives?"
            ],
            "literature": [
                "How has digital media changed the way we read and write?",
                "What makes a story timeless across different cultures?"
            ],
            "education": [
                "How can we make education more accessible globally?",
                "What's the role of technology in modern classrooms?"
            ],
            "generativeAI": [
                "How will generative AI change the creative industries?",
                "What are the ethical considerations of AI-generated content?"
            ]
        }

def get_password_hash(password: str) -> str:
    # Truncate password to 72 bytes for bcrypt compatibility
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate password to 72 bytes for bcrypt compatibility
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    data = load_data()
    user = data["users"].get(user_id)
    if user is None:
        raise credentials_exception
    return user

# API Routes
@app.get("/")
async def root():
    return {"message": "GupShup Cafe API is running!"}

@app.post("/api/auth/signup", response_model=Token)
async def signup(user_data: UserCreate):
    data = load_data()
    
    # Check if user already exists
    for user in data["users"].values():
        if user["email"] == user_data.email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
    
    # Create new user
    user_id = secrets.token_urlsafe(16)
    hashed_password = get_password_hash(user_data.password)
    
    new_user = {
        "id": user_id,
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "interests": user_data.interests,
        "created_at": datetime.utcnow().isoformat()
    }
    
    data["users"][user_id] = new_user
    save_data(data)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_id,
            "name": new_user["name"],
            "email": new_user["email"],
            "interests": new_user["interests"]
        }
    }

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    data = load_data()
    
    # Find user by email
    user = None
    for u in data["users"].values():
        if u["email"] == user_credentials.email:
            user = u
            break
    
    if not user or not verify_password(user_credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "interests": user["interests"]
        }
    }

@app.get("/api/user/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "name": current_user["name"],
        "email": current_user["email"],
        "interests": current_user["interests"]
    }

@app.get("/api/rooms")
async def get_rooms():
    data = load_data()
    return {"rooms": list(data["rooms"].values())}

# Socket.IO events
connected_users = {}
room_states = {}

@sio.event
async def connect(sid, environ, auth):
    print(f"Client {sid} connected")
    
    if auth and "token" in auth:
        try:
            payload = jwt.decode(auth["token"], SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            
            data = load_data()
            user = data["users"].get(user_id)
            
            if user:
                connected_users[sid] = {
                    "user_id": user_id,
                    "user": user,
                    "room": None
                }
                await sio.emit("authenticated", {"user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"]
                }}, room=sid)
            else:
                await sio.disconnect(sid)
        except:
            await sio.disconnect(sid)
    else:
        await sio.disconnect(sid)

@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")
    
    if sid in connected_users:
        user_data = connected_users[sid]
        if user_data["room"]:
            await leave_room_handler(sid, {"roomId": user_data["room"]})
        del connected_users[sid]

@sio.event
async def join_room(sid, data):
    await join_room_handler(sid, data)

@sio.event
async def leave_room(sid, data):
    await leave_room_handler(sid, data)

@sio.event
async def user_ready(sid, data):
    await user_ready_handler(sid, data)

@sio.event
async def start_speaking(sid, data):
    await start_speaking_handler(sid, data)

@sio.event
async def next_speaker(sid, data):
    await next_speaker_handler(sid, data)

@sio.event
async def create_room(sid, data):
    await create_room_handler(sid, data)

# Socket.IO event handlers
async def join_room_handler(sid, data):
    if sid not in connected_users:
        return
    
    room_id = data.get("roomId")
    user_data = connected_users[sid]
    
    # Initialize room state if doesn't exist
    if room_id not in room_states:
        room_states[room_id] = {
            "id": room_id,
            "name": get_room_name(room_id),
            "participants": [],
            "ready_users": set(),
            "topic": None,
            "speaking_order": [],
            "current_speaker_index": -1,
            "state": "waiting"
        }
    
    room_state = room_states[room_id]
    
    # Add user to room
    if user_data["user_id"] not in [p["id"] for p in room_state["participants"]]:
        participant = {
            "id": user_data["user_id"],
            "name": user_data["user"]["name"],
            "sid": sid
        }
        room_state["participants"].append(participant)
    
    # Join socket room
    await sio.enter_room(sid, room_id)
    connected_users[sid]["room"] = room_id
    
    # Notify room about new participant
    await sio.emit("room_joined", {
        "room": {"id": room_id, "name": room_state["name"]},
        "participants": room_state["participants"],
        "topic": room_state["topic"],
        "speakingOrder": room_state["speaking_order"],
        "currentSpeaker": get_current_speaker(room_state),
        "state": room_state["state"]
    }, room=sid)
    
    await sio.emit("user_joined", {
        "user": {"name": user_data["user"]["name"]},
        "participants": room_state["participants"]
    }, room=room_id, skip_sid=sid)

async def leave_room_handler(sid, data):
    if sid not in connected_users:
        return
    
    room_id = data.get("roomId")
    user_data = connected_users[sid]
    
    if room_id in room_states:
        room_state = room_states[room_id]
        
        # Remove user from room
        room_state["participants"] = [
            p for p in room_state["participants"] 
            if p["id"] != user_data["user_id"]
        ]
        room_state["ready_users"].discard(user_data["user_id"])
        
        # Leave socket room
        await sio.leave_room(sid, room_id)
        connected_users[sid]["room"] = None
        
        # Notify remaining participants
        await sio.emit("user_left", {
            "user": {"name": user_data["user"]["name"]},
            "participants": room_state["participants"]
        }, room=room_id)
        
        # Clean up empty room
        if not room_state["participants"]:
            del room_states[room_id]

async def user_ready_handler(sid, data):
    if sid not in connected_users:
        return
    
    room_id = data.get("roomId")
    user_data = connected_users[sid]
    
    if room_id in room_states:
        room_state = room_states[room_id]
        room_state["ready_users"].add(user_data["user_id"])
        
        # Check if all users are ready
        if len(room_state["ready_users"]) == len(room_state["participants"]):
            await assign_topic_and_start(room_id)

async def start_speaking_handler(sid, data):
    if sid not in connected_users:
        return
    
    room_id = data.get("roomId")
    
    if room_id in room_states:
        room_state = room_states[room_id]
        room_state["state"] = "speaking"
        room_state["current_speaker_index"] = 0
        
        current_speaker = get_current_speaker(room_state)
        await sio.emit("speaking_started", {
            "speaker": current_speaker
        }, room=room_id)

async def next_speaker_handler(sid, data):
    if sid not in connected_users:
        return
    
    room_id = data.get("roomId")
    
    if room_id in room_states:
        room_state = room_states[room_id]
        room_state["current_speaker_index"] += 1
        
        if room_state["current_speaker_index"] >= len(room_state["speaking_order"]):
            # Discussion finished, reset room
            room_state["state"] = "waiting"
            room_state["current_speaker_index"] = -1
            room_state["topic"] = None
            room_state["speaking_order"] = []
            room_state["ready_users"] = set()
            
            await sio.emit("room_reset", {}, room=room_id)
        else:
            current_speaker = get_current_speaker(room_state)
            await sio.emit("speaker_changed", {
                "speaker": current_speaker
            }, room=room_id)

async def create_room_handler(sid, data):
    # This would create a new custom room
    # For now, we'll just emit success
    await sio.emit("room_created", {"success": True}, room=sid)

# Helper functions
def get_room_name(room_id):
    room_names = {
        "education": "Education",
        "science-tech": "Science & Technology", 
        "literature": "Literature",
        "generative-ai": "Generative AI"
    }
    return room_names.get(room_id, "Custom Room")

def get_current_speaker(room_state):
    if (room_state["current_speaker_index"] >= 0 and 
        room_state["current_speaker_index"] < len(room_state["speaking_order"])):
        return room_state["speaking_order"][room_state["current_speaker_index"]]
    return None

async def assign_topic_and_start(room_id):
    room_state = room_states[room_id]
    topics = load_topics()
    
    # Get room category and select random topic
    category = get_room_category(room_id)
    if category in topics:
        import random
        topic = random.choice(topics[category])
        room_state["topic"] = topic
    
    # Set speaking order (randomized)
    import random
    room_state["speaking_order"] = room_state["participants"].copy()
    random.shuffle(room_state["speaking_order"])
    
    room_state["state"] = "ready"
    
    await sio.emit("topic_assigned", {
        "topic": room_state["topic"],
        "speakingOrder": room_state["speaking_order"]
    }, room=room_id)

def get_room_category(room_id):
    category_map = {
        "education": "education",
        "science-tech": "scienceAndTechnology",
        "literature": "literature", 
        "generative-ai": "generativeAI"
    }
    return category_map.get(room_id, "currentAffairs")

# Initialize topics file
topics = load_topics()
with open(TOPICS_FILE, 'w') as f:
    json.dump(topics, f, indent=2)

if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, log_level="info")
