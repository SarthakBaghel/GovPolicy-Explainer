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

### 2. **MongoDB** (for user and document metadata storage)
   - **macOS (using Homebrew):**
     ```bash
     brew tap mongodb/brew
     brew install mongodb-community
     brew services start mongodb-community
     ```
   - **Ubuntu/Debian:**
     ```bash
     sudo apt-get install -y mongodb
     sudo systemctl start mongodb
     ```
   - **Windows:**
     - Download from [mongodb.com](https://www.mongodb.com/try/download/community)
     - Run installer and follow setup wizard
   
   - **Or use MongoDB Atlas (Cloud):**
     - Create account at [mongodb.com/cloud](https://www.mongodb.com/cloud/atlas)
     - Create a cluster and get connection string
   
   - **Verify installation:**
     ```bash
     mongo --version
     # or test connection
     mongosh
     ```

### 3. **Ollama** (for LLM inference)
   - Download from [ollama.ai](https://ollama.ai)
   - Install and start the Ollama service
   - Verify installation:
     ```bash
     ollama --version
     ```

### 4. **Tesseract OCR** (for scanned PDF processing)
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

### 5. **FAISS** (Vector database)
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

### Step 3: Configure MongoDB Connection
Create a `.env` file in the project root:
```bash
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=govpolicy_explainer

# JWT Configuration (optional - uses defaults)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
```

**For MongoDB Atlas (Cloud):**
```bash
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/<database>
DATABASE_NAME=govpolicy_explainer
```

Ensure MongoDB is running:
```bash
# macOS
brew services start mongodb-community

# Ubuntu/Debian
sudo systemctl start mongodb

# Or verify local MongoDB is accessible
mongosh
```

### Step 4: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 5: Download Ollama Model
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

### Step 6: Start the Backend Server
From the project root with venv activated:
```bash
uvicorn backend.main:app --reload
```

The API will be available at:
- **Base URL:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs` (Swagger UI)
- **ReDoc:** `http://localhost:8000/redoc`

You should see MongoDB connection message:
```
✓ Connected to MongoDB
```

---

## Running the Application

### FastAPI Backend Server
Start the API server from the project root:
```bash
# Ensure virtual environment is activated
source backend/.venv/bin/activate

# Run the server
uvicorn backend.main:app --reload
```

The API will be available at:
- **Base URL:** `http://localhost:8000`
- **API Docs:** `http://localhost:8000/docs` (Swagger UI)
- **ReDoc:** `http://localhost:8000/redoc`

---

## Authentication & User Management

### 1. Register a New User
**POST** `/api/auth/register`
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully"
}
```

### 2. Login
**POST** `/api/auth/login`
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Use the token for authenticated requests:**
```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/documents/documents
```

---

## Document Management

### 1. Upload Document
**POST** `/api/rag/upload`

Requires authentication. Documents are:
- Parsed into chunks
- Indexed with FAISS embeddings
- Stored in MongoDB with metadata
- Original PDF is deleted (only chunks & index retained)

```bash
curl -X POST "http://localhost:8000/api/rag/upload" \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@policy.pdf"
```

**Response:**
```json
{
  "message": "Uploaded, parsed, and indexed policy.pdf",
  "doc_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "policy.pdf",
  "outputs": "backend/data/outputs/{user_id}/{doc_id}",
  "chunks_file": "backend/data/outputs/{user_id}/{doc_id}/policy_chunks.jsonl",
  "index_dir": "backend/data/outputs/{user_id}/{doc_id}/index"
}
```

### 2. List User Documents
**GET** `/api/documents/documents`

Requires authentication. Returns all documents for the logged-in user.

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/documents/documents
```

**Response:**
```json
{
  "user_id": "67796fef-3205-4248-b16c-6acd29213730",
  "documents": [
    {
      "_id": "69485f3ccf573e1503e9c4e6",
      "doc_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "67796fef-3205-4248-b16c-6acd29213730",
      "filename": "policy.pdf",
      "file_size": 233191,
      "created_at": "2025-12-21T20:57:32.113000",
      "status": "indexed"
    }
  ],
  "count": 1
}
```

### 3. Get Document Details
**GET** `/api/documents/documents/{doc_id}`

Requires authentication.

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/documents/documents/550e8400-e29b-41d4-a716-446655440000
```

### 4. Delete Document
**DELETE** `/api/documents/documents/{doc_id}`

Requires authentication. Deletes document from MongoDB and local storage.

```bash
curl -X DELETE \
  -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/documents/documents/550e8400-e29b-41d4-a716-446655440000
```

---

## RAG Query Endpoints

### Query Documents
**POST** `/api/rag/query`

```bash
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the eligibility criteria?",
    "k": 3
  }'
```

### Search Documents
**POST** `/api/rag/search`

```bash
curl -X POST "http://localhost:8000/api/rag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "policy details",
    "k": 3
  }'
