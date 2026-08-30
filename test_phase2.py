"""
GreenTech Phase 2 - Test Script
Run with: python test_phase2.py
Tests all Phase 2 requirements without needing a browser.
Requires GEMINI_API_KEY in .env for live API tests.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# ─── Test helpers ─────────────────────────────────────────────────────────────

passed = 0
failed = 0

def ok(name):
    global passed
    passed += 1
    print(f"  PASS  {name}")

def fail(name, reason):
    global failed
    failed += 1
    print(f"  FAIL  {name}: {reason}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ─── 1. No-API-key safety ─────────────────────────────────────────────────────
section("TEST GROUP 1: No API key configured")

import services.ai_service as svc
from services.ai_service import get_agricultural_advice, check_ai_status

# Simulate missing key
svc._client = None
original_key = svc.GEMINI_API_KEY  # save
import utils.config as cfg
original_cfg_key = cfg.GEMINI_API_KEY

cfg.GEMINI_API_KEY = ""
svc.GEMINI_API_KEY = ""

try:
    result = get_agricultural_advice("rice", "My leaves are yellow", "English")
    if result["success"] == False and ("key" in result["error"].lower() or "configur" in result["error"].lower()):
        ok("No key -> returns error dict with clear message")
        print(f"         Message: {result['error']}")
    else:
        fail("No key -> error dict", f"Got: {result}")
except Exception as e:
    fail("No key -> must not raise", str(e))

try:
    status = check_ai_status()
    if status["ok"] == False:
        ok("check_ai_status no key -> ok=False")
    else:
        fail("check_ai_status no key", f"Returned ok=True unexpectedly")
except Exception as e:
    fail("check_ai_status no key must not raise", str(e))

try:
    r = get_agricultural_advice("", "yellowing leaves", "English")
    if r["success"] == False:
        ok("Empty crop -> error dict")
    else:
        fail("Empty crop", "Expected success=False")
except Exception as e:
    fail("Empty crop must not raise", str(e))

try:
    r = get_agricultural_advice("rice", "", "English")
    if r["success"] == False:
        ok("Empty problem -> error dict")
    else:
        fail("Empty problem", "Expected success=False")
except Exception as e:
    fail("Empty problem must not raise", str(e))

# Restore key
cfg.GEMINI_API_KEY = original_cfg_key
svc.GEMINI_API_KEY = original_cfg_key
svc._client = None


# ─── 2. Agricultural context lookup ──────────────────────────────────────────
section("TEST GROUP 2: Agricultural context lookup")

from services.ai_service import _get_crop_context, _load_agri_data

data = _load_agri_data()
if data and "crops" in data:
    ok("agriculture.json loaded successfully")
else:
    fail("agriculture.json load", f"Got: {data}")

for crop_name in ["rice", "paddy", "tomato", "cotton", "maize"]:
    ctx = _get_crop_context(crop_name)
    if ctx and len(ctx) > 10:
        ok(f"Context found for '{crop_name}'")
    else:
        fail(f"Context for '{crop_name}'", f"Got empty or short context: '{ctx[:50]}'")

# Unknown crop must return empty string (not error)
unknown_ctx = _get_crop_context("dragonfruit")
if unknown_ctx == "":
    ok("Unknown crop 'dragonfruit' -> empty context (Gemini handles it)")
else:
    fail("Unknown crop context", f"Expected empty string, got: {unknown_ctx[:100]}")

# Alias lookup
paddy_ctx = _get_crop_context("paddy")
if paddy_ctx and "rice" in paddy_ctx.lower() or "paddy" in paddy_ctx.lower():
    ok("Alias 'paddy' resolves to rice entry")
else:
    fail("Alias 'paddy' lookup", f"Got: {paddy_ctx[:100]}")


# ─── 3. Prompt construction ───────────────────────────────────────────────────
section("TEST GROUP 3: Prompt construction")

from services.ai_service import _build_prompt

for lang in ["English", "Telugu", "Hindi", "Tamil", "Kannada"]:
    prompt = _build_prompt("rice", "leaves turning yellow", lang, "")
    if lang in prompt or "తెలుగు" in prompt or "हिन्दी" in prompt or "தமிழ்" in prompt or "ಕನ್ನಡ" in prompt:
        ok(f"Prompt for {lang} contains language instruction")
    else:
        fail(f"Prompt for {lang}", f"Language not found in prompt")

# Prompt includes agricultural context when available
ctx = _get_crop_context("rice")
prompt_with_ctx = _build_prompt("rice", "yellowing leaves", "English", ctx)
if "Agricultural Knowledge Context" in prompt_with_ctx:
    ok("Prompt includes agricultural context block")
else:
    fail("Prompt context block", "Missing Agricultural Knowledge Context section")

# Prompt without context (unknown crop)
prompt_no_ctx = _build_prompt("dragonfruit", "spots on leaves", "English", "")
if "Agricultural Knowledge Context" not in prompt_no_ctx:
    ok("Unknown crop prompt has no empty context block")
else:
    fail("Unknown crop prompt", "Context block present for unknown crop")


# ─── 4. Live Gemini API tests (only if key configured) ───────────────────────
section("TEST GROUP 4: Live Gemini API (requires GEMINI_API_KEY)")

from utils.config import gemini_configured, GEMINI_MODEL

if not gemini_configured():
    print("  SKIP  All live tests — GEMINI_API_KEY not configured in .env")
    print("        Add your key to .env to run live tests.")
else:
    print(f"  INFO  Key configured. Model: {GEMINI_MODEL}")
    print()

    # Test 4a: rice + yellow leaves (English)
    print("  Running: rice + yellow leaves (English)...")
    r = get_agricultural_advice("rice", "My rice leaves are turning yellow and the plants look weak.", "English")
    if r["success"] and len(r["text"]) > 100:
        ok("Live: rice yellow leaves (English) -> got substantive response")
        print(f"         Response length: {len(r['text'])} chars")
        # Check for expected sections
        for section_name in ["Possible Cause", "Recommend", "Prevent"]:
            if section_name.lower() in r["text"].lower():
                ok(f"  Response contains '{section_name}' section")
                break
        else:
            fail("Response structure", "No expected sections found in response")
    else:
        fail("Live rice yellow leaves", f"success={r.get('success')}, error={r.get('error','')}, len={len(r.get('text',''))}")

    # Test 4b: Telugu response
    print("\n  Running: rice + yellow leaves (Telugu)...")
    r_te = get_agricultural_advice("rice", "నా వరి ఆకులు పసుపు రంగులోకి మారుతున్నాయి.", "Telugu")
    if r_te["success"] and len(r_te["text"]) > 50:
        ok("Live: Telugu language request -> got response")
        print(f"         Response preview: {r_te['text'][:120]}...")
    else:
        fail("Live Telugu", f"error={r_te.get('error','')}")

    # Test 4c: Hindi response
    print("\n  Running: tomato + spots (Hindi)...")
    r_hi = get_agricultural_advice("tomato", "My tomato plants have spots on leaves.", "Hindi")
    if r_hi["success"] and len(r_hi["text"]) > 50:
        ok("Live: Hindi language request -> got response")
        print(f"         Response preview: {r_hi['text'][:120]}...")
    else:
        fail("Live Hindi", f"error={r_hi.get('error','')}")

    # Test 4d: arbitrary crop NOT in agriculture.json
    print("\n  Running: dragonfruit (not in agriculture.json)...")
    r_unk = get_agricultural_advice("dragonfruit", "The leaves are developing brown spots and curling.", "English")
    if r_unk["success"] and len(r_unk["text"]) > 50:
        ok("Live: unknown crop 'dragonfruit' -> Gemini handled it (not rejected)")
        print(f"         Response length: {len(r_unk['text'])} chars")
    else:
        fail("Live unknown crop", f"error={r_unk.get('error','')}")

    # Test 4e: different wording for same problem (NLU test)
    print("\n  Running: paddy leaves losing green colour (alternate phrasing)...")
    r_alt = get_agricultural_advice(
        "paddy",
        "My paddy crop has started losing its green colour and the lower leaves look pale.",
        "English"
    )
    if r_alt["success"] and len(r_alt["text"]) > 50:
        ok("Live: alternate phrasing 'losing green colour' -> got response")
    else:
        fail("Live alternate phrasing", f"error={r_alt.get('error','')}")


# ─── 5. Storage utility ───────────────────────────────────────────────────────
section("TEST GROUP 5: Storage utility")

try:
    import importlib
    import utils.storage as storage_mod
    importlib.import_module("utils.storage")
    assert callable(storage_mod.save_to_history), "save_to_history not callable"
    assert callable(storage_mod.get_history),     "get_history not callable"
    assert callable(storage_mod.clear_history),   "clear_history not callable"
    ok("storage.py imports cleanly and all functions are defined")
except Exception as e:
    fail("storage module", str(e))


# ─── Summary ──────────────────────────────────────────────────────────────────
section("SUMMARY")
total = passed + failed
print(f"  {passed}/{total} tests passed")
if failed:
    print(f"  {failed} test(s) FAILED — see above")
    sys.exit(1)
else:
    print("  All tests PASSED")
    sys.exit(0)
