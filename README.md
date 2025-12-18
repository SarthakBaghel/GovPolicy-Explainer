# GovPolicy Explainer - Backend Setup Guide

A multilingual government policy Q&A system using RAG (Retrieval-Augmented Generation) with Ollama, FAISS, and FastAPI.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### 1. **Python 3.10+**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation:
     ```bash
     python --version
     ```

### 2. **Ollama** (for LLM inference)
   - Download from [ollama.ai](https://ollama.ai)
   - Install and start the Ollama service
   - Verify installation:
     ```bash
     ollama --version
     ```

### 3. **Tesseract OCR** (for scanned PDF processing)
   - **macOS:**
     ```bash
     brew install tesseract
     ```
   - **Ubuntu/Debian:**
     ```bash
     sudo apt-get install tesseract-ocr
     ```
   - **Windows:**
     - Download installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
     - Add to PATH environment variable

### 4. **FAISS** (Vector database)
   - Installed via `requirements.txt` (faiss-cpu)

---

## Quick Start

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd govpolicy-explainer
```

### Step 2: Set Up Python Virtual Environment
```bash
# Create virtual environment
python -m venv backend/.venv

# Activate virtual environment
# On macOS/Linux:
source backend/.venv/bin/activate

# On Windows:
backend\.venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Download Ollama Model
Start the Ollama service, then pull the required model:
```bash
ollama pull phi3:mini
```

You can also use other models:
```bash
ollama pull llama2        # Alternative: Llama 2
ollama pull mistral       # Alternative: Mistral
```

Verify the model is available:
```bash
ollama list
```

### Step 5: Prepare Your PDF Files
1. Create the raw PDFs directory:
   ```bash
   mkdir -p backend/data/raw_pdfs
   ```
2. Place your PDF policy documents in `backend/data/raw_pdfs/`

### Step 6: Build the FAISS Index
Run the PDF parsing and indexing pipeline:
```bash
# From the repo root
python -m backend.scripts.parse_pdfs backend/data/raw_pdfs backend/data/outputs/policy_chunks.jsonl

python -m backend.scripts.retriever build \
  --input backend/data/outputs/policy_chunks.jsonl \
  --out_dir backend/data/outputs/index \
  --model sentence-transformers/all-MiniLM-L6-v2
```

---

## Running the Application

### Option 1: FastAPI Backend Server
Start the API server:
```bash
# From backend directory
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Base URL:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs` (Swagger UI)
- **ReDoc:** `http://localhost:8000/redoc`

### Option 2: Command-Line Interface (CLI)
For interactive Q&A testing:
```bash
python -m backend.scripts.rag_cli
```

Type your questions and get answers. Type `exit` or `quit` to quit.

---

## API Endpoints

### 1. Upload & Index PDFs
**POST** `/api/rag/upload`
```bash
curl -X POST "http://localhost:8000/api/rag/upload" \
  -F "file=@your_policy.pdf"
```

### 2. Query the RAG System
**POST** `/api/rag/query`
```bash
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the eligibility criteria?", "k": 3}'
```

### 3. Search Documents
**POST** `/api/rag/search`
```bash
curl -X POST "http://localhost:8000/api/rag/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "policy details", "k": 3}'
```

---

## Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── data/
│   ├── raw_pdfs/          # Place your PDFs here
│   └── outputs/
│       ├── policy_chunks.jsonl  # Parsed chunks
│       └── index/              # FAISS index files
├── routes/
│   ├── rag_routes.py      # RAG query endpoints
│   └── upload_routes.py    # PDF upload endpoints
├── scripts/
│   ├── parse_pdfs.py      # PDF parsing & chunking
│   ├── retriever.py       # FAISS index management
│   ├── rag_pipeline.py    # RAG query pipeline
│   └── rag_cli.py         # CLI interface
└── services/
    ├── parser_service.py   # PDF parsing service
    ├── retriever_service.py # Retrieval service
    └── rag_service.py      # RAG service
```

---

## Configuration

Edit these files to customize behavior:

### [backend/routes/rag_routes.py](backend/routes/rag_routes.py)
- Change `EMBED_MODEL` for different embeddings
- Adjust `INDEX_DIR` for custom index location

### [backend/scripts/rag_pipeline.py](backend/scripts/rag_pipeline.py)
- Change `llm_model` (default: `phi3:mini`)
- Adjust prompt template in `build_prompt()`

### [backend/scripts/parse_pdfs.py](backend/scripts/parse_pdfs.py)
- `max_chars`: Chunk size (default: 1200)
- `overlap`: Chunk overlap (default: 120)
- `min_chars`: Minimum chunk length (default: 30)

---

## Troubleshooting

### "Ollama not found" error
- Ensure Ollama is installed and the service is running
- On macOS: `brew services start ollama`
- Verify: `ollama list` shows available models

### "phi3:mini not found" error
```bash
ollama pull phi3:mini
```

### "Tesseract not found" error
- Install tesseract (see Prerequisites section)
- On macOS: `brew install tesseract`

### "No module named 'backend'" error
- Ensure you're running from the repo root directory
- Virtual environment is activated

### FAISS index build fails
- Ensure `backend/data/raw_pdfs/` contains valid PDFs
- Check PDF file permissions
- Free up disk space

### Memory issues with large PDFs
- Reduce `batch_size` in retriever build command:
  ```bash
  python -m backend.scripts.retriever build \
    --input backend/data/outputs/policy_chunks.jsonl \
    --out_dir backend/data/outputs/index \
    --model sentence-transformers/all-MiniLM-L6-v2 \
    --batch_size 32
  ```

---

## Environment Variables

Create a `.env` file (optional):
```env
OLLAMA_MODEL=phi3:mini
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
INDEX_DIR=backend/data/outputs/index
TOKENIZERS_PARALLELISM=false
```

---

## Performance Tips

1. **Faster embedding:** Use `all-MiniLM-L6-v2` (smaller model)
2. **Better quality:** Use `all-mpnet-base-v2` (larger, slower)
3. **GPU acceleration:** Install FAISS with GPU support (optional)
4. **Parallel tokenization:** Already set `TOKENIZERS_PARALLELISM=false`

---

## System Requirements

- **RAM:** 8 GB minimum (16 GB recommended)
- **Disk:** 5-10 GB for models and index
- **CPU:** Multi-core processor recommended
- **Network:** Required for first-time model downloads

---

## License

[Your License Here]

## Support

For issues or questions, please open an issue on the repository.