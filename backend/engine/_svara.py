"""
Deterministic Vedic Svara (Pitch-Accent) & Recension Contour Engine (with Pāda Rests).
"""
from __future__ import annotations

import re
import unicodedata
from fractions import Fraction
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel, Field

try:
    from backend.engine import _script
except ImportError:
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
    svara: SvaraLabel
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
    reason_code: str
    detail: str
    fallback_endpoint: Optional[str] = None

class VedicContourEnvelope(BaseModel):
    input_triad: Dict[str, str]
    candidates: List[VedicCandidate] = Field(default_factory=list)
    rejected: List[VedicRejected] = Field(default_factory=list)
    engine_version: str = "2.4.0-pada-rests"

UDATTA_MARKS = {"\u0951"}
ANUDATTA_MARKS = {"\u0952"}
SVARITA_EXPLICIT_MARKS = {"\u1CDC"}
SVARITA_DOUBLE_MARKS = {"\u1CDA"}
ALL_VEDIC_MARKS = UDATTA_MARKS | ANUDATTA_MARKS | SVARITA_EXPLICIT_MARKS | SVARITA_DOUBLE_MARKS

_GURU_MATRAS = {"ā", "ī", "ū", "e", "ai", "o", "au", "āṁ", "īṁ", "ūṁ", "ṁ", "ḥ", "āH", "īH", "ūH", "eH", "oH", "āḥ", "īḥ", "ūḥ", "eḥ", "oḥ"}
_GURU_INDEP_VOWELS = {"ā", "ī", "ū", "e", "ai", "o", "au", "A", "I", "U", "E", "O"}
_YOGAVAHA = {"ṁ", "ḥ", "M", "H"}

# Granular Devanagari Akshara Regex matching individual syllables
_AKSHARA_RE = re.compile(
    r"["
    r"\u0900-\u097f\ua8e0-\ua8ff"
    r"]"
    r"(?:\u094d["
    r"\u0900-\u097f"
    r"])?"
    r"["
    r"\u093e-\u094c\u0962\u0963"
    r"]*"
    r"["
    r"\u0901-\u0903\u094d"
    r"]?"
    r"["
    r"\u0951\u0952\u1cd0-\u1cff\u0969"
    r"]*",
    re.UNICODE,
)

RECENSION_PROFILES: Dict[str, Dict[str, Any]] = {
    "rgveda_sakala": {
        "pratisakhya": "Rgveda-pratisakhya",
        "udatta": {"sruti": 6, "octave": 0},
        "anudatta": {"sruti": 6, "octave": -1},
        "svarita": {
            "start_sruti": 22,
            "start_octave": 0,
            "end_sruti": 6,
            "end_octave": -1,
            "kampa_default": KampaSpec(hz=5.5, depth_cents=25.0),
        },
        "svarita_double": {
            "start_sruti": 22,
            "start_octave": 0,
            "end_sruti": 1,
            "end_octave": 0,
            "kampa_default": KampaSpec(hz=6.0, depth_cents=30.0),
        },
        "pracaya": {"sruti": 6, "octave": 0},
        "pluta_matra_multiplier": 3.0,
    },
    "taittiriya": {
        "pratisakhya": "Taittiriya-Pratisakhya",
        "udatta": {"sruti": 20, "octave": 0},
        "anudatta": {"sruti": 4, "octave": -1},
        "svarita": {
            "start_sruti": 20,
            "start_octave": 0,
            "end_sruti": 4,
            "end_octave": -1,
            "kampa_default": None,
        },
        "svarita_double": {
            "start_sruti": 20,
            "start_octave": 0,
            "end_sruti": 6,
            "end_octave": -1,
            "kampa_default": None,
        },
        "pracaya": {"sruti": 20, "octave": 0},
        "pluta_matra_multiplier": 3.0,
    },
    "kanva": {
        "pratisakhya": "Vajasaneyi-Pratisakhya (Kanva)",
        "udatta": {"sruti": 18, "octave": 0},
        "anudatta": {"sruti": 5, "octave": -1},
        "svarita": {
            "start_sruti": 21,
            "start_octave": 0,
            "end_sruti": 5,
            "end_octave": -1,
            "kampa_default": KampaSpec(hz=5.0, depth_cents=22.0),
        },
        "svarita_double": {
            "start_sruti": 21,
            "start_octave": 0,
            "end_sruti": 6,
            "end_octave": -1,
            "kampa_default": KampaSpec(hz=5.0, depth_cents=25.0),
        },
        "pracaya": {"sruti": 18, "octave": 0},
        "pluta_matra_multiplier": 3.0,
    },
    "madhyandina": {
        "pratisakhya": "Vajasaneyi-Pratisakhya (Madhyandina)",
        "udatta": {"sruti": 18, "octave": 0},
        "anudatta": {"sruti": 5, "octave": -1},
        "svarita": {
            "start_sruti": 21,
            "start_octave": 0,
            "end_sruti": 5,
            "end_octave": -1,
            "kampa_default": None,
        },
        "svarita_double": {
            "start_sruti": 21,
            "start_octave": 0,
            "end_sruti": 6,
            "end_octave": -1,
            "kampa_default": None,
        },
        "pracaya": {"sruti": 18, "octave": 0},
        "pluta_matra_multiplier": 3.0,
    },
}

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
        if clean in ("।", "\u0964"):
            if tokens:
                tokens[-1]["rest_after_matras"] = 2.0
            continue
        if clean in ("॥", "\u0965"):
            if tokens:
                tokens[-1]["rest_after_matras"] = 4.0
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
        if i > 0 and resolved[i - 1][0] == "anudatta":
            resolved.append(("anudatta", "derived", "Panini 1.2.40 (anudattam padam ekavarjam)"))
            continue
        resolved.append(("anudatta" if i == 0 else "udatta", "default", "Panini 1.2.37 (udattam anudattam svaritam)"))
    return resolved

def _resolve_sruti_ratio(sruti_index: int, octave: int, table: List[Dict[str, Any]]) -> Tuple[float, float]:
    try:
        from backend.engine import _sruti  # noqa: F401
    except ImportError:
        import _sruti  # type: ignore  # noqa: F401
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
    try:
        from backend.engine import _sruti
    except ImportError:
        import _sruti  # type: ignore
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
            rejected=[VedicRejected(reason_code="NO_SVARA_MARKS", detail="Input lacks Vedic svara marks.")],
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
            
            base_matra = _compute_matra(ak["akshara_clean"], next_clean, ak["is_pluta"], profile["pluta_matra_multiplier"])
            rest_m = ak.get("rest_after_matras", 0.0)
            matra = base_matra + rest_m
            total_matras += matra
            
            _, ak_iast = _script.to_canonical_iast(ak["akshara_clean"])
            events.append(
                ContourEvent(
                    akshara_index=idx,
                    akshara_nfc=ak["akshara_nfc"],
                    akshara_clean=ak["akshara_clean"],
                    akshara_iast=ak_iast,
                    svara=svara,
                    svara_source=source,
                    recension=resolved_recension,
                    pitch=pitch,
                    matra_duration=base_matra,
                    rest_after_matras=rest_m,
                    srutis=srutis,
                    authority=SvaraAuthority(recension=resolved_recension, pratisakhya=profile["pratisakhya"], rule=rule_note),
                )
            )
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
