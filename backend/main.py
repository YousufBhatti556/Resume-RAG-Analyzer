import uvicorn
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth.auth_routes import router as auth_router
from backend.database import models  # Ensures models are registered before table creation
from backend.database.config import Base, engine
from backend.rag.routes import router as rag_router

# Create tables on startup if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS middleware - frontend se requests allow karne ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(rag_router)


@app.get("/")
async def root():
    return {"message": "API is running", "routes": ["/auth/*", "/rag/analyze"]}


@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to check if .env is loading correctly"""
    from backend.config import get_settings
    import os
    settings = get_settings()
    return {
        "google_api_key_set": bool(settings.google_api_key),
        "google_api_key_length": len(settings.google_api_key) if settings.google_api_key else 0,
        "google_api_key_preview": settings.google_api_key[:10] + "..." if settings.google_api_key else None,
        "env_file_path": str(Path(__file__).resolve().parent.parent / ".env"),
        "env_file_exists": (Path(__file__).resolve().parent.parent / ".env").exists(),
        "os_env_google_api_key": bool(os.getenv("GOOGLE_API_KEY")),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)