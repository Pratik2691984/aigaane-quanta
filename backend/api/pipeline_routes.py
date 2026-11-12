"""
Q8: Deterministic unified pipeline route.

Mounts:
  POST /api/v1/pipeline/v2  (alias — new deterministic version)
  POST /api/v3/pipeline     (primary)

Does not touch the legacy /api/v1/pipeline handler in main.py.
"""

import sys
from pathlib import Path
_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

from fastapi import APIRouter, HTTPException, Body
from typing import Optional

router = APIRouter(tags=["pipeline"])

try:
    from _pipeline import run_pipeline as _run_pipeline
    _PIPE_OK = True
    _PIPE_ERR = None
except Exception as e:
    _PIPE_OK = False
    _PIPE_ERR = str(e)


@router.post("/")
@router.post("")
async def pipeline_run(
    payload: dict = Body(..., examples=["text": "dharmakṣetre kurukṣetre", "sa_hz": 240.0}),
):
    """Run the deterministic 5-stage pipeline (normalize → sandhi → morphology → chandas → śruti)."""
    if not _PIPE_OK:
        raise HTTPException(status_code=503, detail=f"Pipeline unavailable: {_PIPE_ERR}")

    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text field is required")

    try:
        sa_hz = float(payload.get("sa_hz", 240.0))
    except (TypeError, ValueError):
        sa_hz = 240.0

    return _run_pipeline(text, sa_hz=sa_hz)