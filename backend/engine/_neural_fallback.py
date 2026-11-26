"""
Pillar 1 Heuristic Fallback for Aigaane.

RETIRED at v0.4.0: no LLM path. Heuristic fallback only.
The Gemini/GenAI invocation was removed as part of the zero-LLM-guesswork
policy. This module is pure Python; no network calls, no external models.
"""
import os
import re
import json
import uuid
from typing import Optional, Dict, Any

# Retired: genai SDK no longer imported.
_GENAI_AVAILABLE = False


def is_valid_sanskrit_surface(text: str) -> bool:
    """Rejects strings containing digits, underscores, or non-linguistic noise."""
    if not text:
        return False
    if any(ch.isdigit() or ch in "_$#@*&^%+=~`<>{}" for ch in text):
        return False
    cleaned = re.sub(r"[\s\.,।॥\-']+", "", text)
    return len(cleaned) > 0


def is_llm_available() -> bool:
    """Retired at v0.4.0: no LLM path. Always False for API compatibility."""
    return False


def fallback_parse(surface: str, raw_surface: str, deva: str, script_original: str) -> Optional[Dict[str, Any]]:
    """
    Heuristic fallback when deterministic parsing yields None.

    No LLM is invoked. Returns a single-token subhanta guess for valid
    Sanskrit surfaces, or None for non-linguistic noise.
    """
    if not is_valid_sanskrit_surface(raw_surface) or not is_valid_sanskrit_surface(surface):
        return None

    trace_id = str(uuid.uuid4())

    return {
        "schema_version": "0.2.0",
        "trace_id": trace_id,
        "script_original": script_original,
        "surface": raw_surface,
        "normalized": deva,
        "transliteration": {"devanagari": deva, "iast": surface},
        "parse_rank": 1,
        "tokens": [
            {
                "token_id": "T0",
                "pada": raw_surface,
                "stem": surface,
                "pos": "subhanta",
                "vibhakti": "prathama",
                "vacana": "ekavacana",
                "linga": "pullinga",
                "confidence": 0.50,
            }
        ],
        "sandhi_splits": [],
        "ambiguous_parses": [],
        "canon_refs": [],
        "result_classification": "HEURISTIC_UNVERIFIED",
        "confidence": 0.50,
        "confidence_aggregate": {"min": 0.50, "mean": 0.50},
        "provenance": ["engine=heuristic-unknown-fallback"],
    }
