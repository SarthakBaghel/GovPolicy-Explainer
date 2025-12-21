# backend/repositories/document_repo.py
from backend.core.mongo_config import get_db
from datetime import datetime
from typing import List

def get_documents_collection():
    """Get the documents collection from MongoDB"""
    db = get_db()
    return db["documents"]

def get_users_collection():
    """Get the users collection from MongoDB"""
    db = get_db()
    return db["users"]

def create_document(doc_id: str, user_id: str, filename: str, file_size: int = 0) -> dict:
    """
    Create a new document entry in MongoDB
    
    Args:
        doc_id: Unique document ID
        user_id: User who uploaded the document
        filename: Original filename
        file_size: Size of the file in bytes
    
    Returns:
        Document data
    """
    documents_collection = get_documents_collection()
    doc_data = {
        "doc_id": doc_id,
        "user_id": user_id,
        "filename": filename,
        "file_size": file_size,
        "created_at": datetime.utcnow(),
        "status": "indexed"
    }
    result = documents_collection.insert_one(doc_data)
    return {
        "_id": str(result.inserted_id),
        **doc_data
    }

def add_document_to_user(user_id: str, doc_id: str) -> bool:
    """
    Add a document ID to a user's document list
    
    Args:
        user_id: User ID
        doc_id: Document ID to add
    
    Returns:
        True if successful
    """
    users_collection = get_users_collection()
    result = users_collection.update_one(
        {"id": user_id},
        {"$addToSet": {"documents": doc_id}}  # $addToSet prevents duplicates
    )
    return result.modified_count > 0

def get_user_documents(user_id: str) -> List[dict]:
    """
    Get all documents for a user
    
    Args:
        user_id: User ID
    
    Returns:
        List of documents belonging to the user
    """
    documents_collection = get_documents_collection()
    docs = list(documents_collection.find({"user_id": user_id}))
    for doc in docs:
        doc["_id"] = str(doc["_id"])
    return docs

def get_document_by_id(doc_id: str) -> dict:
    """Get a document by document ID"""
    documents_collection = get_documents_collection()
    doc = documents_collection.find_one({"doc_id": doc_id})
    if doc:
        doc["_id"] = str(doc["_id"])
    return doc

def delete_document(doc_id: str, user_id: str) -> bool:
    """
    Delete a document (from MongoDB only, local files should be deleted separately)
    
    Args:
        doc_id: Document ID to delete
        user_id: User ID (for verification)
    
    Returns:
        True if successful
    """
    documents_collection = get_documents_collection()
    users_collection = get_users_collection()
    
    # Delete from documents collection
    doc_result = documents_collection.delete_one({"doc_id": doc_id, "user_id": user_id})
    
    # Remove from user's document list
    user_result = users_collection.update_one(
        {"id": user_id},
        {"$pull": {"documents": doc_id}}
    )
    
    return doc_result.deleted_count > 0
