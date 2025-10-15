import argparse
import json
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def load_chunks(input_file):
    """Load text chunks from JSONL file."""
    chunks = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            # Expect structure: {"id": ..., "text": ..., "source": ...}
            chunks.append(data)
    return chunks


def build_index(input_file, out_dir, model_name, batch_size=64, min_chars=30):
    """Build FAISS index from chunks."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    model = SentenceTransformer(model_name)

    chunks = load_chunks(input_file)
    texts = [c["text"] for c in chunks if len(c["text"]) >= min_chars]

    # Encode embeddings
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype="float32")

    # Build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Save index
    faiss.write_index(index, str(out_dir / "index.faiss"))

    # Save metadata aligned with vectors
    with open(out_dir / "meta.jsonl", "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            if len(chunk["text"]) >= min_chars:
                meta = {
                    "id": chunk.get("id", i),
                    "text": chunk["text"],
                    "source": chunk.get("source", "unknown")
                }
                f.write(json.dumps(meta, ensure_ascii=False) + "\n")

    print(f"✅ Index built with {len(texts)} chunks and saved to {out_dir}")


def search(index_dir, query, k=3, model_name="sentence-transformers/all-MiniLM-L6-v2"):
    """Search FAISS index and return top-k results with full text."""
    index_dir = Path(index_dir)

    # Load FAISS
    index = faiss.read_index(str(index_dir / "index.faiss"))

    # Load metadata
    metas = []
    with open(index_dir / "meta.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            metas.append(json.loads(line))

    # Load model
    model = SentenceTransformer(model_name)

    # Encode query
    query_vec = model.encode([query])
    query_vec = np.array(query_vec, dtype="float32")

    # Search
    D, I = index.search(query_vec, k)
    results = [(float(D[0][j]), metas[I[0][j]]) for j in range(len(I[0]))]

    return results


# -------------------------------
# CLI
# -------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retriever for RAG pipeline")
    subparsers = parser.add_subparsers(dest="command")

    # Build
    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("--input", type=str, required=True)
    build_parser.add_argument("--out_dir", type=str, required=True)
    build_parser.add_argument("--model", type=str, required=True)
    build_parser.add_argument("--batch_size", type=int, default=64)
    build_parser.add_argument("--min_chars", type=int, default=30)

    # Search
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--index_dir", type=str, required=True)
    search_parser.add_argument("--query", type=str, required=True)
    search_parser.add_argument("--k", type=int, default=3)
    search_parser.add_argument("--model", type=str, default="sentence-transformers/all-MiniLM-L6-v2")

    args = parser.parse_args()

    if args.command == "build":
        build_index(args.input, args.out_dir, args.model, args.batch_size, args.min_chars)

    elif args.command == "search":
        results = search(args.index_dir, args.query, args.k, args.model)
        for score, meta in results:
            print(f"Score: {score:.4f}, Source: {meta['source']}")
            print(f"Text: {meta['text'][:200]}...\n")


