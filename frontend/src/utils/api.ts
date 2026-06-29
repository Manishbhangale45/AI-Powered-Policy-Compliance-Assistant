import { DocumentRecord, SourceCitation } from "../types";

export interface AskResponse {
  answer: string;
  sources: SourceCitation[];
  confidence: number;
  document_id: string | null;
}

export interface UploadResponse {
  document_id: string;
  filename: string;
  chunk_count: number;
  stored_path: string;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch("/health");
    if (!response.ok) return false;
    const data = await response.json();
    return data.status === "ok";
  } catch (error) {
    console.error("Health check failed:", error);
    return false;
  }
}

export async function fetchDocuments(): Promise<DocumentRecord[]> {
  const response = await fetch("/documents");
  if (!response.ok) {
    throw new Error(`Failed to fetch documents: ${response.statusText}`);
  }
  return response.json();
}

export async function uploadDocument(
  file: File,
  chunkSize?: number,
  chunkOverlap?: number
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let url = "/upload";
  const params = new URLSearchParams();
  if (chunkSize !== undefined) params.append("chunk_size", chunkSize.toString());
  if (chunkOverlap !== undefined) params.append("chunk_overlap", chunkOverlap.toString());
  const queryStr = params.toString();
  if (queryStr) {
    url += `?${queryStr}`;
  }

  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }
  return response.json();
}

export async function askQuestion(
  query: string,
  documentId: string | null = null
): Promise<AskResponse> {
  const response = await fetch("/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query,
      document_id: documentId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Query failed: ${response.statusText}`);
  }
  return response.json();
}

export async function triggerReindex(
  chunkSize?: number,
  chunkOverlap?: number
): Promise<{ reindexed: number; documents: number }> {
  let url = "/reindex";
  const params = new URLSearchParams();
  if (chunkSize !== undefined) params.append("chunk_size", chunkSize.toString());
  if (chunkOverlap !== undefined) params.append("chunk_overlap", chunkOverlap.toString());
  const queryStr = params.toString();
  if (queryStr) {
    url += `?${queryStr}`;
  }

  const response = await fetch(url, {
    method: "POST",
  });
  if (!response.ok) {
    throw new Error(`Reindexing failed: ${response.statusText}`);
  }
  return response.json();
}

export async function deleteDocument(documentId: string): Promise<{ status: string; message: string }> {
  const response = await fetch(`/documents/${documentId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`Deletion failed: ${response.statusText}`);
  }
  return response.json();
}

