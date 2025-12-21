# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your RAG routes
from backend.routes.rag_routes import router as rag_router
from backend.routes.upload_routes import router as upload_router
from backend.routes.auth_routes import router as auth_router

app = FastAPI(
    title="GovPolicy Explainer API",
    description="Backend for multilingual government policy QA system",
    version="1.0.0"
)

# CORS setup for frontend connections (Streamlit/React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(upload_router, prefix="/api/rag", tags=["Upload"])
app.include_router(rag_router, prefix="/api/rag", tags=["RAG"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "GovPolicy Explainer Backend is running 🚀"}
