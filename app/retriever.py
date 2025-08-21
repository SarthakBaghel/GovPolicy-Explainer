# app/retriever.py
import argparse
import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

# Make things stable on macOS / CI:
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import faiss
import numpy as np
from tqdm import tqdm
import torch
from sentence_transformers import SentenceTransformer


# ----------------------------- IO helpers -----------------------------

def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                yield json.loads(s)

def write_lines(path: Path, lines: Iterable[str]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for ln in lines:
            f.write(ln if ln.endswith("\n") else ln + "\n")


# ----------------------------- text prep -----------------------------

def prepare_text(record: Dict) -> str:
    rtype = record.get("type", "paragraph")
    section = (record.get("section") or "").strip()
    text = (record.get("text") or "").strip()
    if rtype == "heading":
        return text
    if section and section.lower() != "general":
        return f"{section}\n{text}"
    return text

def valid_record(record: Dict, min_chars: int) -> bool:
    return len(prepare_text(record)) >= min_chars


# ----------------------------- embeddings -----------------------------

def load_embedder(model_name: str, device: str = "cpu") -> SentenceTransformer:
    # Force CPU by default (most stable on macOS). Switch to 'mps' or 'cuda' later if you want.
    return SentenceTransformer(model_name, device=device)

def encode_texts(
    model: SentenceTransformer,
    texts: List[str],
    batch_size: int = 32,
) -> np.ndarray:
    embs = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    return embs.astype("float32")


# ----------------------------- index build -----------------------------

def build_index(
    input_jsonl: Path,
    out_dir: Path,
    model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
    batch_size: int = 32,
    min_chars: int = 30,
    limit: int = 0,
    device: str = "cpu",
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path = out_dir / "meta.jsonl"
    index_path = out_dir / "index.faiss"
    info_path = out_dir / "build_info.json"
    model_path = out_dir / "model_name.txt"
    device_path = out_dir / "device.txt"

    model = load_embedder(model_name, device=device)

    index = None
    meta_lines: List[str] = []
    buffer_texts: List[str] = []
    buffer_meta: List[Dict] = []

    total_in, total_kept = 0, 0

    for rec in tqdm(iter_jsonl(input_jsonl), desc="Reading records"):
        total_in += 1
        if limit and total_kept >= limit:
            break
        if not valid_record(rec, min_chars=min_chars):
            continue

        text = prepare_text(rec).strip()
        buffer_texts.append(text)

        meta = {
            "policy": rec.get("policy"),
            "section": rec.get("section"),
            "type": rec.get("type"),
            "source": rec.get("source"),
            "preview": (rec.get("text") or "").strip().replace("\n", " ")[:500],
        }
        buffer_meta.append(meta)
        total_kept += 1

        if len(buffer_texts) >= batch_size:
            embs = encode_texts(model, buffer_texts, batch_size=batch_size)
            if index is None:
                d = embs.shape[1]
                index = faiss.IndexFlatIP(d)   # cosine via normalized vectors
            index.add(embs)
            meta_lines.extend(json.dumps(m, ensure_ascii=False) for m in buffer_meta)
            buffer_texts, buffer_meta = [], []

    if buffer_texts:
        embs = encode_texts(model, buffer_texts, batch_size=batch_size)
        if index is None:
            d = embs.shape[1]
            index = faiss.IndexFlatIP(d)
        index.add(embs)
        meta_lines.extend(json.dumps(m, ensure_ascii=False) for m in buffer_meta)

    if index is None or index.ntotal == 0:
        raise RuntimeError("No vectors were added to the index. Check your input JSONL.")

    faiss.write_index(index, str(index_path))
    write_lines(meta_path, meta_lines)
    write_lines(model_path, [model_name])
    write_lines(device_path, [device])

    with info_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "vectors": int(index.ntotal),
                "model": model_name,
                "device": device,
                "min_chars": min_chars,
                "source_file": str(input_jsonl),
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\n✅ Built index:")
    print(f"   • vectors: {index.ntotal}")
    print(f"   • model:   {model_name}")
    print(f"   • device:  {device}")
    print(f"   • saved:   {index_path}")
    print(f"   • meta:    {meta_path}")


# ----------------------------- query -----------------------------

def load_index(index_dir: Path) -> Tuple[faiss.Index, List[Dict], str, str]:
    index_path = index_dir / "index.faiss"
    meta_path = index_dir / "meta.jsonl"
    model_path = index_dir / "model_name.txt"
    device_path = index_dir / "device.txt"

    if not index_path.exists() or not meta_path.exists() or not model_path.exists():
        raise FileNotFoundError("Index directory is missing required files.")

    index = faiss.read_index(str(index_path))
    meta = [json.loads(x) for x in meta_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    model_name = model_path.read_text(encoding="utf-8").strip()
    device = device_path.read_text(encoding="utf-8").strip() if device_path.exists() else "cpu"

    if len(meta) != index.ntotal:
        raise RuntimeError("Meta count does not match vector count.")
    return index, meta, model_name, device

def search(index_dir: Path, query: str, k: int = 3, batch_size: int = 32) -> List[Tuple[float, Dict]]:
    index, meta, model_name, device = load_index(index_dir)
    model = load_embedder(model_name, device=device)
    q_emb = encode_texts(model, [query], batch_size=batch_size)
    scores, ids = index.search(q_emb, k)
    out: List[Tuple[float, Dict]] = []
    for score, idx in zip(scores[0].tolist(), ids[0].tolist()):
        if idx == -1:
            continue
        out.append((float(score), meta[idx]))
    return out


# ----------------------------- CLI -----------------------------

def main():
    ap = argparse.ArgumentParser(description="FAISS retriever (build & query) — macOS/CPU safe")
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_build = sub.add_parser("build", help="Build FAISS index from JSONL chunks")
    ap_build.add_argument("--input", type=str, required=True, help="Path to policy_chunks.jsonl")
    ap_build.add_argument("--out_dir", type=str, default="data/outputs/index", help="Where to save index files")
    ap_build.add_argument("--model", type=str, default="paraphrase-multilingual-MiniLM-L12-v2", help="Sentence-Transformer model")
    ap_build.add_argument("--batch_size", type=int, default=32, help="Embedding batch size (keep modest on CPU)")
    ap_build.add_argument("--min_chars", type=int, default=30, help="Skip very short chunks")
    ap_build.add_argument("--limit", type=int, default=0, help="Optional cap on records (0 = all)")
    ap_build.add_argument("--device", type=str, default="cpu", choices=["cpu","mps","cuda"], help="Device for embeddings")

    ap_query = sub.add_parser("query", help="Query an existing index")
    ap_query.add_argument("--index_dir", type=str, default="data/outputs/index", help="Directory with index.faiss & meta.jsonl")
    ap_query.add_argument("--q", type=str, required=True, help="Your question (Eng/Hindi)")
    ap_query.add_argument("--k", type=int, default=3, help="Top-k results")
    ap_query.add_argument("--batch_size", type=int, default=32, help="Embedding batch size")

    args = ap.parse_args()

    if args.cmd == "build":
        build_index(
            input_jsonl=Path(args.input),
            out_dir=Path(args.out_dir),
            model_name=args.model,
            batch_size=args.batch_size,
            min_chars=args.min_chars,
            limit=args.limit,
            device=args.device,
        )
    elif args.cmd == "query":
        results = search(
            index_dir=Path(args.index_dir),
            query=args.q,
            k=args.k,
            batch_size=args.batch_size,
        )
        if not results:
            print("No results.")
            return
        print("\n🔎 Top matches:\n")
        for i, (score, m) in enumerate(results, 1):
            print(f"[{i}] score={score:.3f}")
            print(f"    policy : {m.get('policy')}")
            print(f"    section: {m.get('section')}")
            print(f"    source : {m.get('source')}")
            print(f"    preview: {m.get('preview')}\n")


if __name__ == "__main__":
    main()
