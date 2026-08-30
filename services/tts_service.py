"""
GreenTech - TTS Service (Phase 4)

Responsibilities:
  - detect installed Windows SAPI voices
  - map GreenTech languages to available system voices
  - speak text in a daemon thread (non-blocking for Streamlit)
  - stop ongoing speech
  - report status cleanly when a language voice is unavailable
  - never crash the application

Architecture:
  - pyttsx3 wraps Windows SAPI (sapi5 driver)
  - Engine is re-created per speak() call: pyttsx3 engines are NOT thread-safe
    and keeping one alive across Streamlit reruns causes COM errors on Windows.
  - Speech runs in a daemon thread so Streamlit's main thread is never blocked.
  - A threading.Event signals the thread to stop early if requested.

Language-to-voice mapping strategy (Windows):
  - We match installed voice names/IDs against BCP-47 language codes.
  - English  → any en-US / en-GB voice (always present on Win10/11)
  - Telugu   → te-IN voice ID substring
  - Hindi    → hi-IN voice ID substring
  - Tamil    → ta-IN voice ID substring
  - Kannada  → kn-IN voice ID substring
  - If no matching voice: return unavailable=True with a clear message.
    The application MUST NOT crash — it simply reports the voice is missing.
"""

from __future__ import annotations

import sys
import threading
from typing import Optional

# BCP-47 substrings to search for in SAPI voice IDs / names
_LANG_VOICE_HINTS: dict[str, list[str]] = {
    "English": ["en-us", "en-gb", "en_us", "en_gb", "english"],
    "Telugu":  ["te-in", "te_in", "telugu"],
    "Hindi":   ["hi-in", "hi_in", "hindi"],
    "Tamil":   ["ta-in", "ta_in", "tamil"],
    "Kannada": ["kn-in", "kn_in", "kannada"],
}

# How to install Indian language voices on Windows 10/11
_INSTALL_GUIDE = (
    "To add {language} voice on Windows: "
    "Settings → Time & Language → Speech → Add voices → search for {language}."
)

# Active speech thread (only one at a time)
_speech_thread: Optional[threading.Thread] = None
_stop_event    = threading.Event()
_current_engine: Optional = None  # Reference to active engine for forced stop


# ─── Voice catalogue ──────────────────────────────────────────────────────────

def _get_all_voices() -> list[dict]:
    """
    Return list of dicts describing all installed SAPI voices.
    Each dict: {"id": str, "name": str, "id_lower": str, "name_lower": str}
    Returns [] if pyttsx3 is not available or SAPI fails.
    """
    try:
        import pyttsx3
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        result = []
        for v in voices:
            vid  = v.id   or ""
            name = v.name or ""
            result.append({
                "id":         vid,
                "name":       name,
                "id_lower":   vid.lower(),
                "name_lower": name.lower(),
            })
        engine.stop()
        return result
    except Exception as e:
        print(f"[GreenTech tts_service] Could not enumerate voices: {e}", file=sys.stderr)
        return []


def _find_voice_for_language(language: str) -> Optional[dict]:
    """
    Find the best installed SAPI voice for the given GreenTech language name.
    Returns the voice dict, or None if no matching voice is installed.
    """
    hints   = _LANG_VOICE_HINTS.get(language, [])
    voices  = _get_all_voices()

    for voice in voices:
        combined = voice["id_lower"] + " " + voice["name_lower"]
        for hint in hints:
            if hint in combined:
                return voice

    return None


# ─── Public API ───────────────────────────────────────────────────────────────

def get_tts_status(language: str = "English") -> dict:
    """
    Check TTS availability for the given language.

    Returns:
        {
            "available":       bool,   # True if a matching voice is installed
            "voice_name":      str,    # name of the matched voice, or ""
            "message":         str,    # human-readable status
            "install_guide":   str,    # how to install the voice (if unavailable)
            "pyttsx3_present": bool,
        }
    """
    try:
        import pyttsx3  # noqa: F401
        pyttsx3_ok = True
    except ImportError:
        return {
            "available":       False,
            "voice_name":      "",
            "message":         "pyttsx3 is not installed. Run: pip install pyttsx3",
            "install_guide":   "",
            "pyttsx3_present": False,
        }

    voice = _find_voice_for_language(language)
    if voice:
        return {
            "available":       True,
            "voice_name":      voice["name"],
            "message":         f"Voice available: {voice['name']}",
            "install_guide":   "",
            "pyttsx3_present": True,
        }
    else:
        # Enhanced guidance for Indian language voice installation
        if language == "English":
            guide = "English voices should be pre-installed on Windows. Please check your system audio settings."
        else:
            guide = (
                f"Install {language} voice: Windows Settings → Time & Language → "
                f"Speech → Manage voices → Add voices → Download {language}. "
                f"Restart GreenTech after installation."
            )
        
        all_voices = _get_all_voices()
        if len(all_voices) <= 2:  # Very few voices - likely missing language packs
            names = "Basic system voices only"
            guide += f" Current voices suggest language packs may not be installed."
        else:
            names = ", ".join(v["name"] for v in all_voices[:3])  # Show first 3 to avoid clutter
            if len(all_voices) > 3:
                names += f" (and {len(all_voices) - 3} more)"
        
        return {
            "available":       False,
            "voice_name":      "",
            "message":         (
                f"{language} voice not found. "
                f"Available voices: {names}."
            ),
            "install_guide":   guide,
            "pyttsx3_present": True,
        }


