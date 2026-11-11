"""
Sandhi (phonological combination) domain routes.

`_sandhi_gen.invert_sandhi` accepts **IAST with diacritics only**
(e.g. `devālayaḥ`), not SLP1 (`devAlayaH`) or Devanagari.
`_sandhi_gen.combine_sandhi` also operates on IAST only.

The engine's `/parse` route handles this by transliterating before
calling the sandhi modules. These routes do the same: they accept any
of SLP1 / IAST / Devanagari, transliterate to IAST, then process.

Endpoints:
  POST /api/v3/sandhi/split    — surface → possible (left, right) pairs
  POST /api/v3/sandhi/combine  — (left, right) → possible surface forms
  GET  /api/v3/sandhi/probe    — module availability
"""
import sys
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["sandhi"])

# Sandhi modules
try:
    import _sandhi
    _SANDHI_OK = True
except Exception:
    _sandhi = None
    _SANDHI_OK = False

try:
    import _sandhi_gen
    _SANDHI_GEN_OK = True
except Exception:
    _sandhi_gen = None
    _SANDHI_GEN_OK = False

# Transliteration
try:
    import _script
    _SCRIPT_OK = True
except Exception:
    _script = None
    _SCRIPT_OK = False


class SandhiSplitRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Surface form in SLP1, IAST, or Devanagari")
    max_candidates: int = Field(10, ge=1, le=50)


class SandhiCombineRequest(BaseModel):
    left: str = Field(..., min_length=1, description="Left pada in SLP1, IAST, or Devanagari")
    right: str = Field(..., min_length=1, description="Right pada in SLP1, IAST, or Devanagari")
    max_candidates: int = Field(5, ge=1, le=50)


def _to_iast(text: str) -> str:
    """
    Convert input to IAST for sandhi modules.

    `_script.to_canonical_iast` returns a tuple (detected_script, iast_text).
    Unpack and return only the IAST string.
    """
    if not _SCRIPT_OK or not hasattr(_script, "to_canonical_iast"):
        return text
    try:
        result = _script.to_canonical_iast(text)
        if isinstance(result, tuple):
            return result[1] if len(result) > 1 else text
        return str(result)
    except Exception:
        return text


# ==============================================================================
#   POST /split — surface form → possible (left, right) boundaries
# ==============================================================================

@router.post("/split")
async def split_sandhi(payload: SandhiSplitRequest):
    """
    Split a surface form into possible sandhi boundaries.

    Accepts SLP1, IAST, or Devanagari. Internally transliterates to IAST
    (the format `_sandhi_gen.invert_sandhi` requires) before splitting.

    Returns:
        {
          "surface": str,           # original input
          "iast": str,              # transliterated form used internally
          "count": int,
          "candidates": [
            {"split": [w1, w2], "rule": str, "sutra": str, "score": float}
          ]
        }
    """
    if not _SANDHI_GEN_OK and not _SANDHI_OK:
        raise HTTPException(status_code=503, detail="No sandhi module available")

    surface = payload.text.strip()
    if not surface:
        raise HTTPException(status_code=400, detail="Empty input")

    iast_form = _to_iast(surface)

    candidates = []
    errors = []

    # Primary: generative inversion on IAST
    if _SANDHI_GEN_OK and hasattr(_sandhi_gen, "invert_sandhi"):
        try:
            result = _sandhi_gen.invert_sandhi(iast_form)
            if isinstance(result, tuple):
                gen_cands, status = result
            else:
                gen_cands, status = result, None

            for item in gen_cands or []:
                if isinstance(item, (tuple, list)) and len(item) >= 4:
                    split_list, rule, sutra, score = item[0], item[1], item[2], item[3]
                    candidates.append({
                        "split": [str(w) for w in split_list],
                        "rule": str(rule),
                        "sutra": str(sutra),
                        "score": float(score),
                    })
                elif isinstance(item, dict):
                    candidates.append({
                        "split": [str(w) for w in item.get("split", item.get("components", []))],
                        "rule": str(item.get("rule", "")),
                        "sutra": str(item.get("sutra", "")),
                        "score": float(item.get("score", 0.85)),
                    })
                else:
                    errors.append(f"unknown candidate shape: {type(item).__name__}")

            if status and not gen_cands:
                errors.append(f"gen status: {status}")
        except Exception as e:
            errors.append(f"gen: {e}")

    # Secondary: legacy split_surface on IAST
    if _SANDHI_OK and hasattr(_sandhi, "split_surface"):
        try:
            legacy_result = _sandhi.split_surface(iast_form)
            if legacy_result:
                for cand in legacy_result:
                    if isinstance(cand, (list, tuple)):
                        candidates.append({
                            "split": [str(w) for w in cand],
                            "rule": "legacy",
                            "sutra": "",
                            "score": 0.75,
                        })
        except Exception as e:
            errors.append(f"legacy: {e}")

    # Deduplicate by split tuple
    seen = {}
    for c in candidates:
        key = tuple(c["split"])
        if key not in seen or c["score"] > seen[key]["score"]:
            seen[key] = c

    final = sorted(seen.values(), key=lambda x: x["score"], reverse=True)[: payload.max_candidates]

    return {
        "surface": surface,
        "iast": iast_form,
        "count": len(final),
        "candidates": final,
        "errors": errors if errors else None,
    }


