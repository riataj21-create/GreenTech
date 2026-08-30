"""
GreenTech - Voice Service (Phase 3, revised)

Responsibilities:
  - dependency availability checks (sounddevice, faster-whisper, ffmpeg)
  - microphone device detection
  - push-to-talk audio recording via sounddevice.InputStream (no fixed time limit)
  - transcription via faster-whisper (multilingual model)
  - language-code mapping for all 5 supported languages
  - all error handling as specified in requirements §6 and §7

Architecture decisions:
  - Push-to-talk: start_recording() opens an InputStream and stores it in a
    shared _recording_state dict. The callback accumulates chunks. The UI
    calls stop_recording() when the user is done — no fixed duration limit.
  - faster-whisper accepts a raw numpy float32 array directly as `audio=`
    parameter — this completely avoids the FFmpeg requirement for recording.
  - WhisperModel is a lazy singleton — loaded once, reused across requests.
    We use the "base" model: multilingual, runs on CPU with int8 quantisation.
  - The UI must NOT contain any of this logic. All errors surface as plain
    strings in the returned dict — never as raw tracebacks.
"""

from __future__ import annotations

import os
import sys
import shutil
import threading
import time
from typing import Optional

# Suppress the HuggingFace symlink warning on Windows
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import numpy as np

from utils.config import LANGUAGES


# ─── Constants ────────────────────────────────────────────────────────────────

SAMPLE_RATE   = 16_000   # Hz — Whisper's target rate (we'll resample to this)
CHANNELS      = 1        # mono
WHISPER_MODEL = "small"  # better accuracy than base, still reasonable size
MIN_DURATION  = 0.5      # seconds — discard recordings shorter than this

WHISPER_LANG_CODES = {
    "English": "en",
    "Telugu":  "te",
    "Hindi":   "hi",
    "Tamil":   "ta",
    "Kannada": "kn",
}


# ─── Push-to-talk recording state ─────────────────────────────────────────────

_recording_state: dict = {
    "stream":  None,   # sounddevice.InputStream or None
    "chunks":  [],     # accumulated float32 frames
    "active":  False,  # True while mic is open
    "error":   "",
}
_state_lock = threading.Lock()


# ─── Lazy Whisper model ───────────────────────────────────────────────────────

_whisper_model = None
_model_lock    = threading.Lock()


def _get_whisper_model():
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    with _model_lock:
        if _whisper_model is not None:
            return _whisper_model
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise RuntimeError("faster-whisper is not installed. Run: pip install faster-whisper")
        try:
            model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
            _whisper_model = model
            return _whisper_model
        except Exception as e:
            err = str(e)
            if any(w in err.lower() for w in ("download", "connection", "http")):
                raise RuntimeError(
                    f"Could not download the Whisper '{WHISPER_MODEL}' model. "
                    "Please check your internet connection and try again."
                )
            raise RuntimeError(f"Failed to load Whisper model '{WHISPER_MODEL}': {err}")


# ─── Dependency checks ────────────────────────────────────────────────────────

def check_dependencies() -> dict:
    status = {
        "sounddevice": False, "faster_whisper": False,
        "ffmpeg": False, "microphone": False,
        "microphone_name": "", "ready": False, "message": "",
    }

    try:
        import sounddevice as sd
        status["sounddevice"] = True
    except ImportError:
        status["message"] = "sounddevice is not installed. Run: pip install sounddevice"
        return status

    try:
        from faster_whisper import WhisperModel  # noqa: F401
        status["faster_whisper"] = True
    except ImportError:
        status["message"] = "faster-whisper is not installed. Run: pip install faster-whisper"
        return status

    status["ffmpeg"] = shutil.which("ffmpeg") is not None

    try:
        import sounddevice as sd
        devices     = sd.query_devices()
        default_idx = sd.default.device[0]
        if default_idx is None or default_idx < 0:
            for i, d in enumerate(devices):
                if d["max_input_channels"] > 0:
                    default_idx = i
                    break
        if default_idx is not None and default_idx >= 0:
            d = devices[default_idx]
            if d["max_input_channels"] > 0:
                status["microphone"]      = True
                status["microphone_name"] = d["name"]
        if not status["microphone"]:
            status["message"] = "No microphone found. Please connect a microphone and try again."
            return status
    except Exception as e:
        status["message"] = f"Could not query audio devices: {e}"
        return status

    status["ready"]   = True
    status["message"] = (
        f"Voice ready. Microphone: {status['microphone_name']}. "
        f"Model: whisper/{WHISPER_MODEL}."
        + ("" if status["ffmpeg"] else " (FFmpeg not found — not required for recording.)")
    )
    return status


# ─── Push-to-talk API ─────────────────────────────────────────────────────────

