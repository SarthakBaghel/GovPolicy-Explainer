from pathlib import Path
from backend.scripts.parse_pdfs import parse_pdf
import json

class ParserService:
    def __init__(self, raw_dir: str = "backend/data/raw_pdfs", output_jsonl: str = "backend/data/outputs/policy_chunks.jsonl"):
        self.raw_dir = Path(raw_dir)
        self.output_jsonl = Path(output_jsonl)
        self.output_jsonl.parent.mkdir(parents=True, exist_ok=True)

    def parse_all_pdfs(self):
        pdfs = sorted(list(self.raw_dir.glob("**/*.pdf")))
        if not pdfs:
            return {"error": "No PDFs found"}

        total_records = 0
        with self.output_jsonl.open("w", encoding="utf-8") as f:
            for pdf in pdfs:
                recs = parse_pdf(pdf)
                for r in recs:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                total_records += len(recs)
        return {"message": f"Parsed {len(pdfs)} PDFs, total records: {total_records}"}
