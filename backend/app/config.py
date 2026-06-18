import os
from pydantic_settings import BaseSettings
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    GEMINI_API_KEY: str | None = None
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/bharatai.db"
    STORAGE_DIR: str = str(BASE_DIR / "storage")
    
    # PDF processing configuration
    MAX_FILE_SIZE_MB: int = 10
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# Ensure storage directory exists
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
