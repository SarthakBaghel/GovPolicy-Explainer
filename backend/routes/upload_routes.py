from fastapi import APIRouter, UploadFile, File, Depends
from pathlib import Path
from backend.services.parser_service import ParserService
from backend.services.retriever_service import RetrieverService
from backend.core.dependencies import get_current_user_id
import shutil

router = APIRouter()

RAW_DIR = Path("backend/data/raw_pdfs")
OUTPUTS_ROOT = Path("backend/data/outputs")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

@router.post("/upload")
async def upload_pdf(
    file: UploadFile,
    user_id: str = Depends(get_current_user_id)
):
    """Upload a PDF and process it into a per-document output folder.
    
    Returns doc_name which clients use to query/search that document.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    file_path = RAW_DIR / file.filename

    with file_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    # Parse only the uploaded PDF into its own output folder
    parser = ParserService(str(RAW_DIR), str(OUTPUTS_ROOT))
    out_dir, out_jsonl = parser.parse_pdf_file(file_path)

    # Build FAISS index into the document's index folder
    index_dir = out_dir / "index"
    retriever = RetrieverService(str(out_jsonl), str(index_dir), EMBED_MODEL)
    retriever.build_faiss_index(chunks_file=str(out_jsonl), index_dir=str(index_dir))

    return {
        "message": f"Uploaded, parsed, and indexed {file.filename}",
        "outputs": str(out_dir),
        "doc_name": out_dir.name,
        "chunks_file": str(out_jsonl),
        "index_dir": str(index_dir)
    }
