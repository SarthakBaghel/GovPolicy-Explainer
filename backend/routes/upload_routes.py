from fastapi import APIRouter, UploadFile, File
from pathlib import Path
from backend.services.parser_service import ParserService
from backend.services.retriever_service import RetrieverService
import shutil

router = APIRouter()

RAW_DIR = Path("backend/data/raw_pdfs")
OUTPUT_JSONL = Path("backend/data/outputs/policy_chunks.jsonl")
INDEX_DIR = Path("backend/data/outputs/index")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    file_path = RAW_DIR / file.filename

    with file_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Parse PDFs
    parser = ParserService(str(RAW_DIR), str(OUTPUT_JSONL))
    parser.parse_all_pdfs()

    # Build FAISS index
    retriever = RetrieverService(str(OUTPUT_JSONL), str(INDEX_DIR), EMBED_MODEL)
    retriever.build_faiss_index()

    return {"message": f"Uploaded, parsed, and indexed {file.filename}"}
