"""
Mode 1 (Vedic Oral Recitation) Engine.
Deterministic, rule-first oral recitation synthesis with zero dependency on
musical tuning (_sruti) or Carnatic rhythm (_tala / _rhythm).
"""
from __future__ import annotations

import hashlib
import io
import math
import struct
import wave
from typing import Dict, List, Literal, Optional, Tuple

from backend.engine.vedic._events import F0Sample, OralContourEvent, OralRenderResult
from backend.engine.vedic._render_oral import render_wav_oral
from backend.engine.vedic._vedic_unicode import segment_vedic_nuclei

SvaraType = Literal["udatta", "anudatta", "svarita", "svarita_double", "pracaya", "pluta"]
WeightType = Literal["L", "G", "Pluta"]

VERIFIED_ORAL_RECENSIONS: Dict[str, Dict[str, object]] = {
    "rgveda_sakala": {
        "base_hz": 220.0,
        "udatta_ratio": 1.125,     # +204 cents above baseline
        "anudatta_ratio": 0.90,    # -182 cents below baseline
        "svarita_start": 1.125,
        "svarita_end": 0.94,
        "kampa_hz": 5.5,
        "kampa_depth_cents": 20.0,
        "laghu_ms": 180.0,
        "guru_ms": 320.0,
        "pluta_ms": 540.0,
        "rule_prefix": "Panini 1.2.29-1.2.40 / Rgveda-pratisakhya",
    },
    "taittiriya": {
        "base_hz": 216.0,
        "udatta_ratio": 1.15,
        "anudatta_ratio": 0.88,
        "svarita_start": 1.15,
        "svarita_end": 0.92,
        "kampa_hz": 5.0,
        "kampa_depth_cents": 18.0,
        "laghu_ms": 185.0,
        "guru_ms": 325.0,
        "pluta_ms": 550.0,
        "rule_prefix": "Panini 1.2.29-1.2.40 / Taittiriya-Pratisakhya",
    },
    "kanva": {
        "base_hz": 218.0,
        "udatta_ratio": 1.135,
        "anudatta_ratio": 0.89,
        "svarita_start": 1.135,
        "svarita_end": 0.93,
        "kampa_hz": 5.2,
        "kampa_depth_cents": 19.0,
        "laghu_ms": 180.0,
        "guru_ms": 320.0,
        "pluta_ms": 540.0,
        "rule_prefix": "Panini 1.2.29-1.2.40 / Vajasaneyi-Pratisakhya (Kanva)",
    },
    "madhyandina": {
        "base_hz": 218.0,
        "udatta_ratio": 1.135,
        "anudatta_ratio": 0.89,
        "svarita_start": 1.135,
        "svarita_end": 0.93,
        "kampa_hz": 5.2,
        "kampa_depth_cents": 19.0,
        "laghu_ms": 180.0,
        "guru_ms": 320.0,
        "pluta_ms": 540.0,
        "rule_prefix": "Panini 1.2.29-1.2.40 / Vajasaneyi-Pratisakhya (Madhyandina)",
    },
}

_GURU_VOWELS = {"आ", "ई", "ऊ", "ॠ", "ॡ", "ए", "ऐ", "ओ", "औ"}
_GURU_MATRAS = {"ा", "ी", "ू", "ॄ", "ॢ", "ॣ", "े", "ै", "ो", "ौ"}
_ANUSVARA_VISARGA = {"ं", "ः"}


def _validate_recension(recension: str) -> Dict[str, object]:
    key = (recension or "").strip()
    if not key or key not in VERIFIED_ORAL_RECENSIONS:
        raise ValueError(
            f"Unsupported or unverified Mode 1 oral recitation recension: {recension!r}"
        )
    return VERIFIED_ORAL_RECENSIONS[key]


def _metrical_weight(clean_akshara: str, is_pluta: bool) -> WeightType:
    if is_pluta:
        return "Pluta"
    if any(ch in _GURU_VOWELS or ch in _GURU_MATRAS or ch in _ANUSVARA_VISARGA for ch in clean_akshara):
        return "G"
    return "L"


def _resolve_svaras(tokens: List[Dict[str, object]]) -> List[Tuple[SvaraType, Literal["marked", "derived"], str]]:
    n = len(tokens)
    explicit: List[Optional[str]] = [
        tok["mark_hint"] if isinstance(tok.get("mark_hint"), str) else None
        for tok in tokens
    ]
    if not any(m is not None for m in explicit):
        raise ValueError("Input lacks Vedic svara marks required for Mode 1 recitation.")

    resolved: List[Tuple[SvaraType, Literal["marked", "derived"], str]] = []
    for i, tok in enumerate(tokens):
        is_pluta = bool(tok.get("is_pluta"))
        if is_pluta:
            resolved.append(("pluta", "marked", "Panini 8.2.82 Pluta quantity"))
            continue

        hint = explicit[i]
        if hint in ("udatta", "anudatta", "svarita", "svarita_double"):
            svara_val: SvaraType = hint  # type: ignore[assignment]
            resolved.append((svara_val, "marked", "Explicit Vedic svara mark"))
            continue

        # Unmarked akshara: check immediate predecessor (Panini 8.4.66 post-udatta svarita)
        prev_hint = explicit[i - 1] if i - 1 >= 0 else None
        if prev_hint == "udatta":
            resolved.append(("svarita", "derived", "Panini 8.4.66 post-udatta svarita"))
            continue

        # Check whether an explicit udatta follows (Panini 1.2.40 pre-udatta anudatta)
        has_following_udatta = any(explicit[j] == "udatta" for j in range(i + 1, n))
        if has_following_udatta:
            resolved.append(("anudatta", "derived", "Panini 1.2.40 pre-udatta anudatta"))
        else:
            resolved.append(("pracaya", "derived", "Panini 1.2.39 post-svarita pracaya"))

    return resolved


