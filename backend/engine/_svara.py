"""
Deterministic Vedic Svara (Pitch-Accent) & Recension Contour Engine.
Zero LLM calls. Maps NFC-normalized Devanagari/IAST/SLP1 Vedic mantras
onto 22-Sruti Just Intonation contours for Studio III AudioWorklet rendering.
"""
from __future__ import annotations

import re
import unicodedata
from fractions import Fraction
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field

try:
    from backend.engine import _sruti, _script
except ImportError:
    import _sruti  # type: ignore
    import _script  # type: ignore


SvaraLabel = Literal[
    "udatta", "anudatta", "svarita", "svarita_double", "pracaya", "pluta",
]

RecensionId = Literal[
    "rgveda_sakala", "taittiriya", "kanva", "madhyandina", "samaveda",
]


class KampaSpec(BaseModel):
    hz: float
    depth_cents: float


class PitchContour(BaseModel):
    start_ratio: float
    end_ratio: float
    glide_cents: float
    kampa: Optional[KampaSpec] = None


class SvaraAuthority(BaseModel):
    recension: str
    pratisakhya: str
    rule: str


class ContourEvent(BaseModel):
    akshara_index: int
    akshara_nfc: str
    akshara_clean: str
    akshara_iast: str
    svara: Optional[SvaraLabel] = None
    svara_source: Literal["marked", "derived", "default"]
    recension: str
    pitch: PitchContour
    matra_duration: float
    rest_after_matras: float = 0.0
    srutis: List[int]
    authority: SvaraAuthority


class VedicCandidate(BaseModel):
    candidate_id: str
    contour_events: List[ContourEvent]
    total_matras: float
    score: float
    authority: SvaraAuthority


class VedicRejected(BaseModel):
    reason_code: Literal[
        "NO_SVARA_MARKS",
        "UNSANDHIED_KSAIPRA",
        "SAMAVEDA_ROUTE",
        "EMPTY_INPUT",
        "SRUTI_TABLE_MISMATCH",
        "TALA_UNKNOWN",
    ]
    detail: str
    fallback_endpoint: Optional[str] = None


class VedicContourEnvelope(BaseModel):
    input_triad: Dict[str, str]
    candidates: List[VedicCandidate] = Field(default_factory=list)
    rejected: List[VedicRejected] = Field(default_factory=list)
    engine_version: str = "2.3.1-svara-contour"


RECENSION_PROFILES: Dict[str, Dict[str, Any]] = {
    "rgveda_sakala": {
        "pratisakhya": "Rgveda-Pratisakhya",
        "udatta": {"sruti": 1, "octave": 0},
        "anudatta": {"sruti": 20, "octave": -1},
        "pracaya": {"sruti": 1, "octave": 0},
        "svarita": {"start_sruti": 5, "start_octave": 0, "end_sruti": 1, "end_octave": 0, "kampa_default": KampaSpec(hz=5.5, depth_cents=28.0)},
        "svarita_double": {"start_sruti": 5, "start_octave": 0, "end_sruti": 20, "end_octave": -1, "kampa_default": KampaSpec(hz=6.0, depth_cents=35.0)},
        "pluta_matra_multiplier": 3.0,
    },
    "taittiriya": {
        "pratisakhya": "Taittiriya-Pratisakhya",
        "udatta": {"sruti": 1, "octave": 0},
        "anudatta": {"sruti": 22, "octave": -1},
        "pracaya": {"sruti": 1, "octave": 0},
        "svarita": {"start_sruti": 5, "start_octave": 0, "end_sruti": 1, "end_octave": 0, "kampa_default": None},
        "svarita_double": {"start_sruti": 5, "start_octave": 0, "end_sruti": 22, "end_octave": -1, "kampa_default": KampaSpec(hz=5.0, depth_cents=25.0)},
        "pluta_matra_multiplier": 3.0,
    },
    "kanva": {
        "pratisakhya": "Vajasaneyi-Pratisakhya (Kanva)",
        "udatta": {"sruti": 1, "octave": 0},
        "anudatta": {"sruti": 20, "octave": -1},
        "pracaya": {"sruti": 1, "octave": 0},
        "svarita": {"start_sruti": 5, "start_octave": 0, "end_sruti": 1, "end_octave": 0, "kampa_default": KampaSpec(hz=5.0, depth_cents=25.0)},
        "svarita_double": {"start_sruti": 5, "start_octave": 0, "end_sruti": 20, "end_octave": -1, "kampa_default": KampaSpec(hz=5.5, depth_cents=30.0)},
        "pluta_matra_multiplier": 3.0,
    },
    "madhyandina": {
        "pratisakhya": "Vajasaneyi-Pratisakhya (Madhyandina)",
        "udatta": {"sruti": 1, "octave": 0},
        "anudatta": {"sruti": 20, "octave": -1},
        "pracaya": {"sruti": 1, "octave": 0},
        "svarita": {"start_sruti": 5, "start_octave": 0, "end_sruti": 1, "end_octave": 0, "kampa_default": None},
        "svarita_double": {"start_sruti": 5, "start_octave": 0, "end_sruti": 20, "end_octave": -1, "kampa_default": None},
        "pluta_matra_multiplier": 3.0,
    },
}


