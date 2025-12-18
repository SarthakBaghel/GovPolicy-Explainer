# backend/repositories/user_repo.py
import json
from pathlib import Path

USERS_FILE = Path("backend/data/users.json")

def load_users():
    if USERS_FILE.exists():
        return json.loads(USERS_FILE.read_text())
    return {}

def save_users(users):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(users, indent=2))
