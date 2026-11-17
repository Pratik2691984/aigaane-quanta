"""
Contextual Sanskrit & Vedic Allophone Realization (P1-2).

Enforces three core Śikṣā phonetic invariants:
  1. Zero Schwa Deletion: word-final and medial short 'a' (अ) is ALWAYS
     preserved as a 1-mātrā vowel nucleus (never deleted as in Hindi).
  2. Contextual Visarga (ः):
       - before k/kh -> Jihvāmūlīya (ᳵ / [x])
       - before p/ph -> Upadhmānīya (ᳶ / [ɸ])
       - before ś/ṣ/s -> homorganic sibilant assimilation
       - at avasāna (pause / । / ॥) -> echo vowel of preceding nucleus
         (e.g., rāmaḥ -> [rɑːmɐhɐ], kaviḥ -> [kɐʋihi], guruḥ -> [ɡuruhu])
  3. Contextual Anusvāra (ं):
       - before sparśa stops -> homorganic nasal (parasavarṇa: ṅ, ñ, ṇ, n, m)
       - before antaḥstha / ūṣman / pause -> anunāsika nasal glide
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from backend.audio.vedic._phoneme_inventory import VARNA_INVENTORY, VarnaSpec, lookup_varna


@dataclass(frozen=True)
class AllophoneToken:
    surface_iast: str
    realized_allophone: str
    ipa: str
    rule_ref: str
    varna: Optional[VarnaSpec]


_NASAL_BY_STHANA = {
    "kanthya": "ṅ",
    "talavya": "ñ",
    "murdhanya": "ṇ",
    "dantya": "n",
    "osthya": "m",
}

_ECHO_VOWEL_IPA = {
    "a": "ɐ",
    "ā": "ɑ",
    "i": "i",
    "ī": "i",
    "u": "u",
    "ū": "u",
    "ṛ": "r̩",
    "ṝ": "r̩",
    "ḷ": "l̩",
    "e": "i",
    "ai": "i",
    "o": "u",
    "au": "u",
}


def tokenize_iast_phonemes(iast_text: str) -> List[str]:
    """
    Segment clean IAST text into maximal Sanskrit phoneme symbols (preserving
    aspirates kh, gh, ch, jh, ṭh, ḍh, th, dh, ph, bh and diphthongs ai, au).
    Preserves final 'a' without schwa deletion.
    """
    text = (iast_text or "").strip()
    tokens: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch.isspace() or ch in "।॥.,'-":
            if ch in ("।", "॥"):
                tokens.append(ch)
            i += 1
            continue
        if i + 1 < n:
            pair = text[i : i + 2]
            if pair in VARNA_INVENTORY:
                tokens.append(pair)
                i += 2
                continue
        if ch in VARNA_INVENTORY:
            tokens.append(ch)
        i += 1
    return tokens


def realize_allophones(phonemes: Sequence[str]) -> List[AllophoneToken]:
    """Map a sequence of IAST phoneme symbols to contextual Śikṣā allophones."""
    out: List[AllophoneToken] = []
    n = len(phonemes)
    last_vowel: Optional[str] = None

    for idx, sym in enumerate(phonemes):
        if sym in ("।", "॥"):
            out.append(AllophoneToken(sym, "avasana_pause", "|", "Pratisakhya avasana", None))
            continue

        nxt: Optional[str] = phonemes[idx + 1] if idx + 1 < n else None
        spec = lookup_varna(sym)
        if spec is not None and spec.group.startswith("svara_"):
            last_vowel = sym

        # 1. Contextual Visarga
        if sym == "ḥ":
            if nxt in ("k", "kh"):
                v = lookup_varna("ḫ")
                out.append(AllophoneToken("ḥ", "jihvamuliya", "x", "Panini 8.3.37 (jihvamuliya)", v))
                continue
            if nxt in ("p", "ph"):
                v = lookup_varna("ɸ")
                out.append(AllophoneToken("ḥ", "upadhmaniya", "ɸ", "Panini 8.3.37 (upadhmaniya)", v))
                continue
            if nxt in ("ś", "ṣ", "s"):
                v = lookup_varna(nxt)
                out.append(AllophoneToken("ḥ", f"visarga_sibilant_{nxt}", v.ipa if v else "h", "Panini 8.3.36", v))
                continue
            if nxt is None or nxt in ("।", "॥"):
                echo = _ECHO_VOWEL_IPA.get(last_vowel or "a", "ɐ")
                out.append(AllophoneToken("ḥ", f"visarga_echo_{last_vowel or 'a'}", f"h{echo}", "Siksa avasana echo-visarga", spec))
                continue
            out.append(AllophoneToken("ḥ", "visarga_glottal", "h", "Default glottal visarga", spec))
            continue

        # 2. Contextual Anusvāra (8.4.58 anusvārasya yayi parasavarṇaḥ)
        if sym == "ṃ":
            nxt_spec = lookup_varna(nxt) if nxt else None
            if nxt_spec is not None and nxt_spec.group.startswith("sparsa_"):
                nasal_sym = _NASAL_BY_STHANA.get(nxt_spec.sthana, "m")
                nasal_spec = lookup_varna(nasal_sym)
                out.append(
                    AllophoneToken(
                        "ṃ",
                        f"parasavarna_{nasal_sym}",
                        nasal_spec.ipa if nasal_spec else "m",
                        "Panini 8.4.58 (parasavarna)",
                        nasal_spec,
                    )
                )
                continue
            out.append(AllophoneToken("ṃ", "anunasika_glide", "w̃", "Panini 8.3.23 (anunasika)", spec))
            continue

        # 3. Default Varna Realization (explicitly retaining word-final 'a')
        rule = "Panini 1.1.9 (no schwa deletion)" if sym == "a" and (nxt is None or nxt in ("।", "॥")) else "Siksa canonical varna"
        out.append(
            AllophoneToken(
                sym,
                f"varna_{sym}",
                spec.ipa if spec else sym,
                rule,
                spec,
            )
        )

    return out
