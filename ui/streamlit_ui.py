from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

import streamlit as st

from backend.config import settings
from rag.pipeline import RAGPipeline


st.set_page_config(page_title=settings.app_name, layout="wide")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Space+Grotesk:wght@500;700&display=swap');

            :root {
                --bg: #07111f;
                --bg-elevated: rgba(10, 18, 34, 0.82);
                --bg-panel: rgba(14, 23, 43, 0.92);
                --bg-soft: rgba(19, 31, 56, 0.72);
                --line: rgba(131, 160, 214, 0.18);
                --line-strong: rgba(131, 160, 214, 0.32);
                --text: #edf3ff;
                --muted: #9fb0cf;
                --accent: #78b8ff;
                --accent-strong: #5f9dff;
                --accent-2: #8cf0d0;
                --warning: #ffd38f;
                --shadow: 0 18px 60px rgba(0, 0, 0, 0.34);
            }

            html, body, [class*="css"] {
                font-family: 'IBM Plex Sans', sans-serif;
                color: var(--text);
            }

            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(120, 184, 255, 0.14), transparent 30%),
                    radial-gradient(circle at 80% 10%, rgba(140, 240, 208, 0.12), transparent 24%),
                    linear-gradient(180deg, #091424 0%, #07111f 45%, #050d18 100%);
            }

            section[data-testid="stSidebar"] {
                background: linear-gradient(180deg, rgba(9, 17, 31, 0.98), rgba(5, 12, 22, 0.98));
                border-right: 1px solid var(--line);
            }

            section[data-testid="stSidebar"] > div {
                padding-top: 1.25rem;
            }

            [data-testid="stHeader"] {
                background: rgba(0, 0, 0, 0);
            }

            .enterprise-shell {
                border: 1px solid var(--line);
                background: linear-gradient(180deg, rgba(12, 21, 40, 0.86), rgba(8, 15, 28, 0.76));
                border-radius: 28px;
                padding: 1.6rem 1.6rem 1.2rem;
                box-shadow: var(--shadow);
                backdrop-filter: blur(16px);
                margin-bottom: 1rem;
            }

            .eyebrow {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.4rem 0.75rem;
                border-radius: 999px;
                border: 1px solid rgba(120, 184, 255, 0.24);
                background: rgba(120, 184, 255, 0.08);
                color: var(--accent);
                font-size: 0.78rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                margin-bottom: 1rem;
            }

            .hero-grid {
                display: grid;
                grid-template-columns: minmax(0, 1.55fr) minmax(300px, 0.85fr);
                gap: 1rem;
                align-items: stretch;
            }

            .hero-title {
                font-family: 'Space Grotesk', sans-serif;
                font-size: clamp(2rem, 4vw, 3.4rem);
                line-height: 1.02;
                letter-spacing: -0.04em;
                margin: 0 0 0.7rem;
            }

            .hero-copy {
                color: var(--muted);
                font-size: 1rem;
                line-height: 1.7;
                max-width: 62ch;
                margin-bottom: 1.1rem;
            }

            .hero-actions {
                display: flex;
                flex-wrap: wrap;
                gap: 0.6rem;
                margin-bottom: 1.1rem;
            }

            .pill {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                padding: 0.5rem 0.8rem;
                border-radius: 999px;
                border: 1px solid var(--line);
                background: rgba(255, 255, 255, 0.03);
                color: var(--text);
                font-size: 0.86rem;
                font-weight: 600;
            }

            .pill strong {
                color: var(--accent);
            }

            .metric-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.8rem;
                margin-top: 1rem;
            }

            .metric-card, .surface-card {
                border: 1px solid var(--line);
                border-radius: 22px;
                background: linear-gradient(180deg, rgba(15, 24, 42, 0.92), rgba(10, 18, 33, 0.92));
                box-shadow: var(--shadow);
            }

            .metric-card {
                padding: 1rem 1.1rem;
            }

            .metric-label {
                color: var(--muted);
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.45rem;
            }

            .metric-value {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.5rem;
                font-weight: 700;
                margin: 0;
            }

            .metric-note {
                color: var(--muted);
                font-size: 0.82rem;
                margin-top: 0.3rem;
            }

            .surface-card {
                padding: 1rem;
                margin-bottom: 1rem;
            }

            .section-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 0.8rem;
                margin-bottom: 0.9rem;
            }

            .section-title {
                margin: 0;
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.05rem;
                letter-spacing: -0.02em;
            }

            .section-subtitle {
                color: var(--muted);
                font-size: 0.88rem;
            }

            .source-list {
                display: grid;
                gap: 0.7rem;
            }

            .source-item {
                border: 1px solid var(--line);
                border-radius: 16px;
                background: rgba(255, 255, 255, 0.03);
                padding: 0.8rem 0.9rem;
            }

            .source-meta {
                display: flex;
                justify-content: space-between;
                gap: 0.75rem;
                font-size: 0.82rem;
                color: var(--muted);
                margin-bottom: 0.45rem;
            }

            .source-body {
                font-size: 0.9rem;
                line-height: 1.55;
                color: var(--text);
            }

            .chat-area {
                border: 1px solid var(--line);
                border-radius: 28px;
                background: linear-gradient(180deg, rgba(13, 22, 39, 0.88), rgba(8, 15, 28, 0.94));
                box-shadow: var(--shadow);
                padding: 1rem 1rem 0.8rem;
            }

            .message-card {
                border: 1px solid var(--line);
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.03);
                padding: 0.95rem 1rem;
                margin-bottom: 0.85rem;
            }

            .message-role {
                font-size: 0.76rem;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: var(--accent-2);
                margin-bottom: 0.5rem;
            }

            .message-user .message-role {
                color: var(--warning);
            }

            .message-content {
                color: var(--text);
                line-height: 1.6;
            }

            .disclaimer {
                color: var(--muted);
                font-size: 0.84rem;
                text-align: center;
                margin-top: 1rem;
            }

            .stChatInput > div {
                border-radius: 18px;
                border: 1px solid var(--line-strong);
                background: rgba(255, 255, 255, 0.04);
            }

            .stButton > button {
                border-radius: 14px;
                border: 1px solid rgba(120, 184, 255, 0.26);
                background: linear-gradient(180deg, rgba(120, 184, 255, 0.2), rgba(95, 157, 255, 0.12));
                color: var(--text);
                font-weight: 700;
                padding: 0.55rem 0.9rem;
            }

            .stButton > button:hover {
                border-color: rgba(140, 240, 208, 0.34);
                color: var(--text);
            }

            .small-label {
                color: var(--muted);
                font-size: 0.8rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin-bottom: 0.3rem;
            }

            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
                font-family: 'Space Grotesk', sans-serif;
                letter-spacing: -0.03em;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_confidence(confidence: float) -> str:
    percentage = max(0.0, min(confidence, 1.0)) * 100
    if percentage >= 80:
        return "High"
    if percentage >= 55:
        return "Moderate"
    return "Low"


@st.cache_resource(show_spinner=False)
def get_pipeline() -> RAGPipeline:
    return RAGPipeline()


def render_metric(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <p class="metric-value">{value}</p>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header(pipeline: RAGPipeline) -> None:
    document_count = len(pipeline.list_documents())
    chunk_count = pipeline.vector_store.count()
    api_status = "Connected" if pipeline.gemini.available else "API key missing"
    st.markdown(
        """
        <div class="enterprise-shell">
            <div class="eyebrow">Governance, Risk, and Compliance intelligence</div>
            <div class="hero-grid">
                <div>
                    <h1 class="hero-title">GRC Compliance Assistant</h1>
                    <p class="hero-copy">
                        A local-first enterprise assistant for policy questions, incident guidance,
                        remote work controls, and compliance lookups. Upload documents, search with
                        grounded retrieval, and review cited answers in one workspace.
                    </p>
                    <div class="hero-actions">
                        <span class="pill"><strong>Local-first</strong> CPU-only embeddings</span>
                        <span class="pill"><strong>Sources</strong> file + page references</span>
                        <span class="pill"><strong>Security</strong> sensitive masking enabled</span>
                    </div>
                </div>
                <div class="surface-card" style="margin: 0;">
                    <div class="section-header">
                        <div>
                            <div class="section-title">Operational status</div>
                            <div class="section-subtitle">Ready for policy retrieval</div>
                        </div>
                    </div>
                    <div class="source-list">
                        <div class="source-item">
                            <div class="source-meta"><span>Gemini API</span><span>{api_status}</span></div>
                            <div class="source-body">Gemini 2.5 Flash generation path</div>
                        </div>
                        <div class="source-item">
                            <div class="source-meta"><span>Vector store</span><span>ChromaDB</span></div>
                            <div class="source-body">Persistent local retrieval index</div>
                        </div>
                        <div class="source-item">
                            <div class="source-meta"><span>Storage</span><span>SQLite</span></div>
                            <div class="source-body">Document registry and metadata</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="metric-grid">
                <div>
                    <div class="metric-card">
                        <div class="metric-label">Indexed documents</div>
                        <p class="metric-value">{document_count}</p>
                        <div class="metric-note">Uploaded policy files available for retrieval</div>
                    </div>
                </div>
                <div>
                    <div class="metric-card">
                        <div class="metric-label">Stored chunks</div>
                        <p class="metric-value">{chunk_count}</p>
                        <div class="metric-note">Chunked with 500 / 100 settings</div>
                    </div>
                </div>
                <div>
                    <div class="metric-card">
                        <div class="metric-label">Response posture</div>
                        <p class="metric-value">Grounded</p>
                        <div class="metric-note">Answer only from retrieved context</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(pipeline: RAGPipeline) -> None:
    st.sidebar.markdown("## GRC Compliance Assistant")
    st.sidebar.caption("Enterprise policy retrieval workspace")

    if not pipeline.gemini.available:
        st.sidebar.warning("GEMINI_API_KEY is not configured. Answers will fall back to a safe placeholder.")

    st.sidebar.markdown("### Workspace")

    uploaded_files = st.sidebar.file_uploader(
        "Upload Documents",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )

    if uploaded_files and st.sidebar.button("Index Uploaded Documents"):
        with st.sidebar.status("Indexing documents...", expanded=True) as status:
            for uploaded_file in uploaded_files:
                suffix = Path(uploaded_file.name).suffix
                with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    temp_path = Path(temp_file.name)
                try:
                    result = pipeline.ingest_file(temp_path, original_name=uploaded_file.name)
                    st.sidebar.success(f"Indexed {uploaded_file.name}")
                    st.sidebar.write(result)
                finally:
                    temp_path.unlink(missing_ok=True)
            status.update(label="Indexing complete", state="complete")

    if st.sidebar.button("Reindex Documents"):
        result = pipeline.reindex_all()
        st.sidebar.success(f"Reindexed {result['reindexed']} documents")

    st.sidebar.divider()
    st.sidebar.markdown("### Indexed Documents")

    documents = pipeline.list_documents()
    if documents:
        document_options = ["All documents"] + [document["original_name"] for document in documents]
        selected = st.sidebar.selectbox("Focus document", document_options, index=0)
        st.session_state.selected_document_name = selected
        for document in documents:
            st.sidebar.markdown(
                f"""
                <div class="surface-card" style="padding: 0.8rem 0.85rem; margin-bottom: 0.65rem;">
                    <div class="small-label">{document['status']}</div>
                    <div style="font-weight: 700; margin-bottom: 0.25rem;">{document['original_name']}</div>
                    <div style="color: var(--muted); font-size: 0.84rem;">{document['chunk_count']} chunks</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.sidebar.info("Upload a policy document to begin.")


def render_chat(pipeline: RAGPipeline) -> None:
    document_name = st.session_state.get("selected_document_name", "All documents")
    document_filter = None
    if document_name and document_name != "All documents":
        for document in pipeline.list_documents():
            if document["original_name"] == document_name:
                document_filter = document["document_id"]
                break

    st.markdown(
        f"""
        <div class="chat-area">
            <div class="section-header">
                <div>
                    <div class="section-title">Policy conversation</div>
                    <div class="section-subtitle">Scoped to {document_name}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        role_class = "message-user" if message["role"] == "user" else "message-assistant"
        with st.container():
            st.markdown(
                f"""
                <div class="message-card {role_class}">
                    <div class="message-role">{message['role']}</div>
                    <div class="message-content">{message['content']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if message.get("sources"):
                with st.expander("Sources", expanded=False):
                    source_rows = []
                    for source in message["sources"]:
                        source_rows.append(
                            f"<div class='source-item'><div class='source-meta'><span>{source['source_file']}</span><span>Page {source['page_number']}</span></div><div class='source-body'>Distance {source['distance']:.3f}</div></div>"
                        )
                    st.markdown("<div class='source-list'>" + "".join(source_rows) + "</div>", unsafe_allow_html=True)

    query = st.chat_input("Ask a compliance question")
    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)
        with st.chat_message("assistant"):
            with st.spinner("Searching policies..."):
                result = pipeline.ask(query=query, document_id=document_filter)
            st.markdown(
                f"""
                <div class="message-card message-assistant">
                    <div class="message-role">assistant</div>
                    <div class="message-content">{result.answer}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(min(max(result.confidence, 0.0), 1.0))
            confidence_label = format_confidence(result.confidence)
            st.caption(f"Confidence: {result.confidence:.2f} ({confidence_label})")
            with st.expander("Sources", expanded=True):
                if result.sources:
                    source_rows = []
                    for source in result.sources:
                        source_rows.append(
                            f"<div class='source-item'><div class='source-meta'><span>{source['source_file']}</span><span>Page {source['page_number']}</span></div><div class='source-body'>Chunk {source['chunk_id']} · distance {source['distance']:.3f}</div></div>"
                        )
                    st.markdown("<div class='source-list'>" + "".join(source_rows) + "</div>", unsafe_allow_html=True)
                else:
                    st.info("No sources available for this response.")
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.answer,
                "sources": result.sources,
            }
        )

    st.markdown(
        """
        <div class="disclaimer">
            Compliance Disclaimer: This assistant provides policy-grounded guidance and does not replace legal, HR, or security review.
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_styles()
    pipeline = get_pipeline()
    render_header(pipeline)
    render_sidebar(pipeline)
    render_chat(pipeline)
