from __future__ import annotations

from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import settings
from ingestion.loader import ExtractedPage


@dataclass(frozen=True, slots=True)
class ChunkRecord:
    chunk_id: str
    text: str
    source_file: str
    page_number: int
    document_id: str
    chunk_index: int
    mime_type: str


class DocumentChunker:
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.chunk_size,
            chunk_overlap=chunk_overlap or settings.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
        )

    def chunk_pages(self, pages: list[ExtractedPage]) -> list[ChunkRecord]:
        chunks: list[ChunkRecord] = []
        for page in pages:
            split_texts = self.splitter.split_text(page.text)
            for index, text in enumerate(split_texts):
                clean_text = text.strip()
                if not clean_text:
                    continue
                chunks.append(
                    ChunkRecord(
                        chunk_id=f"{page.document_id}:{page.page_number}:{index}",
                        text=clean_text,
                        source_file=page.source_file,
                        page_number=page.page_number,
                        document_id=page.document_id,
                        chunk_index=index,
                        mime_type=page.mime_type,
                    )
                )
        return chunks