def start_recording() -> dict:
    """
    Open the microphone and begin accumulating audio indefinitely.
    Returns {"success": True} or {"success": False, "error": str}.
    """
    global _recording_state

    try:
        import sounddevice as sd
    except ImportError:
        return {"success": False, "error": "sounddevice is not installed."}

    with _state_lock:
        if _recording_state["active"]:
            _stop_stream()

        _recording_state["chunks"] = []
        _recording_state["error"]  = ""
        _recording_state["active"] = False

        def _callback(indata, frames, time_info, cb_status):
            if cb_status:
                print(f"[GreenTech voice] stream status: {cb_status}", file=sys.stderr)
            with _state_lock:
                # Amplify quiet input (3x boost) and clip to prevent overflow
                amplified = np.clip(indata.copy() * 3.0, -1.0, 1.0)
                _recording_state["chunks"].append(amplified)

        try:
            # Get device info for native sample rate
            device_info = sd.query_devices(device=None, kind='input')
            native_rate = int(device_info['default_samplerate'])
            print(f"[GreenTech voice] Using native rate: {native_rate}Hz", file=sys.stderr)
            
            stream = sd.InputStream(
                samplerate=native_rate,  # Use native rate, resample later
                channels=CHANNELS,
                dtype="float32",
                callback=_callback,
            )
            stream.start()
            _recording_state["stream"] = stream
            _recording_state["native_rate"] = native_rate
            _recording_state["active"] = True
            return {"success": True}

        except sd.PortAudioError as e:
            err = str(e)
            if "permission" in err.lower() or "access" in err.lower():
                return {"success": False,
                        "error": "Microphone access was denied. Please allow microphone access and try again."}
            return {"success": False, "error": f"Could not open microphone: {err}"}
        except Exception as e:
            return {"success": False, "error": f"Could not start recording: {e}"}


def _stop_stream() -> Optional[np.ndarray]:
    """Internal: stop stream and return concatenated audio, or None."""
    stream = _recording_state.get("stream")
    chunks = list(_recording_state.get("chunks", []))
    native_rate = _recording_state.get("native_rate", SAMPLE_RATE)

    if stream is not None:
        try:
            stream.stop()
            stream.close()
        except Exception:
            pass
        _recording_state["stream"] = None

    _recording_state["active"] = False
    _recording_state["chunks"] = []

    if not chunks:
        return None
        
    # Concatenate all chunks
    audio = np.concatenate(chunks, axis=0).flatten()
    
    # Resample to 16kHz if needed
    if native_rate != SAMPLE_RATE:
        try:
            from scipy.signal import resample
            target_length = int(len(audio) * SAMPLE_RATE / native_rate)
            audio = resample(audio, target_length).astype(np.float32)
            print(f"[GreenTech voice] Resampled from {native_rate}Hz to {SAMPLE_RATE}Hz", file=sys.stderr)
        except ImportError:
            print(f"[GreenTech voice] Warning: scipy not available for resampling. Using audio as-is.", file=sys.stderr)
    
    return audio


def stop_recording() -> dict:
    """
    Stop the microphone and return the captured audio.
    Returns {"success": True, "audio": ndarray, "duration": float}
         or {"success": False, "error": str}
    """
    with _state_lock:
        audio = _stop_stream()

    if audio is None or len(audio) == 0:
        return {"success": False, "error": "No audio was captured. Please try again."}

    duration = len(audio) / SAMPLE_RATE
    if duration < MIN_DURATION:
        return {"success": False,
                "error": "Recording was too short. Please speak for at least half a second."}

    rms = float(np.sqrt(np.mean(audio ** 2)))
    if rms < 1e-6:
        return {"success": False,
                "error": "No audio detected. Please check your microphone and try again."}

    return {"success": True, "audio": audio, "duration": round(duration, 1)}


def is_recording() -> bool:
    """Return True if the microphone is currently open."""
    return _recording_state.get("active", False)


# ─── Telugu text post-processing ─────────────────────────────────────────────

def _clean_telugu_text(text: str) -> str:
    """Clean up Telugu transcription artifacts like repeated characters."""
    import re
    
    if not text:
        return text
    
    # Remove excessive character repetitions (more than 3 of same character)
    # Example: "సార్ల్ల్ల్ల్ల్" → "సార్లు"
    cleaned = re.sub(r'(.)\1{3,}', r'\1', text)
    
    # Remove excessive word repetitions  
    words = cleaned.split()
    deduplicated_words = []
    prev_word = ""
    repeat_count = 0
    
    for word in words:
        if word == prev_word:
            repeat_count += 1
            if repeat_count < 2:  # Allow max 1 repetition
                deduplicated_words.append(word)
        else:
            deduplicated_words.append(word)
            repeat_count = 0
        prev_word = word
    
    result = " ".join(deduplicated_words).strip()
    
    # If text is mostly repetitive characters (>50% repetition), reject it
    if len(result) > 0:
        unique_chars = len(set(result.replace(" ", "")))
        total_chars = len(result.replace(" ", ""))
        if total_chars > 10 and unique_chars / total_chars < 0.3:
            return ""  # Return empty to trigger "no speech detected"
    
    return result


