"""Vedic Svara & Recension Contour API Routes."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.engine._svara import RECENSION_PROFILES, VedicContourEnvelope, generate_vedic_contour

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
