import re
import streamlit as st


def get_custom_css() -> str:
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"], .stApp {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #F8FAFC !important;
            color: #000000 !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 2.8rem !important;
            z-index: 10 !important;
        }

        .block-container {
            padding-top: 3.2rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            max-width: 1400px !important;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #000000 !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 700 !important;
            letter-spacing: -0.015em !important;
        }

        .stMarkdown,
        .stMarkdown p,
        .stMarkdown span,
        .stMarkdown div,
        .stMarkdown li,
        .stMarkdown ul,
        .stMarkdown ol,
        .stMarkdown strong,
        .stMarkdown b,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] div,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] ul,
        [data-testid="stMarkdownContainer"] ol,
        [data-testid="stMarkdownContainer"] strong,
        [data-testid="stMarkdownContainer"] b {
            color: #000000 !important;
            line-height: 1.65 !important;
        }

        [data-testid="stWidgetLabel"] p,
        [data-testid="stWidgetLabel"] label,
        [data-testid="stWidgetLabel"] span {
            color: #000000 !important;
            font-weight: 700 !important;
            font-size: 0.9rem !important;
        }

        .welcome-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.4rem;
            padding: 0.2rem 0 0.8rem 0;
            border-bottom: 1px solid #E2E8F0;
        }

        .welcome-left {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .sparkle-icon {
            font-size: 2.2rem;
            line-height: 1;
            filter: drop-shadow(0 2px 4px rgba(59, 130, 246, 0.25));
        }

        .welcome-title {
            font-size: 1.85rem !important;
            font-weight: 800 !important;
            color: #000000 !important;
            margin: 0 !important;
            line-height: 1.2 !important;
            letter-spacing: -0.02em !important;
        }

        .welcome-subtitle {
            font-size: 0.95rem !important;
            color: #334155 !important;
            margin: 4px 0 0 0 !important;
            font-weight: 500 !important;
            line-height: 1.4 !important;
        }

        .ready-badge {
            background: #DCFCE7 !important;
            color: #15803D !important;
            border: 1px solid #BBF7D0 !important;
            padding: 6px 16px;
            border-radius: 9999px;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            box-shadow: 0 1px 3px rgba(21, 128, 61, 0.1);
        }

        .ready-dot {
            width: 8px;
            height: 8px;
            background-color: #22C55E;
            border-radius: 50%;
            display: inline-block;
        }

        [data-testid="stSidebar"] {
            background-color: #111827 !important;
            border-right: 1px solid #1F2937 !important;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.1) !important;
            margin: 1rem 0 !important;
        }

        .sidebar-brand {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            padding: 0.5rem 0 1.2rem 0;
        }

        .sidebar-logo-icon {
            width: 52px;
            height: 52px;
            background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 20px rgba(59, 130, 246, 0.35);
            margin-bottom: 10px;
        }

        .sidebar-title {
            font-size: 1.45rem !important;
            font-weight: 800 !important;
            color: #FFFFFF !important;
            letter-spacing: -0.02em;
            margin: 0 !important;
        }

        .sidebar-title span {
            color: #818CF8 !important;
        }

        .sidebar-subtitle {
            font-size: 0.76rem !important;
            color: #94A3B8 !important;
            margin-top: 3px !important;
            font-weight: 500 !important;
        }

        .sidebar-section-title {
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            color: #94A3B8 !important;
            margin-bottom: 0.6rem !important;
            text-transform: none !important;
        }

        .doc-item-row {
            background: rgba(30, 41, 59, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 9px 12px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .doc-item-left {
            display: flex;
            align-items: center;
            gap: 10px;
            overflow: hidden;
        }

        .pdf-badge {
            background: #EF4444;
            color: #FFFFFF !important;
            font-size: 0.65rem !important;
            font-weight: 800 !important;
            padding: 2px 6px;
            border-radius: 4px;
            letter-spacing: 0.05em;
        }

        .doc-item-name {
            font-size: 0.84rem !important;
            font-weight: 600 !important;
            color: #F8FAFC !important;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 140px;
        }

        .check-circle {
            background: #10B981;
            color: #FFFFFF !important;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: 700;
        }

        .sidebar-stat-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 7px 4px;
            font-size: 0.86rem !important;
        }

        .sidebar-stat-label {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #CBD5E1 !important;
        }

        .sidebar-stat-val {
            font-weight: 700 !important;
            color: #FFFFFF !important;
        }

        [data-testid="stSidebar"] .stButton button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] {
            background: #1E293B !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] summary span {
            color: #E2E8F0 !important;
            font-weight: 600 !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] input {
            background-color: #0F172A !important;
            color: #FFFFFF !important;
            border: 1px solid #475569 !important;
            border-radius: 8px !important;
        }

        [data-testid="stSidebar"] [data-testid="stExpander"] input::placeholder {
            color: #94A3B8 !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px !important;
            background: #FFFFFF !important;
            border-radius: 12px !important;
            padding: 6px 8px !important;
            border: 1px solid #E2E8F0 !important;
            width: fit-content !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
            margin-bottom: 1.4rem !important;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px !important;
            padding: 8px 20px !important;
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            color: #334155 !important;
            background: transparent !important;
            border: 1px solid transparent !important;
            transition: all 0.2s ease !important;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #1D4ED8 !important;
            background: #F1F5F9 !important;
        }

        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #2563EB !important;
            background: #EFF6FF !important;
            border-color: #BFDBFE !important;
            font-weight: 700 !important;
            box-shadow: 0 1px 3px rgba(37, 99, 235, 0.08) !important;
        }

        .stTabs [data-baseweb="tab-border"] {
            display: none !important;
        }

        [data-testid="stFileUploader"] {
            margin-bottom: 1rem !important;
        }

        [data-testid="stFileUploaderDropzone"] {
            background: linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%) !important;
            border: 2px dashed rgba(255, 255, 255, 0.45) !important;
            border-radius: 16px !important;
            padding: 1.8rem 1.2rem !important;
            box-shadow: 0 8px 22px rgba(59, 130, 246, 0.25) !important;
            text-align: center !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stFileUploaderDropzone"]:hover {
            border-color: #FFFFFF !important;
            box-shadow: 0 10px 26px rgba(99, 102, 241, 0.35) !important;
        }

        [data-testid="stFileUploaderDropzone"] span,
        [data-testid="stFileUploaderDropzone"] div,
        [data-testid="stFileUploaderDropzone"] p,
        [data-testid="stFileUploaderDropzoneInstructions"] {
            color: #FFFFFF !important;
            font-weight: 500 !important;
        }

        [data-testid="stFileUploaderDropzone"] small {
            color: rgba(255, 255, 255, 0.88) !important;
            font-size: 0.78rem !important;
            font-weight: 500 !important;
        }

        [data-testid="stFileUploaderDropzone"] svg {
            fill: #FFFFFF !important;
            stroke: #FFFFFF !important;
            width: 32px !important;
            height: 32px !important;
            margin-bottom: 4px !important;
        }

        [data-testid="stFileUploaderDropzone"] button {
            background-color: #FFFFFF !important;
            color: #1D4ED8 !important;
            font-weight: 700 !important;
            border-radius: 10px !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12) !important;
            padding: 8px 20px !important;
            margin-top: 8px !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stFileUploaderDropzone"] button:hover {
            background-color: #F8FAFC !important;
            color: #1E40AF !important;
            transform: translateY(-1px) !important;
        }

        [data-testid="stFileUploaderFile"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 10px !important;
            padding: 8px 12px !important;
            margin-top: 6px !important;
        }

        [data-testid="stFileUploaderFile"] * {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        .card-quick-features {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            margin-top: 1rem;
            margin-bottom: 1rem;
        }

        .card-quick-features-title {
            font-size: 0.98rem !important;
            font-weight: 700 !important;
            color: #000000 !important;
            margin: 0 0 0.8rem 0 !important;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .feature-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 5px 0;
            font-size: 0.88rem;
            color: #000000;
            font-weight: 500;
        }

        .feature-check {
            width: 18px;
            height: 18px;
            background: #10B981;
            color: #FFFFFF;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.65rem;
            font-weight: bold;
            flex-shrink: 0;
        }

        .card-how-rag {
            background: #F0FDF4;
            border: 1px solid #BBF7D0;
            border-radius: 16px;
            padding: 1.2rem 1.4rem;
        }

        .card-how-rag-title {
            font-size: 0.96rem !important;
            font-weight: 700 !important;
            color: #15803D !important;
            margin: 0 0 0.5rem 0 !important;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .card-how-rag-body {
            font-size: 0.84rem;
            color: #166534;
            line-height: 1.55;
            margin: 0;
            font-weight: 600;
        }

        .empty-hero-card {
            background: #FFFFFF;
            border: 1px dashed #CBD5E1;
            border-radius: 16px;
            padding: 2.2rem 1.8rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .empty-hero-icon {
            font-size: 2.4rem;
            margin-bottom: 0.5rem;
        }

        .empty-hero-title {
            font-size: 1.25rem !important;
            font-weight: 800 !important;
            color: #000000 !important;
            margin-bottom: 0.4rem !important;
        }

        .empty-hero-desc {
            font-size: 0.9rem !important;
            color: #334155 !important;
            max-width: 480px;
            margin: 0 auto 1.2rem auto !important;
            line-height: 1.5 !important;
        }

        [data-testid="stChatMessage"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 16px !important;
            padding: 1.1rem 1.3rem !important;
            margin-bottom: 1rem !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        }

        [data-testid="stChatMessage"],
        [data-testid="stChatMessage"] *,
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] span,
        [data-testid="stChatMessage"] div,
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] ul,
        [data-testid="stChatMessage"] ol,
        [data-testid="stChatMessage"] strong,
        [data-testid="stChatMessage"] b,
        [data-testid="stChatMessage"] em,
        [data-testid="stChatMessage"] h1,
        [data-testid="stChatMessage"] h2,
        [data-testid="stChatMessage"] h3,
        [data-testid="stChatMessage"] h4,
        [data-testid="stChatMessage"] h5,
        [data-testid="stChatMessage"] h6 {
            color: #000000 !important;
            font-size: 0.95rem !important;
            line-height: 1.65 !important;
        }

        [data-testid="stChatMessage"] strong,
        [data-testid="stChatMessage"] b {
            font-weight: 700 !important;
            color: #000000 !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background-color: #DBEAFE !important;
            border-radius: 18px 18px 4px 18px !important;
            border: 1px solid #BFDBFE !important;
            margin-left: 15% !important;
            box-shadow: 0 1px 3px rgba(59, 130, 246, 0.08) !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) * {
            color: #000000 !important;
        }

        .source-pill-footer {
            margin-top: 14px;
            padding-top: 10px;
            border-top: 1px solid #E2E8F0;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .source-tag {
            background: #F1F5F9 !important;
            color: #000000 !important;
            padding: 4px 10px !important;
            border-radius: 6px !important;
            font-size: 0.8rem !important;
            font-weight: 700 !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 5px !important;
            border: 1px solid #CBD5E1 !important;
        }

        [data-testid="stChatInput"] {
            background-color: #FFFFFF !important;
            border-radius: 14px !important;
            border: 1px solid #CBD5E1 !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
        }

        [data-testid="stChatInput"] textarea {
            color: #000000 !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: #64748B !important;
        }

        [data-testid="stChatInput"]:focus-within {
            border-color: #3B82F6 !important;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
        }

        div[data-baseweb="select"] {
            border-radius: 10px !important;
            border-color: #CBD5E1 !important;
        }

        div[data-baseweb="select"] * {
            color: #000000 !important;
            font-weight: 500 !important;
        }

        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            font-size: 0.9rem !important;
        }

        div[data-baseweb="popover"] li:hover {
            background-color: #EFF6FF !important;
            color: #2563EB !important;
        }

        .stButton button[kind="primary"] {
            background-color: #3B82F6 !important;
            color: #FFFFFF !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 2px 6px rgba(59, 130, 246, 0.25) !important;
        }

        .stButton button[kind="primary"]:hover {
            background-color: #2563EB !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35) !important;
        }

        .stButton button[kind="secondary"] {
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }

        .stButton button[kind="secondary"]:hover {
            background-color: #F8FAFC !important;
            border-color: #3B82F6 !important;
            color: #2563EB !important;
        }
    </style>
    """


def apply_custom_css():
    if hasattr(st, "html"):
        st.html(get_custom_css())
    else:
        st.markdown(get_custom_css(), unsafe_allow_html=True)


def render_html(html_str: str):
    if not html_str:
        return
    cleaned = re.sub(r'<!--.*?-->', '', html_str, flags=re.DOTALL)
    cleaned = "\n".join(line.strip() for line in cleaned.splitlines() if line.strip())
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def get_score_badge(score: float) -> str:
    pct = round(score * 100, 1)
    if score >= 0.65:
        return f'<span style="background:#DCFCE7; color:#15803D; padding:3px 10px; border-radius:9999px; font-weight:700; font-size:0.75rem;">★ Match: {pct}%</span>'
    elif score >= 0.45:
        return f'<span style="background:#FEF3C7; color:#B45309; padding:3px 10px; border-radius:9999px; font-weight:700; font-size:0.75rem;">✦ Match: {pct}%</span>'
    else:
        return f'<span style="background:#F1F5F9; color:#475569; padding:3px 10px; border-radius:9999px; font-weight:700; font-size:0.75rem;">Match: {pct}%</span>'
