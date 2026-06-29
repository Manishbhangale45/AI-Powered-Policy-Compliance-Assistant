from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import fitz

from utils.logger import logger
from utils.security import is_supported_document


@dataclass(frozen=True, slots=True)
class ExtractedPage:
    text: str
    page_number: int
    source_file: str
    document_id: str
    mime_type: str


def detect_mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "application/pdf"
    if suffix == ".docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if suffix == ".txt":
        return "text/plain"
    return "application/octet-stream"


def extract_text_from_pdf(path: Path, document_id: str) -> list[ExtractedPage]:
    pages: list[ExtractedPage] = []
    with fitz.open(path) as pdf_document:
        for index, page in enumerate(pdf_document, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append(
                    ExtractedPage(
                        text=text,
                        page_number=index,
                        source_file=path.name,
                        document_id=document_id,
                        mime_type=detect_mime_type(path),
                    )
                )
    return pages


def extract_text_from_docx(path: Path, document_id: str) -> list[ExtractedPage]:
    try:
        from unstructured.partition.docx import partition_docx

        elements = partition_docx(filename=str(path))
        text = "\n".join(element.text for element in elements if getattr(element, "text", None))
        if text.strip():
            return [
                ExtractedPage(
                    text=text.strip(),
                    page_number=1,
                    source_file=path.name,
                    document_id=document_id,
                    mime_type=detect_mime_type(path),
                )
            ]
    except Exception as exc:  # pragma: no cover - fallback path
        logger.info("Falling back to python-docx for DOCX extraction: %s", exc)

    from docx import Document

    document = Document(str(path))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())
    return [
        ExtractedPage(
            text=text.strip(),
            page_number=1,
            source_file=path.name,
            document_id=document_id,
            mime_type=detect_mime_type(path),
        )
    ]


def extract_text_from_txt(path: Path, document_id: str) -> list[ExtractedPage]:
    try:
        from unstructured.partition.text import partition_text

        elements = partition_text(text=path.read_text(encoding="utf-8", errors="ignore"))
        text = "\n".join(element.text for element in elements if getattr(element, "text", None))
    except Exception:  # pragma: no cover - fallback path
        text = path.read_text(encoding="utf-8", errors="ignore")

    text = text.strip()
    if not text:
        return []
    return [
        ExtractedPage(
            text=text,
            page_number=1,
            source_file=path.name,
            document_id=document_id,
            mime_type=detect_mime_type(path),
        )
    ]


def load_document(path: Path, document_id: str) -> list[ExtractedPage]:
    if not is_supported_document(path):
        raise ValueError(f"Unsupported document type: {path.suffix}")

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path, document_id)
    if suffix == ".docx":
        return extract_text_from_docx(path, document_id)
    return extract_text_from_txt(path, document_id)
