from backend.scripts.retriever import build_index, search as search_chunks

class RetrieverService:
    def __init__(self, chunks_file: str = "backend/data/outputs/policy_chunks.jsonl", index_dir: str = "backend/data/outputs/index", embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.chunks_file = chunks_file
        self.index_dir = index_dir
        self.embed_model = embed_model

    def build_faiss_index(self):
        build_index(self.chunks_file, self.index_dir, self.embed_model)
        return {"message": f"Index built at {self.index_dir}"}

    def search(self, query: str, k: int = 3):
        results = search_chunks(self.index_dir, query, k, model_name=self.embed_model)
        return [{"score": r[0], "text": r[1]["text"], "source": r[1]["source"]} for r in results]
