"""
API Routes
RESTful endpoints for the application
"""
from fastapi import APIRouter
from ..services.user_services import User_services
from ..models.user_pydantic_models import LoginModel, SignUpModel, CreateRoomModel, JoinRoomModel, LoginResponseModel
router = APIRouter()

user_service = User_services()

@router.post("/login", response_model=LoginResponseModel, description="User login")
async def login(req:LoginModel):
    """User login endpoint"""
    return user_service.login_user(req)

@router.post("/signup", response_model=LoginResponseModel, description="User signup")
async def signup(req:SignUpModel):
    """User signup endpoint"""
    return user_service.signup_user(req)