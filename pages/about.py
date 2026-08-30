"""
GreenTech - About Page
Project identity, problem statement, and technology overview.
"""

import streamlit as st
from utils.config import (
    COLORS, APP_NAME, APP_SUBTITLE, APP_VERSION,
    APP_PROBLEM_ID, LANGUAGES,
)


def _tech_card(icon: str, title: str, description: str):
    st.markdown(f"""
    <div style="
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 1rem 1.2rem;
        height: 100%;
    ">
        <div style="font-size: 1.4rem; margin-bottom: 0.4rem;">{icon}</div>
        <div style="
            font-size: 0.88rem;
            font-weight: 600;
            color: {COLORS['text_primary']};
            margin-bottom: 0.3rem;
        ">{title}</div>
        <div style="
            font-size: 0.78rem;
            color: {COLORS['text_muted']};
            line-height: 1.55;
        ">{description}</div>
    </div>
    """, unsafe_allow_html=True)


def render():
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="
            font-size: 1.55rem;
            font-weight: 700;
            color: {COLORS['text_primary']};
            margin: 0 0 0.3rem 0;
        ">ℹ️ About GreenTech</h2>
        <p style="
            font-size: 0.88rem;
            color: {COLORS['text_muted']};
            margin: 0;
        ">Project identity and technology overview.</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.6, 1], gap="large")

    # ── LEFT: Identity ────────────────────────────────────────────────────────
    with left:
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.8rem 2rem;
            margin-bottom: 1.2rem;
        ">
            <div style="font-size: 2.2rem; margin-bottom: 0.6rem;">🌿</div>
            <h1 style="
                font-size: 2rem;
                font-weight: 700;
                color: {COLORS['accent_primary']};
                margin: 0 0 0.2rem 0;
            ">{APP_NAME}</h1>
            <p style="
                font-size: 0.95rem;
                color: {COLORS['text_secondary']};
                margin: 0 0 1.2rem 0;
            ">{APP_SUBTITLE}</p>
            <div style="
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 0.8rem;
                font-size: 0.82rem;
            ">
                <div>
                    <span style="color:{COLORS['text_muted']};">Problem Statement</span><br>
                    <span style="color:{COLORS['text_primary']}; font-weight:600;">
                        {APP_PROBLEM_ID}
                    </span>
                </div>
                <div>
                    <span style="color:{COLORS['text_muted']};">Theme</span><br>
                    <span style="color:{COLORS['text_primary']}; font-weight:600;">Software</span>
                </div>
                <div>
                    <span style="color:{COLORS['text_muted']};">Category</span><br>
                    <span style="color:{COLORS['text_primary']}; font-weight:600;">
                        Generative AI &amp; AgriTech
                    </span>
                </div>
                <div>
                    <span style="color:{COLORS['text_muted']};">Version</span><br>
                    <span style="color:{COLORS['text_primary']}; font-weight:600;">
                        {APP_VERSION}
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Mission
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1.2rem;
        ">
            <div style="
                font-size: 0.78rem;
                font-weight: 600;
                letter-spacing: 1px;
                text-transform: uppercase;
                color: {COLORS['text_muted']};
                margin-bottom: 0.7rem;
            ">MISSION</div>
            <p style="
                font-size: 0.88rem;
                color: {COLORS['text_secondary']};
                line-height: 1.7;
                margin: 0;
            ">
                GreenTech gives farmers access to AI-powered agricultural guidance
                in their own language. By combining Google Gemini's natural-language
                understanding with a local agricultural knowledge layer, GreenTech
                helps farmers diagnose crop problems, understand possible causes,
                and take practical action — without needing internet search skills
                or technical knowledge.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Supported languages
        lang_items = "".join([
            f"<li style='margin-bottom:0.3rem;'>"
            f"<span style='color:{COLORS['text_primary']};font-weight:500;'>"
            f"{info['native']}</span>"
            f"<span style='color:{COLORS['text_muted']};'> — {info['label']}</span></li>"
            for info in LANGUAGES.values()
        ])
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 1.2rem 1.4rem;
        ">
            <div style="
                font-size: 0.78rem;
                font-weight: 600;
                letter-spacing: 1px;
                text-transform: uppercase;
                color: {COLORS['text_muted']};
                margin-bottom: 0.7rem;
            ">SUPPORTED LANGUAGES</div>
            <ul style="margin:0; padding-left:1.2rem; font-size:0.86rem; line-height:1.8;">
                {lang_items}
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # ── RIGHT: Technology ─────────────────────────────────────────────────────
    with right:
        st.markdown(f"""
        <div style="
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: {COLORS['text_muted']};
            margin-bottom: 0.8rem;
        ">TECHNOLOGY</div>
        """, unsafe_allow_html=True)

        _tech_card(
            "🤖", "Generative AI",
            "Google Gemini provides genuine natural-language agricultural reasoning "
            "and multilingual response generation.",
        )
        st.markdown("<div style='margin-bottom:0.7rem;'></div>", unsafe_allow_html=True)

        _tech_card(
            "🎤", "Speech AI",
            "Faster-Whisper enables multilingual voice-to-text transcription directly "
            "from the farmer's microphone.",
        )
        st.markdown("<div style='margin-bottom:0.7rem;'></div>", unsafe_allow_html=True)

        _tech_card(
            "🌾", "Agricultural Knowledge",
            "A local crop knowledge layer enriches AI prompts with context about "
            "common crops, diseases, and growing conditions.",
        )
        st.markdown("<div style='margin-bottom:0.7rem;'></div>", unsafe_allow_html=True)

        _tech_card(
            "🔊", "Text-to-Speech",
            "Recommendations can be read aloud using available system voices, "
            "making advice accessible to all farmers.",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Design principles
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 1.1rem 1.2rem;
        ">
            <div style="
                font-size: 0.78rem;
                font-weight: 600;
                letter-spacing: 1px;
                text-transform: uppercase;
                color: {COLORS['text_muted']};
                margin-bottom: 0.6rem;
            ">DESIGN PRINCIPLES</div>
            <ul style="
                margin: 0;
                padding-left: 1.1rem;
                font-size: 0.8rem;
                color: {COLORS['text_muted']};
                line-height: 1.8;
            ">
                <li>Simple. Reliable. Meaningful.</li>
                <li>No technical knowledge required from the farmer.</li>
                <li>Graceful degradation when services are unavailable.</li>
                <li>No fake AI output — ever.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
