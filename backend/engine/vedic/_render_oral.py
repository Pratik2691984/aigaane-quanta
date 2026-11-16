"""
Mode 1 Deterministic Oral WAV Renderer.
Consumes OralContourEvent trajectories directly. Imports _mix only — zero
dependencies on _rhythm, _tala, or _sruti.
"""
from __future__ import annotations

import hashlib
import io
import math
import struct
import wave
from typing import List, Tuple

try:
    from backend.engine import _mix
    from backend.engine.vedic._events import OralContourEvent
except ImportError:
    import _mix  # type: ignore
    from _events import OralContourEvent  # type: ignore


def render_wav_oral(
    events: List[OralContourEvent],
    sample_rate: int = 22050,
    drone_on: bool = False,
    sa_hz: float = 240.0,
) -> Tuple[bytes, str, float]:
    total_sec = sum((e.phonetic_duration_ms + e.rest_after_ms) / 1000.0 for e in events) + 0.15
    n_total = max(1, int(total_sec * sample_rate))
    samples = [0.0] * n_total
    inv_sr = 1.0 / sample_rate
    cursor = 0

    for ev in events:
        dur_sec = ev.phonetic_duration_ms / 1000.0
        dur_i = max(1, int(dur_sec * sample_rate))
        rest_i = max(0, int((ev.rest_after_ms / 1000.0) * sample_rate))

        start_hz = ev.f0_contour[0].hz if ev.f0_contour else sa_hz
        end_hz = ev.f0_contour[-1].hz if ev.f0_contour else start_hz
        voiced = ev.f0_contour[0].voiced if ev.f0_contour else True

        kampa_depth_hz = (
            start_hz * (2.0 ** (ev.kampa_depth_cents / 1200.0) - 1.0)
            if (ev.kampa_hz > 0.0 and ev.kampa_depth_cents > 0.0)
            else 0.0
        )

        attack_n = max(1, int(0.008 * sample_rate))
        release_n = max(1, int(0.010 * sample_rate))
        phase = 0.0
        kampa_phase = 0.0

        if voiced:
            for k in range(dur_i):
                idx = cursor + k
                if idx >= n_total:
                    break
                frac = k / max(1, dur_i - 1)
                base_f = start_hz + (end_hz - start_hz) * frac
                if kampa_depth_hz > 0.0:
                    inst_f = base_f + kampa_depth_hz * math.sin(kampa_phase)
                    kampa_phase += 2.0 * math.pi * ev.kampa_hz * inv_sr
                else:
                    inst_f = base_f

                env = 1.0
                if k < attack_n:
                    env = k / attack_n
                elif k >= dur_i - release_n:
                    env = max(0.0, (dur_i - 1 - k) / release_n)

                samples[idx] += 0.16 * env * math.sin(phase)
                phase += 2.0 * math.pi * inst_f * inv_sr

        cursor += dur_i + rest_i

    samples = _mix.de_click(samples, sample_rate, fade_ms=5.0)
    if drone_on:
        drone = _mix.synth_drone(len(samples), sample_rate, sa_hz=sa_hz, gain_db=-16.0)
        samples = _mix.mix(samples, drone)
    samples = _mix.normalize_rms(samples, target_db=-20.0)
    samples = _mix.peak_limit(samples, ceiling_db=-1.0)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        pcm = bytearray()
        for s in samples:
            clamped = max(-1.0, min(1.0, s))
            pcm.extend(struct.pack("<h", int(round(clamped * 32767.0))))
        wf.writeframes(bytes(pcm))

    wav_bytes = buf.getvalue()
    sha = hashlib.sha256(wav_bytes).hexdigest()
    return wav_bytes, sha, round(len(samples) / sample_rate, 4)
