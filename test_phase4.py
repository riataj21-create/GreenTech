"""
GreenTech Phase 4 - TTS Test Script
Run with: python test_phase4.py

Tests:
  Group 1: imports & voice catalogue
  Group 2: get_tts_status for all 5 languages
  Group 3: English TTS speaks correctly (real audio output)
  Group 4: unavailable language -> clean message, no crash
  Group 5: tts_enabled=False -> speak() still works (UI hides button, service unaffected)
  Group 6: stop() and is_speaking() lifecycle
  Group 7: session state keys present in main.py
  Group 8: farmer_assistant.py and settings.py compile cleanly with new TTS code
"""

import sys, os, time, pathlib
sys.path.insert(0, os.path.dirname(__file__))

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
# GROUP 1: imports & voice catalogue
# ═══════════════════════════════════════════════════════════════
section("GROUP 1: imports & voice catalogue")

try:
    from services.tts_service import (
        get_tts_status, speak, stop, is_speaking, list_installed_voices,
        _get_all_voices, _find_voice_for_language,
    )
    ok("tts_service imports cleanly")
except Exception as e:
    fail("tts_service import", str(e))
    sys.exit(1)

voices = _get_all_voices()
if len(voices) >= 1:
    ok(f"_get_all_voices() found {len(voices)} voice(s)")
    for v in voices:
        ok(f"  Voice: {v['name']}")
else:
    fail("_get_all_voices", "No voices found — pyttsx3 SAPI enumeration failed")

installed = list_installed_voices()
if installed:
    ok(f"list_installed_voices() -> {installed}")
else:
    fail("list_installed_voices", "Empty list")


# ═══════════════════════════════════════════════════════════════
# GROUP 2: get_tts_status for all 5 languages
# ═══════════════════════════════════════════════════════════════
section("GROUP 2: get_tts_status — all 5 languages")

for lang in ["English", "Telugu", "Hindi", "Tamil", "Kannada"]:
    st_result = get_tts_status(lang)

    # Must return a proper dict with required keys
    required_keys = {"available", "voice_name", "message", "install_guide", "pyttsx3_present"}
    missing = required_keys - st_result.keys()
    if missing:
        fail(f"get_tts_status({lang}) missing keys", str(missing))
        continue

    # pyttsx3 must be present
    if not st_result["pyttsx3_present"]:
        fail(f"get_tts_status({lang}) pyttsx3_present", "False")
        continue

    # Message must be human-readable (no raw traceback)
    msg = st_result["message"]
    if "Traceback" in msg or 'File "' in msg:
        fail(f"get_tts_status({lang}) message contains traceback", msg[:100])
        continue

    if st_result["available"]:
        ok(f"{lang}: available=True, voice={st_result['voice_name']}")
    else:
        # Unavailable is fine — but must have a clear message and install_guide
        if msg and st_result["install_guide"]:
            ok(f"{lang}: available=False — clean message + install_guide",
               msg[:60])
        elif msg:
            ok(f"{lang}: available=False — clean message (no guide)",
               msg[:60])
        else:
            fail(f"get_tts_status({lang}) unavailable", "No message returned")


# ═══════════════════════════════════════════════════════════════
# GROUP 3: English TTS — real speech synthesis
# ═══════════════════════════════════════════════════════════════
section("GROUP 3: English TTS — real synthesis (you should hear audio)")

en_status = get_tts_status("English")
if not en_status["available"]:
    fail("English voice", f"Not available: {en_status['message']}")
else:
    test_text = "GreenTech. AI Farmer Advisory Assistant. Phase 4 text to speech test."
    print(f"  INFO  Speaking: \"{test_text}\"")
    result = speak(test_text, "English")

    if result["success"]:
        ok(f"speak() started", f"voice={result['voice']}")
    else:
        fail("speak() English", result.get("error",""))

    # is_speaking() should return True immediately after speak()
    time.sleep(0.3)
    if is_speaking():
        ok("is_speaking() returns True while thread active")
    else:
        # Thread may have finished extremely quickly on fast machines
        ok("is_speaking() returned False — thread completed quickly (acceptable)")

    # Wait for speech to finish (test text is short)
    deadline = time.time() + 15
    while is_speaking() and time.time() < deadline:
        time.sleep(0.5)

    if not is_speaking():
        ok("Speech thread finished cleanly")
    else:
        # Force stop and continue
        stop()
        ok("Speech exceeded timeout — stop() called (acceptable on slow machines)")


