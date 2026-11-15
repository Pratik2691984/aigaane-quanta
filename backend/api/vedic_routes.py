"""Vedic Svara & Recension Contour API Routes."""
from fastapi import APIRouter
from typing import Any, Dict, List, Optional
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
from backend.engine._rhythm import RhythmEvent
from backend.engine._render import render_wav

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


class VedicRenderRequest(BaseModel):
    text: str = Field(..., description="NFC Devanagari mantra with Vedic tone marks")
    recension: str = Field(default="rgveda_sakala")
    tala_name: Optional[str] = Field(default=None, description="Optional tala for grid rhythm")
    bpm: float = Field(default=60.0, gt=0.0, lt=400.0)
    sa_hz: float = Field(default=240.0, gt=50.0, lt=1000.0)
    drone_on: bool = Field(default=True)
    sample_rate: int = Field(default=22050, ge=8000, le=48000)


class RenderCandidate(BaseModel):
    candidate_id: str
    wav_b64: str
    sha256: str
    duration_sec: float
    sample_rate: int
    peak_db: float
    rms_db: float
    n_samples: int
    tala_meta: Optional[Dict[str, Any]] = None


class RenderEnvelope(BaseModel):
    input_triad: Dict[str, str]
    candidates: List[RenderCandidate] = Field(default_factory=list)
    rejected: List[VedicRejected] = Field(default_factory=list)
    engine_version: str = "2.3.1-svara-render"


@router.post("/render", response_model=RenderEnvelope)
def post_vedic_render(req: VedicRenderRequest) -> RenderEnvelope:
    contour_env = generate_vedic_contour(text=req.text, recension=req.recension, sa_hz=req.sa_hz)
    if contour_env.rejected:
        return RenderEnvelope(input_triad=contour_env.input_triad, rejected=contour_env.rejected)
    if not contour_env.candidates:
        return RenderEnvelope(
            input_triad=contour_env.input_triad,
            rejected=[VedicRejected(reason_code="EMPTY_INPUT", detail="No contour produced.")],
        )
    base = contour_env.candidates[0]

    if req.tala_name:
        try:
            rhythm_events, tala_meta = align_to_tala(base.contour_events, tala_name=req.tala_name, bpm=req.bpm)
        except ValueError as exc:
            return RenderEnvelope(
                input_triad=contour_env.input_triad,
                rejected=[VedicRejected(reason_code="TALA_UNKNOWN", detail=str(exc))],
            )
    else:
        rhythm_events = []
        cumul = 0.0
        beat_sec = 60.0 / max(30.0, req.bpm)
        for ev in base.contour_events:
            dur = ev.matra_duration * beat_sec
            rest_matras = max(0, int(round(getattr(ev, "rest_after_matras", 0.0))))
            rest_sec = round(rest_matras * beat_sec, 4)
            rhythm_events.append(RhythmEvent(
                akshara_index=ev.akshara_index,
                svara=ev.svara,
                onset_sec=round(cumul, 4),
                duration_sec=round(dur, 4),
                start_ratio=ev.pitch.start_ratio,
                end_ratio=ev.pitch.end_ratio,
                glide_cents=ev.pitch.glide_cents,
                kampa=ev.pitch.kampa,
                tala_name="",
                avarta_index=0,
                akshara_in_avarta=ev.akshara_index,
                sam_accent=False,
                rest_after_sec=rest_sec,
            ))
            cumul += dur + rest_sec
        tala_meta = None

    wav_bytes, sha, duration_sec, stats = render_wav(
        rhythm_events,
        sa_hz=req.sa_hz,
        sample_rate=req.sample_rate,
        drone_on=req.drone_on,
    )
    import base64 as _b64
    b64 = _b64.b64encode(wav_bytes).decode("ascii")
    return RenderEnvelope(
        input_triad=contour_env.input_triad,
        candidates=[RenderCandidate(
            candidate_id=f"{base.candidate_id}_render",
            wav_b64=b64,
            sha256=sha,
            duration_sec=duration_sec,
            sample_rate=req.sample_rate,
            peak_db=stats["peak_db"],
            rms_db=stats["rms_db"],
            n_samples=stats["n_samples"],
            tala_meta=tala_meta,
        )],
    )
