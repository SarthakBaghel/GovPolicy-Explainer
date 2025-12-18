from backend.scripts.retriever import build_index, search as search_chunks
from pathlib import Path


class RetrieverService:
    def __init__(self, chunks_file: str = "backend/data/outputs/policy_chunks.jsonl", index_dir: str = "backend/data/outputs/index", embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.chunks_file = chunks_file
        self.index_dir = index_dir
        self.embed_model = embed_model

    def build_faiss_index(self, chunks_file: str | None = None, index_dir: str | None = None):
        """Build FAISS index from chunks_file into index_dir."""
        cf = chunks_file or self.chunks_file
        idx = index_dir or self.index_dir
        build_index(cf, idx, self.embed_model)
        return {"message": f"Index built at {idx}"}

    def search(self, query: str, k: int = 3, index_dir: str | None = None):
        """Search FAISS index, optionally override index_dir."""
        idx = index_dir or self.index_dir
        try:
            results = search_chunks(idx, query, k, model_name=self.embed_model)
        except FileNotFoundError as e:
            return {"error": str(e)}
        return [{"score": r[0], "text": r[1]["text"], "source": r[1]["source"]} for r in results]

    def list_available_indexes(self, outputs_root: str | None = None):
        """List document names under outputs_root that have an index."""
        root = Path(outputs_root) if outputs_root else Path("backend/data/outputs")
        docs = []
        if not root.exists():
            return docs
        for p in sorted(root.iterdir()):
            if p.is_dir() and (p / "index" / "index.faiss").exists():
                docs.append(p.name)
        return docs
