from fastapi import APIRouter
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

class SearchRequest(BaseModel):
    query: str
    k: int = 3

@router.post("/query")
def query_rag(req: QueryRequest):
    return rag_service.query(req.question, k=req.k)

@router.post("/search")
def search_chunks(req: SearchRequest):
    return retriever_service.search(req.query, k=req.k)
