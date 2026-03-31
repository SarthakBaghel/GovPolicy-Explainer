# GovPolicy Explainer

GovPolicy Explainer is a FastAPI backend for uploading policy PDFs, breaking them into chunks, building FAISS indexes, and answering questions with Ollama. MongoDB is used for users and document metadata.

This repo is backend-only at the moment.

## What The Codebase Does

- Registers users and issues JWT access tokens
- Uploads PDFs through the API
- Extracts headings, paragraphs, and tables from PDFs
- Falls back to OCR for image-heavy pages
- Builds a per-user, per-document FAISS index with SentenceTransformers
- Stores document metadata in MongoDB
- Lets users list, inspect, and delete their uploaded documents

## Main Stack

- FastAPI
- MongoDB
- FAISS
- SentenceTransformers
- Ollama (`phi3:mini` by default)
- PyMuPDF, pdfplumber, pytesseract

## Repo Shape

```text
backend/
  main.py                  FastAPI app entrypoint
  routes/                  Auth, upload, document, and RAG routes
  services/                Parsing, retrieval, and RAG service wrappers
  scripts/                 PDF parsing, indexing, and CLI helpers
  repositories/            MongoDB access for users and documents
  core/                    Mongo config, JWT helpers, password hashing
  data/
    raw_pdfs/              Temporary upload location
    outputs/               Parsed chunks and FAISS indexes

inspect_mongodb.py         Local MongoDB inspection helper
migrate_mongodb.py         Local migration helper
test_document_flow.py      End-to-end API smoke script
test_verify_documents.py   MongoDB/document verification script
```

## Quick Start

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Python dependencies

```bash
pip install -r backend/requirements.txt
pip install python-multipart python-jose passlib[argon2] Pillow
```

The second command is needed because those packages are imported by the code but are not currently listed in `backend/requirements.txt`.

### 3. Install system dependencies

- MongoDB
- Ollama
- Tesseract OCR

The OCR path uses `eng+hin`, so make sure your Tesseract install includes Hindi language data if you want Hindi OCR to work.

### 4. Start required services

```bash
ollama pull phi3:mini
```

Start MongoDB and make sure Ollama is running before you launch the API.

### 5. Create `.env` in the project root

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=govpolicy_explainer
```

Only MongoDB settings are read from `.env` right now. JWT settings are hardcoded in `backend/core/auth_config.py`.

### 6. Run the API

```bash
uvicorn backend.main:app --reload
```

Useful URLs:

- API root: `http://localhost:8000/`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Typical API Flow

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePassword123"}'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePassword123"}'
```

Use the returned bearer token for authenticated routes.

### Upload a PDF

```bash
curl -X POST http://localhost:8000/api/rag/upload \
  -H "Authorization: Bearer <token>" \
  -F "file=@policy.pdf"
```

On a successful upload, the app:

- saves the file briefly under `backend/data/raw_pdfs/{user_id}/`
- parses it into `backend/data/outputs/{user_id}/{doc_id}/policy_chunks.jsonl`
- builds a FAISS index under `backend/data/outputs/{user_id}/{doc_id}/index/`
- deletes the original uploaded PDF
- stores document metadata in MongoDB

### List or delete uploaded documents

- `GET /api/documents/documents`
- `GET /api/documents/documents/{doc_id}`
- `DELETE /api/documents/documents/{doc_id}`

## Important Notes

- The upload and document-management flow is the most complete path in the repo today.
- The `POST /api/rag/query`, `POST /api/rag/search`, and `GET /api/rag/indexes` routes still reflect an older index layout. They are useful as developer-facing helpers, but they do not fully match the per-user upload structure.
- Those RAG routes are not protected by JWT in the current code.
- The root-level helper scripts are local/debug oriented and include hardcoded absolute paths, so they may need small edits before reuse on another machine.

## Sample Data

The repo already contains example PDFs and generated output under `backend/data/`, which makes it easier to inspect the expected storage layout.

## If Something Fails

- MongoDB errors: check your `.env` and confirm the database is running
- Ollama errors: confirm `ollama pull phi3:mini` has completed and the Ollama service is up
- OCR errors: confirm Tesseract is installed and language data is available
- Upload errors: missing `python-multipart` is a common cause if the extra install step was skipped
- Import errors for `jose`, `passlib`, or `PIL`: install the extra Python packages listed above
