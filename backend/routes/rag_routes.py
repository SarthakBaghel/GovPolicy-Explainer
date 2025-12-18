from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.services.rag_service import RAGService
from backend.services.retriever_service import RetrieverService

router = APIRouter()

INDEX_DIR = "backend/data/outputs/index"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
rag_service = RAGService(index_dir=INDEX_DIR)
retriever_service = RetrieverService(chunks_file="backend/data/outputs/policy_chunks.jsonl", index_dir=INDEX_DIR, embed_model=EMBED_MODEL)


class QueryRequest(BaseModel):
    question: str
    k: int = 3
    doc_name: str | None = None


class SearchRequest(BaseModel):
    query: str
    k: int = 3
    doc_name: str | None = None


@router.post("/query")
def query_rag(req: QueryRequest):
    """Query RAG pipeline. If doc_name provided, target that document's index."""
    idx = None
    if req.doc_name:
        idx = f"backend/data/outputs/{req.doc_name}/index"
    return rag_service.query(req.question, k=req.k, index_dir=idx)


@router.post("/search")
def search_chunks(req: SearchRequest):
    """Search chunks. If doc_name provided, target that document's index."""
    idx = None
    if req.doc_name:
        idx = f"backend/data/outputs/{req.doc_name}/index"
    return retriever_service.search(req.query, k=req.k, index_dir=idx)


@router.get("/indexes")
def list_indexes():
    """Return list of available per-document indexes."""
    docs = retriever_service.list_available_indexes()
    return JSONResponse(content={"indexes": docs})
