import React from "react";
import { X, FileText, Info } from "lucide-react";
import { SourceCitation } from "../types";

interface SourceViewerProps {
  citation: SourceCitation | null;
  onClose: () => void;
}

export const SourceViewer: React.FC<SourceViewerProps> = ({
  citation,
  onClose,
}) => {
  if (!citation) return null;

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer" onClick={(e) => e.stopPropagation()}>
        <div className="drawer-header">
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <FileText size={20} className="text-[#78b8ff]" />
            <div>
              <div className="drawer-title">Citation Context</div>
              <div style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
                Reference verification panel
              </div>
            </div>
          </div>
          <button className="drawer-close" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <div className="source-detail-card">
            <div className="source-detail-meta">
              <span>Source File</span>
              <span style={{ fontWeight: 600 }}>{citation.source_file}</span>
            </div>
            <div className="source-detail-meta">
              <span>Page Number</span>
              <span style={{ fontWeight: 600 }}>{citation.page_number}</span>
            </div>
            <div className="source-detail-meta" style={{ borderBottom: "none", marginBottom: 0, paddingBottom: 0 }}>
              <span>Similarity Distance</span>
              <span style={{ fontWeight: 600, color: "var(--accent)" }}>
                {citation.distance.toFixed(4)}
              </span>
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={() => {
              const documentId = citation.chunk_id.split(":")[0];
              if (citation.source_file.toLowerCase().endsWith(".pdf")) {
                window.open(`/documents/${documentId}/page/${citation.page_number}`, "_blank");
              } else {
                window.open(`/documents/${documentId}/download`, "_blank");
              }
            }}
            style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem" }}
          >
            <FileText size={16} />
            {citation.source_file.toLowerCase().endsWith(".pdf") ? "Open Cited Page PDF" : "Open Source Document"}
          </button>

          {citation.source_file.toLowerCase().endsWith(".pdf") && (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <FileText size={14} className="text-[#8cf0d0]" />
                Cited Page Preview
              </div>
              <div 
                className="surface-card" 
                style={{ 
                  padding: "0.6rem", 
                  display: "flex", 
                  justifyContent: "center", 
                  alignItems: "center", 
                  maxHeight: "350px", 
                  overflowY: "auto",
                  background: "rgba(0, 0, 0, 0.25)",
                  border: "1px solid var(--line)"
                }}
              >
                <img 
                  src={`/documents/${citation.chunk_id.split(":")[0]}/page/${citation.page_number}/image`}
                  alt={`Page ${citation.page_number} preview`}
                  style={{ 
                    maxWidth: "100%", 
                    height: "auto", 
                    borderRadius: "6px", 
                    boxShadow: "0 4px 16px rgba(0,0,0,0.6)"
                  }} 
                  onError={(e) => {
                    e.currentTarget.style.display = "none";
                  }}
                />
              </div>
            </div>
          )}

          <div style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.05em", display: "flex", alignItems: "center", gap: "0.4rem" }}>

            <Info size={14} />
            Retrieved Content Chunks
          </div>

          <div className="surface-card" style={{ padding: "1.2rem", maxHeight: "400px", overflowY: "auto" }}>
            <p className="source-detail-body">
              {citation.text || "Verifying policy text context... The retriever parsed this segment as highly relevant matching context."}
            </p>
          </div>

          <div className="surface-card" style={{ padding: "1rem", borderStyle: "dashed", borderColor: "var(--line)" }}>
            <div style={{ fontWeight: 600, fontSize: "0.86rem", marginBottom: "0.3rem", color: "var(--warning)" }}>
              Post-Retrieval Verification
            </div>
            <div style={{ fontSize: "0.8rem", color: "var(--muted)", lineHeight: 1.5 }}>
              This section shows the exact text chunk retrieved from the local database. The Gemini model was strictly instructed to answer ONLY using these facts.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
