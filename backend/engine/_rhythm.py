"""
Deterministic Vedic chant rhythm alignment.
Maps ContourEvents onto a Carnatic tala cycle (akshara grid) at a given BPM.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

try:
    from backend.engine import _tala
    from backend.engine._svara import ContourEvent, KampaSpec, SvaraAuthority, VedicRejected
except ImportError:
    import _tala  # type: ignore
    from _svara import (  # type: ignore
        ContourEvent,
        KampaSpec,
        SvaraAuthority,
        VedicRejected,
    )


class RhythmEvent(BaseModel):
    akshara_index: int
    svara: Optional[str] = None
    onset_sec: float
    duration_sec: float
    start_ratio: float
    end_ratio: float
    glide_cents: float
    kampa: Optional[KampaSpec] = None
    tala_name: str
    avarta_index: int
    akshara_in_avarta: int
    sam_accent: bool


class VedicAlignedCandidate(BaseModel):
    candidate_id: str
    contour_events: List[ContourEvent]
    rhythm_events: List[RhythmEvent]
    total_sec: float
    tala_meta: Dict[str, Any]
    score: float
    authority: SvaraAuthority


class VedicAlignedEnvelope(BaseModel):
    input_triad: Dict[str, str]
    candidates: List[VedicAlignedCandidate] = Field(default_factory=list)
    rejected: List[VedicRejected] = Field(default_factory=list)
    engine_version: str = "2.3.1-svara-rhythm"


def _resolve_tala(name: str):
    """
    Resolve a tala by display name OR slug.
    _tala.lookup_tala expects a slug ('trisra_dhruva'), NOT the display
    name ('Triśra Dhruva'). So on lookup_tala miss, we scan the registry
    and construct TalaSpec directly from the dict — never calling
    lookup_tala again on the display name.
    """
    if not name:
        return None
    # 1) direct lookup — works if caller passed a slug
    try:
        spec = _tala.lookup_tala(name)
        if spec is not None:
            return spec
    except Exception:
        pass
    # 2) fallback: scan registry by display name, construct TalaSpec
    target = name.strip().lower()
    for t in _tala.list_talas():
        if t["name"].strip().lower() == target:
            return _tala.TalaSpec(
                name=t["name"],
                cycle_length=t["cycle_length"],
                jati=t.get("jati", ""),
                description=t.get("description", ""),
            )
    return None


def align_to_tala(
    contour_events: List[ContourEvent],
    tala_name: str,
    bpm: float = 60.0,
) -> Tuple[List[RhythmEvent], Dict[str, Any]]:
    if bpm <= 0:
        raise ValueError(f"bpm must be > 0, got {bpm}")
    spec = _resolve_tala(tala_name)
    if spec is None:
        raise ValueError(f"Unknown tala: {tala_name!r}")

    beat_sec = 60.0 / bpm
    cycle = max(1, int(spec.cycle_length))
    slot = 0
    avarta = 0
    events: List[RhythmEvent] = []

    for ev in contour_events:
        matra = max(1, int(round(ev.matra_duration)))
        onset_sec = round((avarta * cycle + slot) * beat_sec, 4)
        duration_sec = round(matra * beat_sec, 4)
        events.append(
            RhythmEvent(
                akshara_index=ev.akshara_index,
                svara=ev.svara,
                onset_sec=onset_sec,
                duration_sec=duration_sec,
                start_ratio=ev.pitch.start_ratio,
                end_ratio=ev.pitch.end_ratio,
                glide_cents=ev.pitch.glide_cents,
                kampa=ev.pitch.kampa,
                tala_name=spec.name,
                avarta_index=avarta,
                akshara_in_avarta=slot,
                sam_accent=(slot == 0),
            )
        )
        slot += matra
        while slot >= cycle:
            slot -= cycle
            avarta += 1

    total_sec = round(sum(e.duration_sec for e in events), 4)
    meta = {
        "name": spec.name,
        "cycle_length": cycle,
        "jati": spec.jati,
        "total_avartas": avarta + (1 if slot > 0 else 0) or 1,
        "total_sec": total_sec,
        "bpm": bpm,
    }
    return events, meta
