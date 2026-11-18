"""
Isolated Neural Acoustic Vocoder Adapter Stub (Stage 8 — Track 2).

Keeps PyTorch / Matcha-TTS / HiFi-GAN weights strictly outside the Cloud Run
deterministic kernel container. Fails closed with NeuralWorkerUnavailableError
unless an external verified checkpoint endpoint is explicitly configured.
"""
from __future__ import annotations

import os
from typing import Sequence

from backend.audio.tts.dsp_adapter import SynthesisArtifact
from backend.engine.vedic._events import VedicPhoneticEvent


class NeuralWorkerUnavailableError(RuntimeError):
    """Raised when external neural TTS worker weights/endpoint are not mounted."""


def synthesize_neural_conditioned(
    events: Sequence[VedicPhoneticEvent],
    *,
    speaker_reference_id: str,
    license_id: str,
) -> SynthesisArtifact:
    if not events:
        raise ValueError("Cannot synthesize empty VedicPhoneticEvent sequence")
    if not license_id or license_id == "unknown":
        raise PermissionError("Neural synthesis requires an explicit, verified recording license")

    worker_url = os.environ.get("AIGAANE_NEURAL_TTS_URL", "").strip()
    if not worker_url:
        raise NeuralWorkerUnavailableError(
            "External neural TTS worker not mounted (AIGAANE_NEURAL_TTS_URL unset); "
            "use deterministic DSP adapter or configure an isolated GPU worker."
        )
    raise NeuralWorkerUnavailableError(f"Remote neural worker handshake not yet enabled for {worker_url}")
