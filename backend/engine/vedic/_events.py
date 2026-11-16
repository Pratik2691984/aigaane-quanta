"""
Decoupled Mode 1 (Vedic Oral Recitation) Event Contracts.
Carries vowel-nucleus accent attachment, Unicode mark provenance, time-indexed
Hz trajectories, and phonetic durations without musical sruti or tala fields.
"""
from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class F0Sample(BaseModel):
    t_ms: float
    hz: float
    voiced: bool = True


class OralContourEvent(BaseModel):
    akshara_index: int
    akshara_nfc: str
    akshara_clean: str
    vowel_nucleus: Optional[str] = None
    unicode_marks: List[str] = Field(default_factory=list)
    svara: Literal["udatta", "anudatta", "svarita", "svarita_double", "pracaya", "pluta"]
    svara_source: Literal["marked", "derived", "default"]
    recension: str
    metrical_weight: Literal["L", "G", "Pluta"]
    phonetic_duration_ms: float
    rest_after_ms: float = 0.0
    f0_contour: List[F0Sample] = Field(default_factory=list)
    kampa_hz: float = 0.0
    kampa_depth_cents: float = 0.0
    authority_rule: str


class OralRenderResult(BaseModel):
    recension: str
    events: List[OralContourEvent]
    wav_bytes: bytes
    sha256: str
    duration_sec: float
