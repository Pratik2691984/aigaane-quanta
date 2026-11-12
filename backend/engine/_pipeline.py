"""
Deterministic pipeline orchestrator (Q8).

Chains:
  1. Script normalization  (_script)
  2. Tokenization + sandhi splitting  (_sandhi_gen / _sandhi)
  3. Morphological + semantic attestation  (_lexicon, _semantic_index)
  4. Chandas scansion  (_chhandas)
  5. 22-śruti mapping  (_sruti)

No LLM, no EngineAdapter. Every stage is wrapped so a failure in one
does not abort the others. The response includes per-stage timing and
warnings.
"""

from __future__ import annotations
import time
import re
from typing import Any

try:
    from _script import to_canonical_iast, detect_script
except Exception:
    to_canonical_iast = None
    detect_script = None

try:
    from _sandhi_gen import invert_sandhi
except Exception:
    invert_sandhi = None

try:
    from _sandhi import generate_splits
except Exception:
    generate_splits = None

try:
    from _lexicon import lookup as lexicon_lookup
except Exception:
    lexicon_lookup = None

try:
    from _semantic_index import lookup_semantic
except Exception:
    lookup_semantic = None

try:
    from _chhandas import scan_verse
except Exception:
    scan_verse = None

try:
    from _sruti import get_sruti_table
except Exception:
    get_sruti_table = None


# ----------------------------------------------------------------
# Stage helpers
# ----------------------------------------------------------------

def _stage(name, fn):
    """Run fn() with timing and error capture. Returns (result, info)."""
    t0 = time.perf_counter()
    try:
        result = fn()
        return result, {"name": name, "ok": True, "ms": round((time.perf_counter() - t0) * 1000, 2)}
    except Exception as e:
        return None, {"name": name, "ok": False, "ms": round((time.perf_counter() - t0) * 1000, 2), "error": str(e)}


def _tokenize(text):
    """Split on whitespace and common punctuation, preserving danda."""
    if not text:
        return []
    cleaned = text.replace("|", " ").replace("॥", " ").replace("\n", " ")
    return [t for t in re.split(r"\s+", cleaned.strip()) if t]


# ----------------------------------------------------------------
# Stage implementations
# ----------------------------------------------------------------

def _stage_normalize(text):
    if to_canonical_iast is None:
        return {"input": text, "detected": "unknown", "iast": text}
    detected, iast = to_canonical_iast(text)
    return {"input": text, "detected": detected, "iast": iast}


def _stage_sandhi(tokens):
    """For each token, attempt sandhi split. If none, emit single-part."""
    out = []
    if invert_sandhi is None:
        for tok in tokens:
            out.append({"surface": tok, "splits": [], "split_applied": False})
        return out
    for tok in tokens:
        try:
            splits, err = invert_sandhi(tok)
        except Exception:
            splits, err = [], "exception"
        if splits:
            serialized = []
            for parts, rule, sutra, conf in splits[:3]:
                serialized.append({
                    "parts": parts,
                    "rule": rule,
                    "sutra": sutra,
                    "confidence": conf,
                })
            out.append({"surface": tok, "splits": serialized, "split_applied": True})
        else:
            out.append({"surface": tok, "splits": [], "split_applied": False})
    return out


def _stage_morphology(token_entries):
    """For each split-part, look up morphology and semantics. Best-effort."""
    if lexicon_lookup is None:
        for t in token_entries:
            t["morphology"] = None
            t["semantic"] = None
        return token_entries

    for entry in token_entries:
        # Try each split part first; if no split, try the surface
        candidates = []
        if entry.get("split_applied") and entry["splits"]:
            candidates = entry["splits"][0]["parts"]
        else:
            candidates = [entry["surface"]]

        analyses = []
        for word in candidates:
            try:
                lex = lexicon_lookup(word)
            except Exception:
                lex = None
            sem = None
            if lookup_semantic is not None:
                try:
                    sem = lookup_semantic(word)
                except Exception:
                    sem = None
            analyses.append({
                "word": word,
                "morphology": lex,
                "semantic": sem if (sem and sem.get("found")) else None,
            })
        entry["analyses"] = analyses
        # Backwards-friendly aliases
        first = analyses[0] if analyses else {}
        entry["morphology"] = first.get("morphology")
        entry["semantic"] = first.get("semantic")
    return token_entries


def _stage_chandas(text):
    if scan_verse is None:
        return None
    return scan_verse(text)


def _stage_sruti(chandas_result, sa_hz=240.0):
    """Map syllable weights to śruti intervals. Simplified: assign Sa (1/1) to L,
    Pa (3/2) to G for a coarse mapping. The real Studio III uses svara sequences,
    but for the pipeline summary this is enough."""
    if not chandas_result or get_sruti_table is None:
        return []
    table = get_sruti_table(sa_hz)
    # Find S (Sa) and P (Pa) in the table
    sa = next((r for r in table if r.get("ratio") == "1/1"), None)
    pa = next((r for r in table if r.get("ratio") == "3/2"), None)
    weights = chandas_result.get("weights", [])
    mapping = []
    for i, w in enumerate(weights):
        ref = pa if w == "G" else sa
        if ref is None:
            continue
        mapping.append({
            "index": i + 1,
            "weight": w,
            "name": ref.get("name"),
            "svara": ref.get("svara"),
            "ratio": ref.get("ratio"),
            "hz": ref.get("frequency_hz"),
        })
    return mapping


# ----------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------

def run_pipeline(text: str, sa_hz: float = 240.0) -> dict:
    if not text or not text.strip():
        return {"error": "empty input"}

    warnings = []

    norm, norm_info = _stage("normalize", lambda: _stage_normalize(text))
    if not norm_info["ok"]:
        warnings.append(f"normalize failed: {norm_info.get('error')}")
        norm = {"input": text, "detected": "unknown", "iast": text}

    iast_text = norm.get("iast") or text
    tokens = _tokenize(iast_text)

    sandhi, sandhi_info = _stage("sandhi", lambda: _stage_sandhi(tokens))
    if not sandhi_info["ok"]:
        warnings.append(f"sandhi failed: {sandhi_info.get('error')}")
        sandhi = [{"surface": t, "splits": [], "split_applied": False} for t in tokens]

    morph, morph_info = _stage("morphology", lambda: _stage_morphology(sandhi))
    if not morph_info["ok"]:
        warnings.append(f"morphology failed: {morph_info.get('error')}")
        morph = sandhi

    chandas, chandas_info = _stage("chandas", lambda: _stage_chandas(iast_text))
    if not chandas_info["ok"]:
        warnings.append(f"chandas failed: {chandas_info.get('error')}")

    sruti, sruti_info = _stage("sruti", lambda: _stage_sruti(chandas, sa_hz))
    if not sruti_info["ok"]:
        warnings.append(f"sruti failed: {sruti_info.get('error')}")

    return {
        "input": text,
        "normalized": norm,
        "tokens": morph,
        "chandas": chandas,
        "sruti_map": sruti,
        "stages": [norm_info, sandhi_info, morph_info, chandas_info, sruti_info],
        "warnings": warnings,
    }


if __name__ == "__main__":
    import json
    r = run_pipeline("dharmakṣetre kurukṣetre")
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))