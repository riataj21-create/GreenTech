"""
GreenTech - Farmer Assistant Page

Voice flow (Phase 3 revised):
  1. Select language + enter crop name
  2. Press ⏺ Start Recording → speak → Press ⏹ Stop & Transcribe
  3. Transcript is AUTOMATICALLY used as the problem description
     and Get Advice fires immediately — no extra clicks needed.
  4. Farmer can still edit the transcript before it is sent if they
     want to, by clearing the auto-result and using the text area.

Text flow:
  1. Type crop + problem → Get Advice

Streamlit session-state safety rules:
  - All keys initialised in main.py before any widget.
  - Widget return values used; widget-key state never overwritten post-creation.
"""

import streamlit as st
from utils.config import COLORS, LANGUAGES, ai_configured
from utils.storage import save_to_history


# ─── UI helpers ───────────────────────────────────────────────────────────────

def _label(text: str):
    st.markdown(
        f"<div style='font-size:0.78rem;font-weight:600;letter-spacing:0.9px;"
        f"text-transform:uppercase;color:{COLORS['text_muted']};margin-bottom:0.4rem;'>"
        f"{text}</div>",
        unsafe_allow_html=True,
    )


def _banner(icon: str, message: str, border: str):
    st.markdown(
        f"<div style='background:{COLORS['card']};border:1px solid {border}44;"
        f"border-left:3px solid {border};border-radius:8px;padding:0.75rem 1rem;"
        f"display:flex;align-items:flex-start;gap:0.6rem;margin-bottom:0.75rem;'>"
        f"<span style='font-size:1rem;'>{icon}</span>"
        f"<span style='font-size:0.84rem;color:{COLORS['text_secondary']};line-height:1.5;'>"
        f"{message}</span></div>",
        unsafe_allow_html=True,
    )


# ─── AI call helper (shared by both text and voice paths) ─────────────────────

def _run_advice(crop: str, problem: str, language: str, input_method: str):
    """Call AI service, store result, save to history. Returns True on success."""
    from services.ai_service import get_agricultural_advice
    
    # Show language-specific analysis message
    if language == "English":
        analysis_msg = "🤖 Analyzing your crop problem..."
    else:
        analysis_msg = f"🤖 Analyzing your {language} crop problem..."
    
    with st.spinner(analysis_msg):
        result = get_agricultural_advice(crop=crop, problem=problem, language=language)

    if result["success"]:
        st.session_state["advice_result"]    = result
        st.session_state["voice_transcript"] = ""
        st.session_state["voice_error"]      = ""
        save_to_history(
            crop=crop, problem=problem,
            advice=result["text"], language=language,
            input_method=input_method,
        )
        return True
    else:
        st.error(f"Could not get advice: {result['error']}", icon="⚠️")
        st.session_state["advice_result"] = None
        return False


# ─── Advice result card ───────────────────────────────────────────────────────

