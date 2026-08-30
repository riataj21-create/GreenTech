"""
GreenTech - Settings Page
Application configuration: language, TTS toggle, API/system status, clear history.
API keys are NEVER displayed.
"""

import streamlit as st
from utils.config import COLORS, LANGUAGES, DEFAULT_LANGUAGE, ai_configured, AI_PROVIDER


def _status_row(label: str, ok: bool, ok_text: str, fail_text: str):
    """Render a status indicator row."""
    color = COLORS["success"] if ok else COLORS["text_muted"]
    icon  = "✓" if ok else "○"
    text  = ok_text if ok else fail_text
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.6rem 0;
        border-bottom: 1px solid {COLORS['border']};
    ">
        <span style="font-size: 0.88rem; color: {COLORS['text_secondary']};">{label}</span>
        <span style="
            font-size: 0.82rem;
            color: {color};
            font-weight: 500;
        ">{icon}  {text}</span>
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="
            font-size: 1.55rem;
            font-weight: 700;
            color: {COLORS['text_primary']};
            margin: 0 0 0.3rem 0;
        ">⚙️ Settings</h2>
        <p style="
            font-size: 0.88rem;
            color: {COLORS['text_muted']};
            margin: 0;
        ">Configure GreenTech preferences and review system status.</p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.3, 1], gap="large")

    # ── LEFT: Preferences ─────────────────────────────────────────────────────
    with left:
        st.markdown(f"""
        <div style="
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: {COLORS['text_muted']};
            margin-bottom: 0.8rem;
        ">PREFERENCES</div>
        """, unsafe_allow_html=True)

        # Default response language
        st.markdown(f"<span style='font-size:0.88rem; color:{COLORS['text_secondary']};'>"
                    f"Default Response Language</span>", unsafe_allow_html=True)

        lang_options = list(LANGUAGES.keys())
        # Build display labels: "తెలుగు (Telugu)" etc.
        lang_display = [
            f"{LANGUAGES[k]['native']}  ({k})" if LANGUAGES[k]['native'] != k else k
            for k in lang_options
        ]
        disp_to_key = dict(zip(lang_display, lang_options))
        key_to_disp = {v: k for k, v in disp_to_key.items()}

        current_disp = key_to_disp.get(st.session_state.get("language", DEFAULT_LANGUAGE), lang_display[0])

        selected_disp = st.selectbox(
            "Default Language",
            options=lang_display,
            index=lang_display.index(current_disp),
            label_visibility="collapsed",
            key="settings_lang_select",
        )
        # Always sync — no conditional; avoids post-creation key collision
        new_lang = disp_to_key[selected_disp]
        if new_lang != st.session_state.get("language"):
            st.session_state["language"] = new_lang
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # TTS toggle
        st.markdown(f"<span style='font-size:0.88rem; color:{COLORS['text_secondary']};'>"
                    f"Text-to-Speech (Read Aloud)</span>", unsafe_allow_html=True)
        tts_enabled = st.toggle(
            "Enable TTS",
            value=st.session_state.get("tts_enabled", True),
            key="tts_toggle",
            label_visibility="collapsed",
        )
        st.session_state["tts_enabled"] = tts_enabled
        st.markdown(
            f"<span style='font-size:0.78rem; color:{COLORS['text_muted']};'>"
            f"{'Enabled — responses can be read aloud (Phase 4).' if tts_enabled else 'Disabled.'}"
            f"</span>",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Clear history
        st.markdown(f"""
        <div style="
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: {COLORS['text_muted']};
            margin-bottom: 0.8rem;
        ">DATA</div>
        """, unsafe_allow_html=True)

        history_count = len(st.session_state.get("history", []))
        st.markdown(
            f"<span style='font-size:0.84rem; color:{COLORS['text_secondary']};'>"
            f"{history_count} session record{'s' if history_count != 1 else ''} stored.</span>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

        if st.button("🗑  Clear All History", key="settings_clear_history"):
            from utils.storage import clear_history
            clear_history()
            st.success("History cleared.", icon="✅")
            st.rerun()

    # ── RIGHT: System status ──────────────────────────────────────────────────
    with right:
        st.markdown(f"""
        <div style="
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: {COLORS['text_muted']};
            margin-bottom: 0.8rem;
        ">SYSTEM STATUS</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 10px;
            padding: 0.5rem 1.1rem 0.2rem 1.1rem;
        ">
        """, unsafe_allow_html=True)

        # Live AI connectivity check
        if ai_configured():
            from services.ai_service import check_ai_status
            ai_status = check_ai_status()
            provider_name = ai_status.get("provider", "unknown").title()
            _status_row(
                f"{provider_name} API",
                ai_status["ok"],
                ai_status["message"],
                ai_status["message"],
            )
        else:
            _status_row(
                "AI API",
                False,
                "Configured",
                "Not configured — add OPENROUTER_API_KEY or GEMINI_API_KEY to .env",
            )

        # Weather API status
        from services.weather_service import check_weather_status
        weather_status = check_weather_status()
        _status_row(
            "Weather API (Madanapalli)",
            weather_status["configured"],
            weather_status["message"],
            weather_status["message"],
        )

        # Voice / Faster-Whisper status
        from services.voice_service import get_voice_status
        vs = get_voice_status()
        voice_ok_text   = f"Ready — mic: {vs['mic']}  |  {vs['model']}"
        voice_fail_text = vs["message"]
        _status_row(
            "Voice Input (Faster-Whisper)",
            vs["ready"],
            voice_ok_text,
            voice_fail_text,
        )
        if vs["ready"] and not vs["ffmpeg"]:
            st.markdown(
                f"<div style='font-size:0.74rem;color:{COLORS['text_muted']};"
                f"padding:0.2rem 0 0.4rem 0;'>"
                f"FFmpeg not found — not required for microphone recording.</div>",
                unsafe_allow_html=True,
            )

        # TTS status — check for currently selected language
        current_lang = st.session_state.get("language", "English")
        from services.tts_service import get_tts_status, list_installed_voices
        tts_st = get_tts_status(current_lang)
        tts_ok_text   = f"Voice available: {tts_st['voice_name']}  ({current_lang})"
        tts_fail_text = f"No {current_lang} voice installed — English only available"
        _status_row("Text-to-Speech", tts_st["available"], tts_ok_text, tts_fail_text)
        voices = list_installed_voices()
        if voices:
            st.markdown(
                f"<div style='font-size:0.74rem;color:{COLORS['text_muted']};"
                f"padding:0.1rem 0 0.4rem 0;'>"
                f"Installed: {', '.join(voices)}</div>",
                unsafe_allow_html=True,
            )
        if not tts_st["available"] and tts_st.get("install_guide"):
            st.markdown(
                f"<div style='font-size:0.74rem;color:{COLORS['text_muted']};"
                f"padding:0.1rem 0 0.5rem 0;'>"
                f"💡 {tts_st['install_guide']}</div>",
                unsafe_allow_html=True,
            )
        _status_row(
            "History Storage",
            True,
            f"Persistent JSON  ({len(st.session_state.get('history', []))} entries)",
            "Unavailable",
        )
        from utils.storage import history_file_path
        st.markdown(
            f"<div style='font-size:0.74rem;color:{COLORS['text_muted']};"
            f"padding:0.1rem 0 0.5rem 0;'>📁 {history_file_path()}</div>",
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # API key note
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-left: 3px solid {COLORS['accent_secondary']};
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 0.8rem;
            color: {COLORS['text_muted']};
            line-height: 1.6;
        ">
            <strong style="color:{COLORS['text_secondary']};">API keys are never displayed.</strong><br>
            To configure Gemini, create a <code>.env</code> file in the project root
            using <code>.env.example</code> as a template and add your
            <code>GEMINI_API_KEY</code>.
        </div>
        """, unsafe_allow_html=True)
