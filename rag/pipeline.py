from __future__ import annotations

from dataclasses import dataclass
from dataclasses import asdict
from pathlib import Path
from typing import Any

from backend.config import settings
from ingestion.chunker import DocumentChunker
from ingestion.loader import load_document
from llm.gemini_client import get_gemini_client
from rag.prompt_template import build_prompt
from rag.retrieve import Retriever
from storage.sqlite_store import SQLiteRegistry
from utils.logger import logger
from utils.security import (
    generate_document_id,
    mask_sensitive_information,
    sanitize_filename,
    sha256_bytes,
)
from embedding.embed import get_embedding_service
from vector_db.chroma_store import ChromaVectorStore


@dataclass(frozen=True, slots=True)
class AnswerPayload:
    answer: str
    sources: list[dict[str, Any]]
    confidence: float
    document_id: str | None = None


class RAGPipeline:
    def __init__(
        self,
        docs_dir: Path | None = None,
        vector_dir: Path | None = None,
        sqlite_path: Path | None = None,
        top_k: int | None = None,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        registry: SQLiteRegistry | None = None,
        vector_store: ChromaVectorStore | None = None,
        embedder: Any | None = None,
        retriever: Retriever | None = None,
        gemini_client: Any | None = None,
    ):
        self.docs_dir = Path(docs_dir or settings.docs_dir)
        self.vector_dir = Path(vector_dir or settings.vector_dir)
        self.sqlite_path = Path(sqlite_path or settings.sqlite_path)
        self.top_k = top_k or settings.top_k
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        self.registry = registry or SQLiteRegistry(self.sqlite_path)
        self.chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.vector_store = vector_store or ChromaVectorStore(persist_directory=self.vector_dir)
        self.embedder = embedder or get_embedding_service()
        self.retriever = retriever or Retriever(store=self.vector_store)
        self.gemini = gemini_client or get_gemini_client()

    def ingest_file(self, file_path: Path, original_name: str | None = None) -> dict[str, Any]:
        raw_bytes = file_path.read_bytes()
        original_name = original_name or file_path.name
        sanitized_name = sanitize_filename(original_name)
        document_id = generate_document_id(raw_bytes, sanitized_name)
        target_path = self.docs_dir / f"{document_id}_{sanitized_name}"
        target_path.write_bytes(raw_bytes)

        pages = load_document(target_path, document_id=document_id)
        chunks = self.chunker.chunk_pages(pages)
        chunk_texts = [mask_sensitive_information(chunk.text) for chunk in chunks]
        embeddings = self.embedder.embed_documents(chunk_texts)
        payload_chunks = [
            {
                "chunk_id": chunk.chunk_id,
                "text": masked_text,
                "source_file": chunk.source_file,
                "page_number": chunk.page_number,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "mime_type": chunk.mime_type,
            }
            for chunk, masked_text in zip(chunks, chunk_texts)
        ]
        self.vector_store.upsert_chunks(payload_chunks, embeddings)
        checksum = sha256_bytes(raw_bytes)
        record = SQLiteRegistry.build_record(
            document_id=document_id,
            original_name=original_name,
            stored_path=str(target_path),
            checksum=checksum,
            mime_type=pages[0].mime_type if pages else "application/octet-stream",
            chunk_count=len(chunks),
        )
        self.registry.upsert_document(record)
        logger.info("Indexed document %s with %s chunks", document_id, len(chunks))
        return {
            "document_id": document_id,
            "filename": original_name,
            "chunk_count": len(chunks),
            "stored_path": str(target_path),
        }

    def ask(self, query: str, document_id: str | None = None) -> AnswerPayload:
        retrieval = self.retriever.retrieve(query=query, top_k=self.top_k, document_id=document_id)
        prompt = build_prompt(context=retrieval.context or "", query=mask_sensitive_information(query))
        response = self.gemini.generate(prompt)
        sources = [
            {
                "source_file": chunk.source_file,
                "page_number": chunk.page_number,
                "chunk_id": chunk.chunk_id,
                "distance": chunk.distance,
                "text": chunk.text,
            }
            for chunk in retrieval.chunks
        ]
        answer = response.text or "I could not find this information in company policies."
        return AnswerPayload(answer=answer, sources=sources, confidence=retrieval.confidence, document_id=document_id)

    def list_documents(self) -> list[dict[str, Any]]:
        return [asdict(record) for record in self.registry.list_documents()]

    def delete_document(self, document_id: str) -> None:
        record = self.registry.get_document(document_id)
        if record is None:
            logger.warning("Document with ID %s not found in registry", document_id)
            return

        # 1. Delete from vector store
        try:
            self.vector_store.collection.delete(where={"document_id": document_id})
            logger.info("Deleted vector chunks for document %s", document_id)
        except Exception as e:
            logger.error("Failed to delete vector chunks for document %s: %s", document_id, e)

        # 2. Delete physical file from disk
        path = Path(record.stored_path)
        if path.exists():
            try:
                path.unlink()
                logger.info("Deleted physical file %s", record.stored_path)
            except Exception as e:
                logger.error("Failed to delete file %s: %s", record.stored_path, e)

        # 3. Delete registry entry
        self.registry.delete_document(document_id)
        logger.info("Deleted registry entry for document %s", document_id)

    def reindex_all(self) -> dict[str, int]:
        documents = self.registry.list_documents()
        indexed = 0
        for document in documents:
            path = Path(document.stored_path)
            if path.exists():
                self.ingest_file(path, original_name=document.original_name)
                indexed += 1
        return {"reindexed": indexed, "documents": len(documents)}
