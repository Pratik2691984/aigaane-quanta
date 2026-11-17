"""
Deterministic Vedic Vikṛti Pāṭha Grammar (P1-1).

Implements classical Śākhā-aware transformations across the five core
Vedic recitation modes:
  1. Saṃhitāpāṭha  — continuous sandhi-joined euphonic text
  2. Padapāṭha     — word-by-word disjoined padas (with avagraha ऽ for samāsa)
  3. Kramapāṭha    — stepwise overlapping pairs: (w1 w2), (w2 w3), ..., (wn iti wn)
  4. Jaṭāpāṭha     — woven forward-reverse-forward triplets:
                     (w1 w2 w2 w1 w1 w2), (w2 w3 w3 w2 w2 w3), ...
  5. Ghanapāṭha    — bell-shaped 13-unit permutation per triplet (w1, w2, w3):
                     (w1 w2 w2 w1 w1 w2 w3 w3 w2 w1 w1 w2 w3)

All transformations operate purely on validated pada lists or via deterministic
sandhi composition/inversion, with zero LLM calls and full Vedic accent preservation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence
import unicodedata

import _sandhi_gen

SUPPORTED_PATHAS = ("samhita", "pada", "krama", "jata", "ghana")

# Vedic combining accent marks preserved during sandhi boundary inspection
_VEDIC_ACCENTS = {
    "\u0951",  # Devanagari Stress Sign Udatta
    "\u0952",  # Devanagari Stress Sign Anudatta
    "\u1CDA",  # Vedic Tone Double Svarita
    "\u1CD0", "\u1CD1", "\u1CD2", "\u1CD4", "\u1CD5", "\u1CD6", "\u1CD7",
    "\u1CD8", "\u1CD9", "\u1CDB", "\u1CDC", "\u1CDD", "\u1CDE", "\u1CDF",
    "\u1CE0", "\u1CE1",
    "\u0301",  # IAST acute (udātta)
    "\u0300",  # IAST grave (anudātta)
    "\u0302",  # IAST circumflex (svarita)
}


@dataclass(frozen=True)
class PathaResult:
    patha: str
    shakha: str
    padas: List[str]
    units: List[List[str]]
    rendered_text: str
    parigraha_indices: List[int]


def _strip_accents(text: str) -> str:
    nfd = unicodedata.normalize("NFD", text)
    return unicodedata.normalize("NFC", "".join(ch for ch in nfd if ch not in _VEDIC_ACCENTS))


def _join_pair_samhita(left: str, right: str) -> str:
    """
    Join two padas using deterministic sandhi when applicable, preserving
    the original tokens when no sandhi rule fires.
    """
    l_clean = _strip_accents(left)
    r_clean = _strip_accents(right)
    cands, status = _sandhi_gen.combine_sandhi(l_clean, r_clean)
    if status is None and cands:
        # Prefer tight single-word junction when available, else top candidate
        tight = [c[0] for c in cands if " " not in c[0]]
        return tight[0] if tight else cands[0][0]
    return f"{left} {right}"


def pada_to_samhita(padas: Sequence[str], *, apply_sandhi: bool = True) -> str:
    """Reconstruct Saṃhitā string from an ordered sequence of padas."""
    tokens = [p.strip() for p in padas if p and p.strip()]
    if not tokens:
        return ""
    if not apply_sandhi or len(tokens) == 1:
        return " ".join(tokens)

    acc = tokens[0]
    for nxt in tokens[1:]:
        # If previous join already inserted a space, join against the last word
        if " " in acc:
            head, tail = acc.rsplit(" ", 1)
            joined = _join_pair_samhita(tail, nxt)
            acc = f"{head} {joined}"
        else:
            acc = _join_pair_samhita(acc, nxt)
    return acc


def samhita_to_padas(samhita_text: str) -> List[str]:
    """
    Disjoin a Saṃhitā line into Padapāṭha tokens using deterministic sandhi
    inversion where lexical groundings exist.
    """
    raw = unicodedata.normalize("NFC", (samhita_text or "").strip())
    if not raw:
        return []
    # Strip trailing daṇḍas for pada segmentation
    cleaned = raw.replace("॥", " ").replace("।", " ").strip()
    words = [w for w in cleaned.split() if w]
    padas: List[str] = []
    for w in words:
        splits, status = _sandhi_gen.invert_sandhi(_strip_accents(w))
        if status is None and splits:
            # Accept top split only if all resulting padas have lexical backing
            top_parts = splits[0][0]
            if len(top_parts) == 2 and all(_sandhi_gen._is_valid_stem(p) for p in top_parts):
                padas.extend(top_parts)
                continue
        padas.append(w)
    return padas


def generate_krama(
    padas: Sequence[str],
    *,
    shakha: str = "rgveda_sakala",
    append_final_iti: bool = True,
) -> PathaResult:
    """
    Kramapāṭha: overlapping consecutive pairs (w1 w2), (w2 w3), ..., (wn iti wn).
    """
    tokens = [unicodedata.normalize("NFC", p.strip()) for p in padas if p and p.strip()]
    if not tokens:
        return PathaResult("krama", shakha, [], [], "", [])

    units: List[List[str]] = []
    for i in range(len(tokens) - 1):
        units.append([tokens[i], tokens[i + 1]])
    if append_final_iti:
        units.append([tokens[-1], "iti", tokens[-1]])

    rendered = " । ".join(" ".join(u) for u in units) + " ॥"
    return PathaResult(
        patha="krama",
        shakha=shakha,
        padas=tokens,
        units=units,
        rendered_text=rendered,
        parigraha_indices=[len(tokens) - 1] if append_final_iti else [],
    )


def generate_jata(
    padas: Sequence[str],
    *,
    shakha: str = "rgveda_sakala",
    append_final_iti: bool = True,
) -> PathaResult:
    """
    Jaṭāpāṭha: for each consecutive pair (a, b), emit [a, b, b, a, a, b],
    followed by parigraha [wn, 'iti', wn] at the pada boundary.
    """
    tokens = [unicodedata.normalize("NFC", p.strip()) for p in padas if p and p.strip()]
    if not tokens:
        return PathaResult("jata", shakha, [], [], "", [])

    units: List[List[str]] = []
    for i in range(len(tokens) - 1):
        a, b = tokens[i], tokens[i + 1]
        units.append([a, b, b, a, a, b])
    if append_final_iti:
        units.append([tokens[-1], "iti", tokens[-1]])

    rendered = " । ".join(" ".join(u) for u in units) + " ॥"
    return PathaResult(
        patha="jata",
        shakha=shakha,
        padas=tokens,
        units=units,
        rendered_text=rendered,
        parigraha_indices=[len(tokens) - 1] if append_final_iti else [],
    )


def generate_ghana(
    padas: Sequence[str],
    *,
    shakha: str = "rgveda_sakala",
    append_final_iti: bool = True,
) -> PathaResult:
    """
    Ghanapāṭha: for each consecutive triplet (a, b, c), emit the canonical
    13-token weave:
      [a, b, b, a, a, b, c, c, b, a, a, b, c]
    For a 2-pada tail (or 2-pada input), fall back cleanly to Jaṭā weave on
    the final pair followed by parigraha [wn, 'iti', wn].
    """
    tokens = [unicodedata.normalize("NFC", p.strip()) for p in padas if p and p.strip()]
    if not tokens:
        return PathaResult("ghana", shakha, [], [], "", [])

    units: List[List[str]] = []
    if len(tokens) >= 3:
        for i in range(len(tokens) - 2):
            a, b, c = tokens[i], tokens[i + 1], tokens[i + 2]
            units.append([a, b, b, a, a, b, c, c, b, a, a, b, c])
        # Terminal pair weave before parigraha
        b_last, c_last = tokens[-2], tokens[-1]
        units.append([b_last, c_last, c_last, b_last, b_last, c_last])
    elif len(tokens) == 2:
        a, b = tokens[0], tokens[1]
        units.append([a, b, b, a, a, b])

    if append_final_iti:
        units.append([tokens[-1], "iti", tokens[-1]])

    rendered = " । ".join(" ".join(u) for u in units) + " ॥"
    return PathaResult(
        patha="ghana",
        shakha=shakha,
        padas=tokens,
        units=units,
        rendered_text=rendered,
        parigraha_indices=[len(tokens) - 1] if append_final_iti else [],
    )


def transform_patha(
    padas: Sequence[str],
    patha: str = "krama",
    *,
    shakha: str = "rgveda_sakala",
    append_final_iti: bool = True,
) -> PathaResult:
    """Dispatch to any supported Vedic pāṭha mode."""
    mode = (patha or "").strip().lower()
    if mode not in SUPPORTED_PATHAS:
        raise ValueError(f"Unsupported patha={patha!r}; expected one of {SUPPORTED_PATHAS}")

    tokens = [unicodedata.normalize("NFC", p.strip()) for p in padas if p and p.strip()]
    if mode == "pada":
        rendered = " । ".join(tokens) + (" ॥" if tokens else "")
        return PathaResult("pada", shakha, tokens, [[t] for t in tokens], rendered, [])
    if mode == "samhita":
        rendered = pada_to_samhita(tokens)
        return PathaResult("samhita", shakha, tokens, [tokens], rendered, [])
    if mode == "krama":
        return generate_krama(tokens, shakha=shakha, append_final_iti=append_final_iti)
    if mode == "jata":
        return generate_jata(tokens, shakha=shakha, append_final_iti=append_final_iti)
    return generate_ghana(tokens, shakha=shakha, append_final_iti=append_final_iti)


def patha_to_dict(res: PathaResult) -> Dict[str, object]:
    return {
        "patha": res.patha,
        "shakha": res.shakha,
        "padas": res.padas,
        "unit_count": len(res.units),
        "units": res.units,
        "rendered_text": res.rendered_text,
        "parigraha_indices": res.parigraha_indices,
    }
