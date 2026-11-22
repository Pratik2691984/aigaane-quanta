"""
Mode 1 — Vedic Oral Recitation Orchestrator.
Strictly isolated from musical tuning (_sruti) and Carnatic rhythm (_tala / _rhythm).
Uses _vedic_unicode.segment_vedic_nuclei for P0-2 vowel-nucleus accent binding.
"""
from __future__ import annotations

import unicodedata
from typing import Any, Dict, List

from backend.engine._svara import _compute_matra
from backend.engine.vedic._events import F0Sample, OralContourEvent, OralRenderResult
from backend.engine.vedic._render_oral import render_wav_oral
from backend.engine.vedic._vedic_unicode import segment_vedic_nuclei

ORAL_RECENSION_POLICIES: Dict[str, Dict[str, Any]] = {
    "rgveda_sakala": {
        "udatta_mult": 1.0,
        "anudatta_mult": 0.90,
        "pracaya_mult": 1.0,
        "svarita_start_mult": 1.06,
        "svarita_end_mult": 0.92,
        "kampa_hz": 5.5,
        "kampa_depth_cents": 25.0,
        "matra_ms": 220.0,
        "pluta_mult": 3.0,
    },
    "taittiriya": {
        "udatta_mult": 1.0,
        "anudatta_mult": 0.92,
        "pracaya_mult": 1.0,
        "svarita_start_mult": 1.08,
        "svarita_end_mult": 0.94,
        "kampa_hz": 0.0,
        "kampa_depth_cents": 0.0,
        "matra_ms": 230.0,
        "pluta_mult": 3.0,
    },
    "kanva": {
        "udatta_mult": 1.0,
        "anudatta_mult": 0.90,
        "pracaya_mult": 1.0,
        "svarita_start_mult": 1.07,
        "svarita_end_mult": 0.92,
        "kampa_hz": 5.0,
        "kampa_depth_cents": 22.0,
        "matra_ms": 220.0,
        "pluta_mult": 3.0,
    },
    "madhyandina": {
        "udatta_mult": 1.0,
        "anudatta_mult": 0.91,
        "pracaya_mult": 1.0,
        "svarita_start_mult": 1.07,
        "svarita_end_mult": 0.93,
        "kampa_hz": 0.0,
        "kampa_depth_cents": 0.0,
        "matra_ms": 225.0,
        "pluta_mult": 3.0,
    },
}

def derive_oral_svara_sequence(aksharas: List[Dict[str, Any]]) -> List[tuple]:
    """Paninian Mode 1 svara derivation:
      - Explicit tone mark                         → marked svara
      - Unmarked after udatta                      → derived svarita (8.4.66)
      - Unmarked after svarita/pracaya,
        and before udatta/svarita                  → derived pracaya (1.2.39)
      - Unmarked before udatta/svarita             → default anudatta (1.2.40)
      - Other unmarked baseline                    → default anudatta (never udatta)
    """
    n = len(aksharas)
    resolved: List[tuple] = []
    for i, item in enumerate(aksharas):
        hint = item["mark_hint"]
        prev_svara = resolved[i - 1][0] if i > 0 else None
        next_hint = aksharas[i + 1]["mark_hint"] if i + 1 < n else None
        if hint is not None:
            resolved.append((hint, "marked", "Explicit Vedic tone mark"))
            continue
        if prev_svara == "udatta":
            resolved.append(("svarita", "derived", "Panini 8.4.66"))
            continue
        if prev_svara in ("svarita", "svarita_double", "pracaya") \
           and next_hint not in ("udatta", "svarita", "svarita_double"):
            resolved.append(("pracaya", "derived", "Panini 1.2.39"))
            continue
        if next_hint in ("udatta", "svarita", "svarita_double"):
            resolved.append(("anudatta", "default", "Panini 1.2.40"))
            continue
        resolved.append(("anudatta", "default", "Paninian unmarked anudatta"))
    return resolved

