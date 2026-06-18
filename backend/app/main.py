from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db import init_db
from app.routes import chat, document, tools
from app.config import settings
import os

# Initialize DB tables
init_db()

app = FastAPI(
    title="BharatAI Backend API",
    description="Backend services for BharatAI - Chat, Search, PDF processing, Translation, and Grammar check.",
    version="1.0.0"
)

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)

# Mount static folder to serve generated files
app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

# CORS configurations
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat.router, prefix="/api")
app.include_router(document.router, prefix="/api")
app.include_router(tools.router, prefix="/api")

@app.get("/api/health")
def health_check():
    """Simple API health check endpoint."""
    return {
        "status": "healthy",
        "app": "BharatAI Backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
