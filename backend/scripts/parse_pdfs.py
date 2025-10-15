# scripts/parse_pdfs.py

# to run # from repo root
# python scripts/parse_pdfs.py data/raw_pdfs data/outputs/policy_chunks.jsonl

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any

import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from PIL import Image

# --------------------------- text helpers ---------------------------

def normalize_whitespace(s: str) -> str:
    s = s.replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def fix_hyphenation(s: str) -> str:
    return re.sub(r"(\w+)-\n(\w+)", r"\1\2", s)

def collapse_lines_to_paragraph(lines: List[str]) -> str:
    text = "\n".join(lines)
    text = fix_hyphenation(text)
    text = normalize_whitespace(text)
    return text

def split_into_chunks(text: str, max_chars: int = 1200, overlap: int = 120) -> List[str]:
    if len(text) <= max_chars:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, cur = [], ""
    for sent in sentences:
        if not cur:
            cur = sent
        elif len(cur) + 1 + len(sent) <= max_chars:
            cur += " " + sent
        else:
            chunks.append(cur.strip())
            carry = cur[-overlap:] if len(cur) > overlap else ""
            cur = (carry + " " + sent).strip()
    if cur:
        chunks.append(cur.strip())
    return [c for c in chunks if c]

# --------------------------- heading heuristics ---------------------------

def compute_size_threshold(page_dict: Dict[str, Any]) -> float:
    sizes = []
    for block in page_dict.get("blocks", []):
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                if span.get("text", "").strip():
                    sizes.append(span.get("size", 0))
    if not sizes:
        return 100.0
    sizes.sort()
    median = sizes[len(sizes)//2]
    return max(12.0, median * 1.15)

def is_heading(span_text: str, span_size: float, heading_threshold: float) -> bool:
    txt = span_text.strip()
    if not txt:
        return False
    short = len(txt) <= 140
    looks_like_heading = bool(re.match(r"^([A-Z0-9 .\-:()]+|(\d+(\.\d+)*\s+.+))$", txt))
    return short and (span_size >= heading_threshold or looks_like_heading)

# --------------------------- table extraction ---------------------------

def extract_tables_plumber(pdf_path: Path, page_index: int) -> List[str]:
    tables_txt = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        if page_index >= len(pdf.pages):
            return []
        page = pdf.pages[page_index]
        settings = dict(vertical_strategy="lines", horizontal_strategy="lines")
        tables = page.extract_tables(table_settings=settings)
        if not tables:
            settings = dict(vertical_strategy="text", horizontal_strategy="text")
            tables = page.extract_tables(table_settings=settings)
        for tbl in tables or []:
            lines = []
            for row in tbl:
                row = [normalize_whitespace(cell or "") for cell in row]
                lines.append("\t".join(row))
            if lines:
                tables_txt.append("\n".join(lines))
    return tables_txt

# --------------------------- OCR fallback ---------------------------

def ocr_page(page) -> str:
    pix = page.get_pixmap(dpi=300)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    text = pytesseract.image_to_string(img, lang="eng+hin")
    return normalize_whitespace(text)

# --------------------------- policy name heuristic ---------------------------

def guess_policy_name(pdf_path: Path) -> str:
    stem = pdf_path.stem
    m = re.match(r"^([^_-]+)", stem)
    base = m.group(1) if m else stem
    base = re.sub(r"[^A-Za-z0-9]+", " ", base).strip()
    return base

# --------------------------- main extraction ---------------------------

def parse_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    policy = guess_policy_name(pdf_path)
    doc = fitz.open(str(pdf_path))
    records: List[Dict[str, Any]] = []
    current_section = None

    for pno in range(len(doc)):
        page = doc[pno]
        pdict = page.get_text("dict")

        # If no blocks (scanned PDF) → OCR
        if not pdict["blocks"]:
            print(f"⚠️ Page {pno+1} of {pdf_path.name} looks like image → running OCR...")
            text = ocr_page(page)
            for chunk in split_into_chunks(text):
                records.append({
                    "policy": policy,
                    "section": "OCR Section",
                    "type": "paragraph",
                    "text": chunk,
                    "source": f"{pdf_path.name}#page={pno+1}"
                })
            continue

        heading_threshold = compute_size_threshold(pdict)

        para_lines: List[str] = []
        def flush_paragraph():
            nonlocal para_lines
            if para_lines:
                paragraph = collapse_lines_to_paragraph(para_lines)
                if paragraph:
                    for chunk in split_into_chunks(paragraph):
                        records.append({
                            "policy": policy,
                            "section": current_section or "General",
                            "type": "paragraph",
                            "text": chunk,
                            "source": f"{pdf_path.name}#page={pno+1}"
                        })
                para_lines = []

        for block in pdict.get("blocks", []):
            for line in block.get("lines", []):
                line_text = "".join(span.get("text", "") for span in line.get("spans", []))
                line_text = normalize_whitespace(line_text)
                if not line_text:
                    flush_paragraph()
                    continue

                headingish = False
                for span in line.get("spans", []):
                    if is_heading(span.get("text", ""), span.get("size", 0), heading_threshold):
                        headingish = True
                        break

                if headingish:
                    flush_paragraph()
                    heading_text = normalize_whitespace(line_text)
                    current_section = heading_text
                    records.append({
                        "policy": policy,
                        "section": current_section,
                        "type": "heading",
                        "text": heading_text,
                        "source": f"{pdf_path.name}#page={pno+1}"
                    })
                else:
                    para_lines.append(line_text)

        flush_paragraph()

        # tables
        tables = extract_tables_plumber(pdf_path, pno)
        for t in tables:
            records.append({
                "policy": policy,
                "section": current_section or "General",
                "type": "table",
                "text": t,
                "source": f"{pdf_path.name}#page={pno+1}"
            })

    doc.close()
    return records

def main():
    ap = argparse.ArgumentParser(description="Parse PDFs → JSONL (headings, paragraphs, tables, OCR fallback).")
    ap.add_argument("input_dir", type=str, help="Folder containing PDFs")
    ap.add_argument("output_jsonl", type=str, help="Output JSONL path")
    args = ap.parse_args()

    in_dir = Path(args.input_dir)
    out_path = Path(args.output_jsonl)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(list(in_dir.glob("**/*.pdf")))
    if not pdfs:
        print(f"No PDFs found under: {in_dir.resolve()}")
        return

    total = 0
    with out_path.open("w", encoding="utf-8") as f:
        for pdf in pdfs:
            try:
                recs = parse_pdf(pdf)
                for r in recs:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                total += len(recs)
                print(f"✓ Parsed {pdf.name}: {len(recs)} records")
            except Exception as e:
                print(f"✗ Error parsing {pdf.name}: {e}")

    print(f"\nDone. Wrote {total} records → {out_path}")

if __name__ == "__main__":
    main()
