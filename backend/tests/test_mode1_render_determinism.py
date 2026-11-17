"""
F3 & F4 Closure Tests:
- Mode 1 SHA-256 WAV determinism pin & internal _svara helper guards
- Paninian unmarked pre-udatta anudatta/sannatara verification (F4)
"""
from __future__ import annotations

import subprocess
import sys

from backend.engine.vedic._mode1 import render_oral_recitation

PINNED_MODE1_RV_1_1_1_SHA = "4d3227edfc474d385128b61d8e8c8b999c5d41f6c0463b43532b7f47869e76a4"


def test_mode1_paninian_unmarked_anudatta_and_sha_determinism(monkeypatch):
    import backend.engine._svara as svara

    def _boom(*_a, **_k):
        raise AssertionError("Mode 1 must never call _sruti-bound helpers in _svara")

    monkeypatch.setattr(svara, "_resolve_sruti_ratio", _boom)
    monkeypatch.setattr(svara, "_build_pitch_contour", _boom)

    verse = "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"
    r1 = render_oral_recitation(verse, recension="rgveda_sakala")
    r2 = render_oral_recitation(verse, recension="rgveda_sakala")

    # F4: 'ग्नि' (index 1, unmarked before 'मी\u0951' udatta) must be anudatta (1.2.40), NOT udatta
    assert r1.events[1].akshara_clean == "\u0917\u094d\u0928\u093f"
    assert r1.events[1].svara == "anudatta"
    assert "1.2.40" in r1.events[1].authority_rule

    # F3: Byte-identical WAV determinism across repeated invocations & fresh subprocess
    assert r1.sha256 == r2.sha256
    assert r1.sha256 == PINNED_MODE1_RV_1_1_1_SHA, "Mode 1 renderer drifted from pinned baseline"