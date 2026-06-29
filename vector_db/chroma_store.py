from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from backend.config import settings


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    source_file: str
    page_number: int
    document_id: str
    chunk_index: int
    mime_type: str
    distance: float


class ChromaVectorStore:
    def __init__(self, persist_directory: Path | None = None, collection_name: str = "grc_compliance"):
        self.persist_directory = Path(persist_directory or settings.vector_dir)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        self.collection_name = collection_name
        self.collection: Collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(
        self,
        chunks: list[dict[str, Any]],
        embeddings: list[list[float]],
    ) -> None:
        if not chunks:
            return
        self.collection.upsert(
            ids=[chunk["chunk_id"] for chunk in chunks],
            documents=[chunk["text"] for chunk in chunks],
            embeddings=embeddings,
            metadatas=[
                {
                    "source_file": chunk["source_file"],
                    "page_number": int(chunk["page_number"]),
                    "document_id": chunk["document_id"],
                    "chunk_index": int(chunk["chunk_index"]),
                    "mime_type": chunk["mime_type"],
                }
                for chunk in chunks
            ],
        )

    def query(self, query_embedding: list[float], top_k: int = 5, document_id: str | None = None) -> list[RetrievedChunk]:
        where = {"document_id": document_id} if document_id else None
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        chunks: list[RetrievedChunk] = []
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
            chunks.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=text or "",
                    source_file=metadata.get("source_file", "unknown"),
                    page_number=int(metadata.get("page_number", 1)),
                    document_id=metadata.get("document_id", ""),
                    chunk_index=int(metadata.get("chunk_index", 0)),
                    mime_type=metadata.get("mime_type", ""),
                    distance=float(distance),
                )
            )
        return chunks

    def count(self) -> int:
        return self.collection.count()

    def reset(self) -> None:
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
