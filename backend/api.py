from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from fastapi.responses import FileResponse
from rag.pipeline import RAGPipeline

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = RAGPipeline()


class AskRequest(BaseModel):
    query: str
    document_id: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/documents")
def list_documents() -> list[dict[str, object]]:
    return pipeline.list_documents()


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> dict[str, object]:
    suffix = Path(file.filename or "document").suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(await file.read())
        temp_path = Path(temp_file.name)
    try:
        custom_pipeline = RAGPipeline(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return custom_pipeline.ingest_file(temp_path, original_name=file.filename)
    finally:
        temp_path.unlink(missing_ok=True)


@app.post("/ask")
def ask(payload: AskRequest) -> dict[str, object]:
    query = payload.query.strip()
    document_id = payload.document_id
    if not query:
        return {"answer": "Please provide a question.", "sources": [], "confidence": 0.0}
    result = pipeline.ask(query=query, document_id=document_id)
    return {
        "answer": result.answer,
        "sources": result.sources,
        "confidence": result.confidence,
        "document_id": result.document_id,
    }


@app.post("/reindex")
def reindex(chunk_size: int | None = None, chunk_overlap: int | None = None) -> dict[str, int]:
    custom_pipeline = RAGPipeline(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return custom_pipeline.reindex_all()


@app.delete("/documents/{document_id}")
def delete_document(document_id: str) -> dict[str, str]:
    record = pipeline.registry.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    pipeline.delete_document(document_id)
    return {"status": "success", "message": f"Document {document_id} deleted."}


@app.get("/documents/{document_id}/download")
def download_document(document_id: str) -> FileResponse:
    record = pipeline.registry.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    path = Path(record.stored_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Physical file not found")
    return FileResponse(path, filename=record.original_name, media_type=record.mime_type)


@app.get("/documents/{document_id}/page/{page_number}")
def get_document_page(document_id: str, page_number: int) -> Response | FileResponse:
    from fastapi.responses import Response
    record = pipeline.registry.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    path = Path(record.stored_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Physical file not found")
    
    if record.mime_type == "application/pdf":
        import fitz
        try:
            with fitz.open(path) as doc:
                page_idx = page_number - 1
                if page_idx < 0 or page_idx >= len(doc):
                    raise HTTPException(status_code=400, detail=f"Page {page_number} out of range (1-{len(doc)})")
                new_doc = fitz.open()
                new_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
                pdf_bytes = new_doc.write()
                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={"Content-Disposition": "inline"}
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting page: {str(e)}")
    else:
        return FileResponse(path, filename=record.original_name, media_type=record.mime_type)


@app.get("/documents/{document_id}/page/{page_number}/image")
def get_document_page_image(document_id: str, page_number: int) -> Response:
    from fastapi.responses import Response
    record = pipeline.registry.get_document(document_id)
    if not record:
        raise HTTPException(status_code=404, detail="Document not found")
    path = Path(record.stored_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Physical file not found")
    
    if record.mime_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF documents support image preview")
        
    import fitz
    try:
        with fitz.open(path) as doc:
            page_idx = page_number - 1
            if page_idx < 0 or page_idx >= len(doc):
                raise HTTPException(status_code=400, detail=f"Page {page_number} out of range (1-{len(doc)})")
            page = doc[page_idx]
            pix = page.get_pixmap(dpi=150)
            png_bytes = pix.tobytes("png")
            return Response(
                content=png_bytes,
                media_type="image/png"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering page: {str(e)}")




from fastapi.staticfiles import StaticFiles

# Serve compiled React app if dist folder exists
dist_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="static")