UDATTA_MARKS = {"\u0951", "\u1cd0", "\u1cd1", "\u1cd2"}
ANUDATTA_MARKS = {"\u0952", "\u1cd5", "\u1cd6", "\u1cd7", "\u1cd8", "\u1cd9"}
SVARITA_DOUBLE_MARKS = {"\u1cda", "\u1cdb"}
SVARITA_EXPLICIT_MARKS = {"\u1cdc", "\u1cdd", "\u1cde"}
ALL_VEDIC_MARKS = UDATTA_MARKS | ANUDATTA_MARKS | SVARITA_DOUBLE_MARKS | SVARITA_EXPLICIT_MARKS

_AKSHARA_RE = re.compile(
    r"(?:[\u0915-\u0939\u0958-\u095f]\u094d)*"
    r"(?:[\u0904-\u0914]|[\u0915-\u0939\u0958-\u095f][\u093e-\u094c\u0962\u0963]?)"
    r"[\u0900-\u0903\u093d\u0950]*"
    r"(?:[\u0915-\u0939\u0958-\u095f]\u094d)?"
    r"[\u0951\u0952\u1cd0-\u1cff]*"
    r"\u0969?"
)

_GURU_MATRAS = {"\u093e", "\u0940", "\u0942", "\u0944", "\u0947", "\u0948", "\u094b", "\u094c", "\u0963"}
_GURU_INDEP_VOWELS = {"\u0906", "\u0908", "\u090a", "\u090f", "\u0910", "\u0913", "\u0914", "\u0960", "\u0961"}
_YOGAVAHA = {"\u0901", "\u0902", "\u0903"}


def strip_vedic_marks(text: str) -> str:
    return "".join(ch for ch in text if ch not in ALL_VEDIC_MARKS)


def _extract_mark_hint(akshara_nfc: str) -> Optional[SvaraLabel]:
    for ch in akshara_nfc:
        if ch in SVARITA_DOUBLE_MARKS:
            return "svarita_double"
        if ch in SVARITA_EXPLICIT_MARKS:
            return "svarita"
        if ch in UDATTA_MARKS:
            return "udatta"
        if ch in ANUDATTA_MARKS:
            return "anudatta"
    return None


def segment_vedic_aksharas(text_nfc: str) -> List[Dict[str, Any]]:
    tokens: List[Dict[str, Any]] = []
    matches = list(_AKSHARA_RE.finditer(text_nfc))
    for idx, match in enumerate(matches):
        raw = match.group(0)
        clean = strip_vedic_marks(raw)
        if not clean:
            continue
        gap_start = match.end()
        gap_end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text_nfc)
        gap = text_nfc[gap_start:gap_end]
        if "\u0965" in gap:
            rest_matras = 4.0
        elif "\u0964" in gap:
            rest_matras = 2.0
        else:
            rest_matras = 0.0
        tokens.append({
            "akshara_nfc": raw,
            "akshara_clean": clean,
            "mark_hint": _extract_mark_hint(raw),
            "is_pluta": "\u0969" in raw,
            "rest_after_matras": rest_matras,
        })
    return tokens


