"""
API Routes
RESTful endpoints for the application
"""
from fastapi import APIRouter, HTTPException
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

@router.get("/{user_id}", description="Get user details")
async def get_user(user_id: str):
    """Get user details endpoint"""
    response = user_service.get_user(user_id)
    if response["status"] == "failure":
        raise HTTPException(status_code=404, detail=response["message"])
    return response