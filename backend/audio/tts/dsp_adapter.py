"""
Deterministic DSP Oral Synthesis Adapter (Stage 8).
Consumes validated Mode 1 text/events without altering symbolic derivations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from backend.engine.vedic._mode1 import OralRenderResult, render_oral_recitation


@dataclass(frozen=True)
class SynthesisArtifact:
    backend_id: str
    model_hash: str
    recension: str
    sha256: str
    duration_sec: float
    wav_bytes: bytes
    provenance: Dict[str, object]


def synthesize_dsp_oral(
    text: str,
    *,
    recension: str = "rgveda_sakala",
    sa_hz: float = 240.0,
    tempo_wpm: float = 90.0,
) -> SynthesisArtifact:
    res: OralRenderResult = render_oral_recitation(
        text,
        recension=recension,
        baseline_hz=sa_hz,
        sample_rate=22050,
    )
    return SynthesisArtifact(
        backend_id="deterministic_dsp_oral_v1",
        model_hash="deterministic-dsp-v1",
        recension=res.recension,
        sha256=res.sha256,
        duration_sec=res.duration_sec,
        wav_bytes=res.wav_bytes,
        provenance={
            "event_count": len(res.events),
            "musical_overlay": None,
            "certified_authentic": False,
        },
    )
