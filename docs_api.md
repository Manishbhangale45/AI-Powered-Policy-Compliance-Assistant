# GRC Compliance Assistant REST API Documentation

The GRC Compliance Assistant backend is built with FastAPI. It exposes HTTP endpoints for document upload, listing indexed documents, checking API health, and performing Retrieval-Augmented Generation (RAG) queries.

---

## Service Configuration

*   **Default Base URL**: `http://localhost:8000`
*   **CORS Policy**: Enabled for all origins (`*`)
*   **Response Format**: JSON (`application/json`)

---

## Endpoints

### 1. Health Check
Checks the status of the API service.

*   **URL**: `/health`
*   **Method**: `GET`
*   **Headers**: None
*   **Response Payload (`200 OK`)**:
    ```json
    {
      "status": "ok"
    }
    ```
*   **Example Request**:
    ```bash
    curl -X GET http://localhost:8000/health
    ```

---

### 2. List Documents
Retrieves metadata of all policy files currently registered in the database.

*   **URL**: `/documents`
*   **Method**: `GET`
*   **Headers**: None
*   **Response Payload (`200 OK`)**:
    ```json
    [
      {
        "document_id": "c1f8e30bca821034",
        "original_name": "example_password_policy.docx",
        "stored_path": "data/docs/c1f8e30bca821034_example_password_policy.docx",
        "checksum": "a0f28e21a71...55be32",
        "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "chunk_count": 4,
        "status": "indexed",
        "uploaded_at": "2026-06-18T11:08:32.189422Z"
      }
    ]
    ```
*   **Example Request**:
    ```bash
    curl -X GET http://localhost:8000/documents
    ```

---

### 3. Upload and Index Document
Uploads a new GRC document (PDF, DOCX, or TXT) to the server. The file is sanitized, saved locally, parsed into text, split into 500-character chunks with 100-character overlap, embedded using `BAAI/bge-small-en-v1.5` on the CPU, indexed in ChromaDB, and logged into SQLite.

*   **URL**: `/upload`
*   **Method**: `POST`
*   **Request Headers**: `Content-Type: multipart/form-data`
*   **Form Parameters**:
    *   `file`: The document file to upload (supported: `.pdf`, `.docx`, `.txt`)
*   **Response Payload (`200 OK`)**:
    ```json
    {
      "document_id": "c1f8e30bca821034",
      "filename": "example_password_policy.docx",
      "chunk_count": 4,
      "stored_path": "data\\docs\\c1f8e30bca821034_example_password_policy.docx"
    }
    ```
*   **Example Request**:
    ```bash
    curl -X POST http://localhost:8000/upload \
      -F "file=@/path/to/example_password_policy.docx"
    ```

---

### 4. Query Compliance Index (Ask RAG)
Queries the vector database using a text question and generates a response using Gemini 2.5 Flash grounded strictly in the retrieved document chunks.

*   **URL**: `/ask`
*   **Method**: `POST`
*   **Request Headers**: `Content-Type: application/json`
*   **Request Payload**:
    *   `query` (string, required): The compliance question to ask.
    *   `document_id` (string, optional): A unique ID to filter searches to a single document. If null or omitted, searches across all indexed documents.
    ```json
    {
      "query": "What is the password policy?",
      "document_id": null
    }
    ```
*   **Response Payload (`200 OK`)**:
    ```json
    {
      "answer": "According to the Company Password Policy (page 1), employees are required to use passwords that are at least 14 characters long and change them every 90 days. Additionally, accounts with administrative access require multi-factor authentication (MFA).",
      "sources": [
        {
          "source_file": "example_password_policy.docx",
          "page_number": 1,
          "chunk_id": "c1f8e30bca821034:1:0",
          "distance": 0.142
        }
      ],
      "confidence": 0.858,
      "document_id": null
    }
    ```
*   **Example Request**:
    ```bash
    curl -X POST http://localhost:8000/ask \
      -H "Content-Type: application/json" \
      -d '{"query": "What is the password policy?", "document_id": null}'
    ```
