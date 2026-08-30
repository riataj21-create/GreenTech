"""
GreenTech - Groq Service
Primary fast provider for:
  - Text / agricultural advice  (groq/compound)
  - Audio transcription         (whisper-large-v3-turbo)
  - Translation to English      (groq/compound)

Vision is NOT supported by Groq — handled by Gemini → OpenRouter in farmer_assistant.py.

All functions return plain dicts — never raise to the caller.
API key is never returned or logged.
"""

import io
import sys
import requests

from utils.config import GROQ_API_KEY, GROQ_TEXT_MODEL, GROQ_AUDIO_MODEL, LANGUAGES

# ─── Base URL ────────────────────────────────────────────────────────────────

_BASE = "https://api.groq.com/openai/v1"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }


def groq_configured() -> bool:
    return bool(GROQ_API_KEY)


# ─── Text / Advice ────────────────────────────────────────────────────────────

def call_groq_text(prompt: str, max_tokens: int = 1500, temperature: float = 0.3) -> dict:
    """
    Send a text prompt to Groq and return the response.

    Returns:
        {"success": True,  "text": "...", "model": "..."}
        {"success": False, "error": "..."}
    """
    if not groq_configured():
        return {"success": False, "error": "Groq API key not configured."}

    try:
        r = requests.post(
            f"{_BASE}/chat/completions",
            headers=_headers(),
            json={
                "model": GROQ_TEXT_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        text = data["choices"][0]["message"]["content"].strip()
        if not text:
            return {"success": False, "error": "Groq returned an empty response."}
        return {"success": True, "text": text, "model": GROQ_TEXT_MODEL}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Groq request timed out."}
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code == 401:
            return {"success": False, "error": "Invalid Groq API key."}
        if code == 429:
            return {"success": False, "error": "Groq rate limit reached. Falling back to next provider."}
        return {"success": False, "error": f"Groq HTTP error {code}."}
    except Exception as e:
        print(f"[GreenTech groq_service] text error: {e}", file=sys.stderr)
        return {"success": False, "error": "Groq text call failed."}


# ─── Audio Transcription ──────────────────────────────────────────────────────

def transcribe_audio_groq(audio_bytes: bytes, language: str = "English") -> dict:
    """
    Transcribe audio bytes using Groq Whisper (whisper-large-v3-turbo).

    audio_bytes -- raw WAV bytes (16-bit PCM, 16 kHz, mono)
    language    -- GreenTech language name ("Telugu", "Hindi", etc.)

    Returns:
        {"success": True,  "transcript": "...", "provider": "groq"}
        {"success": False, "error": "..."}
    """
    if not groq_configured():
        return {"success": False, "error": "Groq API key not configured."}

    # Map GreenTech language name → ISO 639-1 code for Whisper
    lang_map = {
        "English": "en",
        "Telugu":  "te",
        "Hindi":   "hi",
        "Tamil":   "ta",
        "Kannada": "kn",
    }
    lang_code = lang_map.get(language, "en")

    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"

        r = requests.post(
            f"{_BASE}/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},  # no Content-Type — multipart
            files={"file": ("audio.wav", audio_file, "audio/wav")},
            data={
                "model": GROQ_AUDIO_MODEL,
                "language": lang_code,
                "response_format": "json",
            },
            timeout=30,
        )
        r.raise_for_status()
        transcript = r.json().get("text", "").strip()
        if not transcript:
            return {"success": False, "error": "Groq Whisper returned empty transcript."}
        return {"success": True, "transcript": transcript, "provider": "groq"}

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Groq Whisper timed out."}
    except requests.exceptions.HTTPError as e:
        code = e.response.status_code
        if code == 429:
            return {"success": False, "error": "Groq Whisper rate limit — falling back to local Whisper."}
        return {"success": False, "error": f"Groq Whisper HTTP error {code}."}
    except Exception as e:
        print(f"[GreenTech groq_service] audio error: {e}", file=sys.stderr)
        return {"success": False, "error": "Groq Whisper call failed."}


# ─── Translation to English ───────────────────────────────────────────────────

def translate_to_english_groq(text: str, source_language: str) -> dict:
    """
    Translate text from source_language to English using Groq.
    Used to normalise non-English voice transcripts before passing to advice.

    Returns:
        {"success": True,  "text": "<english text>"}
        {"success": False, "error": "..."}
    """
    if source_language == "English":
        return {"success": True, "text": text}

    if not groq_configured():
        return {"success": False, "error": "Groq not configured for translation."}

    prompt = (
        f"Translate the following {source_language} text to English accurately. "
        f"Return only the translated text, nothing else.\n\n{text}"
    )
    result = call_groq_text(prompt, max_tokens=500, temperature=0.1)
    if result["success"]:
        return {"success": True, "text": result["text"]}
    return result


# ─── Status check ─────────────────────────────────────────────────────────────

def check_groq_status() -> dict:
    """Quick connectivity test via a direct HTTP call."""
    if not groq_configured():
        return {"ok": False, "message": "Groq API key not configured.", "provider": "groq"}
    try:
        r = requests.get(f"{_BASE}/models",
                         headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                         timeout=8)
        if r.status_code == 200:
            return {"ok": True, "message": f"Groq connected. Model: {GROQ_TEXT_MODEL}", "provider": "groq"}
        return {"ok": False, "message": f"Groq API error {r.status_code}.", "provider": "groq"}
    except Exception as e:
        return {"ok": False, "message": f"Groq unreachable: {e}", "provider": "groq"}
