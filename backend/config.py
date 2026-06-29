from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = Path(os.getenv("DOCS_DIR", str(DATA_DIR / "docs")))
VECTOR_DIR = Path(os.getenv("VECTOR_DIR", str(DATA_DIR / "vectors")))
SQLITE_PATH = Path(os.getenv("SQLITE_PATH", str(DATA_DIR / "app.db")))


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "GRC Compliance Assistant")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    docs_dir: Path = DOCS_DIR
    vector_dir: Path = VECTOR_DIR
    sqlite_path: Path = SQLITE_PATH
    top_k: int = int(os.getenv("TOP_K", "5"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
    temperature: float = float(os.getenv("TEMPERATURE", "0.1"))


settings = Settings()

for directory in (DATA_DIR, settings.docs_dir, settings.vector_dir):
    directory.mkdir(parents=True, exist_ok=True)
