import pytest
from pathlib import Path
from fastapi.testclient import TestClient
import fitz
from backend.api import app
import backend.api
from rag.pipeline import RAGPipeline


@pytest.fixture
def test_client(tmp_path):
    # Setup test pipeline
    test_pipeline = RAGPipeline(
        docs_dir=tmp_path / "docs",
        vector_dir=tmp_path / "vectors",
        sqlite_path=tmp_path / "app.db",
    )
    
    # Store the original pipeline and patch it
    orig_pipeline = backend.api.pipeline
    backend.api.pipeline = test_pipeline
    
    # Create test PDF
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 50), "First page content")
    p2 = doc.new_page()
    p2.insert_text((50, 50), "Second page content")
    doc.save(str(pdf_path))
    doc.close()
    
    # Ingest the test PDF
    ingest_result = test_pipeline.ingest_file(pdf_path)
    doc_id = ingest_result["document_id"]
    
    client = TestClient(app)
    yield client, doc_id
    
    # Restore original pipeline
    backend.api.pipeline = orig_pipeline


def test_get_document_page_pdf(test_client):
    client, doc_id = test_client
    
    # Request page 2
    response = client.get(f"/documents/{doc_id}/page/2")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == "inline"
    
    # Verify the returned PDF is valid and has 1 page
    returned_pdf = fitz.open(stream=response.content, filetype="pdf")
    assert len(returned_pdf) == 1
    text = returned_pdf[0].get_text().strip()
    assert "Second page content" in text
    returned_pdf.close()


def test_get_document_page_image(test_client):
    client, doc_id = test_client
    
    # Request page 1 image
    response = client.get(f"/documents/{doc_id}/page/1/image")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    
    # Verify it has valid PNG signature
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")


def test_get_document_page_out_of_range(test_client):
    client, doc_id = test_client
    
    # Request page 3 (out of range since doc has 2 pages)
    response = client.get(f"/documents/{doc_id}/page/3")
    assert response.status_code == 400
    assert "out of range" in response.json()["detail"]


def test_get_document_page_not_found(test_client):
    client, doc_id = test_client
    
    response = client.get("/documents/nonexistent/page/1")
    assert response.status_code == 404
