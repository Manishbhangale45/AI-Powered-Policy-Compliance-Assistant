from __future__ import annotations

from functools import lru_cache
import hashlib

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - optional dependency import guard
    SentenceTransformer = None

from backend.config import settings


class BGEEmbeddingService:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self._model = None
        self._fallback = HashingEmbeddingService()

    def _load_model(self) -> None:
        if self._model is not None or SentenceTransformer is None:
            return
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._model = SentenceTransformer(self.model_name, device=device)
        except Exception:
            try:
                self._model = SentenceTransformer(self.model_name, device="cpu")
            except Exception:
                self._model = None

    @staticmethod
    def _normalize_vector(vector: np.ndarray) -> list[float]:
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector.astype(float).tolist()
        return (vector / norm).astype(float).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        self._load_model()
        if self._model is None:
            return self._fallback.embed_documents(texts)
        embeddings = self._model.encode(
            [f"passage: {text}" for text in texts],
            batch_size=16,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        return np.asarray(embeddings, dtype=float).tolist()

    def embed_query(self, text: str) -> list[float]:
        self._load_model()
        if self._model is None:
            return self._fallback.embed_query(text)
        embedding = self._model.encode(
            [f"query: {text}"],
            batch_size=1,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )[0]
        return np.asarray(embedding, dtype=float).tolist()


class HashingEmbeddingService:
    dimension: int = 384

    def _embed(self, text: str) -> list[float]:
        vector = np.zeros(self.dimension, dtype=float)
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            index = int(digest[:8], 16) % self.dimension
            weight = 1.0 + (int(digest[8:12], 16) % 100) / 100.0
            vector[index] += weight
        norm = np.linalg.norm(vector)
        if norm:
            vector = vector / norm
        return vector.astype(float).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


@lru_cache(maxsize=1)
def get_embedding_service() -> BGEEmbeddingService:
    return BGEEmbeddingService()
