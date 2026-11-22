"""
P0-2 Vedic Unicode Registry & Vowel-Nucleus Accent Segmenter.
Maintains an explicit character-by-character registry of assigned code points in
Devanagari Stress Signs (U+0951..U+0954) and Vedic Extensions (U+1CD0..U+1CFF),
strictly separates U+0969 (DEVANAGARI DIGIT THREE) as a Pluta quantity marker,
and attaches accent labels to the syllable's vowel nucleus while preserving the
immutable NFC grapheme cluster.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple

AccentCategory = Literal[
    "udatta",
    "anudatta",
    "svarita",
    "svarita_double",
    "svarita_triple",
    "samaveda_tone",
    "nasal_or_breath",
]


@dataclass(frozen=True)
class VedicMarkSpec:
    codepoint: str
    char: str
    unicode_name: str
    accent_category: AccentCategory
    tradition: str
    combining_class: int


# Explicit registry of assigned Vedic marks (never treat U+1CD0..U+1CFF as uniform)
VEDIC_MARK_REGISTRY: Dict[str, VedicMarkSpec] = {
    "\u0951": VedicMarkSpec("U+0951", "\u0951", "DEVANAGARI STRESS SIGN UDATTA", "udatta", "pan_vedic", 230),
    "\u0952": VedicMarkSpec("U+0952", "\u0952", "DEVANAGARI STRESS SIGN ANUDATTA", "anudatta", "pan_vedic", 220),
    "\u0953": VedicMarkSpec("U+0953", "\u0953", "DEVANAGARI GRAVE ACCENT", "anudatta", "editorial_vedic", 230),
    "\u0954": VedicMarkSpec("U+0954", "\u0954", "DEVANAGARI ACUTE ACCENT", "udatta", "editorial_vedic", 230),
    # Vedic Extensions U+1CD0..U+1CFF (selected canonical & recension-specific signs)
    "\u1cd0": VedicMarkSpec("U+1CD0", "\u1cd0", "VEDIC TONE KARSHANA", "samaveda_tone", "samaveda", 230),
    "\u1cd1": VedicMarkSpec("U+1CD1", "\u1cd1", "VEDIC TONE SHARA", "samaveda_tone", "samaveda", 230),
    "\u1cd2": VedicMarkSpec("U+1CD2", "\u1cd2", "VEDIC TONE PRENKHA", "samaveda_tone", "samaveda", 230),
    "\u1cd4": VedicMarkSpec("U+1CD4", "\u1cd4", "VEDIC SIGN YAJURVEDIC MIDLINE SVARITA", "svarita", "yajurveda", 1),
    "\u1cd5": VedicMarkSpec("U+1CD5", "\u1cd5", "VEDIC TONE YAJURVEDIC AGGRAVATED INDEPENDENT SVARITA", "svarita_double", "yajurveda", 220),
    "\u1cd6": VedicMarkSpec("U+1CD6", "\u1cd6", "VEDIC TONE YAJURVEDIC INDEPENDENT SVARITA", "svarita", "yajurveda", 220),
    "\u1cd7": VedicMarkSpec("U+1CD7", "\u1cd7", "VEDIC TONE YAJURVEDIC KATHAKA INDEPENDENT SVARITA", "svarita", "kathaka", 220),
    "\u1cd8": VedicMarkSpec("U+1CD8", "\u1cd8", "VEDIC TONE CANDRA BELOW", "anudatta", "yajurveda", 220),
    "\u1cd9": VedicMarkSpec("U+1CD9", "\u1cd9", "VEDIC TONE YAJURVEDIC KATHAKA INDEPENDENT SVARITA SCHROEDER", "svarita", "kathaka", 220),
    "\u1cda": VedicMarkSpec("U+1CDA", "\u1cda", "VEDIC TONE DOUBLE SVARITA", "svarita_double", "yajurveda_rgveda", 230),
    "\u1cdb": VedicMarkSpec("U+1CDB", "\u1cdb", "VEDIC TONE TRIPLE SVARITA", "svarita_triple", "yajurveda", 230),
    "\u1cdc": VedicMarkSpec("U+1CDC", "\u1cdc", "VEDIC TONE KATHAKA ANUDATTA", "anudatta", "kathaka", 220),
    "\u1cdd": VedicMarkSpec("U+1CDD", "\u1cdd", "VEDIC TONE DOT BELOW", "anudatta", "yajurveda", 220),
    "\u1ce0": VedicMarkSpec("U+1CE0", "\u1ce0", "VEDIC TONE RIGVEDIC KASHMIRI INDEPENDENT SVARITA", "svarita", "rgveda_kashmiri", 230),
    "\u1ce1": VedicMarkSpec("U+1CE1", "\u1ce1", "VEDIC TONE ATHARVAVEDIC INDEPENDENT SVARITA", "svarita", "atharvaveda", 0),
    "\u1ce2": VedicMarkSpec("U+1CE2", "\u1ce2", "VEDIC SIGN VISARGA SVARITA", "nasal_or_breath", "pan_vedic", 1),
    "\u1ce9": VedicMarkSpec("U+1CE9", "\u1ce9", "VEDIC SIGN ANUSVARA ANTARGOMUKHA", "nasal_or_breath", "yajurveda", 0),
    "\u1cf2": VedicMarkSpec("U+1CF2", "\u1cf2", "VEDIC SIGN ARDHAVISARGA", "nasal_or_breath", "pan_vedic", 0),
    "\u1cf4": VedicMarkSpec("U+1CF4", "\u1cf4", "VEDIC TONE CANDRA ABOVE", "svarita", "samaveda_yajurveda", 230),
    "\u1cf8": VedicMarkSpec("U+1CF8", "\u1cf8", "VEDIC TONE RING ABOVE", "svarita", "yajurveda", 230),
    "\u1cf9": VedicMarkSpec("U+1CF9", "\u1cf9", "VEDIC TONE DOUBLE RING ABOVE", "svarita_double", "yajurveda", 230),
}

# Explicitly separate U+0969 (DEVANAGARI DIGIT THREE) from tone marks
PLUTA_QUANTITY_CHAR = "\u0969"
SINGLE_DANDA = "\u0964"
DOUBLE_DANDA = "\u0965"

_INDEPENDENT_VOWELS = set("\u0904\u0905\u0906\u0907\u0908\u0909\u090a\u090b\u090c\u090d\u090e\u090f\u0910\u0911\u0912\u0913\u0914\u0960\u0961")
_MATRA_TO_VOWEL: Dict[str, str] = {
    "\u093e": "\u0906",  # ा -> आ
    "\u093f": "\u0907",  # ि -> इ
    "\u0940": "\u0908",  # ी -> ई
    "\u0941": "\u0909",  # ु -> उ
    "\u0942": "\u090a",  # ू -> ऊ
    "\u0943": "\u090b",  # ृ -> ऋ
    "\u0944": "\u0960",  # ॄ -> ॠ
    "\u0962": "\u090c",  # ॢ -> ऌ
    "\u0963": "\u0961",  # ॣ -> ॡ
    "\u0945": "\u090d",  # ॅ -> ऍ
    "\u0946": "\u090e",  # ॆ -> ऎ
    "\u0947": "\u090f",  # े -> ए
    "\u0948": "\u0910",  # ै -> ऐ
    "\u0949": "\u0911",  # ॉ -> ऑ
    "\u094a": "\u0912",  # ॊ -> ऒ
    "\u094b": "\u0913",  # ो -> ओ
    "\u094c": "\u0914",  # ौ -> औ
}
_VIRAMA = "\u094d"
_CONSONANTS = set(chr(c) for c in range(0x0915, 0x093A)) | set(chr(c) for c in range(0x0958, 0x0960))
_YOGAVAHA = {"\u0901", "\u0902", "\u0903"}

_MARK_CHARS_ESCAPED = "".join(re.escape(k) for k in VEDIC_MARK_REGISTRY)
_AKSHARA_RE = re.compile(
    rf"(?:[\u0915-\u0939\u0958-\u095f]\u094d)*"
    rf"(?:[\u0904-\u0914\u0960-\u0961]|[\u0915-\u0939\u0958-\u095f][\u093a-\u094f\u0962-\u0963]?)"
    rf"[\u0901-\u0903\u0969{_MARK_CHARS_ESCAPED}]*"
)


def is_tone_mark(ch: str) -> bool:
    return ch in VEDIC_MARK_REGISTRY


def strip_vedic_tone_marks(text: str) -> str:
    """Strips registered Vedic tone marks while leaving base script & U+0969 intact."""
    return "".join(ch for ch in text if ch not in VEDIC_MARK_REGISTRY)


def extract_vowel_nucleus(clean_akshara: str) -> Optional[str]:
    """
    Resolves the phonological vowel nucleus of an akshara:
      - Independent vowel -> that vowel (e.g. 'अ')
      - Consonant + matra -> corresponding full vowel (e.g. 'मी' -> 'ई')
      - Consonant without matra or virama -> inherent 'अ' ('\u0905')
      - Halanta consonant (ends with virama) -> None (consonantal coda)
    """
    if not clean_akshara:
        return None
    if clean_akshara.endswith(_VIRAMA):
        return None
    for ch in clean_akshara:
        if ch in _INDEPENDENT_VOWELS:
            return ch
        if ch in _MATRA_TO_VOWEL:
            return _MATRA_TO_VOWEL[ch]
    if any(ch in _CONSONANTS for ch in clean_akshara):
        return "\u0905"
    return None


def segment_vedic_nuclei(text: str) -> Tuple[str, List[Dict[str, object]]]:
    """
    Normalizes input to NFC, preserves raw grapheme clusters, separates U+0969
    as a Pluta quantity flag, and attaches extracted tone marks to the vowel nucleus.
    """
    nfc = unicodedata.normalize("NFC", (text or "").strip())
    matches = list(_AKSHARA_RE.finditer(nfc))
    tokens: List[Dict[str, object]] = []

    for idx, match in enumerate(matches):
        raw_nfc = match.group(0)
        is_pluta = PLUTA_QUANTITY_CHAR in raw_nfc
        no_tone = strip_vedic_tone_marks(raw_nfc)
        clean = no_tone.replace(PLUTA_QUANTITY_CHAR, "")
        if not clean:
            continue

        specs = [VEDIC_MARK_REGISTRY[ch] for ch in raw_nfc if ch in VEDIC_MARK_REGISTRY]
        mark_codes = [s.codepoint for s in specs]
        mark_hint: Optional[str] = None
        for s in specs:
            if s.accent_category in ("svarita_double", "svarita_triple"):
                mark_hint = "svarita_double"
                break
            if s.accent_category in ("svarita", "udatta", "anudatta"):
                mark_hint = s.accent_category

        gap_start = match.end()
        gap_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(nfc)
        gap = nfc[gap_start:gap_end]
        if DOUBLE_DANDA in gap:
            rest_matras = 4.0
        elif SINGLE_DANDA in gap:
            rest_matras = 2.0
        else:
            rest_matras = 0.0

        tokens.append(
            {
                "akshara_nfc": raw_nfc,
                "akshara_clean": clean,
                "vowel_nucleus": extract_vowel_nucleus(clean),
                "mark_hint": mark_hint,
                "unicode_marks": mark_codes,
                "is_pluta": is_pluta,
                "rest_after_matras": rest_matras,
            }
        )
    return nfc, tokens
