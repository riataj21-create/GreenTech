"""
GreenTech - Main Entry Point
Run with: streamlit run main.py
"""

import streamlit as st
from utils.config import APP_NAME, APP_SUBTITLE, COLORS

# ─── Page configuration (must be first Streamlit call) ───────────────────────
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global CSS ───────────────────────────────────────────────────────────────
def inject_global_css():
    st.markdown(f"""
    <style>
    /* ── Reset & Base ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* Main background */
    .stApp {{
        background-color: {COLORS['bg_main']};
        color: {COLORS['text_primary']};
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['bg_secondary']};
        border-right: 1px solid {COLORS['border']};
    }}

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] label {{
        color: {COLORS['text_secondary']} !important;
    }}

    /* Remove default Streamlit padding on main block */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1100px;
    }}

    /* Headings */
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['text_primary']} !important;
    }}

    /* Paragraphs */
    p {{
        color: {COLORS['text_secondary']};
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background-color: {COLORS['accent_primary']};
        color: #0B1220;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.45rem 1.2rem;
        font-size: 0.9rem;
        transition: opacity 0.15s ease;
    }}
    .stButton > button:hover {{
        opacity: 0.88;
        color: #0B1220;
    }}
    .stButton > button:focus {{
        outline: 2px solid {COLORS['accent_primary']};
        outline-offset: 2px;
    }}

    /* ── Inputs ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: {COLORS['card_elevated']};
        color: {COLORS['text_primary']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {COLORS['accent_primary']};
        box-shadow: 0 0 0 2px {COLORS['accent_primary']}33;
    }}

    /* ── Select box ── */
    .stSelectbox > div > div {{
        background-color: {COLORS['card_elevated']};
        border: 1px solid {COLORS['border']};
        border-radius: 6px;
        color: {COLORS['text_primary']};
    }}

    /* ── Radio ── */
    .stRadio > div {{
        gap: 0.5rem;
    }}

    /* ── Divider ── */
    hr {{
        border-color: {COLORS['border']};
        margin: 1.5rem 0;
    }}

    /* ── Info / Warning / Success boxes ── */
    .stAlert {{
        border-radius: 8px;
    }}

    /* ── Sidebar nav radio buttons ── */
    [data-testid="stSidebar"] .stRadio label {{
        color: {COLORS['text_secondary']} !important;
        font-size: 0.95rem;
    }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {COLORS['bg_secondary']}; }}
    ::-webkit-scrollbar-thumb {{ background: {COLORS['border']}; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {COLORS['accent_primary']}; }}
    
    /* ── Hide Streamlit's default page navigation (prevents duplicates) ── */
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    /* Also hide the nav UL that Streamlit injects above custom sidebar content */
    section[data-testid="stSidebar"] > div:first-child > div:first-child ul {{
        display: none !important;
    }}
    section[data-testid="stSidebar"] nav {{
        display: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# ─── Session state initialisation (before any widget) ────────────────────────
def init_session_state():
    defaults = {
        "current_page":   "Home",
        "language":       "English",
        "crop":           "",
        "problem":        "",
        "advice_result":  None,
        "history":        [],
        "tts_enabled":    True,
        "weather_city":   "",   # empty = use default from .env
        # Phase 3 – voice
        "voice_recording":    False,
        "voice_transcript":   "",
        "voice_error":        "",
        "voice_model_ready":  False,
        "voice_auto_advice":  False,   # True after Stop&Transcribe → fires Get Advice
        # Phase 4 – TTS
        "tts_speaking":       False,   # True while speech thread is active
        "tts_message":        "",      # last status/error from tts_service
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Phase 5 — load persistent history from disk (overwrites the empty []
    # default above only if history key was just created)
    from utils.storage import load_history_into_session
    load_history_into_session()


# ─── Sidebar ─────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Logo / brand
        st.markdown(f"""
        <div style="padding: 1rem 0 1.5rem 0; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.25rem;">🌿</div>
            <div style="font-size: 1.3rem; font-weight: 700;
                        color: {COLORS['accent_primary']}; letter-spacing: 0.5px;">
                GreenTech
            </div>
            <div style="font-size: 0.72rem; color: {COLORS['text_muted']};
                        margin-top: 0.15rem;">
                AI Farmer Advisory
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"<hr style='border-color:{COLORS['border']}; margin: 0 0 1rem 0;'>",
                    unsafe_allow_html=True)

        # Navigation
        pages = ["🏠 Home", "🌾 Farmer Assistant", "📋 History", "⚙️ Settings", "ℹ️ About"]
        page_keys = ["Home", "Farmer Assistant", "History", "Settings", "About"]

        # Find current index driven purely by session_state
        current_index = page_keys.index(st.session_state["current_page"]) if st.session_state["current_page"] in page_keys else 0

        selected_index = st.radio(
            "Navigation",
            options=range(len(pages)),
            index=current_index,
            format_func=lambda i: pages[i],
            label_visibility="collapsed",
        )
        # Update only if user actually clicked a different item
        if page_keys[selected_index] != st.session_state["current_page"]:
            st.session_state["current_page"] = page_keys[selected_index]
            st.rerun()

        st.markdown(f"<hr style='border-color:{COLORS['border']}; margin: 1rem 0;'>",
                    unsafe_allow_html=True)

        # AI status badge
        from utils.config import ai_configured, AI_PROVIDER
        if ai_configured():
            badge_color = COLORS["success"]
            provider_name = AI_PROVIDER.title()
            badge_text  = f"{provider_name} AI: Configured"
            badge_icon  = "✓"
        else:
            badge_color = COLORS["text_muted"]
            badge_text  = "AI: Not configured"
            badge_icon  = "○"

        st.markdown(
            f'<div style="padding:0.5rem 0.75rem;border-radius:6px;'
            f'background:{COLORS["card"]};border:1px solid {COLORS["border"]};'
            f'display:flex;align-items:center;gap:0.5rem;">'
            f'<span style="color:{badge_color};font-size:0.85rem;">{badge_icon}</span>'
            f'<span style="color:{COLORS["text_muted"]};font-size:0.78rem;">{badge_text}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Version footer — below badge, no absolute positioning
        st.markdown(
            f'<div style="text-align:center;color:{COLORS["text_muted"]};'
            f'font-size:0.7rem;margin-top:1rem;padding-bottom:0.5rem;">'
            f'GreenTech v1.0.0</div>',
            unsafe_allow_html=True,
        )


# ─── Page router ─────────────────────────────────────────────────────────────
def route_page():
    page = st.session_state["current_page"]

    if page == "Home":
        from pages.home import render
        render()
    elif page == "Farmer Assistant":
        from pages.farmer_assistant import render
        render()
    elif page == "History":
        from pages.history import render
        render()
    elif page == "Settings":
        from pages.settings import render
        render()
    elif page == "About":
        from pages.about import render
        render()


# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    inject_global_css()
    init_session_state()
    render_sidebar()
    route_page()


if __name__ == "__main__":
    main()
