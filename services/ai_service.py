"""
GreenTech - AI Service (Multi-provider with Groq as primary)
Provider priority for text advice:
  1. Groq        (openai/gpt-oss-120b) — fastest
  2. OpenRouter  (openrouter/free)     — fallback
  3. Gemini      (gemini-3.6-flash)    — final fallback

Vision is handled separately in farmer_assistant.py.
API keys are never returned or logged.
"""

import json
import sys
import pathlib
import requests
from typing import Optional

from google import genai
from google.genai import types as genai_types

from utils.config import (
    GEMINI_API_KEY, GEMINI_MODEL, AGRI_FILE, LANGUAGES,
    OPENROUTER_API_KEY, OPENROUTER_MODEL,
    GROQ_API_KEY, GROQ_TEXT_MODEL,
    gemini_configured, openrouter_configured, groq_configured, ai_configured,
)


# ─── Errors ──────────────────────────────────────────────────────────────────

class AIServiceError(Exception):
    pass

class AINotConfiguredError(AIServiceError):
    pass


# ─── Groq call (primary) ──────────────────────────────────────────────────────

def _call_groq(prompt: str) -> dict:
    """Call Groq. Returns {"success": True, "text": ..., "model": ..., "provider": "groq"} or error."""
    from services.groq_service import call_groq_text
    result = call_groq_text(prompt, max_tokens=1500, temperature=0.3)
    if result["success"]:
        return {
            "success": True,
            "text": result["text"],
            "model": GROQ_TEXT_MODEL,
            "provider": "groq",
        }
    return {"success": False, "error": result["error"]}


# ─── Gemini Client (lazy singleton) ───────────────────────────────────────────

_gemini_client: Optional[genai.Client] = None


def _get_gemini_client() -> genai.Client:
    """Return (or create) the Gemini client. Raises AINotConfiguredError if key missing."""
    global _gemini_client
    if _gemini_client is None:
        if not GEMINI_API_KEY:
            raise AINotConfiguredError(
                "Gemini API key is not configured. "
                "Add GEMINI_API_KEY to your .env file."
            )
        _gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    return _gemini_client


# ─── OpenRouter API ───────────────────────────────────────────────────────────

def _call_openrouter(prompt: str) -> dict:
    """
    Call OpenRouter API with the given prompt.
    Returns {"success": True, "text": "...", "model": "..."} or error dict.
    """
    if not OPENROUTER_API_KEY:
        raise AINotConfiguredError(
            "OpenRouter API key is not configured. "
            "Add OPENROUTER_API_KEY to your .env file."
        )
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://greentech.local",
        "X-Title": "GreenTech Agricultural Assistant"
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,  # Reduced from 0.4 for more focused responses
        "max_tokens": 1500,  # Reduced from 2048 for faster generation
        "top_p": 0.9  # Add top_p for more efficient sampling
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        
        # Extract response text
        if "choices" in data and len(data["choices"]) > 0:
            text = data["choices"][0]["message"]["content"].strip()
            if not text:
                return {
                    "success": False,
                    "error": "The AI returned an empty response. Please try again."
                }
            return {
                "success": True,
                "text": text,
                "model": OPENROUTER_MODEL
            }
        else:
            return {
                "success": False,
                "error": "Invalid response format from OpenRouter API."
            }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "The request timed out. Please try again."
        }
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return {
                "success": False,
                "error": "OpenRouter API key is invalid. Please check your .env file."
            }
        elif e.response.status_code == 429:
            return {
                "success": False,
                "error": "Too many requests. Please wait a few seconds and try again."
            }
        elif e.response.status_code == 402:
            return {
                "success": False,
                "error": "OpenRouter API quota exceeded. Please check your account balance."
            }
        else:
            return {
                "success": False,
                "error": f"OpenRouter API error: {e.response.status_code}"
            }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": "Could not connect to OpenRouter API. Please check your internet connection."
        }
    except Exception as e:
        import sys
        print(f"[GreenTech ai_service] OpenRouter error: {e}", file=sys.stderr)
        return {
            "success": False,
            "error": "An error occurred while contacting OpenRouter API. Please try again."
        }


