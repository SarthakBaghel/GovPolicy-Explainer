# backend/routes/document_routes.py
from fastapi import APIRouter, HTTPException, Depends
from backend.core.dependencies import get_current_user_id
from backend.repositories.document_repo import (
    get_user_documents,
    get_document_by_id,
    delete_document
)
import shutil
from pathlib import Path

router = APIRouter()

OUTPUTS_ROOT = Path("backend/data/outputs")
RAW_DIR = Path("backend/data/raw_pdfs")

@router.get("/documents")
async def list_user_documents(user_id: str = Depends(get_current_user_id)):
    """Get all documents for the current user"""
    try:
        documents = get_user_documents(user_id)
        return {
            "user_id": user_id,
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{doc_id}")
async def get_document_info(
    doc_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get information about a specific document"""
    try:
        document = get_document_by_id(doc_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Verify the document belongs to the user
        if document["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{doc_id}")
async def delete_user_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a document (both from MongoDB and local storage)"""
    try:
        # Get document to verify ownership
        document = get_document_by_id(doc_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if document["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete from MongoDB
        delete_document(doc_id, user_id)
        
        # Delete local files
        doc_output_dir = OUTPUTS_ROOT / user_id / doc_id
        if doc_output_dir.exists():
            shutil.rmtree(doc_output_dir)
        
        return {
            "message": "Document deleted successfully",
            "doc_id": doc_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
