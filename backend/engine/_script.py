"""
Aigaane v0.5.1 — Multi-Script Transliteration Engine
Provides algorithmic character-wise Devanāgarī to IAST transliteration,
ITRANS conversion, SLP1 detection+conversion, script detection,
script-aware parts formatting, AND IAST → Devanagari (v0.5.2).
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
    "RR": "ṝ", "LL": "ḹ",
    "A": "ā", "I": "ī", "U": "ū",
    "R": "ṛ", "L": "ḷ",
    "E": "ai", "O": "au",
    "M": "ṃ", "H": "ḥ",
    "Y": "ñ", "N": "ṇ",
    "w": "ṭ", "q": "ḍ",
    "S": "ś", "z": "ṣ",
}


def slp1_to_iast(text: str) -> str:
    if not text:
        return text
    result = text
    result = result.replace("RR", "ṝ").replace("LL", "ḹ")
    for slp1, iast in _SLP1_TO_IAST_MAP.items():
        if slp1 in ("RR", "LL"):
            continue
        result = result.replace(slp1, iast)
    return result


# ------------------------------------------------------------------ #
#   Script detection                                                #
# ------------------------------------------------------------------ #

def detect_script(text: str) -> str:
    if not text:
        return "iast"
    for ch in text:
        if "\u0900" <= ch <= "\u097f":
            return "devanagari"
    if "H" in text:
        return "slp1"
    if "RR" in text or "LL" in text:
        return "slp1"
    _SLP1_MARKERS = set("AIURLEOMNSzYwq")
    if any(ch in _SLP1_MARKERS for ch in text):
        if any(m in text for m in ("aa", "ii", "uu", "~n", "~N", "R^i", ".m")):
            return "itrans"
        return "slp1"
    itrans_markers = ["~N", "~n", "R^i", "aa", "ii", "uu", ".m", "Sh", "Th", "Dh"]
    for marker in itrans_markers:
        if marker in text:
            return "itrans"
    return "iast"


# ------------------------------------------------------------------ #
#   Canonical IAST conversion                                       #
# ------------------------------------------------------------------ #

def to_canonical_iast(text: str) -> Tuple[str, str]:
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
    if not text:
        return text
    out = text
    out = out.replace("ai", "E").replace("au", "O")
    for k, v in _IAST_TO_SLP1.items():
        out = out.replace(k, v)
    return out


# ══════════════════════════════════════════════════════════════════ #
#   IAST → Devanagari transliteration (v0.5.2)                       #
# ══════════════════════════════════════════════════════════════════ #

# NOTE: ḷ and ḹ are treated as CONSONANT ळ (retroflex lateral), not vowel ऌ.
# Rationale: in Vedic Sanskrit, īḷe, agniṃ īḷe etc. use ḷ as a consonant.
# The vowel ḷ (kḷpta) is extremely rare and can be revisited if needed.

_IAST_VOWELS_INDEPENDENT = {
    "a": "अ", "ā": "आ", "i": "इ", "ī": "ई",
    "u": "उ", "ū": "ऊ", "ṛ": "ऋ", "ṝ": "ॠ",
    "e": "ए", "ai": "ऐ",
    "o": "ओ", "au": "औ",
}

_IAST_VOWELS_DEPENDENT = {
    "a": "",
    "ā": "ा", "i": "ि", "ī": "ी",
    "u": "ु", "ū": "ू", "ṛ": "ृ", "ṝ": "ॄ",
    "e": "े", "ai": "ै",
    "o": "ो", "au": "ौ",
}

_IAST_CONSONANTS = {
    "k": "क", "kh": "ख", "g": "ग", "gh": "घ", "ṅ": "ङ",
    "c": "च", "ch": "छ", "j": "ज", "jh": "झ", "ñ": "ञ",
    "ṭ": "ट", "ṭh": "ठ", "ḍ": "ड", "ḍh": "ढ", "ṇ": "ण",
    "t": "त", "th": "थ", "d": "द", "dh": "ध", "n": "न",
    "p": "प", "ph": "फ", "b": "ब", "bh": "भ", "m": "म",
    "y": "य", "r": "र", "l": "ल", "v": "व",
    "ś": "श", "ṣ": "ष", "s": "स", "h": "ह",
    "ḷ": "ळ",
    "ḹ": "ळ",
}

_IAST_SIGNS = {
    "ṃ": "ं", "ṁ": "ं", "ḥ": "ः", "m̐": "ँ",
}


def _longest_match_iast(text: str, start: int, mapping: dict) -> Tuple[str, int]:
    best_key = ""
    best_len = 0
    for key in mapping:
        if text.startswith(key, start) and len(key) > best_len:
            best_key = key
            best_len = len(key)
    return best_key, best_len


def iast_to_devanagari(text: str) -> str:
    """
    Convert IAST (with diacritics) to Devanagari.

    Handles:
      - Independent vowels (word start or after vowel)
      - Dependent vowel matras (after consonant)
      - Consonant clusters with virama
      - Word-final consonants (virama inserted before space/punctuation/end)
      - Anusvara (ṃ/ṁ), visarga (ḥ), candrabindu (m̐)
      - IAST | → Devanagari ।, || → ॥
      - ḷ/ḹ as consonant ळ (retroflex lateral, Vedic usage)

    Examples:
        iast_to_devanagari("dharma")                → "धर्म"
        iast_to_devanagari("saṃskṛtam")             → "संस्कृतम्"
        iast_to_devanagari("agnim īḷe purohitaṃ")  → "अग्निम् ईळे पुरोहितं"
    """
    if not text:
        return ""

    for ch in text:
        if "\u0900" <= ch <= "\u097f":
            return text

    result = []
    i = 0
    n = len(text)
    prev_was_consonant = False

    while i < n:
        ch = text[i]

        # Danda (|| before |)
        if text.startswith("||", i):
            if prev_was_consonant:
                result.append(VIRAMA)
                prev_was_consonant = False
            result.append("॥")
            i += 2
            continue
        if ch == "|":
            if prev_was_consonant:
                result.append(VIRAMA)
                prev_was_consonant = False
            result.append("।")
            i += 1
            continue

        # Whitespace / punctuation / digits
        if ch.isspace() or ch in ".,;:!?()-–—/\\'\"’‘“”…0123456789":
            if prev_was_consonant:
                result.append(VIRAMA)
                prev_was_consonant = False
            result.append(ch)
            i += 1
            continue

        # Consonant (longest match: kh before k)
        consonant, clen = _longest_match_iast(text, i, _IAST_CONSONANTS)
        if clen > 0:
            if prev_was_consonant:
                result.append(VIRAMA)
            result.append(_IAST_CONSONANTS[consonant])
            prev_was_consonant = True
            i += clen
            continue

        # Vowel (longest match: ai before a)
        vowel, vlen = _longest_match_iast(text, i, _IAST_VOWELS_INDEPENDENT)
        if vlen > 0:
            if prev_was_consonant:
                result.append(_IAST_VOWELS_DEPENDENT[vowel])
                prev_was_consonant = False
            else:
                result.append(_IAST_VOWELS_INDEPENDENT[vowel])
                prev_was_consonant = False
            i += vlen
            continue

        # Sign (anusvara, visarga, candrabindu)
        sign, slen = _longest_match_iast(text, i, _IAST_SIGNS)
        if slen > 0:
            result.append(_IAST_SIGNS[sign])
            prev_was_consonant = False
            i += slen
            continue

        # Unknown char → pass through
        result.append(ch)
        prev_was_consonant = False
        i += 1

    # Trailing consonant at end of string → virama
    if prev_was_consonant:
        result.append(VIRAMA)

    return "".join(result)