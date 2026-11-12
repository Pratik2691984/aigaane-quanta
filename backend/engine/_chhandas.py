"""
Aigaane v0.3.0 — Category G & J Chhandas Prosody Engine
25 classical Sanskrit meters (20 classical + 5 Vedic) with Piṅgala-style
syllable weight detection.

Priority 3 (Q5-B) added:
  - pathyā-triṣṭubh (Vedic Triṣṭubh variant A)
  - vipulā-triṣṭubh (Vedic Triṣṭubh variant B)
  - pathyā-jagatī (Vedic Jagatī variant A)
  - āpīḍā-jagatī (Vedic Jagatī variant B)
  - mahāpankti (rare Vedic 4×10 meter)
"""

import unicodedata
from typing import Optional, Dict, List

# ==============================================================================
# METER TABLE — 25 meters (20 classical + 5 Vedic)
# ==============================================================================
# Each entry defines:
#   - canon_name: source text
#   - reference_locator: traditional description
#   - syllables: total syllables for the complete verse
#   - quarters: number of pādas
#   - syllables_per_quarter: int OR "N+M" pattern for mixed meters
#   - varna_pattern: optional L/G pattern string (G=Guru, L=Laghu) for identification
# ==============================================================================

_CHHANDAS_TABLE: Dict[str, dict] = {
    # === Samavṛtta (all 4 pādas same) ===
    "gāyatrī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "gāyatrī 3×8",
        "syllables": 24, "quarters": 3, "syllables_per_quarter": 8,
    },
    "anuṣṭubh": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "anuṣṭubh 4×8",
        "syllables": 32, "quarters": 4, "syllables_per_quarter": 8,
    },
    "triṣṭubh": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "triṣṭubh 4×11",
        "syllables": 44, "quarters": 4, "syllables_per_quarter": 11,
    },
    "jagatī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "jagatī 4×12",
        "syllables": 48, "quarters": 4, "syllables_per_quarter": 12,
    },
    "pankti": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "pankti 5×8",
        "syllables": 40, "quarters": 5, "syllables_per_quarter": 8,
    },
    "bṛhatī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "bṛhatī 8+8+12+8",
        "syllables": 36, "quarters": 4, "syllables_per_quarter": "8+8+12+8",
    },
    "uṣṇih": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "uṣṇih 8+8+12",
        "syllables": 28, "quarters": 3, "syllables_per_quarter": "8+8+12",
    },

    # === Triṣṭubh family (11 syllables) ===
    "indravajrā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "indravajrā 4×11",
        "syllables": 44, "quarters": 4, "syllables_per_quarter": 11,
        "varna_pattern": "GGGGGLLLLGGLG",
    },
    "upendravajrā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "upendravajrā 4×11",
        "syllables": 44, "quarters": 4, "syllables_per_quarter": 11,
        "varna_pattern": "GLLGGLLLLGGLG",
    },
    "upajāti": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "upajāti 4×11 (mixed)",
        "syllables": 44, "quarters": 4, "syllables_per_quarter": 11,
    },

    # === Jagatī family (12 syllables) ===
    "vaṃśasthā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "vaṃśasthā 4×12",
        "syllables": 48, "quarters": 4, "syllables_per_quarter": 12,
    },
    "indravaṃśā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "indravaṃśā 4×12",
        "syllables": 48, "quarters": 4, "syllables_per_quarter": 12,
    },

    # === Major classical kāvya meters ===
    "vasantatilakā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "vasantatilakā 4×14",
        "syllables": 56, "quarters": 4, "syllables_per_quarter": 14,
        "varna_pattern": "GGLGLLLGLLGLLG",
    },
    "mālinī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "mālinī 4×15",
        "syllables": 60, "quarters": 4, "syllables_per_quarter": 15,
    },
    "mālabhāriṇī": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "mālabhāriṇī 4×15",
        "syllables": 60, "quarters": 4, "syllables_per_quarter": 15,
    },
    "mandākrāntā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "mandākrāntā 4×17",
        "syllables": 68, "quarters": 4, "syllables_per_quarter": 17,
        "varna_pattern": "GGGGGLLLLGGLGGGLLG",
    },
    "śārdūlavikrīḍita": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "śārdūlavikrīḍita 4×19",
        "syllables": 76, "quarters": 4, "syllables_per_quarter": 19,
        "varna_pattern": "GGGLLGLLGLLGGGLLGGGLG",
    },
    "sragdharā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "sragdharā 4×21",
        "syllables": 84, "quarters": 4, "syllables_per_quarter": 21,
    },
    "puṣpitāgrā": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "puṣpitāgrā 12+13",
        "syllables": 50, "quarters": 4, "syllables_per_quarter": "12+13",
    },
    "vaitālīya": {
        "canon_name": "Chhandaḥśāstra",
        "reference_locator": "vaitālīya 14+16",
        "syllables": 60, "quarters": 4, "syllables_per_quarter": "14+16",
    },

    # ═══════════════════════════════════════════════════════════════════
    # Vedic meters (Priority 3 — Q5-B)
    # ═══════════════════════════════════════════════════════════════════
    # These are the classical Vedic variants of Triṣṭubh and Jagatī.
    # Distinguished from generic triṣṭubh/jagatī by specific varna_pattern
    # cadence (last 4-5 syllables).

    # === Triṣṭubh variants (11 syllables/pāda) ===
    "pathyā-triṣṭubh": {
        "canon_name": "Vedic Chandas",
        "reference_locator": "pathyā-triṣṭubh 4×11 (Vedic)",
        "syllables": 44, "quarters": 4, "syllables_per_quarter": 11,
        "varna_pattern": "GGGGGLLLLGGLG",
    },
    "vipulā-triṣṭubh": {
        "canon_name": "Vedic Chandas",
        "reference_locator": "vipulā-triṣṭubh 4×11 (Vedic)",
        "syllables": 44, "quarters": 4, "syllables_per_quarter": 11,
        "varna_pattern": "GGGGGLLGLGGLG",
    },

    # === Jagatī variants (12 syllables/pāda) ===
    "pathyā-jagatī": {
        "canon_name": "Vedic Chandas",
        "reference_locator": "pathyā-jagatī 4×12 (Vedic)",
        "syllables": 48, "quarters": 4, "syllables_per_quarter": 12,
        "varna_pattern": "GGGGGLLLLGGLLG",
    },
    "āpīḍā-jagatī": {
        "canon_name": "Vedic Chandas",
        "reference_locator": "āpīḍā-jagatī 4×12 (Vedic)",
        "syllables": 48, "quarters": 4, "syllables_per_quarter": 12,
        "varna_pattern": "GGGGGLLGLGGLLG",
    },

    # === Mahāpankti (10 syllables/pāda — rare Vedic) ===
    "mahāpankti": {
        "canon_name": "Vedic Chandas",
        "reference_locator": "mahāpankti 4×10 (Vedic)",
        "syllables": 40, "quarters": 4, "syllables_per_quarter": 10,
        "varna_pattern": "GGGLGGGLGGGLGGGL",
    },
}

