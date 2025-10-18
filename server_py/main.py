"""
Main Server Application
Sets up FastAPI server with Socket.io for real-time communication
"""

import os
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn
import re
import sys
# import logger
import logging


from src.api.routes import router as api_router
from src.database.database import db
from src.socket.socket_handlers import setup_socket_handlers
from src.api.user_routes import router as user_router
from src.api.room_routes import router as room_router
from src.api.participant_routes import router as participant_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
PORT = int(os.getenv("PORT", "3003"))
PYTHON_ENV = os.getenv("PYTHON_ENV", "development")

# Parse CORS origins
configured_origins = []
if os.getenv("ALLOWED_ORIGINS"):
    configured_origins = os.getenv("ALLOWED_ORIGINS").split(",")
elif os.getenv("CORS_ORIGIN"):
    configured_origins = [os.getenv("CORS_ORIGIN")]

# Default origins for development and production
default_dev_origins = ["http://localhost:5173", "http://localhost:5174"]
default_prod_origins = [
    "https://gup-shup-cafe.vercel.app",
     "https://testing-team.d17x6h4sinckrd.amplifyapp.com/",
     "https://dev.d17x6h4sinckrd.amplifyapp.com/",
     "https://main.d17x6h4sinckrd.amplifyapp.com/"
    # For regex patterns, we'll handle them differently
]

is_production = PYTHON_ENV == "production"


# Combine origins
ALLOWED_ORIGINS = list(set(
    configured_origins if configured_origins else [] +
    (default_prod_origins if is_production else default_dev_origins)
))

# Add regex pattern for Vercel deployments in production
vercel_pattern = re.compile(r".*\.vercel\.app$")

def check_cors_origin(origin: str) -> bool:
    """Check if origin is allowed"""
    if not origin:
        return True  # Allow requests with no origin
    
    # Check exact matches
    if origin in ALLOWED_ORIGINS:
        return True
    
    # Check regex patterns (e.g., Vercel deployments)
    if is_production and vercel_pattern.match(origin):
        return True
    
    return False


# Create FastAPI app
app = FastAPI(
    title="AI Roundtable Discussion Server",
    description="Backend server for AI-powered educational discussions",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if not is_production else ["*"],  # In production, we validate in check_cors_origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Socket.io server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*" if is_production else ALLOWED_ORIGINS,
    logger=False,
    engineio_logger=False
)

# Wrap with ASGI app
socket_app = socketio.ASGIApp(
    sio,
    other_asgi_app=app,
    socketio_path="/socket.io"
)

# Mount API routes
app.include_router(api_router, prefix="/api")
app.include_router(user_router,prefix="/users",tags=["User Management"])
app.include_router(room_router, prefix="/rooms", tags=["Room Management"])
app.include_router(participant_router, prefix="/participants", tags=["Participant Management"])

@app.get("/")
async def root():
    """Basic info endpoint"""
    return {
        "name": "AI Roundtable Discussion Server",
        "version": "1.0.0",
        "description": "Backend server for AI-powered educational discussions",
        "endpoints": {
            "health": "/health",
            "api": "/api",
            "socket": f"ws://localhost:{PORT}"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    import time
    return {
        "status": "healthy",
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "uptime": time.process_time(),
        "environment": PYTHON_ENV
    }


@app.on_event("startup")
async def startup_event():
    """Initialize the server on startup"""
    try:
        # Initialize database
        logger.info("🗄️ Initializing database...")
        db_path = os.getenv("DATABASE_URL", "./database/gupshup_database.db")
        await db.initialize(db_path)
        
        # Setup Socket.io handlers
        logger.info("🔌 Setting up Socket.io handlers...")
        await setup_socket_handlers(sio)
        
        logger.info(f"🚀 Server starting on port {PORT}")
        logger.info(f"📡 Socket.io enabled with CORS origins: {', '.join(ALLOWED_ORIGINS)}")
        if os.getenv("CORS_ORIGIN") and not os.getenv("ALLOWED_ORIGINS"):
            logger.info("ℹ️ Using CORS_ORIGIN (single) – consider switching to ALLOWED_ORIGINS for multiple domains.")
        logger.info(f"🌐 Environment: {PYTHON_ENV}")
        logger.info(f"📊 Health check: http://localhost:{PORT}/health")
        logger.info("")
        logger.info("✅ AI Roundtable Discussion Server is ready!")
        
    except Exception as error:
        print(f"❌ Failed to start server: {str(error)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on server shutdown"""
    print("🛑 Shutting down gracefully...")
    await db.close()
    print("✅ Server closed")


if __name__ == "__main__":
    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=PORT,
        reload=PYTHON_ENV == "development"
    )
