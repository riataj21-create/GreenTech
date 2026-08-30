"""
GreenTech Phase 5 - Storage Test Script
Run with: python test_phase5.py

Strategy: monkey-patch storage_mod.st with a fake whose session_state
is a plain dict. This avoids the mock.patch.object limitation outside
a live Streamlit process.
"""

import sys, os, json, pathlib, shutil, types, tempfile
sys.path.insert(0, os.path.dirname(__file__))

# ─── Helpers ──────────────────────────────────────────────────────────────────
passed = failed = 0

def ok(name, extra=""):
    global passed; passed += 1
    print(f"  PASS  {name}" + (f"  [{extra}]" if extra else ""))

def fail(name, reason):
    global failed; failed += 1
    print(f"  FAIL  {name}: {reason}")

def section(title):
    print(f"\n{'='*62}\n  {title}\n{'='*62}")


# ─── Fake Streamlit with dict-backed session_state ────────────────────────────
_state: dict = {}

class _FakeSt:
    session_state = _state      # just a plain dict attribute

fake_st = _FakeSt()


# ─── Temporary history file ───────────────────────────────────────────────────
import utils.config as cfg
_tmp_dir  = pathlib.Path(tempfile.mkdtemp())
_tmp_file = _tmp_dir / "history.json"

# Patch config paths BEFORE importing storage
cfg.HISTORY_FILE = _tmp_file
cfg.DATA_DIR     = _tmp_dir

# Import and reload storage so it picks up the patched paths
import importlib
import utils.storage as storage_mod
importlib.reload(storage_mod)

# Monkey-patch storage_mod.st so all its session_state refs hit _state
storage_mod.st = fake_st   # type: ignore


def reset_state():
    _state.clear()


# Re-bind the functions to the reloaded module
save_to_history         = storage_mod.save_to_history
get_history             = storage_mod.get_history
clear_history           = storage_mod.clear_history
load_history_into_session = storage_mod.load_history_into_session
history_file_path       = storage_mod.history_file_path
MAX_ENTRIES             = storage_mod.MAX_ENTRIES


# ═══════════════════════════════════════════════════════════════
# GROUP 1: API surface
# ═══════════════════════════════════════════════════════════════
section("GROUP 1: API surface")

for fn in ["save_to_history","get_history","clear_history",
           "load_history_into_session","history_file_path"]:
    if callable(getattr(storage_mod, fn, None)):
        ok(f"storage_mod.{fn} callable")
    else:
        fail(f"storage_mod.{fn}", "missing")

if isinstance(MAX_ENTRIES, int) and MAX_ENTRIES >= 10:
    ok(f"MAX_ENTRIES = {MAX_ENTRIES}")
else:
    fail("MAX_ENTRIES", str(MAX_ENTRIES))


# ═══════════════════════════════════════════════════════════════
# GROUP 2: save -> file written
# ═══════════════════════════════════════════════════════════════
section("GROUP 2: save_to_history -> JSON file written")

reset_state()
_state["history"] = []

save_to_history("rice", "Leaves turning yellow", "AI advice text", "English", "text")

if _tmp_file.exists():
    ok("history.json created on first save")
else:
    fail("history.json created", "file missing")

try:
    data = json.loads(_tmp_file.read_text("utf-8"))
    if isinstance(data, list) and len(data) == 1:
        ok("history.json has 1 entry")
    else:
        fail("entry count", f"{len(data) if isinstance(data,list) else type(data)}")

    e = data[0]
    for field, expected in [("crop","rice"),("problem","Leaves turning yellow"),
                             ("language","English"),("input_method","text")]:
        if e.get(field) == expected:
            ok(f"  entry.{field} = '{expected}'")
        else:
            fail(f"  entry.{field}", f"got '{e.get(field)}'")

    if "timestamp" in e and len(e["timestamp"]) >= 10:
        ok(f"  entry.timestamp = {e['timestamp']}")
    else:
        fail("entry.timestamp", str(e.get("timestamp")))

except Exception as ex:
    fail("history.json parse", str(ex))

# Second save
save_to_history("tomato", "Spots on leaves", "Tomato advice", "Hindi", "voice")
data2 = json.loads(_tmp_file.read_text("utf-8"))
if len(data2) == 2:
    ok("history.json has 2 entries after second save")
else:
    fail("2 entries", str(len(data2)))
if data2[1].get("input_method") == "voice":
    ok("second entry input_method = 'voice'")
else:
    fail("second entry method", data2[1].get("input_method"))


# ═══════════════════════════════════════════════════════════════
# GROUP 3: restart simulation -> persistence
# ═══════════════════════════════════════════════════════════════
section("GROUP 3: restart simulation — load_history_into_session")

reset_state()   # wipe session — file still on disk

if "history" not in _state:
    ok("Session cleared (restart simulation)")
else:
    fail("reset_state", "history key still present")

load_history_into_session()
loaded = _state.get("history", [])
if len(loaded) == 2:
    ok(f"Loaded {len(loaded)} entries from disk after restart")
