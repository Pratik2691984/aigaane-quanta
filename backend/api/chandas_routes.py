"""
Chandas (meter) domain routes.

Exposes Piṅgala-style L/G scansion and meter classification:

  POST /chandas/scan     → full scansion: L/G pattern + mātrā + meter
  POST /chandas/analyze  → meter classification only (lighter)
  GET  /chandas/meters   → list all supported meters
  GET  /chandas/probe    → module availability
"""
import sys
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

router = APIRouter(tags=["chandas"])

try:
    import _chhandas
    _CHHANDAS_OK = True
except Exception:
    _chhandas = None
    _CHHANDAS_OK = False

try:
    import _script
    _SCRIPT_OK = True
except Exception:
    _script = None
    _SCRIPT_OK = False


class ChandasScanRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Verse in IAST with diacritics, or Devanagari")


def _to_iast(text: str) -> str:
    """Convert input to IAST (required by chandas modules)."""
    if not _SCRIPT_OK or not hasattr(_script, "to_canonical_iast"):
        return text
    try:
        result = _script.to_canonical_iast(text)
        if isinstance(result, tuple):
            return result[1] if len(result) > 1 else text
        return str(result)
    except Exception:
        return text


@router.post("/scan")
async def scan_chandas(payload: ChandasScanRequest):
    """
    Full scansion: L/G weights, mātrā count, and meter identification.
    """
    if not _CHHANDAS_OK:
        raise HTTPException(status_code=503, detail="Chandas module unavailable")

    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty input")

    iast = _to_iast(text)

    try:
        result = _chhandas.scan_verse(iast)
        result["surface"] = text  # Preserve original input (may be Devanagari, IAST, etc.)
        result["iast"] = iast
        result["errors"] = None
        return result
    except Exception as e:
        return {
            "surface": text,
            "iast": iast,
            "weights": [],
            "pattern": "",
            "syllable_count": 0,
            "matra_sum": 0,
            "meter": None,
            "errors": str(e),
        }


@router.post("/analyze")
async def analyze_chandas(payload: ChandasScanRequest):
    """
    Lighter endpoint: meter classification only.
    Returns 'found' key for back-compat with legacy frontend expectations.
    """
    if not _CHHANDAS_OK:
        raise HTTPException(status_code=503, detail="Chandas module unavailable")

    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty input")

    iast = _to_iast(text)

    try:
        result = _chhandas.analyze_verse(iast)
        return {
            "surface": text,
            "iast": iast,
            "found": result is not None,  # Back-compat key
            "meter": result,
            "errors": None,
        }
    except Exception as e:
        return {
            "surface": text,
            "iast": iast,
            "found": False,
            "meter": None,
            "errors": str(e),
        }


@router.get("/meters")
async def list_meters():
    """List all supported meters."""
    if not _CHHANDAS_OK:
        raise HTTPException(status_code=503, detail="Chandas module unavailable")

    return {
        "count": len(_chhandas._CHHANDAS_TABLE),
        "meters": [
            {"name": name, **data}
            for name, data in _chhandas._CHHANDAS_TABLE.items()
        ],
    }


@router.get("/probe")
async def chandas_probe():
    return {
        "chhandas_ok": _CHHANDAS_OK,
        "scanner_ok": _CHHANDAS_OK,  # Back-compat: scanner was merged into _chhandas
        "script_ok": _SCRIPT_OK,
        "has_analyze_verse": _CHHANDAS_OK and hasattr(_chhandas, "analyze_verse"),
        "has_scan_iast": _CHHANDAS_OK and hasattr(_chhandas, "scan_verse"),
        "meter_count": len(_chhandas._CHHANDAS_TABLE) if _CHHANDAS_OK else 0,
    }