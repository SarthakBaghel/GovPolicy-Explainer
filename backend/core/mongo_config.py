import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection URL
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "govpolicy_explainer")

# Initialize MongoDB client (lazy loading - will be created on first use)
client = None
db = None

def connect_to_mongodb():
    """Establish connection to MongoDB"""
    global client, db
    try:
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        # Verify connection
        client.admin.command('ping')
        db = client[DATABASE_NAME]
        print("✓ Connected to MongoDB")
        return db
    except ServerSelectionTimeoutError as e:
        print(f"✗ Could not connect to MongoDB: {e}")
        print(f"  Make sure MongoDB is running at {MONGODB_URL}")
        db = None
        return None

def get_db():
    """Get the MongoDB database instance"""
    global db
    if db is None:
        connect_to_mongodb()
    if db is None:
        raise RuntimeError("MongoDB connection not available")
    return db

def close_mongodb_connection():
    """Close the MongoDB connection"""
    global client
    if client:
        client.close()
        print("✓ MongoDB connection closed")