# ─── Agricultural context ─────────────────────────────────────────────────────

_agri_data: Optional[dict] = None


def _load_agri_data() -> dict:
    """Load and cache agriculture.json. Returns empty dict on any error."""
    global _agri_data
    if _agri_data is None:
        try:
            with open(AGRI_FILE, "r", encoding="utf-8") as f:
                _agri_data = json.load(f)
        except Exception:
            _agri_data = {}
    return _agri_data


def _get_crop_context(crop: str) -> str:
    """
    Return a short text block of agricultural context for the given crop.
    If the crop is not found, returns an empty string (Gemini handles it alone).
    """
    data = _load_agri_data()
    crops: dict = data.get("crops", {})

    crop_lower = crop.strip().lower()

    # Direct match
    entry = crops.get(crop_lower)

    # Alias match
    if entry is None:
        for key, info in crops.items():
            if crop_lower in [a.lower() for a in info.get("aliases", [])]:
                entry = info
                break

    if entry is None:
        return ""  # Unknown crop — Gemini will handle it from its own knowledge

    lines = [f"Crop: {crop.title()}"]

    cond = entry.get("growing_conditions", {})
    if cond:
        lines.append(
            f"Growing conditions: climate={cond.get('climate','')}, "
            f"temperature={cond.get('temperature_c','')}°C, "
            f"soil={cond.get('soil','')}"
        )

    problems = entry.get("common_problems", [])
    if problems:
        lines.append("Common problems known for this crop:")
        for p in problems[:4]:  # cap at 4 to keep prompt concise
            symptoms = ", ".join(p.get("symptoms", []))
            lines.append(f"  - {p['name']}: {symptoms}")

    preventive = entry.get("preventive_practices", [])
    if preventive:
        lines.append("Common preventive practices: " + "; ".join(preventive[:3]))

    return "\n".join(lines)


# ─── Prompt construction ──────────────────────────────────────────────────────

def _build_prompt(crop: str, problem: str, language: str, agri_context: str) -> str:
    """
    Construct the full prompt sent to Gemini.
    Language instruction is explicit so the model returns in the selected language.
    """
    lang_info = LANGUAGES.get(language, LANGUAGES["English"])
    lang_native = lang_info["native"]
    lang_label  = lang_info["label"]

    context_block = ""
    if agri_context:
        context_block = f"""
--- Agricultural Knowledge Context ---
{agri_context}
--- End of Context ---

"""

    prompt = f"""You are GreenTech, an expert agricultural advisory AI assistant.
A farmer is seeking practical guidance about a crop problem.

IMPORTANT LANGUAGE INSTRUCTION:
Respond entirely in {lang_native} ({lang_label}).
All headings, text, and advice must be in {lang_native} ({lang_label}).
Only use English if {lang_label} is English.

{context_block}Farmer's crop: {crop}
Farmer's problem description: {problem}

Provide a structured agricultural advisory response using exactly these sections.
Write the section headings in {lang_native} ({lang_label}) as well.

## Problem Summary
Briefly explain what the farmer appears to be experiencing based on their description.

## Possible Causes
List the most likely causes. Use language like "possible cause" or "one possibility" — do not claim certainty.

## What to Check
Give 3–5 practical observations the farmer can make in the field right now.

## Recommended Actions
Give clear, practical, actionable steps the farmer can take. Be specific.

## What to Avoid
Mention 2–3 actions that could worsen the situation.

## Prevention
Give basic preventive guidance to avoid this problem in future.

## When to Contact an Agricultural Expert
Explain clearly when the farmer should seek professional agricultural assistance.

Keep the response practical, empathetic, and accessible to a farmer without technical background.
Do not use overly technical jargon. If you are uncertain, say so honestly."""

    return prompt