else:
    fail("loaded count", f"expected 2, got {len(loaded)}")

if loaded and loaded[0].get("crop") == "rice":
    ok("First loaded entry is 'rice'")

# Double call must not duplicate
load_history_into_session()
if len(_state.get("history",[])) == len(loaded):
    ok("Double load does not duplicate entries")
else:
    fail("double load", f"got {len(_state.get('history',[]))}")


# ═══════════════════════════════════════════════════════════════
# GROUP 4: clear_history -> file deleted, session empty
# ═══════════════════════════════════════════════════════════════
section("GROUP 4: clear_history -> file deleted")

clear_history()

if _state.get("history") == []:
    ok("session_state['history'] == [] after clear")
else:
    fail("session after clear", str(_state.get("history")))

if not _tmp_file.exists():
    ok("history.json deleted after clear_history()")
else:
    fail("file deletion", "file still exists")

if get_history() == []:
    ok("get_history() returns [] after clear")
else:
    fail("get_history after clear", str(get_history()))

# Save after clear works
save_to_history("cotton","Bollworm","Cotton advice","Telugu","voice")
if _tmp_file.exists():
    ok("Can save again after clear")
else:
    fail("save after clear", "file not created")


# ═══════════════════════════════════════════════════════════════
# GROUP 5: MAX_ENTRIES cap
# ═══════════════════════════════════════════════════════════════
section("GROUP 5: MAX_ENTRIES cap")

reset_state()
if _tmp_file.exists():
    _tmp_file.unlink()
_state["history"] = []

overflow = MAX_ENTRIES + 10
for i in range(overflow):
    save_to_history(f"crop_{i}", f"prob_{i}", f"adv_{i}", "English", "text")

final = len(_state.get("history", []))
if final <= MAX_ENTRIES:
    ok(f"Session history capped at {final} (<= {MAX_ENTRIES})")
else:
    fail("session cap", f"{final} > {MAX_ENTRIES}")

file_data = json.loads(_tmp_file.read_text("utf-8"))
if len(file_data) <= MAX_ENTRIES:
    ok(f"File also capped at {len(file_data)} entries")
else:
    fail("file cap", f"{len(file_data)} > {MAX_ENTRIES}")

newest = _state["history"][-1]
if newest.get("crop") == f"crop_{overflow-1}":
    ok("Newest entry preserved after cap")
else:
    fail("newest after cap", newest.get("crop"))


# ═══════════════════════════════════════════════════════════════
# GROUP 6: error resilience
# ═══════════════════════════════════════════════════════════════
section("GROUP 6: error resilience")

# Missing file
reset_state()
if _tmp_file.exists(): _tmp_file.unlink()
try:
    load_history_into_session()
    if isinstance(_state.get("history"), list):
        ok("Missing file -> returns list, no crash")
    else:
        fail("missing file", "not a list")
except Exception as ex:
    fail("missing file must not raise", str(ex))

# Corrupted JSON
reset_state()
_tmp_file.write_text("{ not valid json !!!", "utf-8")
try:
    load_history_into_session()
    if isinstance(_state.get("history"), list):
        ok("Corrupted JSON -> returns list, no crash")
    else:
        fail("corrupted json", "not a list")
except Exception as ex:
    fail("corrupted json must not raise", str(ex))

# Empty file
reset_state()
_tmp_file.write_text("", "utf-8")
try:
    load_history_into_session()
    ok("Empty file -> no crash")
except Exception as ex:
    fail("empty file must not raise", str(ex))

# clear when no file
reset_state()
if _tmp_file.exists(): _tmp_file.unlink()
try:
    clear_history()
    ok("clear_history() with no file -> no crash")
except Exception as ex:
    fail("clear no file", str(ex))


# ═══════════════════════════════════════════════════════════════
# GROUP 7: compile & integration checks
# ═══════════════════════════════════════════════════════════════
section("GROUP 7: compile & integration checks")

for fpath in ["utils/storage.py","main.py","pages/history.py","pages/settings.py"]:
    src = pathlib.Path(fpath).read_text("utf-8")
    try:
        compile(src, fpath, "exec")
        ok(f"{fpath} compiles cleanly")
    except SyntaxError as ex:
        fail(f"{fpath}", str(ex))

main_src = pathlib.Path("main.py").read_text("utf-8")
if "load_history_into_session" in main_src:
    ok("main.py calls load_history_into_session()")
else:
    fail("main.py", "load_history_into_session missing")

settings_src = pathlib.Path("pages/settings.py").read_text("utf-8")
if "clear_history" in settings_src:
    ok("settings.py calls clear_history()")
else:
    fail("settings.py", "clear_history missing")

history_src = pathlib.Path("pages/history.py").read_text("utf-8")
if "get_history" in history_src and "clear_history" in history_src:
    ok("history.py uses get_history() and clear_history()")
else:
    fail("history.py", "get_history or clear_history missing")


# ─── Cleanup ──────────────────────────────────────────────────────────────────
try:
    shutil.rmtree(_tmp_dir)
except Exception:
    pass


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