# ==============================================================================
#   POST /combine — (left, right) → possible surface forms
# ==============================================================================

@router.post("/combine")
async def combine_sandhi_route(payload: SandhiCombineRequest):
    """
    Combine two padas into possible surface forms.

    Accepts SLP1, IAST, or Devanagari for both inputs. Internally
    transliterates to IAST before combining.

    Returns:
        {
          "left": str,              # original left input
          "right": str,             # original right input
          "left_iast": str,         # transliterated left
          "right_iast": str,        # transliterated right
          "count": int,
          "candidates": [
            {"surface": str, "rule": str, "sutra": str, "score": float}
          ]
        }
    """
    if not _SANDHI_GEN_OK or not hasattr(_sandhi_gen, "combine_sandhi"):
        raise HTTPException(status_code=503, detail="combine_sandhi not available in _sandhi_gen")

    left = payload.left.strip()
    right = payload.right.strip()
    if not left or not right:
        raise HTTPException(status_code=400, detail="Empty input on one or both sides")

    left_iast = _to_iast(left)
    right_iast = _to_iast(right)

    candidates = []
    errors = []

    try:
        result = _sandhi_gen.combine_sandhi(left_iast, right_iast)
        if isinstance(result, tuple):
            gen_cands, status = result
        else:
            gen_cands, status = result, None

        for item in gen_cands or []:
            # Expected shape: ('rāmāpi', 'savarna_dirgha', '6.1.101', 0.95)
            if isinstance(item, (tuple, list)) and len(item) >= 4:
                surface, rule, sutra, score = item[0], item[1], item[2], item[3]
                candidates.append({
                    "surface": str(surface),
                    "rule": str(rule),
                    "sutra": str(sutra),
                    "score": float(score),
                })
            elif isinstance(item, dict):
                candidates.append({
                    "surface": str(item.get("surface", "")),
                    "rule": str(item.get("rule", "")),
                    "sutra": str(item.get("sutra", "")),
                    "score": float(item.get("score", 0.85)),
                })
            else:
                errors.append(f"unknown candidate shape: {type(item).__name__}")

        if status and not gen_cands:
            errors.append(f"gen status: {status}")
    except Exception as e:
        errors.append(f"gen: {e}")

    # Deduplicate by surface form
    seen = {}
    for c in candidates:
        key = c["surface"]
        if key not in seen or c["score"] > seen[key]["score"]:
            seen[key] = c

    final = sorted(seen.values(), key=lambda x: x["score"], reverse=True)[: payload.max_candidates]

    return {
        "left": left,
        "right": right,
        "left_iast": left_iast,
        "right_iast": right_iast,
        "count": len(final),
        "candidates": final,
        "errors": errors if errors else None,
    }


# ==============================================================================
#   GET /probe — module availability
# ==============================================================================

@router.get("/probe")
async def sandhi_probe():
    return {
        "sandhi_ok": _SANDHI_OK,
        "sandhi_gen_ok": _SANDHI_GEN_OK,
        "script_ok": _SCRIPT_OK,
        "has_to_canonical_iast": _SCRIPT_OK and hasattr(_script, "to_canonical_iast"),
        "has_combine_sandhi": _SANDHI_GEN_OK and hasattr(_sandhi_gen, "combine_sandhi"),
        "has_invert_sandhi": _SANDHI_GEN_OK and hasattr(_sandhi_gen, "invert_sandhi"),
    }