# ==============================================================================
# SYLLABLE COUNTING
# ==============================================================================

def count_syllables_iast(text: str) -> int:
    """Count syllables by counting vowels (IAST)."""
    clean = unicodedata.normalize("NFC", text.lower().strip())
    clean = clean.replace("ai", "E").replace("au", "O")
    vowel_chars = set("aāiīuūṛṝḷḹeoEO")
    return sum(1 for ch in clean if ch in vowel_chars)


def _compute_weights(text: str) -> List[str]:
    """Compute Piṅgala-style L/G weights for each syllable."""
    s = unicodedata.normalize("NFC", text.lower().strip())

    SHORT_VOWELS = {'a', 'i', 'u', 'ṛ', 'ḷ'}
    LONG_VOWELS = {'ā', 'ī', 'ū', 'ṝ', 'e', 'o'}
    DIPHTHONGS = {'ai', 'au'}
    SIGNS = {'ṃ', 'ḥ'}
    VOWELS = SHORT_VOWELS | LONG_VOWELS | DIPHTHONGS
    ALL_VOWELS = VOWELS | SIGNS

    phonemes = []
    i = 0
    while i < len(s):
        if s[i:i + 2] in DIPHTHONGS:
            phonemes.append(s[i:i + 2])
            i += 2
            continue
        ch = s[i]
        if ch in ALL_VOWELS:
            phonemes.append(ch)
        elif ch.isalpha():
            phonemes.append(ch)
        i += 1

    weights = []
    for idx, p in enumerate(phonemes):
        if p not in VOWELS:
            continue
        if p in LONG_VOWELS or p in DIPHTHONGS:
            weights.append("G")
            continue
        # Short vowel: check following consonants
        consonants = []
        for q in phonemes[idx + 1:]:
            if q in VOWELS:
                break
            consonants.append(q)
        # Guru if: sign follows, or 2+ consonants (closed syllable / saṃyoga)
        if consonants and consonants[0] in SIGNS:
            weights.append("G")
            continue
        if len(consonants) >= 2:
            weights.append("G")
            continue
        weights.append("L")

    return weights


# ==============================================================================
# METER DETECTION
# ==============================================================================

