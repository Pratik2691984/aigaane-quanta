"""
Deterministic mixing + post-processing for Vedic chant WAV renders.
Pure stdlib. No external audio deps.
"""
from __future__ import annotations

import math
from typing import List


def de_click(samples: List[float], sample_rate: int, fade_ms: float = 5.0) -> List[float]:
    n_fade = max(1, int(sample_rate * fade_ms / 1000.0))
    n = len(samples)
    out = list(samples)
    fade_n = min(n_fade, n // 2)
    for i in range(fade_n):
        g = i / fade_n
        out[i] *= g
        out[n - 1 - i] *= g
    return out


def rms(samples: List[float]) -> float:
    if not samples:
        return 0.0
    return math.sqrt(sum(x * x for x in samples) / len(samples))


def peak(samples: List[float]) -> float:
    return max(abs(x) for x in samples) if samples else 0.0


def rms_db(samples: List[float]) -> float:
    r = rms(samples)
    return 20.0 * math.log10(r) if r > 0 else -120.0


def peak_db(samples: List[float]) -> float:
    p = peak(samples)
    return 20.0 * math.log10(p) if p > 0 else -120.0


def normalize_rms(samples: List[float], target_db: float = -20.0) -> List[float]:
    r = rms(samples)
    if r <= 0:
        return list(samples)
    target = 10.0 ** (target_db / 20.0)
    scale = target / r
    return [x * scale for x in samples]


def peak_limit(samples: List[float], ceiling_db: float = -1.0) -> List[float]:
    ceiling = 10.0 ** (ceiling_db / 20.0)
    p = peak(samples)
    if p <= ceiling:
        return list(samples)
    scale = ceiling / p
    return [x * scale for x in samples]


def synth_drone(n_samples: int, sample_rate: int, sa_hz: float = 240.0, gain_db: float = -14.0) -> List[float]:
    """
    Simple tanpura-like drone: Sa + Pa (3/2) + Sa octave, with slow ~0.2 Hz
    amplitude modulation. Deterministic (no randomness).
    """
    if n_samples <= 0:
        return []
    g = 10.0 ** (gain_db / 20.0)
    pa = sa_hz * 1.5
    sa_hi = sa_hz * 2.0
    out = [0.0] * n_samples
    inv_sr = 1.0 / sample_rate
    for i in range(n_samples):
        t = i * inv_sr
        mod = 0.5 + 0.5 * math.sin(2.0 * math.pi * 0.2 * t)
        v = (
            0.5 * math.sin(2.0 * math.pi * sa_hz * t)
            + 0.3 * math.sin(2.0 * math.pi * pa * t)
            + 0.2 * math.sin(2.0 * math.pi * sa_hi * t)
        )
        out[i] = v * g * mod
    return out


def mix(vocal: List[float], drone: List[float]) -> List[float]:
    n = max(len(vocal), len(drone))
    out = [0.0] * n
    for i in range(n):
        v = vocal[i] if i < len(vocal) else 0.0
        d = drone[i] if i < len(drone) else 0.0
        out[i] = v + d
    return out


def compute_rms(samples: list[float]) -> float:
    if not samples:
        return 0.0
    return (sum(s * s for s in samples) / len(samples)) ** 0.5