def _compute_matra(clean_akshara: str, next_clean: Optional[str], is_pluta: bool, pluta_mult: float) -> float:
    if is_pluta:
        return pluta_mult
    is_guru = (
        any(ch in _GURU_MATRAS or ch in _GURU_INDEP_VOWELS or ch in _YOGAVAHA for ch in clean_akshara)
        or clean_akshara.endswith("\u094d")
        or (next_clean is not None and "\u094d" in next_clean)
    )
    return 2.0 if is_guru else 1.0


def derive_svara_sequence(aksharas: List[Dict[str, Any]]) -> List[Tuple[SvaraLabel, Literal["marked", "derived", "default"], str]]:
    n = len(aksharas)
    resolved: List[Tuple[SvaraLabel, Literal["marked", "derived", "default"], str]] = []
    for i, item in enumerate(aksharas):
        hint = item["mark_hint"]
        prev_svara = resolved[i - 1][0] if i > 0 else None
        next_hint = aksharas[i + 1]["mark_hint"] if i + 1 < n else None
        if hint is not None:
            resolved.append((hint, "marked", "Explicit Vedic tone mark"))
            continue
        if prev_svara == "udatta":
            resolved.append(("svarita", "derived", "Panini 8.4.66 (udattad anudattasya svaritah)"))
            continue
        if prev_svara in ("svarita", "svarita_double", "pracaya") and next_hint not in ("udatta", "svarita", "svarita_double"):
            resolved.append(("pracaya", "derived", "Panini 1.2.39 (svaritat samhitayam anudattanam)"))
            continue
        resolved.append(("udatta", "default", "Unmarked neutral baseline"))
    return resolved


def _resolve_sruti_ratio(sruti_index: int, octave: int, table: List[Dict[str, Any]]) -> Tuple[float, float]:
    entry = next((row for row in table if row["index"] == sruti_index), None)
    if entry is None:
        raise ValueError(f"Sruti index {sruti_index} missing from _sruti.get_sruti_table()")
    octave_mult = 2.0 ** octave
    raw_ratio = entry["ratio"]
    numeric_ratio = float(Fraction(raw_ratio)) if isinstance(raw_ratio, str) else float(raw_ratio)
    ratio = round(numeric_ratio * octave_mult, 6)
    cents = round(float(entry["cents"]) + (1200.0 * octave), 2)
    return ratio, cents


def _build_pitch_contour(svara: SvaraLabel, next_svara: Optional[SvaraLabel], profile: Dict[str, Any], sruti_table: List[Dict[str, Any]]) -> Tuple[PitchContour, List[int]]:
    if svara in ("svarita", "svarita_double"):
        spec = profile[svara]
        start_ratio, start_cents = _resolve_sruti_ratio(spec["start_sruti"], spec["start_octave"], sruti_table)
        end_ratio, end_cents = _resolve_sruti_ratio(spec["end_sruti"], spec["end_octave"], sruti_table)
        glide_cents = round(end_cents - start_cents, 2)
        kampa = spec["kampa_default"] if next_svara in ("udatta", "svarita_double") else None
        srutis = sorted({spec["start_sruti"], spec["end_sruti"]})
        return (PitchContour(start_ratio=start_ratio, end_ratio=end_ratio, glide_cents=glide_cents, kampa=kampa), srutis)
    tone_key = "udatta" if svara in ("udatta", "pluta") else svara
    tone_spec = profile[tone_key]
    ratio, _ = _resolve_sruti_ratio(tone_spec["sruti"], tone_spec["octave"], sruti_table)
    return (PitchContour(start_ratio=ratio, end_ratio=ratio, glide_cents=0.0, kampa=None), [tone_spec["sruti"]])


