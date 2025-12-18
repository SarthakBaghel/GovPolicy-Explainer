# backend/models/user.py
from uuid import uuid4
from datetime import datetime

class User:
    def __init__(self, email: str, password_hash: str):
        self.id = str(uuid4())
        self.email = email
        self.password_hash = password_hash
        self.created_at = datetime.utcnow()
