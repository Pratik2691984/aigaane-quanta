from __future__ import annotations

import json
import pytest

from backend.engine import _neural_fallback
from backend.engine.adapter import EngineAdapter
from backend.engine.pydantic_models import Authority, Candidate, KernelEnvelope, OrthographicTriad, ParseToken
from backend.critic.gatekeeper import CegarGatekeeper
from backend.nyaya.schemas import NyayaVerifyRequest
from backend.nyaya.verifier import NyayaVerifier


def test_fallback_parse_classifies_heuristic_unverified():
    res = _neural_fallback.fallback_parse("xyz", "xyz", "xyṣ", "xyz")
    assert res is not None
    assert res["result_classification"] == "HEURISTIC_UNVERIFIED"
    assert res["provenance"] == ["engine=heuristic-unknown-fallback"]


def test_fallback_parse_returns_none_for_noise():
    assert _neural_fallback.fallback_parse("123_bad", "123_bad", "123_bad", "123_bad") is None
    assert _neural_fallback.fallback_parse("", "", "", "") is None


def test_adapter_preserves_heuristic_and_ambiguous_classifications(monkeypatch):
    import backend.engine.adapter as adapter_mod

    monkeypatch.setattr(
        adapter_mod.legacy_engine,
        "parse",
        lambda _iast: {
            "schema_version": "0.2.0",
            "surface": "xyz",
            "normalized": "xyṣ",
            "transliteration": {"devanagari": "xyṣ", "iast": "xyz"},
            "tokens": [
                {
                    "token_id": "T0",
                    "pada": "xyz",
                    "stem": "xyz",
                    "pos": "subhanta",
                    "vibhakti": "prathama",
                    "vacana": "ekavacana",
                    "linga": "pullinga",
                    "confidence": 0.50,
                }
            ],
            "ambiguous_parses": [
                {
                    "tokens": [{"pada": "xyz", "stem": "xyz", "pos": "subhanta", "confidence": 0.40}],
                    "ambiguity_type": "homonym",
                    "confidence": 0.40,
                }
            ],
            "canon_refs": ["2.1.1"],
            "confidence": 0.50,
            "provenance": ["engine=heuristic-unknown-fallback"],
            "result_classification": "HEURISTIC_UNVERIFIED",
        },
    )

    env = EngineAdapter().parse("xyz")
    assert isinstance(env, KernelEnvelope)
    assert len(env.candidates) == 2
    assert env.candidates[0].result_classification == "HEURISTIC_UNVERIFIED"
    assert env.candidates[0].result_classification != "DETERMINISTIC_DERIVATION"
    assert env.candidates[1].result_classification == "AMBIGUOUS_DERIVATION"


def test_gatekeeper_does_not_promote_heuristic_or_unresolved_candidates():
    gk = CegarGatekeeper()
    monkeypatch_target = gk
    monkeypatch_target._attest_stem = lambda _stem: True  # type: ignore[method-assign]

    env = KernelEnvelope(
        input_triad=OrthographicTriad(devanagari="क", iast="ka", slp1="ka"),
        candidates=[
            Candidate(
                candidate_id="cand_01",
                parse=[ParseToken(surface="ka", stem="ka", role="subanta:prathama")],
                sutra_chain=["2.1.1"],
                authority=Authority(recension="Kasika_Vrtti", primary_source="fallback"),
                result_classification="HEURISTIC_UNVERIFIED",
                score=0.90,
            ),
            Candidate(
                candidate_id="cand_02",
                parse=[ParseToken(surface="ka", stem="ka", role="subanta:prathama")],
                sutra_chain=[],
                authority=Authority(recension="Kasika_Vrtti", primary_source="unknown"),
                result_classification=None,
                score=0.50,
            ),
        ],
        rejected=[],
        engine_version="1.0.9-adapter",
    )

    out = gk.verify(env)
    by_score = {round(c.score, 2): c for c in out.candidates}
    assert by_score[0.90].result_classification == "HEURISTIC_UNVERIFIED"
    assert by_score[0.50].result_classification == "UNRESOLVED"


def test_nyaya_verifier_rejects_heuristic_missing_or_unresolved():
    verifier = NyayaVerifier()

    heur = verifier.verify(
        NyayaVerifyRequest(
            candidate_id="cand_01",
            sutra_chain=["1.1.1", "1.1.2"],
            result_classification="HEURISTIC_UNVERIFIED",
        )
    )
    assert heur.is_valid is False

    missing_cls = verifier.verify(
        NyayaVerifyRequest(
            candidate_id="cand_01",
            sutra_chain=["1.1.1"],
            result_classification=None,
        )
    )
    assert missing_cls.is_valid is False

    det = verifier.verify(
        NyayaVerifyRequest(
            candidate_id="cand_01",
            sutra_chain=["1.1.1"],
            result_classification="DETERMINISTIC_DERIVATION",
        )
    )
    assert det.is_valid is True

    # Ensure JSON serialization preserves existing envelope keys
    dumped = json.loads(
        KernelEnvelope(
            input_triad=OrthographicTriad(devanagari="क", iast="ka", slp1="ka"),
            candidates=[],
            rejected=[],
            engine_version="1.0.9-adapter",
        ).model_dump_json()
    )
    assert {"input_triad", "candidates", "rejected", "engine_version"} <= set(dumped.keys())