def generate_vedic_contour(text: str, recension: str = "rgveda_sakala", sa_hz: float = 240.0) -> VedicContourEnvelope:
    raw = (text or "").strip()
    if not raw:
        return VedicContourEnvelope(
            input_triad={"devanagari": "", "iast": "", "slp1": ""},
            rejected=[VedicRejected(reason_code="EMPTY_INPUT", detail="Empty mantra input.")],
        )
    nfc_text = unicodedata.normalize("NFC", raw)
    clean_deva = strip_vedic_marks(nfc_text)
    _, clean_iast = _script.to_canonical_iast(clean_deva)
    clean_slp1 = _script.to_slp1(clean_iast)
    triad = {"devanagari": nfc_text, "iast": clean_iast, "slp1": clean_slp1}

    if recension == "samaveda":
        return VedicContourEnvelope(
            input_triad=triad,
            rejected=[VedicRejected(
                reason_code="SAMAVEDA_ROUTE",
                detail="Samaveda is melodic (Gana); route through /api/v3/studio3/midi/export.",
                fallback_endpoint="/api/v3/studio3/midi/export",
            )],
        )

    profile = RECENSION_PROFILES.get(recension, RECENSION_PROFILES["rgveda_sakala"])
    resolved_recension = recension if recension in RECENSION_PROFILES else "rgveda_sakala"

    aksharas = segment_vedic_aksharas(nfc_text)
    if not aksharas:
        return VedicContourEnvelope(
            input_triad=triad,
            rejected=[VedicRejected(reason_code="NO_SVARA_MARKS", detail="No Devanagari aksaras with Vedic svara marks detected.")],
        )

    has_any_mark = any(a["mark_hint"] is not None for a in aksharas)
    if not has_any_mark:
        return VedicContourEnvelope(
            input_triad=triad,
            rejected=[VedicRejected(reason_code="NO_SVARA_MARKS", detail="Input lacks Vedic svara marks (U+0951 Udatta / U+0952 Anudatta / U+1CDA Svarita).")],
        )

    derived = derive_svara_sequence(aksharas)
    sruti_table = _sruti.get_sruti_table(sa_hz=sa_hz)

    events: List[ContourEvent] = []
    total_matras = 0.0
    try:
        for idx, ak in enumerate(aksharas):
            svara, source, rule_note = derived[idx]
            next_svara = derived[idx + 1][0] if idx + 1 < len(derived) else None
            next_clean = aksharas[idx + 1]["akshara_clean"] if idx + 1 < len(aksharas) else None
            pitch, srutis = _build_pitch_contour(svara, next_svara, profile, sruti_table)
            matra = _compute_matra(ak["akshara_clean"], next_clean, ak["is_pluta"], profile["pluta_matra_multiplier"])
            total_matras += matra
            _, ak_iast = _script.to_canonical_iast(ak["akshara_clean"])
            events.append(ContourEvent(
                akshara_index=idx,
                akshara_nfc=ak["akshara_nfc"],
                akshara_clean=ak["akshara_clean"],
                akshara_iast=ak_iast,
                svara=svara,
                svara_source=source,
                recension=resolved_recension,
                pitch=pitch,
                matra_duration=matra,
                rest_after_matras=ak.get("rest_after_matras", 0.0),
                srutis=srutis,
                authority=SvaraAuthority(recension=resolved_recension, pratisakhya=profile["pratisakhya"], rule=rule_note),
            ))
    except (ValueError, KeyError, ZeroDivisionError) as exc:
        return VedicContourEnvelope(
            input_triad=triad,
            rejected=[VedicRejected(reason_code="SRUTI_TABLE_MISMATCH", detail=str(exc))],
        )

    candidate = VedicCandidate(
        candidate_id=f"vedic_{resolved_recension}_01",
        contour_events=events,
        total_matras=total_matras,
        score=0.98,
        authority=SvaraAuthority(recension=resolved_recension, pratisakhya=profile["pratisakhya"], rule="Panini 1.2.27 + 1.2.39 + 8.4.66"),
    )
    return VedicContourEnvelope(input_triad=triad, candidates=[candidate], rejected=[])
