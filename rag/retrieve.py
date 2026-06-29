from __future__ import annotations

from dataclasses import dataclass

from embedding.embed import get_embedding_service
from vector_db.chroma_store import ChromaVectorStore, RetrievedChunk


@dataclass(frozen=True, slots=True)
class RetrievalResult:
    chunks: list[RetrievedChunk]
    context: str
    confidence: float


class Retriever:
    def __init__(self, store: ChromaVectorStore | None = None):
        self.store = store or ChromaVectorStore()
        self.embedder = get_embedding_service()

    def retrieve(self, query: str, top_k: int = 5, document_id: str | None = None) -> RetrievalResult:
        query_embedding = self.embedder.embed_query(query)
        chunks = self.store.query(query_embedding=query_embedding, top_k=top_k, document_id=document_id)
        context_lines: list[str] = []
        for chunk in chunks:
            context_lines.append(
                f"Source: {chunk.source_file} | Page: {chunk.page_number} | Chunk: {chunk.chunk_index}\n{chunk.text}"
            )
        context = "\n\n---\n\n".join(context_lines)
        confidence = self._confidence_from_distances(chunks)
        return RetrievalResult(chunks=chunks, context=context, confidence=confidence)

    @staticmethod
    def _confidence_from_distances(chunks: list[RetrievedChunk]) -> float:
        if not chunks:
            return 0.0
        best_distance = min(chunk.distance for chunk in chunks)
        confidence = max(0.0, 1.0 - best_distance)
        return round(confidence, 3)
