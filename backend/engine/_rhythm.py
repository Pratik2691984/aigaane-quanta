"""
Deterministic Vedic chant rhythm alignment.
Maps ContourEvents onto a Carnatic tala cycle (akshara grid) at a given BPM.
"""
from __future__ import annotations

import unicodedata
from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

try:
    from backend.engine import _tala
    from backend.engine._svara import ContourEvent, KampaSpec, VedicRejected
except ImportError:
    import _tala  # type: ignore
    from _svara import ContourEvent, KampaSpec, VedicRejected  # type: ignore


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
    rest_after_sec: float = 0.0


class VedicAlignedCandidate(BaseModel):
    candidate_id: str
    contour_events: List[ContourEvent]
    rhythm_events: List[RhythmEvent]
    total_sec: float
    tala_meta: Dict[str, Any]


class VedicAlignedEnvelope(BaseModel):
    input_triad: Dict[str, str] = Field(default_factory=dict)
    candidates: List[VedicAlignedCandidate] = Field(default_factory=list)
    rejected: List[VedicRejected] = Field(default_factory=list)
    engine_version: str = "2.4.0-pada-rests"

    def __iter__(self):
        if self.candidates:
            cand = self.candidates[0]
            yield cand.rhythm_events
            yield cand.tala_meta
        else:
            yield []
            yield {}


def _normalize_str(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    stripped = "".join(c for c in nfkd if not unicodedata.combining(c))
    return stripped.lower().strip().replace("-", "_").replace(" ", "_")


def _resolve_tala(name: str):
    if not name or not str(name).strip():
        default_spec = _tala.lookup_tala("adi")
        if default_spec is None:
            raise ValueError("Default tala 'adi' unavailable")
        return default_spec

    clean_name = _normalize_str(name)
    spec = _tala.lookup_tala(clean_name)
    if spec is not None:
        return spec

    for tala_item in _tala.list_talas():
        t_id = tala_item["name"] if isinstance(tala_item, dict) else str(tala_item)
        if clean_name == _normalize_str(t_id):
            found = _tala.lookup_tala(t_id)
            if found is not None:
                return found

    raise ValueError(f"Unknown tala: {name!r}")


def align_to_tala(
    contour_events: List[ContourEvent],
    tala_name: str = "adi",
    bpm: float = 60.0,
) -> Union[VedicAlignedEnvelope, Tuple[List[RhythmEvent], Dict[str, Any]]]:
    if bpm <= 0:
        raise ValueError(f"bpm must be positive, got {bpm!r}")

    sec_per_matra = 60.0 / float(bpm)
    spec = _resolve_tala(tala_name)
    cycle_len = int(spec.cycle_length)
    if cycle_len <= 0:
        raise ValueError(f"Invalid cycle_length {cycle_len} for tala {spec.name!r}")

    rhythm_events: List[RhythmEvent] = []
    current_matra_offset = 0.0

    for ev in contour_events:
        duration_matras = float(getattr(ev, "matra_duration", 1.0))
        duration_sec = duration_matras * sec_per_matra
        onset_sec = current_matra_offset * sec_per_matra

        slot_pos = int(current_matra_offset)
        avarta_index = slot_pos // cycle_len
        akshara_in_avarta = slot_pos % cycle_len
        sam_accent = akshara_in_avarta == 0

        rest_m = float(getattr(ev, "rest_after_matras", 0.0) or 0.0)
        rest_sec = rest_m * sec_per_matra

        rhythm_events.append(
            RhythmEvent(
                akshara_index=ev.akshara_index,
                svara=ev.svara,
                onset_sec=round(onset_sec, 4),
                duration_sec=round(duration_sec, 4),
                start_ratio=ev.pitch.start_ratio,
                end_ratio=ev.pitch.end_ratio,
                glide_cents=ev.pitch.glide_cents,
                kampa=ev.pitch.kampa,
                tala_name=spec.name,
                avarta_index=avarta_index,
                akshara_in_avarta=akshara_in_avarta,
                sam_accent=sam_accent,
                rest_after_sec=round(rest_sec, 4),
            )
        )
        current_matra_offset += duration_matras + rest_m

    total_sec = round(current_matra_offset * sec_per_matra, 4)
    tala_meta: Dict[str, Any] = {
        "tala_name": spec.name,
        "cycle_length": cycle_len,
        "jati": spec.jati,
        "bpm": bpm,
        "total_duration_sec": total_sec,
        "total_sec": total_sec,
    }

    candidate = VedicAlignedCandidate(
        candidate_id=f"aligned_{_normalize_str(spec.name)}_01",
        contour_events=contour_events,
        rhythm_events=rhythm_events,
        total_sec=total_sec,
        tala_meta=tala_meta,
    )
    return VedicAlignedEnvelope(
        input_triad={},
        candidates=[candidate],
        rejected=[],
    )