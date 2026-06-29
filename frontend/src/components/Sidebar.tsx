import React, { useRef, useState } from "react";
import { Upload, Trash2 } from "lucide-react";
import { DocumentRecord } from "../types";

interface SidebarProps {
  documents: DocumentRecord[];
  onUpload: (file: File, chunkSize?: number, chunkOverlap?: number) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  selectedDocId: string | null;
  setSelectedDocId: (id: string | null) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  documents,
  onUpload,
  onDelete,
  selectedDocId,
  setSelectedDocId,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const chunkSize = 500;
  const chunkOverlap = 100;

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setIsUploading(true);
      setUploadMessage(null);
      try {
        const file = e.target.files[0];
        await onUpload(file, chunkSize, chunkOverlap);
        setUploadMessage(`Successfully indexed ${file.name}`);
        if (fileInputRef.current) fileInputRef.current.value = "";
      } catch (err: any) {
        setUploadMessage(`Upload failed: ${err.message || err}`);
      } finally {
        setIsUploading(false);
      }
    }
  };



  return (
    <div className="sidebar">
      <div>
        <h2 style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: "1.25rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <ShieldLogo />
          GRC Workspace
        </h2>
        <span style={{ color: "var(--muted)", fontSize: "0.8rem" }}>Policy retrieval and audit desk</span>
      </div>

      <div className="upload-container">
        <div style={{ fontSize: "0.84rem", fontWeight: 600, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Upload & Index
        </div>
        <div 
          className="upload-zone"
          onClick={() => !isUploading && fileInputRef.current?.click()}
        >
          <Upload size={24} className="text-[#78b8ff]" />
          <div className="upload-zone-text">
            {isUploading ? "Uploading..." : "Click to upload policy"}
          </div>
          <div className="upload-zone-formats">PDF, DOCX, or TXT</div>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            accept=".pdf,.docx,.txt" 
            style={{ display: "none" }}
            disabled={isUploading}
          />
        </div>
        {uploadMessage && (
          <div style={{ fontSize: "0.8rem", color: uploadMessage.startsWith("Success") ? "var(--accent-2)" : "var(--error)", marginTop: "0.2rem" }}>
            {uploadMessage}
          </div>
        )}
      </div>



      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        <div style={{ fontSize: "0.84rem", fontWeight: 600, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Filter Context
        </div>
        <select 
          className="select-control"
          value={selectedDocId || ""}
          onChange={(e) => setSelectedDocId(e.target.value ? e.target.value : null)}
        >
          <option value="">All Documents</option>
          {documents.map((doc) => (
            <option key={doc.document_id} value={doc.document_id}>
              {doc.original_name}
            </option>
          ))}
        </select>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.8rem", flexGrow: 1, overflowY: "auto" }}>
        <div style={{ fontSize: "0.84rem", fontWeight: 600, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Indexed Documents ({documents.length})
        </div>
        <div className="doc-list">
          {documents.length === 0 ? (
            <div style={{ color: "var(--muted)", fontSize: "0.88rem", fontStyle: "italic", textAlign: "center", padding: "1rem" }}>
              No policies uploaded yet.
            </div>
          ) : (
            documents.map((doc) => (
              <div
                key={doc.document_id}
                className={`doc-item ${selectedDocId === doc.document_id ? "border-[#78b8ff] bg-[rgba(120,184,255,0.02)]" : ""}`}
                style={{ cursor: "pointer" }}
                onClick={() => setSelectedDocId(selectedDocId === doc.document_id ? null : doc.document_id)}
              >
                <div className="doc-item-header">
                  <div className="doc-item-title" title={doc.original_name}>
                    {doc.original_name}
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                    <span className="doc-item-badge">
                      {doc.status}
                    </span>
                    <button
                      className="doc-delete-btn"
                      title="Delete document"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm(`Are you sure you want to delete "${doc.original_name}"?`)) {
                          onDelete(doc.document_id);
                        }
                      }}
                    >
                      <Trash2 size={13} />
                    </button>
                  </div>
                </div>
                <div className="doc-item-meta" style={{ display: "flex", justifyContent: "space-between", marginTop: "0.2rem" }}>
                  <span>{doc.chunk_count} chunks</span>
                  <span style={{ fontSize: "0.75rem", opacity: 0.8 }}>
                    {new Date(doc.uploaded_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

const ShieldLogo = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-[#78b8ff]">
    <path d="M20 13c0 5-3.5 7.5-7.66 9.7a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 .76-.97l8-2a1 1 0 0 1 .48 0l8 2A1 1 0 0 1 20 6z" />
  </svg>
);
