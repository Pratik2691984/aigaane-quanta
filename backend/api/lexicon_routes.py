"""
Lexicon (Kośa) domain routes — dictionary-style access to the 2-5K stem lexicon.

Wraps `_lexicon.lookup()` (morphological analysis) and `_semantic_index.lookup_semantic()`
(etymological + semantic metadata).

Provides:
  POST /lexicon/lookup           → full morphology with match strategy attribution
  POST /lexicon/attest           → boolean: is this stem attested?
  GET  /lexicon/semantic         → semantic metadata (dhātu, nirukta, synonyms, citations)
  GET  /lexicon/semantic/stats   → coverage stats of the semantic index
  GET  /lexicon/semantic/search  → search by dhātu or synonym
  GET  /lexicon/probe            → module availability
"""
import sys
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

router = APIRouter(tags=["lexicon"])

try:
    import _lexicon
    _LEXICON_OK = True
except Exception:
    _lexicon = None
    _LEXICON_OK = False

try:
    import _semantic_index
    _SEMANTIC_OK = True
except Exception:
    _semantic_index = None
    _SEMANTIC_OK = False


# ==============================================================================
# MATCHING STRATEGIES (unchanged from original)
# ==============================================================================

_MATCH_STRATEGIES = [
    "exact", "strip_aH", "strip_AH", "strip_H",
    "strip_aḥ", "strip_āḥ", "strip_ḥ",
    "add_a", "add_A",
]


def _try_lookup_with_strategy(text: str) -> tuple:
    """Try lookup with fallback strategies. Returns (result, strategy_used, tried_count)."""
    strategies_tried = []

    # Strategy 1: exact
    strategies_tried.append("exact")
    try:
        hit = _lexicon.lookup(text)
        if hit:
            return (hit, "exact", len(strategies_tried))
    except Exception:
        pass

    # Strategy 2: strip SLP1 endings
    slp1_endings = [("aH", "strip_aH"), ("AH", "strip_AH"), ("H", "strip_H")]
    for suffix, name in slp1_endings:
        if text.endswith(suffix) and len(text) > len(suffix):
            base = text[: -len(suffix)]
            strategies_tried.append(name)
            try:
                hit = _lexicon.lookup(base)
                if hit:
                    return (hit, name, len(strategies_tried))
                hit = _lexicon.lookup(base + "a")
                if hit:
                    return (hit, name + "+a", len(strategies_tried))
            except Exception:
                pass

    # Strategy 3: strip IAST endings
    iast_endings = [("aḥ", "strip_aḥ"), ("āḥ", "strip_āḥ"), ("ḥ", "strip_ḥ")]
    for suffix, name in iast_endings:
        if text.endswith(suffix) and len(text) > len(suffix):
            base = text[: -len(suffix)]
            strategies_tried.append(name)
            try:
                hit = _lexicon.lookup(base)
                if hit:
                    return (hit, name, len(strategies_tried))
                hit = _lexicon.lookup(base + "a")
                if hit:
                    return (hit, name + "+a", len(strategies_tried))
            except Exception:
                pass

    # Strategy 4: add 'a' at end (recover bare stem)
    strategies_tried.append("add_a")
    try:
        hit = _lexicon.lookup(text + "a")
        if hit:
            return (hit, "add_a", len(strategies_tried))
    except Exception:
        pass

    return (None, None, len(strategies_tried))


# ==============================================================================
# REQUEST MODELS
# ==============================================================================

class LexiconLookupRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Stem or inflected form")


class LexiconAttestRequest(BaseModel):
    stem: str = Field(..., min_length=1, description="Bare stem to check")


# ==============================================================================
# ENDPOINT: /lookup — existing, unchanged
# ==============================================================================

@router.post("/lookup")
async def lexicon_lookup(payload: LexiconLookupRequest):
    """Dictionary-style lookup with strategy attribution."""
    if not _LEXICON_OK:
        raise HTTPException(status_code=503, detail="Lexicon module unavailable")

    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty input")

    result, strategy, tried = _try_lookup_with_strategy(text)

    if not result:
        return {
            "surface": text,
            "found": False,
            "strategy": None,
            "strategies_tried": tried,
            "analysis": None,
            "message": f"'{text}' not attested (tried {tried} strategies)",
        }

    return {
        "surface": text,
        "found": True,
        "strategy": strategy,
        "strategies_tried": tried,
        "analysis": {
            "stem": result.get("stem"),
            "pos": result.get("pos"),
            "linga": result.get("linga"),
            "vibhakti": result.get("vibhakti"),
            "vacana": result.get("vacana"),
            "confidence": result.get("confidence", 0.0),
            "dhatu": result.get("dhatu"),
            "gana": result.get("gana"),
        },
    }


