"""
Vedic Unicode extension coverage and mark classification helpers (F2).
Keeps U+1CD0-U+1CFF classification explicit and separates pluta U+0969 from tone marks.
"""
from __future__ import annotations

import unicodedata
from typing import Dict, List

VEDIC_EXT_START = 0x1CD0
VEDIC_EXT_END = 0x1CFF
PLUTA_DEVANAGARI = "\u0969"

KNOWN_VEDIC_TONE_MARKS = {
    "\u0951": "udatta_devanagari",
    "\u0952": "anudatta_devanagari",
    "\u1cd0": "vedic_tone_karshana",
    "\u1cd1": "vedic_tone_shara",
    "\u1cd2": "vedic_tone_prashlishta",
    "\u1cda": "vedic_tone_double_above",
    "\u1cdb": "vedic_tone_triple_above",
    "\u1cdc": "vedic_tone_kathaka_udatta",
    "\u1cdd": "vedic_tone_kathaka_anudatta",
    "\u1cde": "vedic_tone_kathaka_svarita",
    "\u1cdf": "vedic_tone_jaiminiya_svarita",
    "\u1ce0": "vedic_tone_jaiminiya_ring_above",
    "\u1ce2": "vedic_tone_shanka_above",
    "\u1ce3": "vedic_tone_suspending_stroke",
    "\u1ce4": "vedic_tone_curve_above",
    "\u1ce5": "vedic_tone_curve_below",
    "\u1ce6": "vedic_tone_dot_below",
    "\u1ce7": "vedic_tone_two_dots_below",
    "\u1ce8": "vedic_tone_three_dots_below",
}


def find_unclassified_vedic_marks(text: str) -> List[Dict[str, str]]:
    """Return any U+1CD0-U+1CFF codepoints in text not in KNOWN_VEDIC_TONE_MARKS."""
    norm = unicodedata.normalize("NFC", text or "")
    unclassified: List[Dict[str, str]] = []
    seen = set()
    for ch in norm:
        cp = ord(ch)
        if VEDIC_EXT_START <= cp <= VEDIC_EXT_END and ch not in KNOWN_VEDIC_TONE_MARKS:
            code_hex = f"U+{cp:04X}"
            if code_hex not in seen:
                seen.add(code_hex)
                unclassified.append(
                    {
                        "codepoint": code_hex,
                        "char": ch,
                        "name": unicodedata.name(ch, "UNCLASSIFIED_VEDIC_EXTENSION"),
                        "category": "pluta_mark" if ch == PLUTA_DEVANAGARI else "unclassified_vedic_ext",
                    }
                )
    return unclassified


def audit_vedic_extensions_coverage(text: str) -> Dict[str, object]:
    """Summarize Vedic extension codepoints, known tone marks, pluta marks, and gaps."""
    norm = unicodedata.normalize("NFC", text or "")
    ext_chars = [ch for ch in norm if VEDIC_EXT_START <= ord(ch) <= VEDIC_EXT_END]
    pluta_count = norm.count(PLUTA_DEVANAGARI)
    unclassified = find_unclassified_vedic_marks(norm)
    known_hits = sorted({f"U+{ord(ch):04X}" for ch in ext_chars if ch in KNOWN_VEDIC_TONE_MARKS})
    return {
        "extension_range": "U+1CD0-U+1CFF",
        "extension_char_count": len(ext_chars),
        "known_tone_codepoints": known_hits,
        "pluta_u0969_count": pluta_count,
        "unclassified_marks": unclassified,
        "has_unclassified": len(unclassified) > 0,
    }
