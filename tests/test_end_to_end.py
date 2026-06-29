from pathlib import Path

from rag.pipeline import RAGPipeline


def test_end_to_end_reindex_roundtrip(tmp_path: Path):
    pipeline = RAGPipeline(
        docs_dir=tmp_path / "docs",
        vector_dir=tmp_path / "vectors",
        sqlite_path=tmp_path / "app.db",
    )
    sample = tmp_path / "incident.txt"
    sample.write_text("Incidents must be reported within 1 hour.", encoding="utf-8")

    ingest_result = pipeline.ingest_file(sample)
    assert ingest_result["chunk_count"] >= 1