```

---

## Command-Line Interface (CLI)
For interactive Q&A testing:
```bash
python -m backend.scripts.rag_cli
```

Type your questions and get answers. Type `exit` or `quit` to quit.

---

## Project Structure

```
backend/
├── main.py                    # FastAPI app entry point
├── requirements.txt           # Python dependencies
├── core/
│   ├── mongo_config.py       # MongoDB connection
│   ├── jwt_utils.py          # JWT token management
│   ├── security.py           # Password hashing & verification
│   ├── dependencies.py       # Authentication dependencies
│   └── auth_config.py        # Auth configuration
├── data/
│   ├── raw_pdfs/            # Temporary PDF storage (deleted after processing)
│   └── outputs/
│       └── {user_id}/
│           └── {doc_id}/
│               ├── policy_chunks.jsonl  # Parsed chunks
│               └── index/               # FAISS index files
├── models/
│   └── user.py              # User data model
├── repositories/
│   ├── user_repo.py         # MongoDB user operations
│   └── document_repo.py      # MongoDB document operations
├── routes/
│   ├── auth_routes.py       # Authentication endpoints
│   ├── document_routes.py    # Document management endpoints
│   ├── upload_routes.py      # PDF upload & processing
│   └── rag_routes.py         # RAG query endpoints
├── scripts/
│   ├── parse_pdfs.py        # PDF parsing & chunking
│   ├── retriever.py         # FAISS index management
│   ├── rag_pipeline.py      # RAG query pipeline
│   └── rag_cli.py           # CLI interface
└── services/
    ├── parser_service.py     # PDF parsing service
    ├── retriever_service.py  # Retrieval service
    └── rag_service.py        # RAG service
```

---

## Database Schema

### MongoDB Collections

#### `users`
```json
{
  "_id": ObjectId,
  "id": "uuid-string",
  "email": "user@example.com",
  "password_hash": "hashed_password",
  "documents": ["doc-id-1", "doc-id-2"],
  "created_at": ISODate
}
```

#### `documents`
```json
{
  "_id": ObjectId,
  "doc_id": "uuid-string",
  "user_id": "uuid-string",
  "filename": "policy.pdf",
  "file_size": 233191,
  "created_at": ISODate,
  "status": "indexed"
}
```

---

## Configuration

### Environment Variables (.env file)
Create a `.env` file in the project root:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
# Or for MongoDB Atlas:
# MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/
DATABASE_NAME=govpolicy_explainer

# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256

# Embedding Model (optional)
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Other
TOKENIZERS_PARALLELISM=false
```

### Backend Configuration Files

#### [backend/core/mongo_config.py](backend/core/mongo_config.py)
- MongoDB connection settings
- Database initialization

#### [backend/routes/upload_routes.py](backend/routes/upload_routes.py)
- `EMBED_MODEL`: Change embedding model
- `OUTPUTS_ROOT`: Custom output directory

#### [backend/scripts/rag_pipeline.py](backend/scripts/rag_pipeline.py)
- `llm_model`: Change LLM model (default: `phi3:mini`)
- Adjust prompt template

#### [backend/scripts/parse_pdfs.py](backend/scripts/parse_pdfs.py)
- `max_chars`: Chunk size (default: 1200)
- `overlap`: Chunk overlap (default: 120)

---

## Troubleshooting

