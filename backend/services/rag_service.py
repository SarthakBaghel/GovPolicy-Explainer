from backend.scripts.rag_pipeline import rag_answer


class RAGService:
    def __init__(self, index_dir: str = "backend/data/outputs/index", embed_model: str = "sentence-transformers/all-MiniLM-L6-v2", llm_model: str = "phi3:mini"):
        self.index_dir = index_dir
        self.embed_model = embed_model
        self.llm_model = llm_model

    def query(self, question: str, k: int = 3, index_dir: str | None = None):
        """Query RAG pipeline, optionally override index_dir for per-document queries."""
        idx = index_dir or self.index_dir
        answer = rag_answer(
            question,
            index_dir=idx,
            k=k,
            embed_model=self.embed_model,
            llm_model=self.llm_model
        )
        return {"question": question, "answer": answer}