# ─── Main public function ─────────────────────────────────────────────────────

def get_agricultural_advice(
    crop: str,
    problem: str,
    language: str = "English",
    timeout_seconds: int = 30,
) -> dict:
    """
    Get AI agricultural advice.
    Provider waterfall: Groq → OpenRouter → Gemini.
    Never raises — all exceptions return error dicts.
    """
    crop    = crop.strip()
    problem = problem.strip()

    if not crop:
        return {"success": False, "error": "Please enter the crop name.", "crop": crop, "language": language}
    if not problem:
        return {"success": False, "error": "Please describe the problem.", "crop": crop, "language": language}
    if not ai_configured():
        return {"success": False, "error": "No AI provider configured. Add GROQ_API_KEY, OPENROUTER_API_KEY or GEMINI_API_KEY to .env.", "crop": crop, "language": language}

    agri_context = _get_crop_context(crop)
    prompt       = _build_prompt(crop, problem, language, agri_context)

    errors = []

    # ── 1. Groq (fastest) ─────────────────────────────────────────────────────
    if groq_configured():
        result = _call_groq(prompt)
        if result["success"]:
            return {
                "success": True,
                "text": result["text"],
                "crop": crop, "language": language,
                "model": result["model"], "provider": "groq",
            }
        errors.append(f"Groq: {result['error']}")
        print(f"[GreenTech ai_service] Groq failed: {result['error']} — trying OpenRouter", file=sys.stderr)

    # ── 2. OpenRouter (fallback) ──────────────────────────────────────────────
    if openrouter_configured():
        result = _call_openrouter(prompt)
        if result["success"]:
            return {
                "success": True,
                "text": result["text"],
                "crop": crop, "language": language,
                "model": result["model"], "provider": "openrouter",
            }
        errors.append(f"OpenRouter: {result['error']}")
        print(f"[GreenTech ai_service] OpenRouter failed: {result['error']} — trying Gemini", file=sys.stderr)

    # ── 3. Gemini (final fallback) ────────────────────────────────────────────
    if gemini_configured():
        try:
            client = _get_gemini_client()
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=2048,
                ),
            )
            text = response.text
            if text and text.strip():
                return {
                    "success": True,
                    "text": text.strip(),
                    "crop": crop, "language": language,
                    "model": GEMINI_MODEL, "provider": "gemini",
                }
            errors.append("Gemini: empty response")
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "quota" in err_str.lower():
                errors.append("Gemini: quota exceeded")
            elif "API_KEY_INVALID" in err_str:
                errors.append("Gemini: invalid API key")
            else:
                errors.append(f"Gemini: {err_str[:80]}")
            print(f"[GreenTech ai_service] Gemini failed: {err_str[:100]}", file=sys.stderr)

    # All providers failed
    return {
        "success": False,
        "error": "All AI providers failed. " + " | ".join(errors),
        "crop": crop, "language": language,
    }


# ─── Status check ─────────────────────────────────────────────────────────────

def check_ai_status() -> dict:
    """
    Returns status of the first available provider.
    """
    from services.groq_service import check_groq_status
    if groq_configured():
        return check_groq_status()
    if openrouter_configured():
        result = _call_openrouter("Reply with one word: OK")
        ok = result["success"] and bool(result.get("text"))
        return {
            "ok": ok,
            "message": f"OpenRouter connected. Model: {OPENROUTER_MODEL}" if ok else result.get("error",""),
            "provider": "openrouter",
        }
    if gemini_configured():
        try:
            client = _get_gemini_client()
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents="Reply with one word: OK",
                config=genai_types.GenerateContentConfig(max_output_tokens=10),
            )
            if response.text:
                return {"ok": True, "message": f"Gemini connected. Model: {GEMINI_MODEL}", "provider": "gemini"}
        except Exception as e:
            return {"ok": False, "message": str(e)[:80], "provider": "gemini"}
    return {"ok": False, "message": "No AI provider configured.", "provider": "none"}
