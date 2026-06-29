export interface DocumentRecord {
  document_id: string;
  original_name: string;
  stored_path: string;
  checksum: string;
  mime_type: string;
  chunk_count: number;
  status: string;
  uploaded_at: string;
}

export interface SourceCitation {
  source_file: string;
  page_number: number;
  chunk_id: string;
  distance: number;
  text?: string; // Optional detailed context text associated
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
  confidence?: number;
}

export interface SystemStatus {
  apiConnected: boolean;
  documentCount: number;
  chunkCount: number;
}
