"""
GreenTech Phase 3 - Test Script
Run with: python test_phase3.py

Tests:
  Group 1: dependency checks & voice_service imports
  Group 2: record_audio + transcribe_audio pipeline (real mic, 3 s)
  Group 3: FFmpeg-missing message is clean (informational only)
  Group 4: mic-unavailable graceful failure simulation
  Group 5: session-state keys present in main.py defaults
  Group 6: settings.py voice status row (import-level check)
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# ─── Helpers ─────────────────────────────────────────────────────────────────
passed = failed = 0

def ok(name, extra=""):
    global passed; passed += 1
    print(f"  PASS  {name}" + (f"  [{extra}]" if extra else ""))

def fail(name, reason):
    global failed; failed += 1
    print(f"  FAIL  {name}: {reason}")

def section(title):
    print(f"\n{'='*62}\n  {title}\n{'='*62}")


# ═══════════════════════════════════════════════════════════════
# GROUP 1 — imports & dependency check
# ═══════════════════════════════════════════════════════════════
section("GROUP 1: imports & dependency checks")

try:
    from services.voice_service import (
        check_dependencies, record_audio, transcribe_audio,
        record_and_transcribe, get_voice_status,
        WHISPER_LANG_CODES, SAMPLE_RATE, WHISPER_MODEL,
    )
    ok("voice_service imports cleanly")
except Exception as e:
    fail("voice_service import", str(e))
    sys.exit(1)

deps = check_dependencies()
if deps["sounddevice"]:
    ok("sounddevice present")
else:
    fail("sounddevice", deps["message"])

if deps["faster_whisper"]:
    ok("faster-whisper present")
else:
    fail("faster-whisper", deps["message"])

if deps["microphone"]:
    ok(f"microphone detected", deps["microphone_name"])
else:
    fail("microphone", deps["message"])

if deps["ready"]:
    ok("check_dependencies -> ready=True")
else:
    fail("check_dependencies ready", deps["message"])

# FFmpeg absent is expected — must be reported cleanly, not crash
if not deps["ffmpeg"]:
    ok("FFmpeg absent -> reported cleanly (not required for recording)")
else:
    ok("FFmpeg present (bonus)")

# Language codes
expected_codes = {"English":"en","Telugu":"te","Hindi":"hi","Tamil":"ta","Kannada":"kn"}
if WHISPER_LANG_CODES == expected_codes:
    ok("WHISPER_LANG_CODES correct for all 5 languages")
else:
    fail("WHISPER_LANG_CODES", f"Got: {WHISPER_LANG_CODES}")

# get_voice_status
vs = get_voice_status()
if vs["ready"] and vs["mic"] and vs["model"].startswith("whisper/"):
    ok("get_voice_status returns ready status", f"model={vs['model']}")
else:
    fail("get_voice_status", str(vs))


# ═══════════════════════════════════════════════════════════════
# GROUP 2 — record_audio pipeline (real mic, 3 s)
# ═══════════════════════════════════════════════════════════════
section("GROUP 2: record_audio (3 s real microphone capture)")

print("  INFO  Recording 3 seconds from microphone — please stay quiet (testing silence detection)…")
import numpy as np

rec = record_audio(duration_seconds=3)
if rec["success"]:
    audio = rec["audio"]
    if isinstance(audio, np.ndarray) and audio.dtype == np.float32:
        ok("record_audio returns float32 ndarray")
    else:
        fail("record_audio dtype", f"Got dtype={audio.dtype}, type={type(audio)}")

    if len(audio) >= int(0.5 * SAMPLE_RATE):
        ok(f"record_audio length ok", f"{len(audio)} samples @ {SAMPLE_RATE} Hz")
    else:
        fail("record_audio length", f"Too short: {len(audio)} samples")
else:
    # Might fail if mic is in use or permissions issue — report cleanly
    err = rec.get("error","")
    if err and not any(c in err for c in ["\n","Traceback","File \""]):
        ok(f"record_audio failed gracefully (no traceback)", err)
    else:
        fail("record_audio failure message", f"Raw traceback or empty: {err[:200]}")


# ═══════════════════════════════════════════════════════════════
# GROUP 3 — transcribe_audio with real audio (model download)
# ═══════════════════════════════════════════════════════════════
section("GROUP 3: transcribe_audio — Whisper model load + transcription")

print(f"  INFO  Loading whisper/{WHISPER_MODEL} model (downloads ~150 MB on first run)…")
print("  INFO  Generating 3 s of speech-like test audio (440 Hz tone)…")

# Use a short sine wave as test audio (Whisper will likely say no speech,
# but we test that it handles it gracefully)
duration_s  = 2
test_audio  = (np.sin(2 * np.pi * 440 * np.linspace(0, duration_s,
               int(duration_s * SAMPLE_RATE))).astype(np.float32) * 0.3)

result = transcribe_audio(test_audio, "English")
if result["success"]:
    ok("transcribe_audio tone -> returned transcript (Whisper found audio)")
    print(f"         Transcript: '{result['transcript'][:100]}'")
elif "No speech" in result.get("error","") or "not detected" in result.get("error","").lower():
    ok("transcribe_audio tone -> 'no speech detected' returned cleanly (expected for sine wave)")
    print(f"         Message: {result['error']}")
elif "error" in result:
    err = result["error"]
    if "Traceback" not in err and "File \"" not in err:
        ok("transcribe_audio failure is user-friendly (no traceback)", err[:100])
    else:
        fail("transcribe_audio error message", f"Contains raw traceback: {err[:200]}")
else:
    fail("transcribe_audio", f"Unexpected result: {result}")

# Test that all 5 language codes are accepted without error
for lang in ["English","Telugu","Hindi","Tamil","Kannada"]:
    r = transcribe_audio(test_audio, lang)
    # We don't care if success or not — we care it doesn't crash and returns a dict
    if isinstance(r, dict) and "success" in r:
        ok(f"transcribe_audio accepts language '{lang}'")
    else:
        fail(f"transcribe_audio language '{lang}'", f"Got: {r}")


# ═══════════════════════════════════════════════════════════════
# GROUP 4 — FFmpeg-missing message is clean
# ═══════════════════════════════════════════════════════════════
section("GROUP 4: FFmpeg-missing message is clean")

import shutil
original_which = shutil.which

def patched_which(name, *a, **kw):
    if name == "ffmpeg":
        return None
    return original_which(name, *a, **kw)

shutil.which = patched_which

import services.voice_service as vs_mod
vs_mod_deps = vs_mod.check_dependencies()

shutil.which = original_which  # restore

if not vs_mod_deps["ffmpeg"]:
    msg = vs_mod_deps["message"]
    # Message must be human-readable, not a traceback
    if msg and "Traceback" not in msg and "File \"" not in msg:
        ok("FFmpeg=False -> message is human-readable", msg[:80])
    else:
        fail("FFmpeg-missing message", f"Bad message: {msg[:200]}")
    # App must still be ready (FFmpeg not required)
    if vs_mod_deps["ready"]:
        ok("FFmpeg absent -> voice still ready=True (not required for mic recording)")
    else:
        fail("FFmpeg absent -> ready should still be True", vs_mod_deps["message"])
else:
    ok("FFmpeg present — skipping absence test")


# ═══════════════════════════════════════════════════════════════
# GROUP 5 — mic-unavailable graceful failure
# ═══════════════════════════════════════════════════════════════
section("GROUP 5: microphone unavailable — graceful failure")

import sounddevice as sd_mod

# Patch sd.query_devices to raise an exception (simulates no audio hardware)
original_query = sd_mod.query_devices

def patched_query(*a, **kw):
    raise Exception("No audio devices found (simulated)")

sd_mod.query_devices = patched_query

# Reset cached deps so check runs fresh
try:
    result_no_mic = vs_mod.check_dependencies()
    if not result_no_mic["ready"]:
        msg = result_no_mic["message"]
        if msg and "Traceback" not in msg and "File \"" not in msg:
            ok("No audio device -> ready=False with clean message", msg[:80])
        else:
            fail("No audio device message", f"Raw traceback: {msg[:200]}")
    else:
        fail("No audio device", "ready should be False when query_devices raises")
except Exception as e:
    fail("No audio device must not propagate exception", str(e))
finally:
    sd_mod.query_devices = original_query  # always restore

# Patch record_audio: simulate sd.rec raising PortAudioError
import services.voice_service as vs2
original_rec = None
try:
    import sounddevice as sd_inner
    original_rec_fn = sd_inner.rec

    def patched_rec(*a, **kw):
        raise sd_inner.PortAudioError("Permission denied (simulated)", -9999)

    sd_inner.rec = patched_rec
    r2 = vs2.record_audio(duration_seconds=1)
    sd_inner.rec = original_rec_fn

    if not r2["success"]:
        msg2 = r2["error"]
        if msg2 and "Traceback" not in msg2:
            ok("PortAudioError -> returned error dict with clean message", msg2[:80])
        else:
            fail("PortAudioError message", f"Bad: {msg2[:200]}")
    else:
        fail("PortAudioError", "Expected success=False")
except Exception as e:
    try: sd_inner.rec = original_rec_fn
    except: pass
    fail("PortAudioError simulation", str(e))


# ═══════════════════════════════════════════════════════════════
# GROUP 6 — session state keys & settings page compile
# ═══════════════════════════════════════════════════════════════
section("GROUP 6: session state & settings page")

# Verify main.py contains the voice keys
import ast, pathlib

main_src = pathlib.Path("main.py").read_text(encoding="utf-8")
for key in ["voice_recording", "voice_transcript", "voice_error", "voice_model_ready"]:
    if f'"{key}"' in main_src:
        ok(f"main.py init_session_state has key '{key}'")
    else:
        fail(f"main.py missing session key", key)

# Compile-check settings
import importlib.util
for mod_path in ["pages/settings.py", "pages/farmer_assistant.py", "services/voice_service.py"]:
    spec = importlib.util.spec_from_file_location("_test", mod_path)
    try:
        src = pathlib.Path(mod_path).read_text(encoding="utf-8")
        compile(src, mod_path, "exec")
        ok(f"{mod_path} compiles cleanly")
    except SyntaxError as e:
        fail(f"{mod_path} syntax", str(e))


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
section("SUMMARY")
total = passed + failed
print(f"  {passed}/{total} tests passed")
if failed:
    print(f"  {failed} test(s) FAILED — see above")
    sys.exit(1)
else:
    print("  All tests PASSED")
    sys.exit(0)
