from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
SENSITIVE_PATTERNS = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    re.compile(r"\b(?:sk|rk|pk|ak)_[A-Za-z0-9]{16,}\b", re.IGNORECASE),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-+=/]+"),
    re.compile(r"(?i)password\s*[:=]\s*[^\s]+"),
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
]


def is_supported_document(path: Path) -> bool:
    return path.suffix.lower() in ALLOWED_EXTENSIONS


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name.strip().replace(" ", "_")
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    return name or "document"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mask_sensitive_information(text: str) -> str:
    sanitized = text
    for pattern in SENSITIVE_PATTERNS:
        sanitized = pattern.sub("[REDACTED]", sanitized)
    return sanitized


def generate_document_id(file_bytes: bytes, filename: str) -> str:
    seed = f"{filename}:{hashlib.sha256(file_bytes).hexdigest()}".encode("utf-8")
    return hashlib.sha256(seed).hexdigest()[:16]


def read_file_bytes(path: Path) -> bytes:
    return path.read_bytes()


def env_value(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else default