def speak(text: str, language: str = "English") -> dict:
    """
    Speak `text` using the best available voice for `language`.
    Falls back to English voice if requested language unavailable.
    Runs in a daemon thread — returns immediately.

    Returns:
        {"success": True,  "voice": voice_name}           — speech started
        {"success": False, "error": str,
         "install_guide": str}                             — unavailable or error
    """
    global _speech_thread, _stop_event, _current_engine

    if not text or not text.strip():
        return {"success": False, "error": "No text to speak."}

    # Check voice availability first
    status = get_tts_status(language)
    if status["available"]:
        voice_id = _find_voice_for_language(language)["id"]
        voice_name = status["voice_name"]
    else:
        # Fallback to English for Indian languages if not available
        if language in ["Telugu", "Hindi", "Tamil", "Kannada"]:
            english_status = get_tts_status("English")
            if english_status["available"]:
                voice_id = _find_voice_for_language("English")["id"]
                voice_name = f"{english_status['voice_name']} (English fallback)"
            else:
                return {
                    "success":       False,
                    "error":         f"Neither {language} nor English voice available",
                    "install_guide": status["install_guide"],
                }
        else:
            return {
                "success":       False,
                "error":         status["message"],
                "install_guide": status["install_guide"],
            }

    # Stop any ongoing speech before starting new
    stop()

    # Reset stop event
    _stop_event = threading.Event()
    local_stop  = _stop_event

    def _speak_thread():
        global _current_engine
        try:
            import pyttsx3
            engine = pyttsx3.init()
            _current_engine = engine  # Store reference for forced stop
            
            engine.setProperty("voice",  voice_id)
            engine.setProperty("rate",   155)   # words per minute — clear, not rushed
            engine.setProperty("volume", 1.0)

            # Trim text: Whisper / Gemini responses can be very long.
            # Speak up to ~1 000 words to stay practical.
            words     = text.split()
            max_words = 1000
            spoken    = " ".join(words[:max_words])
            if len(words) > max_words:
                spoken += " … response truncated for speech."

            # Check stop before starting
            if local_stop.is_set():
                engine.stop()
                _current_engine = None
                return

            # Split text into smaller chunks to allow more responsive stopping
            sentences = spoken.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
            
            for sentence in sentences:
                if local_stop.is_set():
                    break
                
                sentence = sentence.strip()
                if sentence:
                    engine.say(sentence)
                    engine.runAndWait()
                    
                    # Small delay to check stop signal between sentences
                    if local_stop.is_set():
                        break

            engine.stop()
            _current_engine = None

        except Exception as e:
            # Never surface raw tracebacks — log to stderr only
            print(f"[GreenTech tts_service speak error] {e}", file=sys.stderr)
            _current_engine = None

    _speech_thread = threading.Thread(target=_speak_thread, daemon=True)
    _speech_thread.start()

    return {"success": True, "voice": voice_name}


def stop() -> None:
    """Signal any running speech thread to stop and force-stop the engine if needed."""
    global _speech_thread, _stop_event, _current_engine
    
    _stop_event.set()
    
    # Try to force-stop the current engine
    if _current_engine is not None:
        try:
            _current_engine.stop()
        except Exception as e:
            print(f"[GreenTech tts_service] Force stop error: {e}", file=sys.stderr)
    
    if _speech_thread and _speech_thread.is_alive():
        _speech_thread.join(timeout=2.0)  # Give it slightly more time to cleanup
        
    _speech_thread = None
    _current_engine = None


def is_speaking() -> bool:
    """Return True if a speech thread is currently active."""
    return _speech_thread is not None and _speech_thread.is_alive()


def can_speak(language: str = "English") -> bool:
    """
    Check if TTS is available for the language, including English fallback.
    Returns True if speech is possible (native voice or English fallback).
    """
    status = get_tts_status(language)
    if status["available"]:
        return True
    
    # Check English fallback for Indian languages
    if language in ["Telugu", "Hindi", "Tamil", "Kannada"]:
        english_status = get_tts_status("English")
        return english_status["available"]
    
    return False


def list_installed_voices() -> list[str]:
    """Return a list of installed voice names (for display in Settings)."""
    return [v["name"] for v in _get_all_voices()]
