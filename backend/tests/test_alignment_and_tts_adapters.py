"""
Gate P2-1 Acceptance Tests:
- Praat TextGrid interval parser & F0 RMSE / duration MAE evaluator
- Isolated Stage-8 DSP & Neural synthesis adapters (zero torch import)
- Provenance-tracked RV 1.1.1 corpus_manifest.json validation
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from backend.audio.tts.dsp_adapter import synthesize_dsp_oral
from backend.audio.tts.neural_adapter import (
    NeuralWorkerUnavailableError,
    synthesize_neural_conditioned,
)
from backend.audio.vedic._alignment import evaluate_f0_and_timing, parse_textgrid
from backend.engine.vedic._events import VedicPhoneticEvent
from backend.engine.vedic._mode1 import render_oral_recitation

SAMPLE_TEXTGRID = """File type = "ooTextFile"
Object class = "TextGrid"

xmin = 0.0
xmax = 1.69
tiers? <exists>
size = 1
item []:
    item [1]:
        class = "IntervalTier"
        name = "akshara"
        xmin = 0.0
        xmax = 1.69
        intervals: size = 4
        intervals [1]:
            xmin = 0.00
            xmax = 0.44
            text = "अ॒"
        intervals [2]:
            xmin = 0.44
            xmax = 0.66
            text = "ग्नि"
        intervals [3]:
            xmin = 0.66
            xmax = 1.10
            text = "मी॑"
        intervals [4]:
            xmin = 1.10
            xmax = 1.54
            text = "ळे"
"""


def test_textgrid_parser_and_f0_rmse_evaluator():
    tiers = parse_textgrid(SAMPLE_TEXTGRID)
    assert "akshara" in tiers
    ivs = tiers["akshara"]
    assert len(ivs) == 4
    assert [iv.text for iv in ivs] == ["अ॒", "ग्नि", "मी॑", "ळे"]
    assert pytest.approx(ivs[0].duration_ms, abs=0.1) == 440.0

    report = evaluate_f0_and_timing(
        predicted_f0_hz=[216.0, 216.0, 240.0, 254.4],
        reference_f0_hz=[216.0, 216.0, 240.0, 254.4],
        predicted_durations_ms=[440.0, 220.0, 440.0, 440.0],
        reference_intervals=ivs,
        expert_reviewed=False,
    )
    assert report.interval_count == 4
    assert report.f0_rmse_hz == 0.0
    assert report.f0_rmse_cents == 0.0
    assert report.f0_correlation == 1.0
    assert report.duration_mae_ms == 0.0
    # Governing acceptance rule: never certified without explicit expert review
    assert report.certified_authentic is False


def test_stage8_dsp_and_neural_adapters_stay_isolated_from_torch():
    verse = "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"
    art = synthesize_dsp_oral(verse, recension="rgveda_sakala")
    assert art.backend_id == "deterministic_dsp_oral_v1"
    assert art.provenance["musical_overlay"] is None
    assert art.provenance["certified_authentic"] is False
    assert "torch" not in sys.modules

    res = render_oral_recitation(verse, recension="rgveda_sakala")
    events = [VedicPhoneticEvent.from_oral_event(e, text_source="rv_1_1_1") for e in res.events]

    # Must reject unverified/unknown license before touching worker
    with pytest.raises(PermissionError, match="verified recording license"):
        synthesize_neural_conditioned(events, speaker_reference_id="spk_01", license_id="unknown")

    # Must fail closed cleanly when worker URL is unset
    with pytest.raises(NeuralWorkerUnavailableError):
        synthesize_neural_conditioned(events, speaker_reference_id="spk_01", license_id="CC-BY-SA-4.0")

    assert "torch" not in sys.modules


def test_corpus_manifest_provenance_invariants():
    manifest = json.loads(Path("backend/data/vedic/corpus_manifest.json").read_text(encoding="utf-8-sig"))
    assert manifest["target_tradition"] == "rgveda_sakala"
    entry = manifest["entries"][0]
    assert entry["record_id"] == "rv_1_1_1"
    assert entry["license"] == "unknown"
    assert entry["expert_reviewed"] is False
