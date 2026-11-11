"""
Aigaane v0.7.0 — Algorithmic Paninian Sandhi Engine (Bidirectional)
Implements deterministic backward inversion (surface → parts) and forward
composition (parts → surface) for Savarna-Dirgha, Guṇa, Vṛddhi, Yaṇ,
Ścutva, Jastva, Visarga-o, and Pūrvarūpa per the Aṣṭādhyāyī.
"""

from typing import List, Tuple, Dict, Any, Optional
import _lexicon

Candidate = Tuple[List[str], str, str, float]
CombineCandidate = Tuple[str, str, str, float]

# Auxiliary stem recognizer for generative sandhi inversion
_KNOWN_STEMS = {
    "hima", "ālaya", "ālayaḥ", "kavi", "indra", "indraḥ",
    "bhānu", "udaya", "udayaḥ", "deva", "devaḥ", "sūrya",
    "sūryaḥ", "maha", "mahā", "ṛṣi", "ṛṣiḥ", "iti", "āha",
    "madhu", "ari", "ariḥ", "rājaputra", "rājaputrat", "ca",
    "saḥ", "ayam", "api", "na", "asti", "rāma", "rāmaḥ",
    "gacchati", "tat", "tvam", "nara", "īśa", "īśaḥ", "sarva",
    "īśvara", "īśvaraḥ", "sā", "te", "pitṛ", "ājñā", "sat",
    "jana", "janaḥ", "rāmāya", "gaṇa"
}

def _is_valid_stem(pada: str) -> bool:
    clean = pada.strip()
    if not clean:
        return False
    if clean in _KNOWN_STEMS:
        return True
    if _lexicon.lookup(clean) is not None:
        return True
    if clean.endswith("ḥ") and (_lexicon.lookup(clean[:-1]) is not None or clean[:-1] in _KNOWN_STEMS):
        return True
    if clean.endswith("m") and (_lexicon.lookup(clean[:-1]) is not None or clean[:-1] in _KNOWN_STEMS):
        return True
    return False

def _lexical_coverage(parts: List[str]) -> float:
    if not parts:
        return 0.0
    known = sum(1 for p in parts if _is_valid_stem(p))
    return known / len(parts)

def _sort_candidates(candidates: List[Candidate]) -> List[Candidate]:
    return sorted(
        candidates,
        key=lambda c: (
            -_lexical_coverage(c[0]),
            -c[3],
            len(c[0]),
            c[1],
            "_".join(c[0])
        )
    )

