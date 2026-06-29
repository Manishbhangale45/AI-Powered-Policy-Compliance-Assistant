from pathlib import Path

from rag.pipeline import RAGPipeline


def test_upload_txt_document(tmp_path: Path):
    pipeline = RAGPipeline(
        docs_dir=tmp_path / "docs",
        vector_dir=tmp_path / "vectors",
        sqlite_path=tmp_path / "app.db",
    )
    sample = tmp_path / "policy.txt"
    sample.write_text("Passwords must be changed every 90 days.", encoding="utf-8")

    result = pipeline.ingest_file(sample)

    assert result["chunk_count"] >= 1
    assert result["document_id"]


def test_delete_document(tmp_path: Path):
    pipeline = RAGPipeline(
        docs_dir=tmp_path / "docs",
        vector_dir=tmp_path / "vectors",
        sqlite_path=tmp_path / "app.db",
    )
    sample = tmp_path / "policy.txt"
    sample.write_text("Passwords must be changed every 90 days.", encoding="utf-8")

    result = pipeline.ingest_file(sample)
    doc_id = result["document_id"]

    assert pipeline.registry.get_document(doc_id) is not None
    assert pipeline.vector_store.count() > 0
    assert Path(result["stored_path"]).exists()

    pipeline.delete_document(doc_id)

    assert pipeline.registry.get_document(doc_id) is None
    assert pipeline.vector_store.count() == 0
    assert not Path(result["stored_path"]).exists()