def _render_advice_card(result: dict, language: str):
    st.markdown("<br>", unsafe_allow_html=True)
    crop  = result.get("crop", "")
    lang  = result.get("language", "English")
    model = result.get("model", "")
    text  = result.get("text", "")

    st.markdown(
        f"<div style='background:{COLORS['card_elevated']};"
        f"border:1px solid {COLORS['accent_primary']}55;"
        f"border-radius:12px 12px 0 0;padding:0.9rem 1.4rem;"
        f"display:flex;justify-content:space-between;align-items:center;'>"
        f"<span style='font-size:1rem;font-weight:700;color:{COLORS['accent_primary']};'>"
        f"🌿 AI Agricultural Advice</span>"
        f"<span style='font-size:0.75rem;color:{COLORS['text_muted']};'>"
        f"{crop} · {lang}{'  ·  ' + model if model else ''}</span>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='background:{COLORS['card']};"
        f"border:1px solid {COLORS['accent_primary']}33;border-top:none;"
        f"border-radius:0 0 12px 12px;padding:1.2rem 1.4rem;"
        f"font-size:0.88rem;color:{COLORS['text_secondary']};"
        f"line-height:1.75;white-space:pre-wrap;'>{text}</div>",
        unsafe_allow_html=True,
    )

    # TTS row
    tts_enabled = st.session_state.get("tts_enabled", True)
    if not tts_enabled:
        st.markdown(
            f"<div style='font-size:0.75rem;color:{COLORS['text_muted']};margin-top:0.5rem;'>"
            f"Read Aloud is disabled in Settings.</div>",
            unsafe_allow_html=True,
        )
        return

    from services.tts_service import get_tts_status, speak, stop, is_speaking, can_speak
    tts_status = get_tts_status(language)
    tts_available = can_speak(language)  # Check including fallback
    tts_msg    = st.session_state.get("tts_message", "")

    col_read, col_stop, col_info = st.columns([1, 1, 3])
    with col_read:
        read_label   = "🔊  Reading…" if is_speaking() else "🔊  Read Aloud"
        read_clicked = st.button(read_label, key="fa_tts_read_btn",
                                 use_container_width=True,
                                 disabled=not tts_available)  # Use fallback-aware check
    with col_stop:
        stop_clicked = st.button("⏹  Stop", key="fa_tts_stop_btn",
                                 use_container_width=True,
                                 disabled=not is_speaking())
    with col_info:
        if not tts_available:
            # Only show error if no fallback available
            guide = tts_status.get("install_guide", "")
            st.markdown(
                f"<div style='font-size:0.78rem;color:{COLORS['warning']};padding:0.35rem 0;'>"
                f"⚠️  {tts_status['message']}"
                + (f"<br><span style='color:{COLORS['text_muted']};'>💡 {guide}</span>" if guide else "")
                + "</div>", unsafe_allow_html=True,
            )
        elif not tts_status["available"] and language in ["Telugu", "Hindi", "Tamil", "Kannada"]:
            # Show fallback message for Indian languages
            st.markdown(
                f"<div style='font-size:0.78rem;color:{COLORS['text_muted']};padding:0.35rem 0;'>"
                f"ℹ️  Using English voice for {language} text (install {language} voice for native audio)"
                + "</div>", unsafe_allow_html=True,
            )
        elif tts_msg:
            c = COLORS["success"] if any(w in tts_msg.lower() for w in ("reading","started")) else COLORS["text_muted"]
            st.markdown(
                f"<div style='font-size:0.78rem;color:{c};padding:0.35rem 0;'>{tts_msg}</div>",
                unsafe_allow_html=True,
            )

    if read_clicked and tts_available:  # Use fallback-aware check
        r = speak(text, language)
        st.session_state["tts_message"] = f"🔊 Reading aloud using {r['voice']}…" if r["success"] else f"⚠️ {r['error']}"
        st.rerun()
    if stop_clicked:
        stop()
        st.session_state["tts_message"] = "Stopped."
        st.rerun()


# ─── Voice section ────────────────────────────────────────────────────────────

