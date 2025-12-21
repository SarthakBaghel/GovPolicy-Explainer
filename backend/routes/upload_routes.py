from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pathlib import Path
from backend.services.parser_service import ParserService
from backend.services.retriever_service import RetrieverService
from backend.core.dependencies import get_current_user_id
from backend.repositories.document_repo import create_document, add_document_to_user
import shutil
from uuid import uuid4

router = APIRouter()

RAW_DIR = Path("backend/data/raw_pdfs")
OUTPUTS_ROOT = Path("backend/data/outputs")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

@router.post("/upload")
async def upload_pdf(
    file: UploadFile,
    user_id: str = Depends(get_current_user_id)
):
    """Upload a PDF and process it into a per-user, per-document output folder.
    
    Files are organized as: backend/data/outputs/{user_id}/{doc_id}/
    - Generates unique doc_id for each upload
    - Stores document metadata in MongoDB with user association
    - Stores actual document files locally only
    
    Returns doc_id which clients use to query/search that document.
    """
    try:
        # Generate unique document ID
        doc_id = str(uuid4())
        
        # Create user-specific directories
        user_raw_dir = RAW_DIR / user_id
        user_outputs_dir = OUTPUTS_ROOT / user_id
        user_raw_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file locally
        file_path = user_raw_dir / file.filename
        with file_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        # Parse only the uploaded PDF into its own output folder under user directory
        # Using doc_id as the output folder name
        parser = ParserService(str(user_raw_dir), str(user_outputs_dir))
        out_dir, out_jsonl = parser.parse_pdf_file(file_path, doc_name=doc_id)

        # Build FAISS index into the document's index folder
        index_dir = out_dir / "index"
        retriever = RetrieverService(str(out_jsonl), str(index_dir), EMBED_MODEL)
        retriever.build_faiss_index(chunks_file=str(out_jsonl), index_dir=str(index_dir))

        # Delete the original PDF file after successful processing
        # We only need the chunks and embeddings (index) for future queries
        if file_path.exists():
            file_path.unlink()
            print(f"✓ Deleted original PDF: {file_path}")

        # Save document metadata to MongoDB
        create_document(
            doc_id=doc_id,
            user_id=user_id,
            filename=file.filename,
            file_size=file.size
        )
        
        # Add document ID to user's document list
        add_document_to_user(user_id, doc_id)

        return {
            "message": f"Uploaded, parsed, and indexed {file.filename}",
            "doc_id": doc_id,
            "filename": file.filename,
            "outputs": str(out_dir),
            "chunks_file": str(out_jsonl),
            "index_dir": str(index_dir),
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
