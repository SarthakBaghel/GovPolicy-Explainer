import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection URL
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "govpolicy_explainer")

# Initialize MongoDB client
try:
    client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
    # Verify connection
    client.admin.command('ping')
    db = client[DATABASE_NAME]
    print("✓ Connected to MongoDB")
except ServerSelectionTimeoutError:
    print("✗ Could not connect to MongoDB. Make sure MongoDB is running.")
    db = None

def get_db():
    """Get the MongoDB database instance"""
    if db is None:
        raise RuntimeError("MongoDB connection not available")
    return db

def close_mongodb_connection():
    """Close the MongoDB connection"""
    if client:
        client.close()
