# backend/core/security.py
from passlib.context import CryptContext

# Use argon2id instead of bcrypt (no 72-byte limit, more modern)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
