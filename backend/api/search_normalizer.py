import re
import unicodedata
from pathlib import Path
from typing import List

DIA_FOLD = {
    "\u0101": "a", "\u012b": "i", "\u016b": "u",
    "\u1e5b": "r", "\u1e5d": "r", "\u1e37": "l", "\u1e39": "l",
    "\u1e45": "n", "\u00f1": "n", "\u1e47": "n",
    "\u015b": "s", "\u1e63": "s",
    "\u1e43": "m", "\u1e21": "m", "\u1e25": "h",
}

TOPIC_EXPANSIONS = {
    "music": ["sangita", "svara", "gita", "gana", "sama"],
    "sangeeta": ["sangita", "svara", "gita"],
    "sangeet": ["sangita", "svara", "gita"],
    "chant": ["mantra", "veda", "svara", "stotra"],
    "fire": ["agni", "vaishvanara", "hutashana"],
    "duty": ["dharma", "karma", "vrata"],
}

def fold_diacritics_and_phonetics(text: str) -> str:
    s = unicodedata.normalize("NFC", text or "").lower()
    folded = []
    for ch in s:
        if unicodedata.combining(ch):
            continue
        folded.append(DIA_FOLD.get(ch, ch))
    out = "".join(folded)
    # Common transliteration/English phonetic equivalents
    out = out.replace("ee", "i").replace("oo", "u")
    out = re.sub(r"(?<=[a-z])h(?=[a-z])", "", out)
    out = re.sub(r"[^0-9a-z\u0900-\u097f\s]+", " ", out)
    return re.sub(r"\s+", " ", out).strip()

def sanitize_fts_tokens(raw_query: str) -> List[str]:
    norm = fold_diacritics_and_phonetics(raw_query)
    raw_tokens = [t for t in norm.split() if len(t) >= 2]
    expanded: List[str] = []
    for tok in raw_tokens:
        if tok not in expanded:
            expanded.append(tok)
        for extra in TOPIC_EXPANSIONS.get(tok, []):
            if extra not in expanded:
                expanded.append(extra)
    return expanded[:8]

def build_fts5_match_query(raw_query: str) -> str:
    tokens = sanitize_fts_tokens(raw_query)
    if not tokens:
        cleaned = re.sub(r"[^\w\u0900-\u097f]+", "", raw_query or "")
        return f'"{cleaned}"*' if cleaned else ""
    return " OR ".join(f'"{tok}"*' for tok in tokens)
THEME_KEYWORDS = {
    "music": [
        "music", "sangita", "sangeeta", "sangeet", "svara", "swara",
        "gita", "gana", "sama", "samaveda", "gandharva", "vina", "venu",
        "mridanga", "shankha", "raga", "tala", "sruti",
    ],
    "gandharva": ["gandharva", "sangita", "sangeeta", "raga", "sruti", "tala"],
    "instrument": ["vina", "venu", "mridanga", "shankha", "dundubhi", "bheri", "vadya"],
    "chant": ["mantra", "veda", "svara", "stotra", "sama", "rc", "yajus"],
    "fire": ["agni", "vaishvanara", "hutashana", "havya"],
    "duty": ["dharma", "karma", "vrata", "svadharma"],
}

THEME_GLOSSES = {
    "music": "Musical / melodic resonance (svara, gāna, or sāman context)",
    "gandharva": "Gāndharva / melodic-rhythmic art context",
    "instrument": "Sacred or classical sound instrument (vīṇā, veṇu, śaṅkha, or percussion) context",
    "chant": "Vedic recitation, mantra, or stotra context",
    "fire": "Agni / ritual fire offering context",
    "duty": "Dharma, karma, or vowed observance context",
}


def detect_themes(query: str, text: str = "", iast: str = "", source: str = "") -> list[str]:
    """Deterministically infer matching theme tags from query and verse fields."""
    combined = " ".join(
        part for part in (
            fold_diacritics_and_phonetics(query),
            fold_diacritics_and_phonetics(iast),
            fold_diacritics_and_phonetics(text),
            fold_diacritics_and_phonetics(source),
        )
        if part
    )
    tokens = set(combined.split())
    matched: list[str] = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(
            kw in tokens
            or any(tok.startswith(kw) for tok in tokens if len(kw) >= 4)
            for kw in keywords
        ):
            matched.append(theme)
    if "samaveda" in combined and "music" not in matched:
        matched.append("music")
    return matched


def build_verse_gloss(themes: list[str], source: str = "", meter: str = "") -> str:
    """Return a concise, deterministic English gloss/context note for a verse."""
    if themes:
        primary = themes[0]
        base = THEME_GLOSSES.get(primary, f"Thematic match: {primary}")
    else:
        base = "Lexical / transliteration match in canonical corpus"
    extras: list[str] = []
    if source:
        extras.append(f"source: {source}")
    if meter:
        extras.append(f"meter: {meter}")
    return f"{base} ({'; '.join(extras)})" if extras else base
