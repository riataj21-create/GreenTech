"""
GreenTech - Configuration System
Centralizes all application settings. Loads from .env if present.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists (silently skip if missing)
load_dotenv()


# ─── Application Identity ────────────────────────────────────────────────────

APP_NAME = "GreenTech"
APP_SUBTITLE = "Multilingual AI Farmer Advisory Assistant"
APP_TAGLINE = "Describe your crop problem and get practical guidance."
APP_VERSION = "1.0.0"
APP_PROBLEM_ID = "I-NXS-010"


# ─── Supported Languages ─────────────────────────────────────────────────────

LANGUAGES = {
    "English":  {"code": "en", "label": "English",  "native": "English"},
    "Telugu":   {"code": "te", "label": "Telugu",   "native": "తెలుగు"},
    "Hindi":    {"code": "hi", "label": "Hindi",    "native": "हिन्दी"},
    "Tamil":    {"code": "ta", "label": "Tamil",    "native": "தமிழ்"},
    "Kannada":  {"code": "kn", "label": "Kannada",  "native": "ಕನ್ನಡ"},
}

DEFAULT_LANGUAGE = "English"


# ─── Gemini (Phase 2) ─────────────────────────────────────────────────────────

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL:   str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")


# ─── OpenRouter (Fallback AI Provider) ────────────────────────────────────────

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL:   str = os.getenv("OPENROUTER_MODEL", "openrouter/free")


# ─── Groq (Primary fast provider — text + audio) ──────────────────────────────

GROQ_API_KEY:     str = os.getenv("GROQ_API_KEY", "")
GROQ_TEXT_MODEL:  str = os.getenv("GROQ_TEXT_MODEL", "openai/gpt-oss-120b")
GROQ_AUDIO_MODEL: str = os.getenv("GROQ_AUDIO_MODEL", "whisper-large-v3-turbo")

# Provider priority: groq → openrouter → gemini
AI_PROVIDER: str = os.getenv("AI_PROVIDER", "groq").lower()


def gemini_configured() -> bool:
    return bool(GEMINI_API_KEY)

def openrouter_configured() -> bool:
    return bool(OPENROUTER_API_KEY)

def groq_configured() -> bool:
    return bool(GROQ_API_KEY)

def ai_configured() -> bool:
    return groq_configured() or openrouter_configured() or gemini_configured()


# ─── Cloudflare Workers AI (vision) ──────────────────────────────────────────

CLOUDFLARE_API_TOKEN:    str = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ACCOUNT_ID:   str = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_VISION_MODEL: str = os.getenv("CLOUDFLARE_VISION_MODEL", "@cf/meta/llama-3.2-11b-vision-instruct")

def cloudflare_configured() -> bool:
    return bool(CLOUDFLARE_API_TOKEN) and bool(CLOUDFLARE_ACCOUNT_ID)


# ─── Weather API (Madanapalli) ───────────────────────────────────────────────

WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
WEATHER_CITY: str = os.getenv("WEATHER_CITY", "Madanapalli")
WEATHER_COUNTRY_CODE: str = os.getenv("WEATHER_COUNTRY_CODE", "IN")


def weather_configured() -> bool:
    """Return True if weather API key is configured."""
    return bool(WEATHER_API_KEY)


# ─── UI Colors ────────────────────────────────────────────────────────────────

COLORS = {
    "bg_main":        "#0B1220",
    "bg_secondary":   "#0F172A",
    "card":           "#111C2E",
    "card_elevated":  "#162238",
    "border":         "#24344D",
    "text_primary":   "#F8FAFC",
    "text_secondary": "#CBD5E1",
    "text_muted":     "#94A3B8",
    "accent_primary": "#14B8A6",
    "accent_secondary":"#38BDF8",
    "warning":        "#F59E0B",
    "success":        "#22C55E",
    "danger":         "#EF4444",
}


# ─── Paths ────────────────────────────────────────────────────────────────────

import pathlib

ROOT_DIR     = pathlib.Path(__file__).parent.parent
DATA_DIR     = ROOT_DIR / "data"
ASSETS_DIR   = ROOT_DIR / "assets"
HISTORY_FILE = DATA_DIR / "history.json"
AGRI_FILE    = DATA_DIR / "agriculture.json"
