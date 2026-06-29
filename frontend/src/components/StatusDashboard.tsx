import React from "react";
import { Shield, Database, Cpu, Activity } from "lucide-react";

interface StatusDashboardProps {
  apiConnected: boolean;
  documentCount: number;
  chunkCount: number;
}

export const StatusDashboard: React.FC<StatusDashboardProps> = ({
  apiConnected,
  documentCount,
  chunkCount,
}) => {
  return (
    <div className="enterprise-shell">
      <div className="eyebrow">
        <Shield size={12} className="inline mr-1" />
        Governance, Risk, and Compliance Intelligence
      </div>
      <div className="hero-grid">
        <div>
          <h1 className="hero-title">GRC Compliance Assistant</h1>
          <p className="hero-copy">
            A local-first enterprise assistant for policy questions, incident guidance,
            remote work controls, and compliance lookups. Upload documents, search with
            grounded retrieval, and review cited answers in one workspace.
          </p>
          <div className="hero-actions">
            <span className="pill">
              <Cpu size={14} className="text-[#78b8ff]" />
              <strong>Local-first</strong> CPU-only embeddings
            </span>
            <span className="pill">
              <Database size={14} className="text-[#78b8ff]" />
              <strong>Sources</strong> file + page references
            </span>
            <span className="pill">
              <Shield size={14} className="text-[#78b8ff]" />
              <strong>Security</strong> sensitive masking enabled
            </span>
          </div>
        </div>

        <div className="surface-card" style={{ margin: 0 }}>
          <div className="section-header">
            <div>
              <div className="section-title">Operational Status</div>
              <div className="section-subtitle">Ready for policy retrieval</div>
            </div>
            <Activity size={16} className="text-[#8cf0d0]" />
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.7rem" }}>
            <div className="surface-card" style={{ padding: "0.8rem", background: "rgba(255, 255, 255, 0.01)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "var(--muted)" }}>
                <span>Gemini API</span>
                <span className="status-badge">
                  <span className={`status-dot ${apiConnected ? "status-dot-ok" : "status-dot-warn"}`} />
                  {apiConnected ? "Connected" : "API Key Missing"}
                </span>
              </div>
              <div style={{ fontSize: "0.88rem", marginTop: "0.2rem" }}>Gemini 2.5 Flash Generation Path</div>
            </div>
            <div className="surface-card" style={{ padding: "0.8rem", background: "rgba(255, 255, 255, 0.01)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "var(--muted)" }}>
                <span>Vector Store</span>
                <span style={{ fontWeight: 600 }}>ChromaDB</span>
              </div>
              <div style={{ fontSize: "0.88rem", marginTop: "0.2rem" }}>Persistent Local Retrieval Index</div>
            </div>
            <div className="surface-card" style={{ padding: "0.8rem", background: "rgba(255, 255, 255, 0.01)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", color: "var(--muted)" }}>
                <span>Storage</span>
                <span style={{ fontWeight: 600 }}>SQLite</span>
              </div>
              <div style={{ fontSize: "0.88rem", marginTop: "0.2rem" }}>Document Registry and Metadata</div>
            </div>
          </div>
        </div>
      </div>

      <div className="metric-grid">
        <div className="metric-card">
          <div className="metric-label">Indexed Documents</div>
          <p className="metric-value">{documentCount}</p>
          <div className="metric-note">Uploaded policy files available for retrieval</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Stored Chunks</div>
          <p className="metric-value">{chunkCount}</p>
          <div className="metric-note">Chunked with 500 / 100 settings</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Response Posture</div>
          <p className="metric-value" style={{ color: "var(--accent-2)" }}>Grounded</p>
          <div className="metric-note">Answers generated strictly from retrieved context</div>
        </div>
      </div>
    </div>
  );
};
