"""Vedic Svara & Recension Contour API Routes."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.engine._svara import (
    RECENSION_PROFILES,
    VedicContourEnvelope,
    VedicRejected,
    generate_vedic_contour,
)
from backend.engine._rhythm import (
    VedicAlignedCandidate,
    VedicAlignedEnvelope,
    align_to_tala,
)

router = APIRouter(tags=["Vedic Svara & Acoustics"])


class VedicContourRequest(BaseModel):
    text: str = Field(..., description="NFC Devanagari mantra with Vedic tone marks")
    recension: str = Field(default="rgveda_sakala")
    sa_hz: float = Field(default=240.0, gt=50.0, lt=1000.0)


@router.post("/contour", response_model=VedicContourEnvelope)
def post_vedic_contour(req: VedicContourRequest) -> VedicContourEnvelope:
    return generate_vedic_contour(text=req.text, recension=req.recension, sa_hz=req.sa_hz)


@router.get("/recensions")
def get_vedic_recensions():
    return {
        "recensions": [
            {"id": k, "pratisakhya": v["pratisakhya"], "udatta_sruti": v["udatta"]["sruti"], "anudatta_sruti": v["anudatta"]["sruti"]}
            for k, v in RECENSION_PROFILES.items()
        ]
    }


class VedicAlignRequest(BaseModel):
    text: str = Field(..., description="NFC Devanagari mantra with Vedic tone marks")
    recension: str = Field(default="rgveda_sakala")
    tala_name: str = Field(..., description="Carnatic tala name, e.g. 'Triśra Dhruva'")
    bpm: float = Field(default=60.0, gt=0.0, lt=400.0)
    sa_hz: float = Field(default=240.0, gt=50.0, lt=1000.0)


@router.post("/align", response_model=VedicAlignedEnvelope)
def post_vedic_align(req: VedicAlignRequest) -> VedicAlignedEnvelope:
    contour_env = generate_vedic_contour(
        text=req.text,
        recension=req.recension,
        sa_hz=req.sa_hz,
    )
    if contour_env.rejected:
        return VedicAlignedEnvelope(
            input_triad=contour_env.input_triad,
            rejected=contour_env.rejected,
        )
    if not contour_env.candidates:
        return VedicAlignedEnvelope(
            input_triad=contour_env.input_triad,
            rejected=[VedicRejected(reason_code="EMPTY_INPUT", detail="No contour produced.")],
        )
    base = contour_env.candidates[0]
    try:
        rhythm_events, tala_meta = align_to_tala(
            base.contour_events,
            tala_name=req.tala_name,
            bpm=req.bpm,
        )
    except ValueError as exc:
        return VedicAlignedEnvelope(
            input_triad=contour_env.input_triad,
            rejected=[VedicRejected(
                reason_code="TALA_UNKNOWN",
                detail=str(exc),
            )],
        )
    aligned = VedicAlignedCandidate(
        candidate_id=f"{base.candidate_id}_aligned",
        contour_events=base.contour_events,
        rhythm_events=rhythm_events,
        total_sec=tala_meta["total_sec"],
        tala_meta=tala_meta,
        score=base.score,
        authority=base.authority,
    )
    return VedicAlignedEnvelope(
        input_triad=contour_env.input_triad,
        candidates=[aligned],
        rejected=[],
    )
