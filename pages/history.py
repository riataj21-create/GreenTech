"""
GreenTech - History Page (Phase 5)

Features:
  - reads from persistent JSON via storage.get_history()
  - newest entry shown first
  - search / filter by crop name
  - input-method badge (text / voice)
  - language badge
  - expandable advice viewer
  - clear all (calls storage.clear_history() → deletes file)
  - jump-to Farmer Assistant when empty
"""

import streamlit as st
from utils.config import COLORS
from utils.storage import get_history, clear_history, history_file_path


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _badge(label: str, bg: str, fg: str = "#0B1220") -> str:
    return (
        f"<span style='background:{bg};color:{fg};font-size:0.7rem;"
        f"font-weight:600;padding:0.15rem 0.55rem;border-radius:20px;"
        f"letter-spacing:0.4px;'>{label}</span>"
    )


def _method_badge(method: str) -> str:
    if method == "voice":
        return _badge("🎤 voice", COLORS["accent_secondary"] + "33", COLORS["accent_secondary"])
    return _badge("⌨ text", COLORS["border"], COLORS["text_secondary"])


def _lang_badge(language: str) -> str:
    return _badge(language, COLORS["accent_primary"] + "22", COLORS["accent_primary"])


# ─── Main render ──────────────────────────────────────────────────────────────

def render():
    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(
        f"<div style='margin-bottom:1.5rem;'>"
        f"<h2 style='font-size:1.55rem;font-weight:700;"
        f"color:{COLORS['text_primary']};margin:0 0 0.3rem 0;'>📋 History</h2>"
        f"<p style='font-size:0.88rem;color:{COLORS['text_muted']};margin:0;'>"
        f"Your previous advisory sessions — saved locally and persistent across restarts."
        f"</p></div>",
        unsafe_allow_html=True,
    )

    history: list = get_history()

    # ── Empty state ───────────────────────────────────────────────────────────
    if not history:
        st.markdown(
            f"<div style='background:{COLORS['card']};border:1px solid {COLORS['border']};"
            f"border-radius:12px;padding:3rem 2rem;text-align:center;'>"
            f"<div style='font-size:2.5rem;margin-bottom:0.8rem;'>📋</div>"
            f"<div style='font-size:1rem;font-weight:600;"
            f"color:{COLORS['text_secondary']};margin-bottom:0.4rem;'>No history yet</div>"
            f"<div style='font-size:0.84rem;color:{COLORS['text_muted']};'>"
            f"Your advisory sessions will appear here after you use the Farmer Assistant."
            f"</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        col_l, col_btn, col_r = st.columns([2, 1.6, 2])
        with col_btn:
            if st.button("🌾  Go to Farmer Assistant", use_container_width=True, key="hist_goto_btn"):
                st.session_state["current_page"] = "Farmer Assistant"
                st.rerun()
        return

    # ── Toolbar: search + count + clear ──────────────────────────────────────
    col_search, col_spacer, col_clear = st.columns([2.5, 0.5, 1])

    with col_search:
        search = st.text_input(
            "Search",
            placeholder="Filter by crop name…",
            label_visibility="collapsed",
            key="hist_search_input",
        )

    with col_clear:
        if st.button("🗑  Clear All", key="hist_clear_btn", use_container_width=True):
            clear_history()
            st.success("History cleared.", icon="✅")
            st.rerun()

    # Apply search filter
    query = search.strip().lower()
    filtered = (
        [e for e in history if query in e.get("crop", "").lower()
         or query in e.get("problem", "").lower()]
        if query else history
    )

    # Count line
    total_shown = len(filtered)
    total_all   = len(history)
    count_text  = (
        f"{total_shown} of {total_all} session{'s' if total_all != 1 else ''}"
        if query else
        f"{total_all} session{'s' if total_all != 1 else ''} stored"
    )
    st.markdown(
        f"<div style='font-size:0.8rem;color:{COLORS['text_muted']};"
        f"margin:0.4rem 0 0.9rem 0;'>{count_text}"
        f"  ·  <span style='color:{COLORS['text_muted']};font-size:0.72rem;'>"
        f"📁 {history_file_path()}</span></div>",
        unsafe_allow_html=True,
    )

    if not filtered:
        st.markdown(
            f"<div style='color:{COLORS['text_muted']};font-size:0.88rem;"
            f"padding:1rem 0;'>No sessions match <strong>{search}</strong>.</div>",
            unsafe_allow_html=True,
        )
        return

    # ── Entry list (newest first) ─────────────────────────────────────────────
    for idx, entry in enumerate(reversed(filtered)):
        crop      = entry.get("crop", "Unknown crop")
        timestamp = entry.get("timestamp", "")
        language  = entry.get("language", "English")
        method    = entry.get("input_method", "text")
        problem   = entry.get("problem", "")
        advice    = entry.get("advice", "")

        # Build expander label
        label = f"[{timestamp}]  {crop}"

        with st.expander(label, expanded=(idx == 0)):

            # Badges row
            badges = _method_badge(method) + "  " + _lang_badge(language)
            st.markdown(
                f"<div style='margin-bottom:0.75rem;display:flex;gap:0.4rem;"
                f"align-items:center;flex-wrap:wrap;'>{badges}</div>",
                unsafe_allow_html=True,
            )

            # Problem
            st.markdown(
                f"<div style='font-size:0.78rem;font-weight:600;"
                f"color:{COLORS['text_muted']};letter-spacing:0.6px;"
                f"text-transform:uppercase;margin-bottom:0.3rem;'>PROBLEM</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div style='background:{COLORS['card_elevated']};"
                f"border:1px solid {COLORS['border']};border-radius:8px;"
                f"padding:0.75rem 1rem;font-size:0.86rem;"
                f"color:{COLORS['text_secondary']};line-height:1.6;"
                f"margin-bottom:0.9rem;'>{problem}</div>",
                unsafe_allow_html=True,
            )

            # Advice
            if advice:
                st.markdown(
                    f"<div style='font-size:0.78rem;font-weight:600;"
                    f"color:{COLORS['text_muted']};letter-spacing:0.6px;"
                    f"text-transform:uppercase;margin-bottom:0.3rem;'>AI ADVICE</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='background:{COLORS['card']};"
                    f"border:1px solid {COLORS['accent_primary']}33;"
                    f"border-radius:8px;padding:0.9rem 1rem;"
                    f"font-size:0.84rem;color:{COLORS['text_secondary']};"
                    f"line-height:1.7;white-space:pre-wrap;'>{advice}</div>",
                    unsafe_allow_html=True,
                )

            # Re-use button: pre-fill Farmer Assistant
            st.markdown("<div style='margin-top:0.7rem;'></div>", unsafe_allow_html=True)
            col_reuse, col_spacer2 = st.columns([1.2, 3])
            with col_reuse:
                if st.button(
                    "↩  Ask again",
                    key=f"hist_reuse_{idx}",
                    use_container_width=True,
                ):
                    # Pre-fill crop and clear previous advice so the user
                    # can type a new problem (or reuse the old one manually)
                    st.session_state["current_page"] = "Farmer Assistant"
                    # Clear stale widget state so text inputs reset
                    for k in ["fa_crop_input", "fa_problem_input"]:
                        st.session_state.pop(k, None)
                    st.session_state["advice_result"] = None
                    st.rerun()