# Syllables-per-pāda → candidate meters (for full-verse matching)
_PADA_COUNT_TO_METERS = {
    # Samavṛtta (uniform pāda length)
    8: ["anuṣṭubh"],
    10: ["mahāpankti"],
    11: ["triṣṭubh", "indravajrā", "upendravajrā", "upajāti"],
    12: ["jagatī", "vaṃśasthā", "indravaṃśā"],
    14: ["vasantatilakā"],
    15: ["mālinī", "mālabhāriṇī"],
    17: ["mandākrāntā"],
    19: ["śārdūlavikrīḍita"],
    21: ["sragdharā"],
}

# Total syllable counts → candidate meters (for full-verse matching)
# Order matters: specific variants first, generic fallbacks last.
_TOTAL_SYLLABLES_TO_METERS = {
    # Vedic
    24: ["gāyatrī"],
    28: ["uṣṇih"],
    36: ["bṛhatī"],
    40: ["pankti", "mahāpankti"],
    # Classical
    32: ["anuṣṭubh"],
    44: ["triṣṭubh", "pathyā-triṣṭubh", "vipulā-triṣṭubh", "indravajrā", "upendravajrā", "upajāti"],
    48: ["jagatī", "pathyā-jagatī", "āpīḍā-jagatī", "vaṃśasthā", "indravaṃśā"],
    50: ["puṣpitāgrā"],
    56: ["vasantatilakā"],
    60: ["mālinī", "mālabhāriṇī", "vaitālīya"],
    68: ["mandākrāntā"],
    76: ["śārdūlavikrīḍita"],
    84: ["sragdharā"],
}


def detect_meter(weights: List[str]) -> Optional[dict]:
    """
    Detect the meter based on L/G weights.

    Strategy:
      1. If pattern matches a known varna_pattern → specific meter
      2. If total syllable count matches a known meter → return candidate
      3. If syllable count matches a per-pāda length → return candidate
      4. Otherwise → None
    """
    n = len(weights)
    pattern = "".join(weights)

    # 1. Try varna pattern match (most specific)
    #    Iterate in reverse to prefer later-added (more specific) meters
    for meter_name, meter_data in reversed(list(_CHHANDAS_TABLE.items())):
        if meter_data.get("varna_pattern") == pattern:
            return {"meter": meter_name, **meter_data, "match_type": "varna_pattern"}

    # 2. Try total syllable count
    if n in _TOTAL_SYLLABLES_TO_METERS:
        candidates = _TOTAL_SYLLABLES_TO_METERS[n]
        # If pattern matches a varna_pattern of any candidate, return that
        for candidate in candidates:
            cdata = _CHHANDAS_TABLE[candidate]
            if cdata.get("varna_pattern") == pattern:
                return {"meter": candidate, **cdata, "match_type": "total_with_pattern"}
        # Otherwise return first candidate
        meter_name = candidates[0]
        return {"meter": meter_name, **_CHHANDAS_TABLE[meter_name], "match_type": "total_syllables"}

    # 3. Try per-pāda (input is a single pāda)
    if n in _PADA_COUNT_TO_METERS:
        candidates = _PADA_COUNT_TO_METERS[n]
        meter_name = candidates[0]
        return {"meter": meter_name, **_CHHANDAS_TABLE[meter_name], "match_type": "pada_syllables"}

    # 4. Half-verse: multiply by 2
    if n * 2 in _TOTAL_SYLLABLES_TO_METERS:
        meter_name = _TOTAL_SYLLABLES_TO_METERS[n * 2][0]
        return {"meter": meter_name, **_CHHANDAS_TABLE[meter_name], "match_type": "half_verse"}

    # 5. Quarter-verse: multiply by 4
    if n * 4 in _TOTAL_SYLLABLES_TO_METERS:
        meter_name = _TOTAL_SYLLABLES_TO_METERS[n * 4][0]
        return {"meter": meter_name, **_CHHANDAS_TABLE[meter_name], "match_type": "quarter_verse"}

    return None


# ==============================================================================
# PUBLIC API
# ==============================================================================

def analyze_verse(surface: str) -> Optional[dict]:
    """
    Analyze a Sanskrit verse and identify its meter.
    Works for full verses, half-verses, single pādas, or single words.
    """
    weights = _compute_weights(surface)
    return detect_meter(weights)


def scan_verse(surface: str) -> dict:
    """
    Full scansion + meter identification.
    Returns weights, syllable count, matra sum, and meter info.
    """
    weights = _compute_weights(surface)
    meter = detect_meter(weights)

    return {
        "surface": surface,
        "weights": weights,
        "pattern": "".join(weights),
        "syllable_count": len(weights),
        "matra_sum": sum(2 if w == "G" else 1 for w in weights),
        "meter": meter,
    }


def lookup(surface: str) -> Optional[dict]:
    """Legacy alias for analyze_verse."""
    return analyze_verse(surface)