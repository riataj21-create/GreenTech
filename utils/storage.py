"""
GreenTech - Storage Utility (Phase 5)

Persistent history using a local JSON file (data/history.json).

Design:
  - Single source of truth is the JSON file on disk.
  - st.session_state["history"] is a write-through cache:
      every save/clear writes to disk immediately.
  - load_history_into_session() is called once at app startup
    (main.py → init_session_state) to populate the cache from disk.
  - All disk I/O is wrapped in try/except — a corrupted or missing
    file never crashes the application.
  - History is capped at MAX_ENTRIES to prevent unbounded growth.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from utils.config import HISTORY_FILE, DATA_DIR

MAX_ENTRIES = 200   # keep the last N sessions


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _ensure_data_dir() -> None:
    """Create the data/ directory if it does not exist."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[GreenTech storage] Could not create data dir: {e}", file=sys.stderr)


def _read_file() -> list[dict]:
    """
    Read history from disk.
    Returns a list of entry dicts, or [] on any error.
    """
    try:
        if not HISTORY_FILE.exists():
            return []
        raw = HISTORY_FILE.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        data = json.loads(raw)
        if isinstance(data, list):
            return data
        return []
    except Exception as e:
        print(f"[GreenTech storage] Could not read history file: {e}", file=sys.stderr)
        return []


def _write_file(entries: list[dict]) -> None:
    """
    Write `entries` to disk atomically (write to .tmp, then rename).
    Silently logs errors — never raises.
    """
    _ensure_data_dir()
    tmp = Path(str(HISTORY_FILE) + ".tmp")
    try:
        tmp.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp.replace(HISTORY_FILE)   # atomic on same filesystem
    except Exception as e:
        print(f"[GreenTech storage] Could not write history file: {e}", file=sys.stderr)
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass


# ─── Public API ───────────────────────────────────────────────────────────────

def load_history_into_session() -> None:
    """
    Load history from disk into st.session_state["history"].
    Call once at app startup, before any widget is created.
    Safe to call multiple times — only loads if session key is missing.
    """
    if "history" not in st.session_state:
        st.session_state["history"] = _read_file()


def save_to_history(
    crop: str,
    problem: str,
    advice: str,
    language: str,
    input_method: str = "text",
) -> None:
    """
    Append a new advisory session to both session state and disk.
    Enforces MAX_ENTRIES cap (oldest entries dropped first).
    """
    if "history" not in st.session_state:
        st.session_state["history"] = _read_file()

    entry: dict[str, Any] = {
        "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M"),
        "crop":         crop.strip(),
        "problem":      problem.strip(),
        "advice":       advice.strip(),
        "language":     language,
        "input_method": input_method,
    }

    entries: list = st.session_state["history"]
    entries.append(entry)

    # Cap
    if len(entries) > MAX_ENTRIES:
        entries = entries[-MAX_ENTRIES:]
        st.session_state["history"] = entries

    _write_file(entries)


def get_history() -> list[dict]:
    """Return the current history list from session state."""
    return st.session_state.get("history", [])


def clear_history() -> None:
    """
    Remove all history from session state AND from disk.
    Called from both the History page and the Settings page.
    """
    st.session_state["history"] = []
    try:
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
    except Exception as e:
        print(f"[GreenTech storage] Could not delete history file: {e}", file=sys.stderr)


def history_file_path() -> Path:
    """Return the path to the history file (for display in Settings)."""
    return HISTORY_FILE
