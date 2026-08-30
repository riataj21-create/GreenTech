"""
GreenTech - Home Page
Landing page: brand, quick intro, and a "Get Started" shortcut.
"""

import streamlit as st
from utils.config import COLORS, APP_NAME, APP_SUBTITLE, APP_TAGLINE, LANGUAGES


def _card(icon: str, title: str, body: str):
    """Render a feature highlight card."""
    st.markdown(f"""
    <div style="
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
        padding: 1.25rem 1.4rem;
        height: 100%;
    ">
        <div style="font-size: 1.6rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="
            font-size: 0.95rem;
            font-weight: 600;
            color: {COLORS['text_primary']};
            margin-bottom: 0.35rem;
        ">{title}</div>
        <div style="
            font-size: 0.82rem;
            color: {COLORS['text_muted']};
            line-height: 1.5;
        ">{body}</div>
    </div>
    """, unsafe_allow_html=True)


def render():
    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align: center; padding: 2.5rem 0 1.5rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🌿</div>
        <h1 style="
            font-size: 2.6rem;
            font-weight: 700;
            color: {COLORS['accent_primary']};
            margin: 0 0 0.3rem 0;
            letter-spacing: -0.5px;
        ">{APP_NAME}</h1>
        <p style="
            font-size: 1.05rem;
            color: {COLORS['text_secondary']};
            margin: 0 0 0.6rem 0;
        ">{APP_SUBTITLE}</p>
        <p style="
            font-size: 0.9rem;
            color: {COLORS['text_muted']};
            max-width: 520px;
            margin: 0 auto;
            line-height: 1.6;
        ">{APP_TAGLINE}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Get Started button ────────────────────────────────────────────────────
    col_l, col_btn, col_r = st.columns([2, 1.2, 2])
    with col_btn:
        if st.button("🌾  Get Started", use_container_width=True):
            st.session_state["current_page"] = "Farmer Assistant"
            st.rerun()

    # ── Weather Widget for Madanapalli ────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    
    from services.weather_service import get_current_weather, get_weather_icon_emoji, get_farming_advice_for_weather
    weather = get_current_weather()
    
    if weather["success"]:
        icon_emoji = get_weather_icon_emoji(weather["icon"])
        farming_advice = get_farming_advice_for_weather(weather)
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['card']} 0%, {COLORS['card_elevated']} 100%);
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="font-size: 2.5rem;">{icon_emoji}</div>
                <div>
                    <div style="font-size: 1.8rem; font-weight: 700; color: {COLORS['text_primary']};">
                        {weather['temperature']}°C
                    </div>
                    <div style="font-size: 0.9rem; color: {COLORS['text_muted']};">
                        📍 {weather['city']}
                    </div>
                </div>
                <div style="text-align: left;">
                    <div style="font-size: 0.85rem; color: {COLORS['text_secondary']};">
                        {weather['description']}
                    </div>
                    <div style="font-size: 0.78rem; color: {COLORS['text_muted']};">
                        Feels like {weather['feels_like']}°C
                    </div>
                    <div style="font-size: 0.78rem; color: {COLORS['text_muted']};">
                        💨 {weather['wind_speed']} m/s • 💧 {weather['humidity']}%
                    </div>
                </div>
            </div>
            
            <div style="
                background: {COLORS['bg_secondary']};
                border-radius: 8px;
                padding: 1rem;
                margin-top: 1rem;
            ">
                <div style="
                    font-size: 0.75rem;
                    color: {COLORS['accent_primary']};
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                ">🌾 Farming Advice</div>
                <div style="
                    font-size: 0.82rem;
                    color: {COLORS['text_secondary']};
                    line-height: 1.5;
                ">{farming_advice}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Weather error - show minimal message
        st.markdown(f"""
        <div style="
            background: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            margin-bottom: 1rem;
        ">
            <div style="color: {COLORS['text_muted']}; font-size: 0.85rem;">
                🌤️ Weather data for Madanapalli unavailable
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Feature cards ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: {COLORS['text_muted']};
        margin-bottom: 0.9rem;
    ">WHAT GREENTECH DOES</div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _card("🤖", "Generative AI",
              "Powered by Google Gemini for genuine natural-language agricultural reasoning.")
    with c2:
        _card("🌐", "Multilingual",
              "Interact in English, Telugu, Hindi, Tamil, or Kannada — get answers in your language.")
    with c3:
        _card("🎤", "Voice Input",
              "Speak your crop problem naturally. Faster-Whisper converts speech to text.")
    with c4:
        _card("🌾", "Agricultural AI",
              "Local crop knowledge combined with AI reasoning for practical field guidance.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Supported languages strip (functional language selector) ──────────────
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 1.2rem;
        background: {COLORS['card']};
        border: 1px solid {COLORS['border']};
        border-radius: 10px;
    ">
        <div style="
            font-size: 0.78rem;
            color: {COLORS['text_muted']};
            margin-bottom: 0.7rem;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            font-weight: 600;
        ">SELECT YOUR LANGUAGE</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Functional language selection
    col1, col2, col3, col4, col5 = st.columns(5)
    language_cols = [col1, col2, col3, col4, col5]
    
    current_lang = st.session_state.get("language", "English")
    
    for i, (lang_key, lang_info) in enumerate(LANGUAGES.items()):
        with language_cols[i]:
            # Create button with selected state styling
            is_selected = (current_lang == lang_key)
            button_style = f"""
                background: {'linear-gradient(135deg, ' + COLORS['accent_primary'] + ' 0%, ' + COLORS['success'] + ' 100%)' if is_selected else COLORS['card_elevated']};
                color: {'#0B1220' if is_selected else COLORS['text_secondary']};
                border: 1px solid {COLORS['accent_primary'] if is_selected else COLORS['border']};
                border-radius: 8px;
                padding: 0.6rem 0.4rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.2s ease;
                font-weight: {'700' if is_selected else '500'};
                font-size: 0.8rem;
                margin-bottom: 0.5rem;
            """
            
            if st.button(
                f"{'✅ ' if is_selected else ''}{lang_info['native']}", 
                key=f"lang_select_{lang_key}",
                use_container_width=True
            ):
                st.session_state["language"] = lang_key
                st.success(f"Language changed to {lang_info['native']} ({lang_key})")
                st.rerun()

    # ── Workflow steps ────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        color: {COLORS['text_muted']};
        margin-bottom: 0.9rem;
    ">HOW IT WORKS</div>
    """, unsafe_allow_html=True)

    steps = [
        ("1", "Select Language",    "Choose English, Telugu, Hindi, Tamil, or Kannada."),
        ("2", "Enter Your Problem", "Type or speak about your crop problem naturally."),
        ("3", "AI Analysis",        "Gemini reasons using agricultural knowledge and your description."),
        ("4", "Get Advice",         "Receive a structured recommendation in your selected language."),
    ]

    cols = st.columns(4)
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div style="
                background: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
                padding: 1.1rem 1.2rem;
                position: relative;
            ">
                <div style="
                    font-size: 1.4rem;
                    font-weight: 700;
                    color: {COLORS['accent_primary']};
                    margin-bottom: 0.4rem;
                ">{num}</div>
                <div style="
                    font-size: 0.88rem;
                    font-weight: 600;
                    color: {COLORS['text_primary']};
                    margin-bottom: 0.3rem;
                ">{title}</div>
                <div style="
                    font-size: 0.78rem;
                    color: {COLORS['text_muted']};
                    line-height: 1.5;
                ">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
