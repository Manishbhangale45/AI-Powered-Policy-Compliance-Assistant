import React, { useEffect, useState } from "react";
import { Sidebar } from "./components/Sidebar";
import { ChatInterface } from "./components/ChatInterface";
import { SourceViewer } from "./components/SourceViewer";
import { DocumentRecord, ChatMessage, SourceCitation } from "./types";
import * as api from "./utils/api";

export const App: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeCitation, setActiveCitation] = useState<SourceCitation | null>(null);

  const loadStatusAndRegistry = async () => {
    try {
      const docs = await api.fetchDocuments();
      setDocuments(docs);
    } catch (err) {
      console.error("Failed to load backend documents:", err);
    }
  };

  useEffect(() => {
    loadStatusAndRegistry();
    // Poll status every 10 seconds
    const interval = setInterval(loadStatusAndRegistry, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleUpload = async (file: File, chunkSize?: number, chunkOverlap?: number) => {
    await api.uploadDocument(file, chunkSize, chunkOverlap);
    await loadStatusAndRegistry();
  };


  const handleDeleteDocument = async (documentId: string) => {
    try {
      await api.deleteDocument(documentId);
      if (selectedDocId === documentId) {
        setSelectedDocId(null);
      }
      await loadStatusAndRegistry();
    } catch (err: any) {
      console.error("Failed to delete document:", err);
      alert(`Failed to delete document: ${err.message || err}`);
    }
  };


  const handleSendMessage = async (text: string) => {
    const userMsgId = Date.now().toString();
    const userMsg: ChatMessage = {
      id: userMsgId,
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsGenerating(true);

    try {
      const response = await api.askQuestion(text, selectedDocId);
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        confidence: response.confidence,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: `Sorry, I encountered an error while querying the backend: ${error.message || error}`,
        sources: [],
        confidence: 0,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsGenerating(false);
    }
  };

  const getFocusedDocumentName = () => {
    if (!selectedDocId) return "All Documents";
    const doc = documents.find((d) => d.document_id === selectedDocId);
    return doc ? doc.original_name : "Focused Selection";
  };

  return (
    <div className="app-container">
      <Sidebar
        documents={documents}
        onUpload={handleUpload}
        onDelete={handleDeleteDocument}
        selectedDocId={selectedDocId}
        setSelectedDocId={setSelectedDocId}
      />

      <div className="main-content">

        <ChatInterface
          messages={messages}
          onSendMessage={handleSendMessage}
          isGenerating={isGenerating}
          onCitationClick={setActiveCitation}
          documentName={getFocusedDocumentName()}
        />

        <div className="disclaimer">
          Compliance Disclaimer: This assistant provides policy-grounded guidance and does not replace official legal, HR, or security consultations.
        </div>
      </div>

      <SourceViewer
        citation={activeCitation}
        onClose={() => setActiveCitation(null)}
      />
    </div>
  );
};
