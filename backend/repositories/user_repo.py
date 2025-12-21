# backend/repositories/user_repo.py
from backend.core.mongo_config import get_db
from bson.objectid import ObjectId

def get_users_collection():
    """Get the users collection from MongoDB"""
    db = get_db()
    return db["users"]

def user_exists(email: str) -> bool:
    """Check if a user with the given email exists"""
    collection = get_users_collection()
    return collection.find_one({"email": email}) is not None

def create_user(user_id: str, email: str, password_hash: str) -> dict:
    """Create a new user in MongoDB"""
    collection = get_users_collection()
    user_data = {
        "id": user_id,
        "email": email,
        "password_hash": password_hash,
        "documents": []  # Initialize empty documents array
    }
    result = collection.insert_one(user_data)
    return {
        "_id": str(result.inserted_id),
        **user_data
    }

def get_user_by_email(email: str) -> dict:
    """Get a user by email from MongoDB"""
    collection = get_users_collection()
    user = collection.find_one({"email": email})
    if user:
        user["_id"] = str(user["_id"])
    return user

def get_user_by_id(user_id: str) -> dict:
    """Get a user by ID from MongoDB"""
    collection = get_users_collection()
    user = collection.find_one({"id": user_id})
    if user:
        user["_id"] = str(user["_id"])
    return user


# Keep legacy functions for backward compatibility
def load_users():
    """Legacy function - returns empty dict for backward compatibility"""
    return {}

def save_users(users):
    """Legacy function - no-op for backward compatibility"""
    pass

