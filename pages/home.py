"""
GreenTech - Home Page
"""

import streamlit as st
from utils.config import COLORS, APP_NAME, APP_SUBTITLE, APP_TAGLINE, LANGUAGES


def _card(icon, title, body):
    st.markdown(
        f'<div style="background:{COLORS["card"]};border:1px solid {COLORS["border"]};'
        f'border-radius:10px;padding:1.25rem 1.4rem;height:100%;">'
        f'<div style="font-size:1.6rem;margin-bottom:0.5rem;">{icon}</div>'
        f'<div style="font-size:0.95rem;font-weight:600;color:{COLORS["text_primary"]};'
        f'margin-bottom:0.35rem;">{title}</div>'
        f'<div style="font-size:0.82rem;color:{COLORS["text_muted"]};line-height:1.5;">{body}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render():
    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="text-align:center;padding:2.5rem 0 1.5rem 0;">'
        f'<div style="font-size:3rem;margin-bottom:0.5rem;">🌿</div>'
        f'<h1 style="font-size:2.6rem;font-weight:700;color:{COLORS["accent_primary"]};'
        f'margin:0 0 0.3rem 0;letter-spacing:-0.5px;">{APP_NAME}</h1>'
        f'<p style="font-size:1.05rem;color:{COLORS["text_secondary"]};margin:0 0 0.6rem 0;">{APP_SUBTITLE}</p>'
        f'<p style="font-size:0.9rem;color:{COLORS["text_muted"]};max-width:520px;margin:0 auto;'
        f'line-height:1.6;">{APP_TAGLINE}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Get Started button ────────────────────────────────────────────────────
    _, col_btn, _ = st.columns([2, 1.5, 2])
    with col_btn:
        if st.button("🌾  Get Started", use_container_width=True, key="get_started_btn"):
            st.session_state["current_page"] = "Farmer Assistant"
            st.session_state["nav_radio"] = "🌾 Farmer Assistant"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Weather Widget ────────────────────────────────────────────────────────
    try:
        from services.weather_service import (
            get_current_weather,
            get_weather_icon_emoji,
            get_farming_advice_for_weather,
        )
        # Use user-selected city if set, else default (Madanapalle)
        user_city = st.session_state.get("weather_city", "")
        weather = get_current_weather(city=user_city)
    except Exception:
        weather = {"success": False, "error": "Service unavailable"}

    if weather.get("success"):
        icon_emoji  = get_weather_icon_emoji(weather["icon"])
        farming_tip = get_farming_advice_for_weather(weather)

        st.markdown(
            f'<div style="background:linear-gradient(135deg,{COLORS["card"]} 0%,'
            f'{COLORS["card_elevated"]} 100%);border:1px solid {COLORS["border"]};'
            f'border-radius:12px;padding:1.5rem;margin-bottom:1rem;">'

            # top row: icon + stats
            f'<div style="display:flex;align-items:center;justify-content:center;gap:1.5rem;">'
            f'<div style="font-size:3rem;">{icon_emoji}</div>'
            f'<div>'
            f'<div style="font-size:2rem;font-weight:700;color:{COLORS["text_primary"]};">'
            f'{weather["temperature"]}°C</div>'
            f'<div style="font-size:0.9rem;color:{COLORS["text_secondary"]};">'
            f'{weather["description"]}</div>'
            f'<div style="font-size:0.8rem;color:{COLORS["text_muted"]};">'
            f'Feels like {weather["feels_like"]}°C</div>'
            f'<div style="font-size:0.8rem;color:{COLORS["text_muted"]};">'
            f'📍 {weather["city"]} &nbsp;|&nbsp; '
            f'💨 {weather["wind_speed"]} m/s &nbsp;|&nbsp; 💧 {weather["humidity"]}%</div>'
            f'</div>'
            f'</div>'

            # farming advice row
            f'<div style="background:{COLORS["bg_secondary"]};border-radius:8px;'
            f'padding:0.9rem;margin-top:1rem;">'
            f'<div style="font-size:0.72rem;color:{COLORS["accent_primary"]};font-weight:700;'
            f'text-transform:uppercase;letter-spacing:0.6px;margin-bottom:0.4rem;">'
            f'🌾 Farming Advice</div>'
            f'<div style="font-size:0.83rem;color:{COLORS["text_secondary"]};line-height:1.6;">'
            f'{farming_tip}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="background:{COLORS["card"]};border:1px solid {COLORS["border"]};'
            f'border-radius:8px;padding:1rem;text-align:center;margin-bottom:1rem;">'
            f'<div style="color:{COLORS["text_muted"]};font-size:0.85rem;">'
            f'🌤️ Weather data for Madanapalle unavailable</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── What GreenTech Does ───────────────────────────────────────────────────
    st.markdown(
        f'<div style="font-size:0.78rem;font-weight:600;letter-spacing:1.2px;'
        f'text-transform:uppercase;color:{COLORS["text_muted"]};margin-bottom:0.9rem;">'
        f'WHAT GREENTECH DOES</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _card("🤖", "Generative AI",
              "Powered by OpenRouter / Gemini for natural-language agricultural reasoning.")
    with c2:
        _card("🌐", "Multilingual",
              "Interact in English, Telugu, Hindi, Tamil, or Kannada.")
    with c3:
        _card("🎤", "Voice Input",
              "Speak your crop problem naturally — Faster-Whisper converts speech to text.")
    with c4:
        _card("🌾", "Agricultural AI",
              "Local crop knowledge combined with AI for practical field guidance.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Language Selector ─────────────────────────────────────────────────────
    st.markdown(
        f'<div style="font-size:0.78rem;font-weight:600;letter-spacing:1.2px;'
        f'text-transform:uppercase;color:{COLORS["text_muted"]};margin-bottom:0.75rem;">'
        f'SELECT YOUR LANGUAGE</div>',
        unsafe_allow_html=True,
    )

    lang_cols = st.columns(len(LANGUAGES))
    current_lang = st.session_state.get("language", "English")

    for col, (lang_key, lang_info) in zip(lang_cols, LANGUAGES.items()):
        with col:
            is_selected = current_lang == lang_key
            label = f"✅ {lang_info['native']}" if is_selected else lang_info["native"]
            if st.button(label, key=f"lang_{lang_key}", use_container_width=True):
                st.session_state["language"] = lang_key
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How It Works ──────────────────────────────────────────────────────────
    st.markdown(
        f'<div style="font-size:0.78rem;font-weight:600;letter-spacing:1.2px;'
        f'text-transform:uppercase;color:{COLORS["text_muted"]};margin-bottom:0.9rem;">'
        f'HOW IT WORKS</div>',
        unsafe_allow_html=True,
    )

    steps = [
        ("1", "Select Language",    "Choose English, Telugu, Hindi, Tamil, or Kannada."),
        ("2", "Enter Your Problem", "Type or speak about your crop problem naturally."),
        ("3", "AI Analysis",        "AI reasons using agricultural knowledge."),
        ("4", "Get Advice",         "Receive a recommendation in your selected language."),
    ]

    for col, (num, title, desc) in zip(st.columns(4), steps):
        with col:
            st.markdown(
                f'<div style="background:{COLORS["card"]};border:1px solid {COLORS["border"]};'
                f'border-radius:10px;padding:1.1rem 1.2rem;">'
                f'<div style="font-size:1.4rem;font-weight:700;color:{COLORS["accent_primary"]};'
                f'margin-bottom:0.4rem;">{num}</div>'
                f'<div style="font-size:0.88rem;font-weight:600;color:{COLORS["text_primary"]};'
                f'margin-bottom:0.3rem;">{title}</div>'
                f'<div style="font-size:0.78rem;color:{COLORS["text_muted"]};line-height:1.5;">'
                f'{desc}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