# ==============================================================================
# ENDPOINT: /attest — existing, unchanged
# ==============================================================================

@router.post("/attest")
async def lexicon_attest(payload: LexiconAttestRequest):
    """Boolean attestation check."""
    if not _LEXICON_OK:
        raise HTTPException(status_code=503, detail="Lexicon module unavailable")

    stem = payload.stem.strip()
    if not stem:
        raise HTTPException(status_code=400, detail="Empty input")

    try:
        hit = _lexicon.lookup(stem)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lookup failed: {e}")

    return {
        "stem": stem,
        "attested": hit is not None,
        "confidence": hit.get("confidence", 0.0) if hit else 0.0,
    }


# ==============================================================================
# NEW ENDPOINT: /semantic — semantic metadata lookup
# ==============================================================================

@router.get("/semantic")
async def lookup_semantic_endpoint(
    stem: str = Query(..., min_length=1, description="Sanskrit stem (e.g., 'dharma')"),
):
    """
    Semantic metadata: dhātu, gaṇa, nirukta, gloss, synonyms, antonyms, citations.

    Unlike /lookup (which does morphological analysis on an inflected form),
    /semantic takes a bare stem and returns its etymological + semantic metadata.
    """
    if not _SEMANTIC_OK:
        raise HTTPException(status_code=503, detail="Semantic index unavailable")

    stem_clean = stem.strip().lower()
    if not stem_clean:
        raise HTTPException(status_code=400, detail="Empty stem")

    try:
        result = _semantic_index.lookup_semantic(stem_clean)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic lookup failed: {e}")

    if result is None:
        return {
            "stem": stem_clean,
            "found": False,
            "suggestion": "Try a common Sanskrit term like 'dharma', 'karma', 'ātman', 'brahman', 'yoga', 'mokṣa'.",
        }

    return {
        "stem": stem_clean,
        "found": True,
        **result,
    }


# ==============================================================================
# NEW ENDPOINT: /semantic/stats — coverage stats
# ==============================================================================

@router.get("/semantic/stats")
async def semantic_stats():
    """Return statistics about the semantic index coverage."""
    if not _SEMANTIC_OK:
        raise HTTPException(status_code=503, detail="Semantic index unavailable")

    return _semantic_index.get_stats()


# ==============================================================================
# NEW ENDPOINT: /semantic/search — search by dhātu or synonym
# ==============================================================================

@router.get("/semantic/search")
async def semantic_search(
    dhatu: Optional[str] = Query(None, description="Search by dhātu (e.g., 'dhṛ')"),
    synonym: Optional[str] = Query(None, description="Search by synonym (e.g., 'dharmya')"),
):
    """
    Search the semantic index by dhātu or synonym.

    Examples:
      /lexicon/semantic/search?dhatu=dhṛ       → all words derived from √dhṛ
      /lexicon/semantic/search?synonym=dharmya → all words with 'dharmya' as synonym
    """
    if not _SEMANTIC_OK:
        raise HTTPException(status_code=503, detail="Semantic index unavailable")

    if not dhatu and not synonym:
        raise HTTPException(
            status_code=400,
            detail="Must provide either 'dhatu' or 'synonym' parameter",
        )

    try:
        if dhatu:
            results = _semantic_index.search_by_dhatu(dhatu.strip())
            return {
                "search_type": "dhatu",
                "query": dhatu.strip(),
                "count": len(results),
                "results": results,
            }
        else:
            results = _semantic_index.search_by_synonym(synonym.strip())
            return {
                "search_type": "synonym",
                "query": synonym.strip(),
                "count": len(results),
                "results": results,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {e}")


# ==============================================================================
# ENDPOINT: /probe — module availability
# ==============================================================================

@router.get("/probe")
async def lexicon_probe():
    return {
        "lexicon_ok": _LEXICON_OK,
        "semantic_ok": _SEMANTIC_OK,
        "has_lookup": _LEXICON_OK and hasattr(_lexicon, "lookup"),
        # Back-compat: legacy test/client expects this key
        "has_lookup_classical_verb": _LEXICON_OK and hasattr(_lexicon, "lookup_classical_verb"),
        # Back-compat: legacy test/client expects 'strategies'
        "strategies": _MATCH_STRATEGIES,
        # New: also expose under canonical name
        "match_strategies": _MATCH_STRATEGIES,
        "semantic_entries": (
            _semantic_index.get_stats()["total_entries"] if _SEMANTIC_OK else 0
        ),
    }