def _render_voice_section(language: str):
    """
    Push-to-talk:
      ⏺ Start Recording  → mic opens, farmer speaks freely
      ⏹ Stop & Transcribe → mic closes, Whisper runs,
                            transcript auto-fills problem box
                            and Get Advice fires immediately.
    """
    from services.voice_service import (
        check_dependencies, start_recording, stop_recording,
        transcribe_audio, is_recording,
    )

    deps = check_dependencies()

    st.markdown(
        f"<div style='background:{COLORS['card']};border:1px solid {COLORS['border']};"
        f"border-radius:12px;padding:1.4rem 1.6rem;margin-bottom:1rem;'>"
        f"<div style='font-size:0.82rem;font-weight:600;color:{COLORS['accent_primary']};"
        f"margin-bottom:0.8rem;letter-spacing:0.5px;'>🎤 VOICE INPUT</div>",
        unsafe_allow_html=True,
    )

    if not deps["ready"]:
        st.markdown(
            f"<div style='font-size:0.84rem;color:{COLORS['warning']};padding:0.5rem 0;'>"
            f"⚠️  {deps['message']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # Mic info
    mic_name     = deps.get("microphone_name", "")
    ffmpeg_ok    = deps.get("ffmpeg", False)
    ffmpeg_color = COLORS["success"] if ffmpeg_ok else COLORS["text_muted"]
    ffmpeg_txt   = "✓" if ffmpeg_ok else "○ not needed"
    st.markdown(
        f"<div style='font-size:0.78rem;color:{COLORS['text_muted']};margin-bottom:0.9rem;"
        f"display:flex;gap:1.2rem;flex-wrap:wrap;'>"
        f"<span>🎙 {mic_name}</span><span>whisper/small</span>"
        f"<span style='color:{ffmpeg_color};'>FFmpeg: {ffmpeg_txt}</span></div>",
        unsafe_allow_html=True,
    )

    currently_recording = is_recording()

    # Show either Start or Stop — not both disabled — to avoid Streamlit
    # dropping button events when disabled state flips between reruns.
    if not currently_recording:
        col_start, col_clear = st.columns([2.5, 1.0])
        with col_start:
            start_clicked = st.button(
                "⏺  Start Recording",
                key="voice_start_btn",
                use_container_width=True,
            )
        with col_clear:
            clear_clicked = st.button("✕  Clear", key="voice_clear_btn",
                                      use_container_width=True)
        stop_clicked = False
    else:
        col_stop, col_clear = st.columns([2.5, 1.0])
        with col_stop:
            stop_clicked = st.button(
                "⏹  Stop & Transcribe",
                key="voice_stop_btn",
                use_container_width=True,
            )
        with col_clear:
            clear_clicked = st.button("✕  Clear", key="voice_clear_btn",
                                      use_container_width=True)
        start_clicked = False

    if currently_recording:
        st.markdown(
            f"<div style='font-size:0.82rem;color:{COLORS['danger']};font-weight:600;"
            f"margin:0.5rem 0;'>● Recording — speak now, then press Stop & Transcribe</div>",
            unsafe_allow_html=True,
        )

    # ── Clear ─────────────────────────────────────────────────────────────────
    if clear_clicked:
        from services.voice_service import _state_lock, _stop_stream
        with _state_lock:
            _stop_stream()
        st.session_state["voice_transcript"]    = ""
        st.session_state["voice_error"]         = ""
        st.session_state["voice_auto_advice"]   = False
        st.markdown("</div>", unsafe_allow_html=True)
        st.rerun()

    # ── Start ─────────────────────────────────────────────────────────────────
    if start_clicked and not currently_recording:
        r = start_recording()
        st.session_state["voice_error"] = "" if r["success"] else r["error"]
        st.markdown("</div>", unsafe_allow_html=True)
        st.rerun()

    # ── Stop & Transcribe → auto-advice ──────────────────────────────────────
    if stop_clicked and currently_recording:
        with st.spinner("🎤 Processing your recording..."):
            audio_result = stop_recording()

        if not audio_result["success"]:
            st.session_state["voice_error"]      = audio_result["error"]
            st.session_state["voice_transcript"] = ""
            st.markdown("</div>", unsafe_allow_html=True)
            st.rerun()
        else:
            with st.spinner(f"🔍 Transcribing {language} speech with Whisper..."):
                tx = transcribe_audio(audio_result["audio"], language)

            if tx["success"]:
                st.session_state["voice_transcript"]  = tx["transcript"]
                st.session_state["voice_error"]       = ""
                # Signal main render to auto-fire Get Advice with this transcript
                st.session_state["voice_auto_advice"] = True
            else:
                st.session_state["voice_transcript"]  = ""
                st.session_state["voice_error"]       = tx["error"]
                st.session_state["voice_auto_advice"] = False

        st.markdown("</div>", unsafe_allow_html=True)
        st.rerun()

    # ── Error display ─────────────────────────────────────────────────────────
    voice_error = st.session_state.get("voice_error", "")
    if voice_error:
        st.markdown(
            f"<div style='background:{COLORS['card_elevated']};"
            f"border-left:3px solid {COLORS['danger']};"
            f"border-radius:8px;padding:0.65rem 0.9rem;"
            f"font-size:0.83rem;color:{COLORS['warning']};margin-top:0.5rem;'>"
            f"⚠️  {voice_error}</div>",
            unsafe_allow_html=True,
        )

    # ── Transcript display (read-only, for reference) ─────────────────────────
    transcript = st.session_state.get("voice_transcript", "")
    if transcript and not st.session_state.get("voice_auto_advice"):
        # Only show the editor if auto-advice hasn't fired yet
        st.markdown(
            f"<div style='font-size:0.78rem;font-weight:600;color:{COLORS['success']};"
            f"margin:0.8rem 0 0.3rem 0;'>✓ TRANSCRIPT</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='background:{COLORS['card_elevated']};"
            f"border-radius:8px;padding:0.65rem 0.9rem;"
            f"font-size:0.85rem;color:{COLORS['text_secondary']};'>"
            f"{transcript}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ─── Main render ──────────────────────────────────────────────────────────────

def render():
    # Page header
    st.markdown(
        f"<div style='margin-bottom:1.5rem;'>"
        f"<h2 style='font-size:1.55rem;font-weight:700;"
        f"color:{COLORS['text_primary']};margin:0 0 0.3rem 0;'>"
        f"🌾 Farmer Assistant</h2>"
        f"<p style='font-size:0.88rem;color:{COLORS['text_muted']};margin:0;'>"
        f"Type or speak your crop problem and get AI-powered agricultural guidance."
        f"</p></div>",
        unsafe_allow_html=True,
    )

    if not ai_configured():
        _banner(
            "ℹ️",
            "AI API is not configured. Add your <strong>OPENROUTER_API_KEY</strong> or "
            "<strong>GEMINI_API_KEY</strong> to <code>.env</code> to enable AI advice. "
            "See <strong>.env.example</strong>.",
            COLORS["accent_secondary"],
        )

    # Language
    _label("Language")
    lang_keys    = list(LANGUAGES.keys())
    lang_display = [
        f"{v['native']}  ({v['label']})" if v["label"] != v["native"] else v["label"]
        for v in LANGUAGES.values()
    ]
    d2k = dict(zip(lang_display, lang_keys))
    k2d = {v: k for k, v in d2k.items()}
    current_disp  = k2d.get(st.session_state.get("language", "English"), lang_display[0])
    selected_disp = st.selectbox("Language", options=lang_display,
                                 index=lang_display.index(current_disp),
                                 label_visibility="collapsed", key="fa_lang_select")
    language = d2k[selected_disp]
    st.session_state["language"] = language

    st.markdown("<div style='margin:1rem 0 0.5rem 0;'></div>", unsafe_allow_html=True)

    # Crop
    _label("Crop")
    crop_val = st.text_input("Crop",
                              placeholder="e.g. Rice, Paddy, Tomato, Cotton, Maize…",
                              label_visibility="collapsed", key="fa_crop_input")

    st.markdown("<div style='margin:1rem 0 0.5rem 0;'></div>", unsafe_allow_html=True)

    # Voice section
    _label("Voice Input  (optional — auto-submits after transcription)")
    _render_voice_section(language)

    # ── Auto-advice from voice transcript ─────────────────────────────────────
    # Fires immediately after Stop & Transcribe succeeds — no button needed.
    if st.session_state.get("voice_auto_advice"):
        st.session_state["voice_auto_advice"] = False   # consume the flag
        transcript = st.session_state.get("voice_transcript", "").strip()
        crop       = crop_val.strip()

        if not crop:
            st.warning("Please enter the crop name first, then record again.", icon="⚠️")
        elif not transcript:
            st.warning("Transcription was empty. Please try recording again.", icon="⚠️")
        elif not ai_configured():
            st.error("AI API key is not configured. Add OPENROUTER_API_KEY or GEMINI_API_KEY to your .env file.", icon="🔑")
        else:
            # Auto-fill the problem text area with transcript
            st.session_state["fa_problem_input"] = transcript
            _run_advice(crop, transcript, language, "voice")
            st.rerun()

    # ── Problem text area (text path) ─────────────────────────────────────────
    _label("Describe the Problem  (or use Voice Input above)")

    problem_val = st.text_area(
        "Problem",
        placeholder=(
            "Describe what is happening to your crop in plain language…\n\n"
            "Example: My rice leaves are turning yellow and the plants look weak."
        ),
        height=130,
        label_visibility="collapsed",
        key="fa_problem_input",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Get Advice button (text path)
    col_l, col_btn, col_r = st.columns([0.5, 2, 0.5])
    with col_btn:
        advice_clicked = st.button("🌿  Get Advice", use_container_width=True,
                                   key="fa_advice_btn")

    if advice_clicked:
        crop    = crop_val.strip()
        problem = problem_val.strip()
        if not crop:
            st.warning("Please enter the crop name before requesting advice.", icon="⚠️")
        elif not problem:
            st.warning("Please describe the problem (or use Voice Input above).", icon="⚠️")
        elif not ai_configured():
            st.error("AI API key is not configured. Add OPENROUTER_API_KEY or GEMINI_API_KEY to your .env file.", icon="🔑")
        else:
            _run_advice(crop, problem, language, "text")

    # ── Advice result ─────────────────────────────────────────────────────────
    if st.session_state.get("advice_result") and st.session_state["advice_result"].get("success"):
        _render_advice_card(st.session_state["advice_result"], language)
        st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)
        if st.button("↩  New Query", key="fa_new_query_btn"):
            from services.tts_service import stop as tts_stop
            tts_stop()
            st.session_state["advice_result"]    = None
            st.session_state["voice_transcript"] = ""
            st.session_state["voice_error"]      = ""
            st.session_state["voice_auto_advice"]= False
            st.session_state["tts_message"]      = ""
            st.rerun()

    # Tips
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='background:{COLORS['card']};border:1px solid {COLORS['border']};"
        f"border-radius:10px;padding:1rem 1.3rem;'>"
        f"<div style='font-size:0.78rem;font-weight:600;color:{COLORS['accent_primary']};"
        f"letter-spacing:0.8px;text-transform:uppercase;margin-bottom:0.5rem;'>"
        f"HOW TO USE VOICE</div>"
        f"<ol style='margin:0;padding-left:1.2rem;"
        f"color:{COLORS['text_muted']};font-size:0.82rem;line-height:1.9;'>"
        f"<li>Enter the <strong style='color:{COLORS['text_secondary']};'>crop name</strong> above.</li>"
        f"<li>Select your <strong style='color:{COLORS['text_secondary']};'>language</strong>.</li>"
        f"<li>Press <strong style='color:{COLORS['text_secondary']};'>⏺ Start Recording</strong> and speak your problem.</li>"
        f"<li>Press <strong style='color:{COLORS['text_secondary']};'>⏹ Stop & Transcribe</strong> — advice appears automatically.</li>"
        f"</ol></div>",
        unsafe_allow_html=True,
    )