def _build_f0_samples(
    start_ms: float,
    dur_ms: float,
    base_hz: float,
    svara: SvaraType,
    cfg: Dict[str, object],
) -> List[F0Sample]:
    u_ratio = float(cfg["udatta_ratio"])
    a_ratio = float(cfg["anudatta_ratio"])
    s_start = float(cfg["svarita_start"])
    s_end = float(cfg["svarita_end"])

    steps = 4
    samples: List[F0Sample] = []
    for k in range(steps):
        frac = k / float(max(steps - 1, 1))
        t_ms = round(start_ms + frac * dur_ms, 2)
        if svara == "udatta":
            ratio = u_ratio
        elif svara == "anudatta":
            ratio = a_ratio
        elif svara in ("svarita", "svarita_double"):
            ratio = s_start + (s_end - s_start) * frac
        elif svara == "pluta":
            ratio = u_ratio * (1.0 - 0.04 * frac)
        else:  # pracaya
            ratio = 1.0
        hz = round(base_hz * ratio, 2)
        samples.append(F0Sample(t_ms=t_ms, hz=hz, voiced=True))
    return samples


def _synthesize_wav_bytes(
    events: List[OralContourEvent],
    base_hz: float,
    sample_rate: int = 22050,
) -> Tuple[bytes, float]:
    wav_bytes, _, total_sec = render_wav_oral(
        events,
        sample_rate=sample_rate,
        drone_on=False,
        sa_hz=base_hz,
    )
    return wav_bytes, total_sec


def render_oral_recitation(
    text: str,
    recension: str = "rgveda_sakala",
    sample_rate: int = 22050,
    baseline_hz: Optional[float] = None,
) -> OralRenderResult:
    """
    Deterministically render Vedic Mode 1 oral recitation from accented Devanagari text.
    Raises ValueError on unsupported/unverified recensions or unmarked inputs.
    """
    cfg = _validate_recension(recension)
    rec_key = recension.strip()

    _, tokens = segment_vedic_nuclei(text or "")
    if not tokens:
        raise ValueError("No Devanagari aksharas found for Mode 1 recitation.")

    svara_assignments = _resolve_svaras(tokens)
    base_hz = float(baseline_hz) if baseline_hz is not None else float(cfg["base_hz"])
    laghu_ms = float(cfg["laghu_ms"])
    guru_ms = float(cfg["guru_ms"])
    pluta_ms = float(cfg["pluta_ms"])
    rule_prefix = str(cfg["rule_prefix"])

    events: List[OralContourEvent] = []
    t_ms_cursor = 0.0

    for idx, tok in enumerate(tokens):
        clean = str(tok["akshara_clean"])
        nfc_ak = str(tok["akshara_nfc"])
        is_pluta = bool(tok.get("is_pluta"))
        weight = _metrical_weight(clean, is_pluta=is_pluta)
        if weight == "Pluta":
            dur_ms = pluta_ms
        elif weight == "G":
            dur_ms = guru_ms
        else:
            dur_ms = laghu_ms

        rest_matras = float(tok.get("rest_after_matras") or 0.0)
        rest_ms = round(rest_matras * laghu_ms, 2)

        svara_label, svara_src, rule_note = svara_assignments[idx]
        f0_contour = _build_f0_samples(t_ms_cursor, dur_ms, base_hz, svara_label, cfg)

        kampa_hz = float(cfg["kampa_hz"]) if svara_label in ("svarita", "svarita_double") else 0.0
        kampa_cents = float(cfg["kampa_depth_cents"]) if svara_label in ("svarita", "svarita_double") else 0.0

        vowel_nuc = tok.get("vowel_nucleus")
        u_marks = tok.get("unicode_marks")

        events.append(
            OralContourEvent(
                akshara_index=idx,
                akshara_nfc=nfc_ak,
                akshara_clean=clean,
                vowel_nucleus=vowel_nuc if isinstance(vowel_nuc, str) else None,
                unicode_marks=[str(m) for m in u_marks] if isinstance(u_marks, list) else [],
                svara=svara_label,
                svara_source=svara_src,
                recension=rec_key,
                metrical_weight=weight,
                phonetic_duration_ms=dur_ms,
                rest_after_ms=rest_ms,
                f0_contour=f0_contour,
                kampa_hz=kampa_hz,
                kampa_depth_cents=kampa_cents,
                authority_rule=f"{rule_prefix}; {rule_note}",
            )
        )
        t_ms_cursor += dur_ms + rest_ms

    wav_bytes, total_sec = _synthesize_wav_bytes(events, base_hz=base_hz, sample_rate=sample_rate)
    digest = hashlib.sha256(wav_bytes).hexdigest()

    return OralRenderResult(
        recension=rec_key,
        events=events,
        wav_bytes=wav_bytes,
        sha256=digest,
        duration_sec=total_sec,
    )
