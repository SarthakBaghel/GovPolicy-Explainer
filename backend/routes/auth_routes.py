# backend/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import uuid4

from backend.core.security import hash_password, verify_password
from backend.core.jwt_utils import create_access_token
from backend.repositories.user_repo import (
    user_exists,
    create_user,
    get_user_by_email
)

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(data: RegisterRequest):
    """Register a new user and save to MongoDB"""
    
    # Check if email already exists in database
    if user_exists(data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    user_id = str(uuid4())
    password_hash = hash_password(data.password)
    
    # Save user to MongoDB
    create_user(user_id, data.email, password_hash)

    return {"message": "User registered successfully"}

@router.post("/login")
def login(data: LoginRequest):
    """Login user by verifying credentials against MongoDB"""
    
    # Retrieve user from MongoDB
    user = get_user_by_email(data.email)

    # Verify user exists and password is correct
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token
    token = create_access_token(user["id"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }
