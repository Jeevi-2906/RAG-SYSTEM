import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

load_dotenv(override=True)

import config
from rag.document_processor import DocumentProcessor
from rag.chunking import IntelligentChunker
from rag.embeddings import EmbeddingManager
from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.generator import AnswerGenerator
from utils.helpers import apply_custom_css, render_html, get_score_badge

st.set_page_config(
    page_title="DocuMind AI — RAG Document Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_css()


@st.cache_resource(show_spinner=False)
def get_embedding_manager():
    return EmbeddingManager(model_name=config.EMBEDDING_MODEL_NAME)


@st.cache_resource(show_spinner=False)
def get_vector_store():
    return VectorStore(persist_directory=config.CHROMA_PERSIST_DIR)


@st.cache_resource(show_spinner=False)
def get_generator(api_key: str):
    return AnswerGenerator(api_key=api_key)


embed_manager = get_embedding_manager()
vector_store = get_vector_store()
chunker = IntelligentChunker(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
retriever = Retriever(vector_store=vector_store, embedding_manager=embed_manager)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_retrieved_chunks" not in st.session_state:
    st.session_state.last_retrieved_chunks = []
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = (
        os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or config.GEMINI_API_KEY or ""
    )

active_api_key = st.session_state.gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
generator = get_generator(active_api_key)

stats = vector_store.get_collection_stats()

with st.sidebar:
    render_html("""
    <div class="sidebar-brand">
        <div class="sidebar-logo-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C4.89543 2 4 2.89543 4 4V20C4 21.1046 4.89543 22 6 22H18C19.1046 22 20 21.1046 20 20V8L14 2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M14 2V8H20" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 13H15" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 17H13" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="16.5" cy="16.5" r="3.5" stroke="#93c5fd" stroke-width="2"/>
                <path d="M19 19L21.5 21.5" stroke="#93c5fd" stroke-width="2" stroke-linecap="round"/>
            </svg>
        </div>
        <h1 class="sidebar-title">DocuMind <span>AI</span></h1>
        <p class="sidebar-subtitle">RAG-Powered Document Assistant</p>
    </div>
    """)

    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        st.session_state.chat_history = []
        st.session_state.last_retrieved_chunks = []
        st.session_state.last_query = ""
        st.rerun()

    st.markdown("---")

    render_html('<p class="sidebar-section-title">📁 Uploaded Documents History</p>')

    if stats["documents"]:
        for doc_item in stats["documents"]:
            doc_name = doc_item["filename"]
            render_html(f"""
            <div class="doc-item-row">
                <div class="doc-item-left">
                    <span class="pdf-badge">PDF</span>
                    <span class="doc-item-name" title="{doc_name}">{doc_name}</span>
                </div>
                <div class="check-circle">✓</div>
            </div>
            """)
    else:
        render_html("""
        <div style="background: rgba(255,255,255,0.03); border: 1px dashed rgba(255,255,255,0.15); border-radius: 8px; padding: 12px; text-align: center; font-size: 0.78rem; color: #94a3b8;">
            No documents in collection.<br>Upload PDFs on the right panel near the chat.
        </div>
        """)

    render_html("<div style='height: 12px;'></div>")

    render_html(f"""
    <div class="sidebar-stat-row">
        <div class="sidebar-stat-label">📄 Total Pages</div>
        <div class="sidebar-stat-val">{stats['total_pages']}</div>
    </div>
    <div class="sidebar-stat-row">
        <div class="sidebar-stat-label">🗂️ Total Chunks</div>
        <div class="sidebar-stat-val">{stats['total_chunks']}</div>
    </div>
    """)

    render_html("<div style='height: 14px;'></div>")

    if st.button("🗑️ Clear All", use_container_width=True):
        vector_store.clear_collection()
        st.session_state.chat_history = []
        st.session_state.last_retrieved_chunks = []
        st.session_state.last_query = ""
        st.rerun()

    render_html("<div style='height: 10px;'></div>")
    with st.expander("⚙️ Key Settings", expanded=False):
        api_input = st.text_input(
            "Gemini API Key",
            value=st.session_state.gemini_api_key,
            type="password",
            placeholder="AIzaSy...",
            help="Configured locally in .env"
        )
        if st.button("Save Key", key="save_api_key_btn", use_container_width=True):
            if api_input.strip():
                st.session_state.gemini_api_key = api_input.strip()
                env_path = config.BASE_DIR / ".env"
                with open(env_path, "w", encoding="utf-8") as f:
                    f.write(f"GEMINI_API_KEY={api_input.strip()}\n")
                st.success("API Key Saved!")
                st.rerun()

is_ready = stats["total_chunks"] > 0
ready_text = "Ready" if is_ready else "Add Documents"
dot_color = "#22C55E" if is_ready else "#F59E0B"

render_html(f"""
<div class="welcome-header">
    <div class="welcome-left">
        <span class="sparkle-icon">✨</span>
        <div>
            <h1 class="welcome-title">Welcome to DocuMind AI!</h1>
            <p class="welcome-subtitle">Ask questions from your documents and get accurate answers.</p>
        </div>
    </div>
    <div>
        <div class="ready-badge">
            <span class="ready-dot" style="background-color: {dot_color};"></span> {ready_text}
        </div>
    </div>
</div>
""")

if not active_api_key:
    st.warning("⚠️ **Gemini API Key required:** Please enter your Google Gemini API Key in the left sidebar under 'Key Settings' or save it in `.env`.")

tab_chat, tab_context, tab_compare = st.tabs([
    "💬 Document Chat",
    "📄 Retrieved Context",
    "⚖️ RAG vs LLM"
])

with tab_chat:
    col_chat, col_side = st.columns([2.5, 1.15], gap="large")

    with col_side:
        render_html("""
        <div style="margin-bottom: 8px;">
            <p style="font-size: 1.05rem; font-weight: 800; color: #000000; margin: 0 0 2px 0;">Upload Documents</p>
            <p style="font-size: 0.82rem; color: #334155; margin: 0;">Drag and drop PDF files here or click to browse.</p>
        </div>
        """)

        uploaded_files = st.file_uploader(
            "Upload Documents",
            type=["pdf"],
            accept_multiple_files=True,
            help="Limit 200MB per file • Multiple PDF support",
            key="chat_uploader_widget",
            label_visibility="collapsed"
        )

        if uploaded_files:
            if st.button("🚀 Process & Index Documents", use_container_width=True, type="primary"):
                with st.spinner("Processing, chunking & indexing PDF documents..."):
                    processed_docs = 0
                    new_chunks = 0
                    errors = []

                    for up_file in uploaded_files:
                        extract_res = DocumentProcessor.extract_text_from_pdf(up_file, filename=up_file.name)
                        if not extract_res["success"]:
                            errors.append(extract_res["error"])
                            continue

                        doc_chunks = chunker.chunk_document(extract_res)
                        if not doc_chunks:
                            errors.append(f"No extractable text in '{up_file.name}'.")
                            continue

                        chunk_texts = [c["text"] for c in doc_chunks]
                        chunk_embeddings = embed_manager.embed_texts(chunk_texts)
                        vector_store.add_chunks(doc_chunks, chunk_embeddings)
                        processed_docs += 1
                        new_chunks += len(doc_chunks)

                    if processed_docs > 0:
                        st.success(f"✓ Indexed {processed_docs} file(s) ({new_chunks} chunks)!")
                        st.rerun()
                    for err in errors:
                        st.error(f"❌ {err}")

        render_html("""
        <div class="card-quick-features">
            <div class="card-quick-features-title">
                <span>⚡</span> Quick Features
            </div>
            <div class="feature-item">
                <span class="feature-check">✓</span> Upload Multiple PDFs
            </div>
            <div class="feature-item">
                <span class="feature-check">✓</span> Chat with Documents
            </div>
            <div class="feature-item">
                <span class="feature-check">✓</span> View Retrieved Chunks
            </div>
            <div class="feature-item">
                <span class="feature-check">✓</span> Compare RAG vs LLM
            </div>
        </div>
        """)

        render_html("""
        <div class="card-how-rag">
            <div class="card-how-rag-title">
                <span>💡</span> How RAG Works?
            </div>
            <p class="card-how-rag-body">
                It retrieves relevant information from your documents and uses it to generate accurate, verified answers.
            </p>
        </div>
        """)

    with col_chat:
        if not st.session_state.chat_history:
            render_html("""
            <div class="empty-hero-card">
                <div class="empty-hero-icon">🤖</div>
                <div class="empty-hero-title">Ready to Answer from Your Documents</div>
                <div class="empty-hero-desc">
                    Ask questions grounded strictly in your uploaded PDFs. No hallucinations, full citations.
                </div>
            </div>
            """)

            st.markdown("<p style='font-size:0.86rem; font-weight:700; color:#000000; margin-bottom:0.4rem;'>💡 Try an example question:</p>", unsafe_allow_html=True)
            sp1, sp2 = st.columns(2)
            prompt_to_run = None
            with sp1:
                if st.button("📌 What are the main topics in the document?", use_container_width=True):
                    prompt_to_run = "What are the main topics and key concepts in the uploaded document?"
            with sp2:
                if st.button("📌 Summarize the core concepts", use_container_width=True):
                    prompt_to_run = "Please provide a concise summary of the core concepts in the uploaded document."

            if prompt_to_run:
                st.session_state.chat_history.append({"role": "user", "content": prompt_to_run})
                st.session_state.last_query = prompt_to_run
                with st.spinner("Searching document context & generating grounded answer..."):
                    retrieved_chunks = retriever.retrieve(prompt_to_run, top_k=config.DEFAULT_TOP_K)
                    st.session_state.last_retrieved_chunks = retrieved_chunks
                    rag_res = generator.generate_rag_answer(
                        question=prompt_to_run,
                        retrieved_chunks=retrieved_chunks
                    )
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": rag_res["answer"],
                        "sources": rag_res.get("sources", [])
                    })
                st.rerun()

        else:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else None):
                    st.markdown(msg["content"])
                    if msg.get("sources"):
                        source_pills = "".join([f'<span class="source-tag">📄 {s}</span> ' for s in msg["sources"]])
                        render_html(f'<div class="source-pill-footer">{source_pills}</div>')

        user_input = st.chat_input("Ask a question about your documents...")
        if user_input:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.last_query = user_input
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant", avatar="🤖"):
                if stats["total_chunks"] == 0:
                    reply = "⚠️ No documents indexed yet. Please upload a PDF using the upload card on the right and click **Process & Index Documents**."
                    st.warning(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply, "sources": []})
                elif not active_api_key:
                    reply = "⚠️ Google Gemini API key is missing. Please enter your API key in the sidebar under 'Key Settings'."
                    st.error(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply, "sources": []})
                else:
                    with st.spinner("Searching document context & generating grounded answer..."):
                        retrieved_chunks = retriever.retrieve(user_input, top_k=config.DEFAULT_TOP_K)
                        st.session_state.last_retrieved_chunks = retrieved_chunks

                        rag_res = generator.generate_rag_answer(
                            question=user_input,
                            retrieved_chunks=retrieved_chunks
                        )

                        st.markdown(rag_res["answer"])
                        if rag_res.get("sources"):
                            source_pills = "".join([f'<span class="source-tag">📄 {s}</span> ' for s in rag_res["sources"]])
                            render_html(f'<div class="source-pill-footer">{source_pills}</div>')

                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": rag_res["answer"],
                            "sources": rag_res.get("sources", [])
                        })

with tab_context:
    st.markdown("### 🔍 Retrieved Semantic Chunks")
    st.markdown("<p style='color:#334155; font-size:0.9rem;'>Inspect the exact passages retrieved from ChromaDB that are passed into Gemini.</p>", unsafe_allow_html=True)

    query = st.session_state.get("last_query", "")
    chunks = st.session_state.get("last_retrieved_chunks", [])

    if query:
        st.markdown(f"**Latest Question:** *\"{query}\"*")

    if not chunks:
        st.info("No retrieved chunks yet. Ask a question in the Document Chat tab to view semantic search results.")
    else:
        st.markdown(f"**Top {len(chunks)} Relevant Chunks Retrieved:**")
        for idx, chunk in enumerate(chunks, 1):
            source = chunk.get("source", "Document.pdf")
            page = chunk.get("page", 1)
            score = chunk.get("similarity_score", 0.0)
            chunk_id = chunk.get("chunk_id", f"c_{idx}")
            text = chunk.get("text", "")
            badge = get_score_badge(score)

            render_html(f"""
            <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-left:4px solid #3B82F6; border-radius:12px; padding:16px; margin-bottom:14px; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; border-bottom:1px solid #F1F5F9; padding-bottom:6px;">
                    <div>
                        <span style="background:#EFF6FF; color:#2563EB; font-weight:700; padding:3px 8px; border-radius:6px; font-size:0.75rem;">📄 {source}</span>
                        <span style="background:#F1F5F9; color:#475569; font-weight:600; padding:3px 8px; border-radius:6px; font-size:0.75rem; margin-left:6px;">Page {page}</span>
                        <span style="font-size:0.75rem; color:#94A3B8; margin-left:8px;">ID: {chunk_id}</span>
                    </div>
                    <div>
                        {badge}
                    </div>
                </div>
                <div style="font-size:0.9rem; color:#000000; line-height:1.6; white-space:pre-wrap; background:#F8FAFC; padding:12px; border-radius:8px;">{text}</div>
            </div>
            """)

with tab_compare:
    st.markdown("### ⚖️ Side-by-Side Comparison: Normal LLM vs. DocuMind RAG")
    st.markdown("<p style='color:#334155; font-size:0.9rem;'>Demonstrate the power of retrieval: see how a standard LLM answers without your files vs. RAG grounded in your documents.</p>", unsafe_allow_html=True)

    preset = st.selectbox(
        "Select an Example Question or enter your own:",
        options=[
            "— Custom Question —",
            "What are the main topics and key concepts covered in this document?",
            "Can you provide a summary of the uploaded document?",
            "What are the specific technical architectures, protocols, or models described?",
            "What is the recipe for baking a traditional chocolate cake?"
        ]
    )

    comp_val = preset if preset != "— Custom Question —" else ""
    compare_query = st.text_input("Question for Comparison:", value=comp_val)

    if st.button("⚡ Run Side-by-Side Comparison", type="primary") and compare_query:
        if not active_api_key:
            st.error("Please enter a Google Gemini API Key.")
        elif stats["total_chunks"] == 0:
            st.warning("Please upload a PDF first.")
        else:
            with st.spinner("Executing comparative evaluation..."):
                normal_res = generator.generate_normal_answer(compare_query)
                retrieved_chunks = retriever.retrieve(compare_query, top_k=config.DEFAULT_TOP_K)
                rag_res = generator.generate_rag_answer(compare_query, retrieved_chunks)

                c1, c2 = st.columns(2)
                with c1:
                    render_html("""
                    <div style="background:#FFFFFF; border:1px solid #CBD5E1; border-radius:12px; padding:16px; margin-bottom:12px; box-shadow:0 1px 4px rgba(0,0,0,0.03);">
                        <h4 style="color:#64748B; margin:0 0 6px 0; font-size:1.05rem;">🌐 Standard Gemini (No Retrieval)</h4>
                        <p style="font-size:0.8rem; color:#94A3B8; margin:0;">Answers purely from pre-training data. Has no access to your uploaded files.</p>
                    </div>
                    """)
                    st.markdown(normal_res["answer"])

                with c2:
                    render_html("""
                    <div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:12px; padding:16px; margin-bottom:12px; box-shadow:0 2px 8px rgba(37,99,235,0.08);">
                        <h4 style="color:#1D4ED8; margin:0 0 6px 0; font-size:1.05rem;">🛡️ DocuMind RAG (ChromaDB + Gemini)</h4>
                        <p style="font-size:0.8rem; color:#60A5FA; margin:0;">Grounds the answer strictly in verified retrieved chunks with citations.</p>
                    </div>
                    """)
                    st.markdown(rag_res["answer"])
                    if rag_res.get("sources"):
                        st.markdown("<p style='font-weight:700; color:#000000; margin-top:12px;'>Verified Citations:</p>", unsafe_allow_html=True)
                        pill_html = "".join([f'<span class="source-tag">📄 {s}</span> ' for s in rag_res["sources"]])
                        render_html(f'<div class="source-pill-footer">{pill_html}</div>')