# ─── Transcription ────────────────────────────────────────────────────────────

def transcribe_audio(audio: np.ndarray, language: str = "English") -> dict:
    """Transcribe float32 audio array with faster-whisper."""
    lang_code = WHISPER_LANG_CODES.get(language, "en")

    try:
        model = _get_whisper_model()
    except RuntimeError as e:
        return {"success": False, "error": str(e)}

    try:
        # Language-specific optimization - Telugu needs special handling
        if language == "Telugu":
            # Telugu-specific parameters to avoid garbled output
            vad_params = {"min_silence_duration_ms": 600}  # Longer silence for Telugu phonetics
            beam_size = 4  # Reduced beam size for more conservative decoding
            patience = 1.0  # Standard patience to avoid over-processing
            temperature = [0.0, 0.2]  # Try multiple temperatures for Telugu
            best_of = 2  # Reduced attempts for cleaner output
        elif language in ["Hindi", "Tamil", "Kannada"]:
            # Other Indian languages: balanced parameters
            vad_params = {"min_silence_duration_ms": 400}
            beam_size = 6
            patience = 1.5
            temperature = 0.0
            best_of = 3
        else:
            # English and other languages - optimized for speed
            vad_params = {"min_silence_duration_ms": 300}
            beam_size = 5
            patience = 1.0
            temperature = 0.0
            best_of = 3

        segments, info = model.transcribe(
            audio=audio,
            language=lang_code,
            beam_size=beam_size,
            best_of=best_of,
            patience=patience,
            temperature=temperature,
            condition_on_previous_text=False,  # Avoid context bleeding
            vad_filter=True,
            vad_parameters=vad_params,
            word_timestamps=False,  # Focus on accuracy over timestamps
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        
        # Post-process Telugu text to clean up repetitions
        if language == "Telugu" and text:
            text = _clean_telugu_text(text)
            
            # If Telugu cleaning resulted in empty/poor text, try English transcription as fallback
            if not text or len(text.strip()) < 5:
                print(f"[GreenTech voice_service] Telugu transcription poor, trying English fallback", file=sys.stderr)
                try:
                    # Retry with English language code
                    segments_en, info_en = model.transcribe(
                        audio=audio,
                        language="en",
                        beam_size=5,
                        best_of=3,
                        patience=1.0,
                        temperature=0.0,
                        condition_on_previous_text=False,
                        vad_filter=True,
                        vad_parameters={"min_silence_duration_ms": 300},
                        word_timestamps=False,
                    )
                    english_text = " ".join(seg.text.strip() for seg in segments_en).strip()
                    if english_text and len(english_text) > len(text):
                        text = english_text
                        print(f"[GreenTech voice_service] Using English fallback transcription for Telugu", file=sys.stderr)
                except Exception as e:
                    print(f"[GreenTech voice_service] English fallback failed: {e}", file=sys.stderr)
    except Exception as e:
        err = str(e)
        print(f"[GreenTech voice_service] transcription error: {err}", file=sys.stderr)
        if "ffmpeg" in err.lower():
            return {"success": False,
                    "error": ("FFmpeg is not installed. "
                              "Install from https://ffmpeg.org/download.html and add to PATH.")}
        return {"success": False, "error": f"Transcription failed: {err}"}

    if not text:
        return {"success": False,
                "error": "No speech detected. Please speak clearly and try again."}

    return {"success": True, "transcript": text, "language": language, "language_code": lang_code}


# ─── Legacy blocking pipeline (kept for test_phase3.py compatibility) ─────────

def record_audio(duration_seconds: int = 5) -> dict:
    """Blocking record. Tests use this; UI uses push-to-talk instead."""
    duration_seconds = max(1, min(duration_seconds, 60))
    r = start_recording()
    if not r["success"]:
        return r
    time.sleep(duration_seconds)
    return stop_recording()


def record_and_transcribe(duration_seconds: int = 5, language: str = "English") -> dict:
    """Blocking record + transcribe. Kept for test compatibility."""
    rec = record_audio(duration_seconds)
    if not rec["success"]:
        return rec
    return transcribe_audio(rec["audio"], language)


# ─── Status ───────────────────────────────────────────────────────────────────

def get_voice_status() -> dict:
    deps = check_dependencies()
    return {
        "ready":   deps["ready"],
        "message": deps["message"],
        "model":   f"whisper/{WHISPER_MODEL}" if deps["faster_whisper"] else "not installed",
        "mic":     deps["microphone_name"],
        "ffmpeg":  deps["ffmpeg"],
    }
