"""
API Routes
RESTful endpoints for the application
"""
from fastapi import APIRouter, HTTPException
from ..services.user_services import User_services
from ..models.user_pydantic_models import (
    LoginModel, SignUpModel, LoginSignUpResponseModel, UserUpdateModel,
    UpdateUserCEFRModel, UpdateUserLastActiveModel, UpdateUserPasswordModel
)
router = APIRouter()

user_service = User_services()

@router.post("/login", response_model=LoginSignUpResponseModel, description="User login")
async def login(req:LoginModel):
    """User login endpoint"""
    return user_service.login_user(req)

@router.post("/signup", response_model=LoginSignUpResponseModel, description="User signup")
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

@router.get("/", description="List users")
async def list_users():
    return user_service.list_users()

@router.patch("/{user_id}", description="Update user")
async def update_user(user_id: str, payload: UserUpdateModel):
    resp = user_service.update_user(user_id, payload)
    if resp["status"] == "failure":
        raise HTTPException(status_code=400, detail=resp["message"])
    return resp

@router.delete("/{user_id}", description="Delete user")
async def delete_user(user_id: str):
    return user_service.delete_user(user_id)

@router.patch("/cefr-level", description="Update user's CEFR level")
async def update_cefr_level(payload: UpdateUserCEFRModel):
    resp = user_service.update_user_cefr_level(payload)
    if resp["status"] == "failure":
        raise HTTPException(status_code=400, detail=resp["message"])
    return resp

@router.patch("/last-active", description="Update user's last active timestamp")
async def update_last_active(payload: UpdateUserLastActiveModel):
    resp = user_service.update_user_last_active(payload)
    if resp["status"] == "failure":
        raise HTTPException(status_code=400, detail=resp["message"])
    return resp

@router.patch("/password", description="Update user's password")
async def update_password(payload: UpdateUserPasswordModel):
    resp = user_service.update_user_password(payload)
    if resp["status"] == "failure":
        raise HTTPException(status_code=400, detail=resp["message"])
    return resp