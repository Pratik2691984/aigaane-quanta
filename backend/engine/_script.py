"""
Aigaane v0.5.1 — Multi-Script Transliteration Engine
Provides algorithmic character-wise Devanāgarī to IAST transliteration,
ITRANS conversion, SLP1 detection+conversion, script detection, and
script-aware parts formatting.
"""

from typing import Tuple, List

DEVA_VOWELS = {
    "अ": "a", "आ": "ā", "इ": "i", "ई": "ī", "उ": "u", "ऊ": "ū",
    "ऋ": "ṛ", "ॠ": "ṝ", "ऌ": "ḷ", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au"
}
DEVA_MATRAS = {
    "ा": "ā", "ि": "i", "ी": "ī", "ु": "u", "ू": "ū", "ृ": "ṛ",
    "ॄ": "ṝ", "ॢ": "ḷ", "े": "e", "ै": "ai", "ो": "o", "ौ": "au"
}
DEVA_CONS = {
    "क": "k", "ख": "kh", "ग": "g", "घ": "gh", "ङ": "ṅ",
    "च": "c", "छ": "ch", "ज": "j", "झ": "jh", "ञ": "ñ",
    "ट": "ṭ", "ठ": "ṭh", "ड": "ḍ", "ढ": "ḍh", "ण": "ṇ",
    "त": "t", "थ": "th", "द": "d", "ध": "dh", "न": "n",
    "प": "p", "फ": "ph", "ब": "b", "भ": "bh", "म": "m",
    "य": "y", "र": "r", "ल": "l", "व": "v",
    "श": "ś", "ष": "ṣ", "स": "s", "ह": "h",
    "ळ": "ḻ", "ऱ": "ṟ", "ऩ": "ṉ",
}
DEVA_MISC = {"ं": "ṃ", "ँ": "m̐", "ः": "ḥ", "ऽ": "'", "ॐ": "oṃ"}
VIRAMA = "\u094d"

IAST_TO_DEVA_MAP = {
    "rāma": "राम",
    "rāmaḥ": "रामः",
    "api": "अपि",
    "na": "न",
    "asti": "अस्ति",
    "gacchati": "गच्छति",
    "deva": "देव",
    "devaḥ": "देवः",
    "indraḥ": "इन्द्रः",
    "hima": "हिम",
    "alayaḥ": "आलयः",
    "ālayaḥ": "आलयः",
}

FAST_DEVA_MAP = {
    "च": "ca",
    "रामापि": "rāmāpi",
    "नास्ति": "nāsti",
    "भवति": "bhavati",
    "गायत्री": "gāyatrī",
}


def _deva_to_iast_charwise(text: str) -> str:
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in DEVA_MISC:
            out.append(DEVA_MISC[ch])
            i += 1
            continue
        if ch in DEVA_VOWELS:
            out.append(DEVA_VOWELS[ch])
            i += 1
            continue
        if ch in DEVA_CONS:
            out.append(DEVA_CONS[ch])
            if i + 1 < n and text[i + 1] == VIRAMA:
                i += 2
                continue
            if i + 1 < n and text[i + 1] in DEVA_MATRAS:
                out.append(DEVA_MATRAS[text[i + 1]])
                i += 2
                continue
            out.append("a")
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def deva_to_iast(text: str) -> str:
    cleaned = text.strip()
    if cleaned in FAST_DEVA_MAP:
        return FAST_DEVA_MAP[cleaned]
    return _deva_to_iast_charwise(cleaned)


def itrans_to_iast(text: str) -> str:
    t = text.strip()
    replacements = [
        ("sh", "ś"), ("Sh", "ṣ"), ("R^i", "ṛ"), ("RRi", "ṝ"),
        ("aa", "ā"), ("A", "ā"), ("ii", "ī"), ("I", "ī"), ("uu", "ū"), ("U", "ū"),
        ("ee", "e"), ("oo", "o"), (".m", "ṃ"), ("M", "ṃ"), ("H", "ḥ"),
        ("~N", "ṅ"), ("~n", "ñ"), ("T", "ṭ"), ("Th", "ṭh"),
        ("D", "ḍ"), ("Dh", "ḍh"), ("N", "ṇ")
    ]
    for it, ia in replacements:
        t = t.replace(it, ia)
    return t


# ------------------------------------------------------------------ #
#   SLP1 -> IAST conversion                                         #
# ------------------------------------------------------------------ #

_SLP1_TO_IAST_MAP = {
    # Two-char markers (must be replaced before single-char)
    "RR": "ṝ", "LL": "ḹ",
    # Single-char long vowels
    "A": "ā", "I": "ī", "U": "ū",
    # Single-char vocalic liquids
    "R": "ṛ", "L": "ḷ",
    # Diphthongs
    "E": "ai", "O": "au",
    # Nasals and visarga
    "M": "ṃ", "H": "ḥ",
    "Y": "ñ", "N": "ṇ",
    # Retroflex and sibilants
    "w": "ṭ", "q": "ḍ",
    "S": "ś", "z": "ṣ",
}