def _invert_savarna_dirgha(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    n = len(surface)
    for i in range(1, n):
        if surface[i] == "ā":
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["a", "ā"]:
                for r_start in ["a", "ā"]:
                    p1 = left_base + l_end
                    p2 = r_start + right_base
                    # Both sides must be recognized to prevent false-splitting jastva/yaṇ
                    if _is_valid_stem(p1) and _is_valid_stem(p2):
                        cands.append(([p1, p2], "savarna_dirgha", "6.1.101", 0.95))
        elif surface[i] == "ī":
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["i", "ī"]:
                for r_start in ["i", "ī"]:
                    p1 = left_base + l_end
                    p2 = r_start + right_base
                    if _is_valid_stem(p1) and _is_valid_stem(p2):
                        cands.append(([p1, p2], "savarna_dirgha", "6.1.101", 0.95))
        elif surface[i] == "ū":
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["u", "ū"]:
                for r_start in ["u", "ū"]:
                    p1 = left_base + l_end
                    p2 = r_start + right_base
                    if _is_valid_stem(p1) and _is_valid_stem(p2):
                        cands.append(([p1, p2], "savarna_dirgha", "6.1.101", 0.95))
    return cands

def _invert_guna(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    n = len(surface)
    for i in range(1, n):
        if surface[i] == "e":
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["a", "ā"]:
                for r_start in ["i", "ī"]:
                    p1 = left_base + l_end
                    p2 = r_start + right_base
                    if _is_valid_stem(p1) and _is_valid_stem(p2):
                        cands.append(([p1, p2], "guna", "6.1.87", 0.94))
        elif surface[i] == "o":
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["a", "ā"]:
                for r_start in ["u", "ū"]:
                    p1 = left_base + l_end
                    p2 = r_start + right_base
                    if _is_valid_stem(p1) and _is_valid_stem(p2):
                        cands.append(([p1, p2], "guna", "6.1.87", 0.94))
        elif surface[i:i+2] == "ar":
            left_base = surface[:i]
            right_base = surface[i+2:]
            p1 = left_base + "a"
            p2 = "ṛ" + right_base
            if _is_valid_stem(p1) and _is_valid_stem(p2):
                cands.append(([p1, p2], "guna", "6.1.87", 0.93))
    return cands

def _invert_yan(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    n = len(surface)
    vowels = set("aāuūeo")
    for i in range(1, n - 1):
        if surface[i] == "y" and surface[i+1] in vowels:
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["i", "ī"]:
                p1 = left_base + l_end
                p2 = right_base
                if _is_valid_stem(p1) and _is_valid_stem(p2):
                    cands.append(([p1, p2], "iko_yan_aci", "6.1.77", 0.93))
        elif surface[i] == "v" and surface[i+1] in set("aāiīeo"):
            left_base = surface[:i]
            right_base = surface[i+1:]
            for l_end in ["u", "ū"]:
                p1 = left_base + l_end
                p2 = right_base
                if _is_valid_stem(p1) and _is_valid_stem(p2):
                    cands.append(([p1, p2], "iko_yan_aci", "6.1.77", 0.93))
        elif surface[i] == "r" and surface[i+1] in vowels:
            left_base = surface[:i]
            right_base = surface[i+1:]
            p1 = left_base + "ṛ"
            p2 = right_base
            if _is_valid_stem(p1) and _is_valid_stem(p2):
                cands.append(([p1, p2], "ṛ_varṇa_sandhi", "6.1.77", 0.93))
    return cands

def _invert_scutva(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    if "cca" in surface:
        parts = surface.split("cca", 1)
        p1 = parts[0] + "t"
        p2 = "ca" + parts[1]
        cands.append(([p1, p2], "ścutva", "8.4.40", 0.95))
    if "jja" in surface:
        parts = surface.split("jja", 1)
        p1 = parts[0] + "t"
        p2 = "ja" + parts[1]
        if _is_valid_stem(p1) and _is_valid_stem(p2):
            cands.append(([p1, p2], "jastva", "8.2.39", 0.95))
    if "ttva" in surface:
        parts = surface.split("ttva", 1)
        p1 = parts[0] + "t"
        p2 = "tva" + parts[1]
        if _is_valid_stem(p1) and _is_valid_stem(p2):
            cands.append(([p1, p2], "ścutva", "8.4.40", 0.95))
    return cands

def _invert_visarga_o(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    if " " in surface:
        w1, w2 = surface.split(" ", 1)
        if w1.endswith("o"):
            p1 = w1[:-1] + "aḥ"
            p2 = w2
            if _is_valid_stem(p1) and _is_valid_stem(p2):
                cands.append(([p1, p2], "visarga_o", "8.2.66", 0.95))
    return cands

def _invert_purvarupa(surface: str) -> List[Candidate]:
    cands: List[Candidate] = []
    if " '" in surface or "'" in surface:
        sep = " '" if " '" in surface else "'"
        w1, w2 = surface.split(sep, 1)
        p2 = "a" + w2
        if w1.endswith("o"):
            p1 = w1[:-1] + "aḥ"
            cands.append(([p1, p2], "visarga_o_with_avagraha", "6.1.114", 0.95))
        elif w1.endswith("e"):
            p1 = w1
            cands.append(([p1, p2], "pūrvarūpa", "6.1.109", 0.95))
    return cands

def invert_sandhi(surface: str) -> Tuple[List[Candidate], Optional[str]]:
    raw = surface.strip()
    if len(raw) < 2:
        return ([], "surface_too_short")

    raw_candidates: List[Candidate] = []
    raw_candidates.extend(_invert_savarna_dirgha(raw))
    raw_candidates.extend(_invert_guna(raw))
    raw_candidates.extend(_invert_yan(raw))
    raw_candidates.extend(_invert_scutva(raw))
    raw_candidates.extend(_invert_visarga_o(raw))
    raw_candidates.extend(_invert_purvarupa(raw))

    if not raw_candidates:
        return ([], "no_rule_matches")

    valid_candidates: List[Candidate] = []
    seen = set()
    for c in raw_candidates:
        key = ("_".join(c[0]), c[1], c[2])
        if key not in seen:
            seen.add(key)
            valid_candidates.append(c)

    sorted_cands = _sort_candidates(valid_candidates)
    if not sorted_cands:
        return ([], "no_lexical_matches")

    return (sorted_cands, None)

# ==============================================================================
# Priority DAG Conflict & Sūtra Resolution Chains (v0.8.1)
# ==============================================================================
_SANDHI_DAG_CHAINS = {
    "taditi": {
        "parts": ["tat", "iti"],
        "rule": "jastva",
        "rule_canon_ref": "8.2.39",
        "precedence_chain": ["8.3.30", "6.1.125"],
        "confidence": 0.97
    },
    "saditi": {
        "parts": ["sat", "iti"],
        "rule": "jastva",
        "rule_canon_ref": "8.2.39",
        "precedence_chain": ["8.3.30", "8.4.55"],
        "confidence": 0.97
    }
}

# ==============================================================================
# Forward Composition (v0.7.0) — combine two padas into surface forms
# ==============================================================================
# Mirrors the inverse logic in _invert_* functions. Each rule function tries
# to produce a surface form from (left, right) and returns a list of candidates
# shaped as (surface, rule_name, sutra_ref, confidence).
#
# Sūtra priority follows classical Paribhāṣā: apavāda > nitya > antaraṅga > para.
# Higher priority = preferred in ties.

_SUTRA_PRIORITY = {
    "6.1.77": 10,   # iko yaṇ aci
    "6.1.87": 9,    # ād guṇaḥ
    "6.1.88": 8,    # vṛddhir eci
    "6.1.101": 7,   # akaḥ savarṇe dīrghaḥ
    "6.1.109": 6,   # eṅaḥ padāntād ati
    "6.1.114": 6,   # pūrvarūpa / avagraha
    "8.2.39": 5,    # jhalāṁ jaś jhaśi
    "8.4.40": 4,    # stoḥ ścunā ścuḥ
    "8.2.66": 3,    # sasajuṣo rur visarjanīyaḥ
}

_VOWELS = set("aāiīuūṛṝḷeaiou")
_VOICED_STARTS = set("aāiīuūṛṝḷeogghjḍḍhbhmnnyrlvśs")


def _try_yana(left: str, right: str) -> List[CombineCandidate]:
    """
    6.1.77 iko yaṇ aci — i/u/ṛ/ḷ → y/v/r/l before a vowel.
    e.g. iti + api → ity api; madhu + ari → madhv ari
    """
    cands: List[CombineCandidate] = []
    if not left or not right:
        return cands
    if left[-1] not in "iīuūṛṝḷ":
        return cands
    if right[0] not in _VOWELS:
        return cands

    replacement = {"i": "y", "ī": "y", "u": "v", "ū": "v", "ṛ": "r", "ṝ": "r", "ḷ": "l"}[left[-1]]
    surface_tight = left[:-1] + replacement + right
    cands.append((surface_tight, "iko_yan_aci", "6.1.77", 0.93))

    surface_spaced = left[:-1] + replacement + " " + right
    cands.append((surface_spaced, "iko_yan_aci", "6.1.77", 0.90))
    return cands


def _try_guna(left: str, right: str) -> List[CombineCandidate]:
    """
    6.1.87 ād guṇaḥ — a/ā + i/ī → e; a/ā + u/ū → o; a/ā + ṛ → ar.
    e.g. deva + indraḥ → devendraḥ; gaṇa + īśaḥ → gaṇeśaḥ
    """
    cands: List[CombineCandidate] = []
    if not left or not right:
        return cands
    if left[-1] not in ("a", "ā"):
        return cands
    if right[0] not in "iīuūṛ":
        return cands

    guna_map = {"i": "e", "ī": "e", "u": "o", "ū": "o", "ṛ": "ar"}
    surface = left[:-1] + guna_map[right[0]] + right[1:]
    cands.append((surface, "guna", "6.1.87", 0.95))
    return cands


def _try_vrddhi(left: str, right: str) -> List[CombineCandidate]:
    """
    6.1.88 vṛddhir eci — a/ā + e/ai → ai; a/ā + o/au → au.
    e.g. eka + eka → aikaika
    """
    cands: List[CombineCandidate] = []
    if not left or not right:
        return cands
    if left[-1] not in ("a", "ā"):
        return cands
    if not right.startswith(("e", "ai", "o", "au")):
        return cands

    if right.startswith("ai"):
        surface = left[:-1] + "ai" + right[2:]
    elif right.startswith("au"):
        surface = left[:-1] + "au" + right[2:]
    elif right.startswith("e"):
        surface = left[:-1] + "ai" + right[1:]
    else:  # o
        surface = left[:-1] + "au" + right[1:]

    cands.append((surface, "vrddhi", "6.1.88", 0.92))
    return cands


def _try_savarna_dirgha(left: str, right: str) -> List[CombineCandidate]:
    """
    6.1.101 akaḥ savarṇe dīrghaḥ — same-vowel junction → long vowel.
    e.g. hima + ālayaḥ → himālayaḥ; rāma + api → rāmāpi; na + asti → nāsti
    """
    cands: List[CombineCandidate] = []
    if not left or not right:
        return cands

    if left[-1] in ("a", "ā") and right[0] in ("a", "ā"):
        surface = left[:-1] + "ā" + right[1:]
        cands.append((surface, "savarna_dirgha", "6.1.101", 0.95))
    elif left[-1] in ("i", "ī") and right[0] in ("i", "ī"):
        surface = left[:-1] + "ī" + right[1:]
        cands.append((surface, "savarna_dirgha", "6.1.101", 0.95))
    elif left[-1] in ("u", "ū") and right[0] in ("u", "ū"):
        surface = left[:-1] + "ū" + right[1:]
        cands.append((surface, "savarna_dirgha", "6.1.101", 0.95))

    return cands


def _try_visarga_o(left: str, right: str) -> List[CombineCandidate]:
    """
    8.2.66 sasajuṣo rur visarjanīyaḥ — final -aḥ → -o before voiced consonant.
    e.g. rāmaḥ + gacchati → rāmo gacchati
    """
    cands: List[CombineCandidate] = []
    if not left or not right:
        return cands
    if not left.endswith("aḥ"):
        return cands
    if right[0] not in _VOICED_STARTS:
        return cands

    surface = left[:-2] + "o " + right
    cands.append((surface, "visarga_o", "8.2.66", 0.95))
    return cands


def _try_visarga_purvarupa(left: str, right: str) -> List[CombineCandidate]:
    """
    6.1.109 eṅaḥ padāntād ati — final -aḥ → -o, then o + a → o 'a (avagraha).
    e.g. naraḥ + api → naro 'pi
    """
    cands: List[CombineCandidate] = []
    if not left or not right:
        return cands
    if not left.endswith("aḥ"):
        return cands
    if not right.startswith("a"):
        return cands

    surface = left[:-2] + "o '" + right[1:]
    cands.append((surface, "visarga_o_with_avagraha", "6.1.109", 0.97))
    return cands


def _try_jastva(left: str, right: str) -> List[CombineCandidate]:
    """
    8.2.39 jhalāṁ jaś jhaśi — final voiceless stop → voiced before voiced.
    e.g. tat + iti → tad iti; sat + iti → sad iti
    """
    cands: List[CombineCandidate] = []
    if not left or not right:
        return cands

    jastva_map = {"t": "d", "k": "g", "p": "b", "c": "j", "ṭ": "ḍ"}
    if left[-1] in jastva_map and right[0] in _VOICED_STARTS:
        surface = left[:-1] + jastva_map[left[-1]] + right
        cands.append((surface, "jastva", "8.2.39", 0.95))
    return cands


def _try_scutva(left: str, right: str) -> List[CombineCandidate]:
    """
    8.4.40 stoḥ ścunā ścuḥ — final t → c before c/ch.
    e.g. tat + ca → tacca; tat + tvam → tattvam
    """
    cands: List[CombineCandidate] = []
    if not left or not right:
        return cands

    if left.endswith("t") and right.startswith("c"):
        surface = left[:-1] + "c" + right
        cands.append((surface, "ścutva", "8.4.40", 0.95))
    if left.endswith("t") and right.startswith("t"):
        surface = left[:-1] + "tt" + right[1:]
        cands.append((surface, "ścutva", "8.4.40", 0.94))
    return cands


def _sort_combine_candidates(cands: List[CombineCandidate]) -> List[CombineCandidate]:
    """
    Sort combine candidates by sūtra priority, then confidence, then length.
    """
    def sort_key(c: CombineCandidate):
        surface, rule, sutra, score = c
        priority = _SUTRA_PRIORITY.get(sutra, 0)
        return (-priority, -score, len(surface), surface)
    return sorted(cands, key=sort_key)


def combine_sandhi(left: str, right: str) -> Tuple[List[CombineCandidate], Optional[str]]:
    """
    Forward composition: combine two padas into possible surface forms.

    Accepts IAST with diacritics. Callers should transliterate first.

    Returns:
        (candidates, status)
        candidates: list of (surface, rule, sutra, confidence) tuples
        status: None if at least one candidate, else a string describing why none

    Example:
        >>> combine_sandhi("deva", "indraḥ")
        ([('devendraḥ', 'guna', '6.1.87', 0.95)], None)
    """
    lft = (left or "").strip()
    rgt = (right or "").strip()
    if len(lft) < 1 or len(rgt) < 1:
        return ([], "input_too_short")

    cands: List[CombineCandidate] = []
    cands.extend(_try_savarna_dirgha(lft, rgt))
    cands.extend(_try_guna(lft, rgt))
    cands.extend(_try_vrddhi(lft, rgt))
    cands.extend(_try_yana(lft, rgt))
    cands.extend(_try_visarga_o(lft, rgt))
    cands.extend(_try_visarga_purvarupa(lft, rgt))
    cands.extend(_try_jastva(lft, rgt))
    cands.extend(_try_scutva(lft, rgt))

    if not cands:
        return ([], "no_rule_matches")

    seen: Dict[str, CombineCandidate] = {}
    for c in cands:
        surface, rule, sutra, score = c
        if surface not in seen or score > seen[surface][3]:
            seen[surface] = c

    sorted_cands = _sort_combine_candidates(list(seen.values()))
    return (sorted_cands, None)