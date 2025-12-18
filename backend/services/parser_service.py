from pathlib import Path
from backend.scripts.parse_pdfs import parse_pdf
import json
import shutil
import re


def _sanitize_name(name: str) -> str:
    """Sanitize document name for use as a folder."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)


class ParserService:
    def __init__(self, raw_dir: str = "backend/data/raw_pdfs", outputs_root: str = "backend/data/outputs"):
        self.raw_dir = Path(raw_dir)
        self.outputs_root = Path(outputs_root)
        self.outputs_root.mkdir(parents=True, exist_ok=True)

    def parse_all_pdfs(self):
        """Parse all PDFs in raw_dir and write to outputs_root/policy_chunks.jsonl (legacy)."""
        pdfs = sorted(list(self.raw_dir.glob("**/*.pdf")))
        if not pdfs:
            return {"error": "No PDFs found"}

        total_records = 0
        out_path = self.outputs_root / "policy_chunks.jsonl"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            for pdf in pdfs:
                recs = parse_pdf(pdf)
                for r in recs:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                total_records += len(recs)
        return {"message": f"Parsed {len(pdfs)} PDFs, total records: {total_records}", "path": str(out_path)}

    def parse_pdf_file(self, pdf_path: Path, doc_name: str | None = None):
        """Parse a single PDF into a per-document output folder.
        
        Clears any previous outputs for this document to prevent mixing.
        Returns (out_dir, out_jsonl_path).
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        name = doc_name or pdf_path.stem
        name = _sanitize_name(name)
        out_dir = self.outputs_root / name

        # Clear previous outputs for this document
        if out_dir.exists() and out_dir.is_dir():
            shutil.rmtree(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        out_jsonl = out_dir / "policy_chunks.jsonl"
        records = parse_pdf(pdf_path)
        with out_jsonl.open("w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        return out_dir, out_jsonl