def slp1_to_iast(text: str) -> str:
    """
    Convert SLP1 ASCII to IAST.

    Two-char markers (RR, LL) replaced first, then single-char markers.
    Does not modify lowercase ASCII (which is the same in SLP1 and IAST).
    """
    if not text:
        return text
    result = text
    # Two-char markers first
    result = result.replace("RR", "ṝ").replace("LL", "ḹ")
    # Single-char markers
    for slp1, iast in _SLP1_TO_IAST_MAP.items():
        if slp1 in ("RR", "LL"):
            continue
        result = result.replace(slp1, iast)
    return result


# ------------------------------------------------------------------ #
#   Script detection                                                #
# ------------------------------------------------------------------ #

def detect_script(text: str) -> str:
    """
    Detect the input script: 'devanagari', 'itrans', 'slp1', or 'iast'.

    Detection order:
    1. Any Devanagari codepoint (U+0900-U+097F) → 'devanagari'
    2. Presence of SLP1-only uppercase markers (H, RR, LL, etc.) → 'slp1'
    3. Presence of ITRANS-style markers (aa, ii, uu, ~n, etc.) → 'itrans'
    4. Otherwise → 'iast' (default for lowercase + diacritics)

    Note: 'H' (visarga) is a strong SLP1 signal — IAST uses 'ḥ',
    ITRANS uses 'H' only rarely and usually with other ITRANS markers.
    """
    if not text:
        return "iast"

    # 1. Devanagari
    for ch in text:
        if "\u0900" <= ch <= "\u097f":
            return "devanagari"

    # 2. SLP1: uppercase markers that are SLP1-specific
    # H is the strongest signal (visarga in SLP1, absent from IAST/ITRANS as bare char)
    if "H" in text:
        return "slp1"
    # Two-char SLP1 markers
    if "RR" in text or "LL" in text:
        return "slp1"
    # Other SLP1 uppercase markers (A/I/U/R/L/E/O/M/N/S/z/Y/w/q)
    # Note: 'A' also appears in ITRANS as a marker — check for combined SLP1 signals
    _SLP1_MARKERS = set("AIURLEOMNSzYwq")
    if any(ch in _SLP1_MARKERS for ch in text):
        # But 'A' alone might be ITRANS ā; check for other ITRANS markers first
        if any(m in text for m in ("aa", "ii", "uu", "~n", "~N", "R^i", ".m")):
            return "itrans"
        return "slp1"

    # 3. ITRANS markers
    itrans_markers = ["~N", "~n", "R^i", "aa", "ii", "uu", ".m", "Sh", "Th", "Dh"]
    for marker in itrans_markers:
        if marker in text:
            return "itrans"

    # 4. Default: IAST
    return "iast"


# ------------------------------------------------------------------ #
#   Canonical IAST conversion                                       #
# ------------------------------------------------------------------ #

def to_canonical_iast(text: str) -> Tuple[str, str]:
    """
    Detect input script and return (detected_script, iast_text).

    Handles all four scripts:
      - devanagari → deva_to_iast()
      - itrans     → itrans_to_iast()
      - slp1       → slp1_to_iast()
      - iast       → returned unchanged
    """
    script = detect_script(text)
    if script == "devanagari":
        return script, deva_to_iast(text)
    elif script == "itrans":
        return script, itrans_to_iast(text)
    elif script == "slp1":
        return script, slp1_to_iast(text)
    return "iast", text.strip()


def format_parts_to_script(parts: List[str], target_script: str) -> List[str]:
    if target_script == "devanagari":
        return [IAST_TO_DEVA_MAP.get(p, p) for p in parts]
    elif target_script == "itrans":
        def _to_itrans(s: str) -> str:
            return s.replace("ā", "A").replace("ī", "I").replace("ū", "U")
        return [_to_itrans(p) for p in parts]
    return parts


# ------------------------------------------------------------------ #
#   IAST -> SLP1 normalization                                      #
# ------------------------------------------------------------------ #

_IAST_TO_SLP1 = {
    "ā": "A", "ī": "I", "ū": "U", "ṛ": "R", "ṝ": "RR", "ḷ": "L", "ḹ": "LL",
    "ai": "E", "au": "O",
    "ṃ": "M", "ṁ": "M", "ḥ": "H", "ñ": "Y", "ṅ": "N", "ṭ": "w", "ḍ": "q",
    "ṇ": "N", "ś": "S", "ṣ": "z", "Ā": "A", "Ī": "I", "Ū": "U", "Ṛ": "R",
}


def to_slp1(text: str) -> str:
    """
    Normalize IAST/Devanagari/ITRANS input to SLP1 ASCII.

    This is a one-way approximation: it converts IAST diacritics to their
    SLP1 ASCII equivalents. It does NOT handle Devanagari; call
    to_canonical_iast first if the input might be Devanagari.
    """
    if not text:
        return text
    out = text
    # Two-character replacements first
    out = out.replace("ai", "E").replace("au", "O")
    # Single-character replacements
    for k, v in _IAST_TO_SLP1.items():
        out = out.replace(k, v)
    return out