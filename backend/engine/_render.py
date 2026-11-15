"""
Deterministic WAV renderer for Vedic chant.
Takes rhythm events -> synthesizes sine-based chant -> adds drone ->
normalizes -> outputs byte-identical WAV given same inputs.
"""
from __future__ import annotations

import hashlib
import io
import math
import struct
import wave
from typing import Dict, List, Tuple

try:
    from backend.engine import _mix
    from backend.engine._rhythm import RhythmEvent
except ImportError:
    import _mix  # type: ignore
    from _rhythm import RhythmEvent  # type: ignore


def _synth_vocal(rhythm_events: List[RhythmEvent], sample_rate: int, sa_hz: float) -> List[float]:
    total_sec = sum(e.duration_sec for e in rhythm_events) + 0.2
    n = int(total_sec * sample_rate)
    samples = [0.0] * n
    inv_sr = 1.0 / sample_rate
    attack_sec = 0.008
    release_sec = 0.010

    for ev in rhythm_events:
        start_i = int(ev.onset_sec * sample_rate)
        dur_i = max(1, int(ev.duration_sec * sample_rate))
        start_f = ev.start_ratio * sa_hz
        end_f = ev.end_ratio * sa_hz
        gain = 0.22 if ev.sam_accent else 0.15
        phase = 0.0

        attack_n = max(1, int(attack_sec * sample_rate))
        release_n = max(1, int(release_sec * sample_rate))

        for i in range(dur_i):
            idx = start_i + i
            if idx >= n:
                break
            t_frac = i / dur_i
            freq = start_f + (end_f - start_f) * t_frac
            phase += 2.0 * math.pi * freq * inv_sr
            s = math.sin(phase) + 0.1 * math.sin(2.0 * phase)
            if i < attack_n:
                env = i / attack_n
            elif i > dur_i - release_n:
                env = max(0.0, (dur_i - i) / release_n)
            else:
                env = 1.0
            samples[idx] += s * gain * env
    return samples


def render_wav(
    rhythm_events: List[RhythmEvent],
    sa_hz: float = 240.0,
    sample_rate: int = 22050,
    drone_on: bool = True,
    target_rms_db: float = -20.0,
    ceiling_db: float = -1.0,
) -> Tuple[bytes, str, float, Dict[str, float]]:
    """
    Returns (wav_bytes, sha256_hex, duration_sec, stats) where
    stats = {"peak_db": ..., "rms_db": ..., "n_samples": ...}.
    """
    vocal = _synth_vocal(rhythm_events, sample_rate, sa_hz)
    if drone_on:
        drone = _mix.synth_drone(len(vocal), sample_rate, sa_hz=sa_hz, gain_db=-14.0)
        mixed = _mix.mix(vocal, drone)
    else:
        mixed = list(vocal)

    mixed = _mix.de_click(mixed, sample_rate, fade_ms=5.0)
    mixed = _mix.normalize_rms(mixed, target_db=target_rms_db)
    mixed = _mix.peak_limit(mixed, ceiling_db=ceiling_db)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for s in mixed:
            v = max(-1.0, min(1.0, s))
            wf.writeframes(struct.pack("<h", int(v * 32767)))
    wav_bytes = buf.getvalue()
    sha = hashlib.sha256(wav_bytes).hexdigest()
    duration = len(mixed) / sample_rate
    stats = {
        "peak_db": round(_mix.peak_db(mixed), 2),
        "rms_db": round(_mix.rms_db(mixed), 2),
        "n_samples": len(mixed),
    }
    return wav_bytes, sha, round(duration, 3), stats
