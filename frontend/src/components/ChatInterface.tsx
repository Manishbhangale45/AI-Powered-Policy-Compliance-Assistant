import React, { useState, useRef, useEffect } from "react";
import { Send, FileSearch, HelpCircle } from "lucide-react";
import { ChatMessage, SourceCitation } from "../types";

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => Promise<void>;
  isGenerating: boolean;
  onCitationClick: (citation: SourceCitation) => void;
  documentName: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isGenerating,
  onCitationClick,
  documentName,
}) => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const suggestionQueries = [
    "What is the password policy?",
    "When should incidents be reported?",
    "Can customer data be shared externally?",
    "What controls apply to remote work?",
    "What is the escalation process?",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isGenerating]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isGenerating) {
      onSendMessage(input.trim());
      setInput("");
    }
  };

  const formatConfidence = (confidence: number): { label: string; color: string } => {
    const percentage = confidence * 100;
    if (percentage >= 80) return { label: "High Confidence", color: "var(--accent-2)" };
    if (percentage >= 55) return { label: "Moderate Confidence", color: "var(--warning)" };
    return { label: "Low Confidence", color: "var(--error)" };
  };

  const renderMessageContent = (text: string) => {
    // Strip all occurrences of " | Chunk: X", ", Chunk: X", or similar chunk indicators
    let cleanText = text.replace(/\s*\|\s*Chunk:\s*\d+/gi, "");
    cleanText = cleanText.replace(/,\s*Chunk:\s*\d+/gi, "");
    cleanText = cleanText.replace(/\s*\(Chunk:\s*\d+\)/gi, "");
    cleanText = cleanText.replace(/\s*\(Chunk\s*\d+\)/gi, "");

    // Ensure newlines exist before bullet points that might be collapsed on a single line
    let normalized = cleanText.replace(/(?<!\n)\s*\*\s+/g, "\n* ");
    
    // Clean up any double empty lines
    normalized = normalized.replace(/\n\s*\n/g, "\n");
    
    const lines = normalized.split("\n");
    return lines.map((line, lineIdx) => {
      const trimmed = line.trim();
      if (!trimmed) return null;
      
      const isBullet = trimmed.startsWith("*");
      let displayLine = line;
      if (isBullet) {
        displayLine = trimmed.replace(/^\*\s*/, "");
      }
      
      // Parse markdown bold **text**
      const parts = displayLine.split("**");
      const elements = parts.map((part, idx) => {
        if (idx % 2 === 1) {
          return <strong key={idx} style={{ color: "var(--text)", fontWeight: 600 }}>{part}</strong>;
        }
        return part;
      });
      
      if (isBullet) {
        return (
          <div 
            key={lineIdx} 
            style={{ 
              display: "flex", 
              gap: "0.5rem", 
              marginLeft: "0.8rem", 
              marginTop: "0.4rem", 
              lineHeight: "1.6",
              color: "var(--text)"
            }}
          >
            <span style={{ color: "var(--accent)", fontWeight: "bold" }}>•</span>
            <div style={{ flex: 1 }}>{elements}</div>
          </div>
        );
      }
      
      return (
        <div 
          key={lineIdx} 
          style={{ 
            marginTop: lineIdx > 0 ? "0.6rem" : 0, 
            lineHeight: "1.6",
            color: "var(--text)" 
          }}
        >
          {elements}
        </div>
      );
    });
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <FileSearch size={18} className="text-[#78b8ff]" />
          <div>
            <div style={{ fontWeight: 600, fontSize: "0.95rem" }}>Policy Conversation</div>
            <div style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
              Context Focus: <span style={{ color: "var(--accent)", fontWeight: 500 }}>{documentName}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div style={{ display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", height: "100%", textAlign: "center", gap: "1rem", padding: "1.5rem" }}>
            <HelpCircle size={40} style={{ color: "var(--muted)", opacity: 0.5 }} />
            <div>
              <h3 style={{ fontFamily: "var(--font-display)", fontSize: "1.1rem", marginBottom: "0.3rem" }}>Ask a Compliance Question</h3>
              <p style={{ color: "var(--muted)", fontSize: "0.9rem", maxWidth: "450px" }}>
                Query company policies securely. Responses are strictly grounded inside the uploaded compliance files and citation sources will be generated.
              </p>
            </div>
            <div className="suggestion-grid">
              {suggestionQueries.map((query, idx) => (
                <div 
                  key={idx} 
                  className="suggestion-pill"
                  onClick={() => !isGenerating && onSendMessage(query)}
                >
                  {query}
                </div>
              ))}
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div 
              key={message.id} 
              className={`message-bubble ${message.role === "user" ? "message-user" : "message-assistant"}`}
            >
              <div className="message-role">
                {message.role}
              </div>
              <div className="message-content">
                {renderMessageContent(message.content)}
              </div>
              {message.role === "assistant" && message.confidence !== undefined && (
                <div className="message-confidence">
                  <div className="confidence-bar-bg">
                    <div 
                      className="confidence-bar-fill"
                      style={{ 
                        width: `${Math.min(Math.max(message.confidence, 0), 1) * 100}%`,
                        backgroundColor: formatConfidence(message.confidence).color 
                      }}
                    />
                  </div>
                  <span style={{ color: formatConfidence(message.confidence).color, fontWeight: 500 }}>
                    {message.confidence.toFixed(2)} ({formatConfidence(message.confidence).label})
                  </span>
                </div>
              )}
              {message.role === "assistant" && message.sources && message.sources.length > 0 && (
                <div className="citation-container">
                  {message.sources.map((source, idx) => (
                    <div 
                      key={idx} 
                      className="citation-chip"
                      onClick={() => onCitationClick(source)}
                    >
                      <FileTextIcon />
                      <span>{source.source_file} (Page {source.page_number})</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
        {isGenerating && (
          <div className="message-bubble message-assistant" style={{ opacity: 0.7 }}>
            <div className="message-role">assistant</div>
            <div className="message-content" style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span className="animate-pulse">Searching vector databases & analyzing policies...</span>
            </div>
          </div>
        )}
        <div ref={scrollToBottom} />
      </div>

      <form className="chat-input-area" onSubmit={handleSubmit}>
        <div className="input-wrapper">
          <input 
            type="text" 
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a compliance or policy question..."
            disabled={isGenerating}
          />
          <button 
            type="submit" 
            className="send-btn"
            disabled={!input.trim() || isGenerating}
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </div>
  );
};

const FileTextIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="mr-0.5">
    <path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z" />
    <path d="M14 2v4a2 2 0 0 0 2 2h4" />
    <path d="M10 9H8" />
    <path d="M16 13H8" />
    <path d="M16 17H8" />
  </svg>
);