def render_oral_recitation(
    text: str,
    recension: str = "rgveda_sakala",
    baseline_hz: float = 240.0,
    sample_rate: int = 22050,
) -> OralRenderResult:
    norm_recension = (recension or "").strip().lower()
    if norm_recension == "samaveda" or norm_recension.startswith("samaveda_"):
        raise ValueError("Samaveda Gana is melodic and excluded from Mode 1 oral recitation.")
    if recension not in ORAL_RECENSION_POLICIES:
        raise ValueError(f"Unsupported or unverified recension for Mode 1 oral recitation: {recension!r}")
    policy = ORAL_RECENSION_POLICIES[recension]
    resolved_recension = recension

    _, aksharas = segment_vedic_nuclei(text)
    if not aksharas or not any(a["mark_hint"] is not None for a in aksharas):
        raise ValueError("Input lacks Vedic svara marks required for Mode 1 recitation.")

    derived = derive_oral_svara_sequence(aksharas)
    events: List[OralContourEvent] = []
    matra_ms = float(policy["matra_ms"])

    for idx, ak in enumerate(aksharas):
        svara, source, rule_note = derived[idx]
        next_svara = derived[idx + 1][0] if idx + 1 < len(derived) else None
        next_clean = str(aksharas[idx + 1]["akshara_clean"]) if idx + 1 < len(aksharas) else None
        clean_str = str(ak["akshara_clean"])
        is_pluta = bool(ak["is_pluta"])

        matra_val = _compute_matra(clean_str, next_clean, is_pluta, float(policy["pluta_mult"]))
        weight = "Pluta" if is_pluta else ("G" if matra_val >= 2.0 else "L")
        dur_ms = round(matra_val * matra_ms, 2)
        rest_ms = round(float(ak.get("rest_after_matras", 0.0)) * matra_ms, 2)

        if svara in ("svarita", "svarita_double"):
            start_hz = round(baseline_hz * float(policy["svarita_start_mult"]), 3)
            end_hz = round(baseline_hz * float(policy["svarita_end_mult"]), 3)
            use_kampa = next_svara in ("udatta", "svarita_double") and policy["kampa_hz"] > 0.0
            k_hz = float(policy["kampa_hz"]) if use_kampa else 0.0
            k_cents = float(policy["kampa_depth_cents"]) if use_kampa else 0.0
        elif svara == "anudatta":
            start_hz = end_hz = round(baseline_hz * float(policy["anudatta_mult"]), 3)
            k_hz = k_cents = 0.0
        else:
            start_hz = end_hz = round(baseline_hz * float(policy["udatta_mult"]), 3)
            k_hz = k_cents = 0.0

        events.append(
            OralContourEvent(
                akshara_index=idx,
                akshara_nfc=str(ak["akshara_nfc"]),
                akshara_clean=clean_str,
                vowel_nucleus=ak["vowel_nucleus"] if isinstance(ak["vowel_nucleus"], str) else None,
                unicode_marks=list(ak["unicode_marks"]),  # type: ignore[arg-type]
                svara=svara,
                svara_source=source,
                recension=resolved_recension,
                metrical_weight=weight,
                phonetic_duration_ms=dur_ms,
                rest_after_ms=rest_ms,
                f0_contour=[
                    F0Sample(t_ms=0.0, hz=start_hz, voiced=True),
                    F0Sample(t_ms=dur_ms, hz=end_hz, voiced=True),
                ],
                kampa_hz=k_hz,
                kampa_depth_cents=k_cents,
                authority_rule=rule_note,
            )
        )

    wav_bytes, sha, duration_sec = render_wav_oral(
        events, sample_rate=sample_rate, drone_on=False, sa_hz=baseline_hz
    )
    return OralRenderResult(
        recension=resolved_recension,
        events=events,
        wav_bytes=wav_bytes,
        sha256=sha,
        duration_sec=duration_sec,
    )