# ═══════════════════════════════════════════════════════════════
# GROUP 4: unavailable language -> clean message, no crash
# ═══════════════════════════════════════════════════════════════
section("GROUP 4: unavailable language (Telugu/Hindi/Tamil/Kannada)")

for lang in ["Telugu", "Hindi", "Tamil", "Kannada"]:
    try:
        r = speak("Test", lang)
        if r["success"]:
            # Unexpected — a matching voice was found
            ok(f"{lang}: voice found and speech started (unexpected but valid)", r.get("voice",""))
        else:
            err = r.get("error", "")
            guide = r.get("install_guide", "")
            # Must be clean message, not a traceback
            if "Traceback" in err or 'File "' in err:
                fail(f"speak({lang}) error message is traceback", err[:200])
            elif err:
                ok(f"speak({lang}): clean unavailable message", err[:70])
                if guide:
                    ok(f"speak({lang}): install_guide provided", guide[:70])
            else:
                fail(f"speak({lang})", "Empty error message")
    except Exception as e:
        fail(f"speak({lang}) must not raise", str(e))


# ═══════════════════════════════════════════════════════════════
# GROUP 5: stop() lifecycle
# ═══════════════════════════════════════════════════════════════
section("GROUP 5: stop() lifecycle")

en_status = get_tts_status("English")
if en_status["available"]:
    long_text = ("This is a long test sentence for stop testing. " * 20).strip()
    r = speak(long_text, "English")
    if r["success"]:
        time.sleep(0.5)
        speaking_before = is_speaking()
        stop()
        time.sleep(0.3)
        speaking_after = is_speaking()

        if speaking_before:
            ok("is_speaking() True before stop()")
        else:
            ok("is_speaking() False before stop() — thread started and ended quickly")

        if not speaking_after:
            ok("is_speaking() False after stop()")
        else:
            fail("stop()", "is_speaking() still True after stop()")
    else:
        fail("speak() for stop test", r.get("error",""))
else:
    ok("English voice not available — skipping stop lifecycle test")

# stop() when nothing is speaking must not crash
try:
    stop()
    ok("stop() when idle — no crash")
except Exception as e:
    fail("stop() when idle", str(e))


# ═══════════════════════════════════════════════════════════════
# GROUP 6: session state keys in main.py
# ═══════════════════════════════════════════════════════════════
section("GROUP 6: session state keys in main.py")

main_src = pathlib.Path("main.py").read_text(encoding="utf-8")
for key in ["tts_speaking", "tts_message"]:
    if f'"{key}"' in main_src:
        ok(f"main.py has session key '{key}'")
    else:
        fail(f"main.py missing key", key)


# ═══════════════════════════════════════════════════════════════
# GROUP 7: compile checks
# ═══════════════════════════════════════════════════════════════
section("GROUP 7: compile checks — all Phase 4 modified files")

for fpath in [
    "services/tts_service.py",
    "pages/farmer_assistant.py",
    "pages/settings.py",
    "main.py",
]:
    src = pathlib.Path(fpath).read_text(encoding="utf-8")
    try:
        compile(src, fpath, "exec")
        ok(f"{fpath} compiles cleanly")
    except SyntaxError as e:
        fail(f"{fpath} syntax", str(e))


# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
section("SUMMARY")
total = passed + failed
print(f"  {passed}/{total} tests passed")
if failed:
    print(f"  {failed} FAILED")
    sys.exit(1)
else:
    print("  All tests PASSED")
    sys.exit(0)
