"""
Studio III Vocal Audio Renderer & WAV Export.
Deterministic synthesis from rhythm + contour events with pāda rest support.
"""
from __future__ import annotations

import hashlib
import io
import math
import struct
import wave
from typing import Any, Dict, List, Tuple

try:
    from backend.engine import _mix
except ImportError:
    import _mix  # type: ignore


def _compute_rms_fallback(samples: List[float]) -> float:
    if not samples:
        return 0.0
    return math.sqrt(sum(s * s for s in samples) / len(samples))


def render_wav(
    contour_events: List[Any],
    rhythm_events: List[Any],
    sa_hz: float = 240.0,
    sample_rate: int = 44100,
    drone_on: bool = True,
) -> Tuple[bytes, str, float, Dict[str, Any]]:
    if rhythm_events:
        total_duration = max(
            (
                float(getattr(ev, "onset_sec", 0.0))
                + float(getattr(ev, "duration_sec", 0.0))
                + float(getattr(ev, "rest_after_sec", 0.0) or 0.0)
            )
            for ev in rhythm_events
        )
    else:
        total_duration = 1.0

    if total_duration <= 0.0:
        total_duration = 1.0

    n_samples = max(1, int(round(total_duration * sample_rate)))
    vocal_samples = [0.0] * n_samples
    contour_map = {
        getattr(ce, "akshara_index", i): ce for i, ce in enumerate(contour_events)
    }

    for i_ev, re_item in enumerate(rhythm_events):
        ak_idx = getattr(re_item, "akshara_index", i_ev)
        ce = contour_map.get(ak_idx)
        onset_sec = float(getattr(re_item, "onset_sec", 0.0))
        duration_sec = float(getattr(re_item, "duration_sec", 0.5))

        start_sample = max(0, int(round(onset_sec * sample_rate)))
        duration_samples = max(0, int(round(duration_sec * sample_rate)))
        end_sample = min(n_samples, start_sample + duration_samples)
        actual_len = end_sample - start_sample
        if actual_len <= 0:
            continue

        if ce is not None and hasattr(ce, "pitch"):
            start_f = float(ce.pitch.start_ratio) * sa_hz
            end_f = float(ce.pitch.end_ratio) * sa_hz
            kampa = getattr(ce.pitch, "kampa", None)
        else:
            start_f = float(getattr(re_item, "start_ratio", 1.0)) * sa_hz
            end_f = float(getattr(re_item, "end_ratio", 1.0)) * sa_hz
            kampa = getattr(re_item, "kampa", None)

        event_buf = [0.0] * actual_len
        for i in range(actual_len):
            t_frac = i / float(actual_len - 1) if actual_len > 1 else 0.0
            inst_freq = start_f + (end_f - start_f) * t_frac
            if kampa is not None:
                t_abs = (start_sample + i) / float(sample_rate)
                depth_hz = inst_freq * ((2.0 ** (float(kampa.depth_cents) / 1200.0)) - 1.0)
                inst_freq += depth_hz * math.sin(2.0 * math.pi * float(kampa.hz) * t_abs)
            phase = 2.0 * math.pi * inst_freq * ((start_sample + i) / float(sample_rate))
            event_buf[i] = math.sin(phase) * 0.5

        if hasattr(_mix, "de_click"):
            event_buf = _mix.de_click(event_buf, sample_rate, fade_ms=5.0)

        for i in range(actual_len):
            vocal_samples[start_sample + i] += event_buf[i]

    if drone_on and hasattr(_mix, "synth_drone"):
        drone_samples = _mix.synth_drone(n_samples, sample_rate, sa_hz, gain_db=-14.0)
    else:
        drone_samples = [0.0] * n_samples

    mixed = [v + d for v, d in zip(vocal_samples, drone_samples)]

    if hasattr(_mix, "normalize_rms"):
        mixed = _mix.normalize_rms(mixed, target_db=-20.0)
    if hasattr(_mix, "peak_limit"):
        mixed = _mix.peak_limit(mixed, ceiling_db=-1.0)

    peak_abs = max((abs(s) for s in mixed), default=0.0)
    peak_db = 20.0 * math.log10(peak_abs) if peak_abs > 1e-12 else -100.0
    rms_val = (
        _mix.compute_rms(mixed)
        if hasattr(_mix, "compute_rms")
        else _compute_rms_fallback(mixed)
    )
    rms_db = 20.0 * math.log10(rms_val) if rms_val > 1e-12 else -100.0

    wav_io = io.BytesIO()
    with wave.open(wav_io, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        pcm_data = bytearray()
        for s in mixed:
            clamped = max(-1.0, min(1.0, float(s)))
            val = max(-32768, min(32767, int(round(clamped * 32767.0))))
            pcm_data.extend(struct.pack("<h", val))
        wf.writeframes(pcm_data)

    wav_bytes = wav_io.getvalue()
    sha256 = hashlib.sha256(wav_bytes).hexdigest()
    stats: Dict[str, Any] = {
        "peak_db": round(peak_db, 2),
        "rms_db": round(rms_db, 2),
        "duration_sec": round(total_duration, 2),
        "n_samples": n_samples,
    }
    return wav_bytes, sha256, total_duration, stats