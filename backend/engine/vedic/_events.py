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


class OrthographyDomain(BaseModel):
    akshara_index: int
    original_nfc: str
    clean_text: str
    codepoints: List[str]
    normalization: Literal["NFC"] = "NFC"


class LinguisticsDomain(BaseModel):
    vowel_nucleus: Optional[str] = None
    is_pluta: bool = False


class SvaraDomain(BaseModel):
    label: Literal["udatta", "anudatta", "svarita", "svarita_double", "pracaya", "pluta"]
    source: Literal["marked", "derived", "default"]
    unicode_marks: List[str] = Field(default_factory=list)
    recension: str
    authority_rule: str


class ProsodyDomain(BaseModel):
    metrical_weight: Literal["L", "G", "Pluta"]
    phonetic_duration_ms: float
    pause_after_ms: float = 0.0
    timing_policy: str


class AcousticsDomain(BaseModel):
    f0_contour: List[F0Sample]
    kampa_hz: float = 0.0
    kampa_depth_cents: float = 0.0


class ProvenanceDomain(BaseModel):
    text_source: Optional[str] = None
    ruleset_version: str = "1.0.0"
    renderer_id: str = "mode1-oral-dsp-v1"


class ValidationDomain(BaseModel):
    symbolic_deterministic: bool = True
    linguistic_status: Literal["verified", "rule_derived", "unverified"] = "rule_derived"
    acoustic_status: Literal["placeholder_policy", "reference_aligned", "expert_certified"] = "placeholder_policy"
    expert_reviewed: bool = False


class VedicPhoneticEvent(BaseModel):
    schema_version: Literal["3.1.0"] = "3.1.0"
    event_id: str
    execution_mode: Literal[
        "vedic_oral_recitation",
        "classical_metrical_chanting",
        "musical_sanskrit_rendering",
    ] = "vedic_oral_recitation"
    orthography: OrthographyDomain
    linguistics: LinguisticsDomain
    svara: SvaraDomain
    prosody: ProsodyDomain
    acoustics: AcousticsDomain
    musical_overlay: Optional[dict] = None
    provenance: ProvenanceDomain
    validation: ValidationDomain

    @classmethod
    def from_oral_event(
        cls,
        ev: OralContourEvent,
        text_source: Optional[str] = None,
    ) -> "VedicPhoneticEvent":
        return cls(
            event_id=f"evt_{ev.akshara_index:04d}",
            execution_mode="vedic_oral_recitation",
            orthography=OrthographyDomain(
                akshara_index=ev.akshara_index,
                original_nfc=ev.akshara_nfc,
                clean_text=ev.akshara_clean,
                codepoints=[f"U+{ord(c):04X}" for c in ev.akshara_nfc],
            ),
            linguistics=LinguisticsDomain(
                vowel_nucleus=ev.vowel_nucleus,
                is_pluta=(ev.metrical_weight == "Pluta"),
            ),
            svara=SvaraDomain(
                label=ev.svara,
                source=ev.svara_source,
                unicode_marks=list(ev.unicode_marks),
                recension=ev.recension,
                authority_rule=ev.authority_rule,
            ),
            prosody=ProsodyDomain(
                metrical_weight=ev.metrical_weight,
                phonetic_duration_ms=ev.phonetic_duration_ms,
                pause_after_ms=ev.rest_after_ms,
                timing_policy=f"{ev.recension}_recension_policy_v1",
            ),
            acoustics=AcousticsDomain(
                f0_contour=list(ev.f0_contour),
                kampa_hz=ev.kampa_hz,
                kampa_depth_cents=ev.kampa_depth_cents,
            ),
            musical_overlay=None,
            provenance=ProvenanceDomain(text_source=text_source),
            validation=ValidationDomain(
                symbolic_deterministic=True,
                linguistic_status="verified" if ev.svara_source == "marked" else "rule_derived",
                acoustic_status="placeholder_policy",
                expert_reviewed=False,
            ),
        )
