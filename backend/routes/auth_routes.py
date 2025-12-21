# backend/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from uuid import uuid4

from backend.core.security import hash_password, verify_password
from backend.core.jwt_utils import create_access_token
from backend.repositories.user_repo import load_users, save_users

router = APIRouter()

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(data: RegisterRequest):
    users = load_users()

    if data.email in users:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid4())
    users[data.email] = {
        "id": user_id,
        "password_hash": hash_password(data.password)
    }

    save_users(users)

    return {"message": "User registered successfully"}

@router.post("/login")
def login(data: LoginRequest):
    users = load_users()
    user = users.get(data.email)

    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user["id"])

    return {
        "access_token": token,
        "token_type": "bearer"
    }