### MongoDB Connection Issues
```
ERROR: Could not connect to MongoDB
```
- Ensure MongoDB is running: `mongosh` or `mongo`
- Check connection string in `.env`
- For MongoDB Atlas, verify IP whitelisting
- Check network connectivity

### "User already registered" on multiple logins
- Different email addresses are required for each user
- Use unique emails: `user1@example.com`, `user2@example.com`

### Authentication Token Expired
- Login again to get a new token
- Check token expiration time in [backend/core/jwt_utils.py](backend/core/jwt_utils.py)

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
- Run: `source backend/.venv/bin/activate`

### PDF Upload Fails with 500 Error
- Check if PDF is valid and readable
- Ensure sufficient disk space
- Check backend logs for parsing errors
- Verify FAISS and sentence-transformers are installed

### FAISS Index Build Fails
- Ensure `backend/data/raw_pdfs/` contains valid PDFs
- Free up disk space
- Reduce batch size if memory is limited

### Memory Issues with Large PDFs
- Reduce embedding batch size
- Upload PDFs individually
- Increase server RAM

### Document Not Found After Upload
- Verify MongoDB is running and accessible
- Check MongoDB logs for errors
- Ensure user is authenticated (JWT token is valid)

---

## Testing the Backend

### Run Complete Test Suite
Test authentication, document upload, listing, and deletion:

```bash
python test_document_flow.py
```

Expected output:
```
✓ PASS   - Login
✓ PASS   - Upload Document
✓ PASS   - List Documents
✓ PASS   - Get Document Info
✓ PASS   - Delete Document

Total: 5/6 tests passed
```

### Manual Testing with cURL

**1. Register User:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123"}'
```

**2. Login:**
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "TestPass123"}' \
  | jq -r '.access_token')

echo "Token: $TOKEN"
```

**3. Upload Document:**
```bash
curl -X POST "http://localhost:8000/api/rag/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@backend/data/raw_pdfs/policy_on_adoption_of_oss.pdf"
```

**4. List User Documents:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/documents/documents | jq .
```

**5. Query Documents:**
```bash
curl -X POST "http://localhost:8000/api/rag/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the policy about?", "k": 3}'
```

---

## System Requirements

- **RAM:** 8 GB minimum (16 GB recommended)
- **Disk:** 5-10 GB for models and embeddings
- **CPU:** Multi-core processor recommended
- **MongoDB:** Running locally or accessible via network
- **Network:** Required for first-time model/embedding downloads

---

## Performance Tips

1. **Faster embedding:** Use `all-MiniLM-L6-v2` (smaller model)
2. **Better quality:** Use `all-mpnet-base-v2` (larger, slower)
3. **GPU acceleration:** Install FAISS with GPU support (optional)
4. **Parallel tokenization:** Already set `TOKENIZERS_PARALLELISM=false`
5. **Database:** Use MongoDB Atlas for cloud deployment

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                       │
├──────────────────────┬──────────────────────────────────┤
│   Authentication     │    Document Management           │
│  - User Registration │  - Upload & Parse PDFs           │
│  - JWT Login         │  - Index with FAISS              │
│  - Token Validation  │  - Store Metadata in MongoDB     │
└──────────────────────┴──────────────────────────────────┘
          │                          │
          ▼                          ▼
    ┌──────────────┐         ┌──────────────────┐
    │   MongoDB    │         │   File Storage   │
    │ - Users      │         │  - Chunks        │
    │ - Documents  │         │  - FAISS Index   │
    │ - Sessions   │         │                  │
    └──────────────┘         └──────────────────┘
```

---

## Features

✅ **User Management**
- Secure registration and login
- JWT-based authentication
- Password hashing with bcrypt

✅ **Document Management**
- Multi-user document upload
- Automatic PDF parsing and chunking
- FAISS vector indexing
- Document-level access control
- Automatic PDF deletion after processing (storage optimization)

✅ **RAG Capabilities**
- Semantic search with FAISS
- Integration with Ollama LLMs
- Support for local and cloud-based models
- Multilingual support

✅ **Data Isolation**
- Per-user document storage
- Isolated FAISS indexes
- User-specific MongoDB documents

---

## License

[Your License Here]

## Support

For issues or questions, please open an issue on the repository.