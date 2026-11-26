from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_ENGINE = _REPO / "backend" / "engine"
for _p in (str(_REPO), str(_ENGINE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from backend.engine import _prakriya
import _lexicon
import _tinanta


def test_gacchati_prakriya_trace_and_engine_agreement():
    trace = _prakriya.derive_gacchati()
    assert trace.result_classification == "DETERMINISTIC_DERIVATION"
    assert trace.surface == "gacchati"
    assert len(trace.steps) == 4
    assert trace.sutra_chain == [
        "3.2.123",
        "3.4.78",
        "1.4.101",
        "1.3.3",
        "1.3.9",
        "3.1.68",
        "1.3.8",
        "7.3.77",
        "1.4.14",
    ]
    assert trace.anuvrtti["lakara"] == "laṭ"
    assert trace.anuvrtti["purusha"] == "prathama_purusha"
    assert trace.anuvrtti["vacana"] == "ekavacana"

    conj = _tinanta.conjugate("gam", "laṭ", "prathama_purusha", "ekavacana", "parasmaipada")
    assert conj.get("surface") == trace.surface

    lex_hit = _lexicon.lookup("gacchati")
    assert lex_hit is not None
    assert lex_hit.get("dhatu") == trace.prakruti


def test_ramah_prakriya_trace_and_tripadi_ordering():
    trace = _prakriya.derive_ramah()
    assert trace.result_classification == "DETERMINISTIC_DERIVATION"
    assert trace.surface == "rāmaḥ"
    assert len(trace.steps) == 4
    assert "8.2.1" in trace.sutra_chain
    assert "8.2.66" in trace.sutra_chain
    assert "8.3.15" in trace.sutra_chain
    assert trace.sutra_chain.index("1.3.9") < trace.sutra_chain.index("8.2.66")
    assert trace.sutra_chain.index("8.2.66") < trace.sutra_chain.index("8.3.15")

    lex_hit = _lexicon.lookup("rāmaḥ")
    assert lex_hit is not None
    assert lex_hit.get("stem") == trace.prakruti


def test_prakriya_traces_are_deterministic_and_unresolved_for_unknown():
    t1 = _prakriya.derive_form("gacchati")
    t2 = _prakriya.derive_form("gacchati")
    assert t1 is not None and t2 is not None
    assert t1.to_dict() == t2.to_dict()

    assert _prakriya.derive_form("nonexistent_xyz_form") is None
def test_bhavati_and_tisthati_prakriya_traces_and_engine_agreement():
    bh_trace = _prakriya.derive_bhavati()
    assert bh_trace.result_classification == "DETERMINISTIC_DERIVATION"
    assert bh_trace.surface == "bhavati"
    assert bh_trace.prakruti == "bhū"
    assert len(bh_trace.steps) == 4
    assert "7.3.84" in bh_trace.sutra_chain
    assert "1.4.14" in bh_trace.sutra_chain

    bh_conj = _tinanta.conjugate("bhū", "laṭ", "prathama_purusha", "ekavacana", "parasmaipada")
    assert bh_conj.get("surface") == bh_trace.surface

    bh_lex = _lexicon.lookup("bhavati")
    assert bh_lex is not None
    assert bh_lex.get("dhatu") == bh_trace.prakruti

    th_trace = _prakriya.derive_tisthati()
    assert th_trace.result_classification == "DETERMINISTIC_DERIVATION"
    assert th_trace.surface == "tiṣṭhati"
    assert th_trace.prakruti == "sthā"
    assert len(th_trace.steps) == 4
    assert "7.4.61" in th_trace.sutra_chain
    assert "1.4.14" in th_trace.sutra_chain

    th_conj = _tinanta.conjugate("sthā", "laṭ", "prathama_purusha", "ekavacana", "parasmaipada")
    assert th_conj.get("surface") == th_trace.surface

    th_lex = _lexicon.lookup("tiṣṭhati")
    assert th_lex is not None
    assert th_lex.get("dhatu") == th_trace.prakruti

    assert _prakriya.derive_form("bhavati") is not None
    assert _prakriya.derive_form("tiṣṭhati") is not None
def test_ramasya_prakriya_trace_and_lexicon_agreement():
    trace = _prakriya.derive_ramasya()
    assert trace.result_classification == "DETERMINISTIC_DERIVATION"
    assert trace.surface == "rāmasya"
    assert trace.prakruti == "rāma"
    assert trace.category == "subanta"
    assert len(trace.steps) == 3
    assert "2.3.50" in trace.sutra_chain
    assert "4.1.2" in trace.sutra_chain
    assert "1.4.14" in trace.sutra_chain

    lex_hit = _lexicon.lookup("rāmasya")
    assert lex_hit is not None
    assert lex_hit.get("stem") == trace.prakruti
    assert lex_hit.get("vibhakti") == "shasthi"

    assert _prakriya.derive_form("rāmasya") is not None
    assert _prakriya.derive_form("ramasya") is not None
def test_tripadi_and_adhikara_validation_on_registered_and_invalid_traces():
    for form in ("gacchati", "bhavati", "tiṣṭhati", "rāmaḥ", "rāmasya"):
        trace = _prakriya.derive_form(form)
        assert trace is not None
        assert _prakriya.validate_prakriya_trace(trace) == []

    # Invalid 1: Sapadasaptadhyayee rule (7.3.84) recorded after Tripadi rule (8.3.15)
    bad_purvatrasiddham = _prakriya.PrakriyaTrace(
        query_form="invalid_order",
        prakruti="bhū",
        category="tinanta",
        adhikaras_active=["tripadi", "angasya"],
        anuvrtti={},
        segments=["bhū"],
        surface="bhū",
        sutra_chain=[],
        result_classification="UNRESOLVED",
    )
    _prakriya._record_step(
        trace=bad_purvatrasiddham,
        stage="tripadi",
        sutra_ids=["8.3.15"],
        rule_title="visarga",
        adhikara="tripadi",
        next_segments=["bhūḥ"],
        next_surface="bhūḥ",
    )
    _prakriya._record_step(
        trace=bad_purvatrasiddham,
        stage="anga",
        sutra_ids=["7.3.84"],
        rule_title="guna after tripadi",
        adhikara="angasya",
        next_segments=["bhoḥ"],
        next_surface="bhoḥ",
    )
    v_order = _prakriya.validate_prakriya_trace(bad_purvatrasiddham)
    assert any(v.startswith("PURVATRASIDDHAM_VIOLATION:") for v in v_order)

    # Invalid 2: Adhikara mismatch between step adhikara and registered SutraRule.adhikara
    bad_adhikara = _prakriya.PrakriyaTrace(
        query_form="bad_adhikara",
        prakruti="gam",
        category="tinanta",
        adhikaras_active=["pratyaya", "angasya"],
        anuvrtti={},
        segments=["gam"],
        surface="gam",
        sutra_chain=[],
        result_classification="UNRESOLVED",
    )
    _prakriya._record_step(
        trace=bad_adhikara,
        stage="pratyaya_yojana",
        sutra_ids=["7.3.77"],
        rule_title="mismatched adhikara",
        adhikara="pratyaya",
        next_segments=["gaccha"],
        next_surface="gaccha",
    )
    v_adh = _prakriya.validate_prakriya_trace(bad_adhikara)
    assert any(v.startswith("ADHIKARA_MISMATCH:") for v in v_adh)
def test_vibhasa_visarga_multi_branch_trace_and_validation():
    trace = _prakriya.derive_vibhasa_visarga()
    assert trace.result_classification == "AMBIGUOUS_DERIVATION"
    assert len(trace.branches) == 2
    assert "8.3.36" in trace.branches[0]
    assert "8.4.40" not in trace.branches[0]
    assert "8.3.36" in trace.branches[1]
    assert "8.4.40" in trace.branches[1]
    assert "rāmaḥ śete" in trace.anuvrtti["variant_surfaces"]
    assert "rāmaś śete" in trace.anuvrtti["variant_surfaces"]
    assert _prakriya.validate_prakriya_trace(trace) == []

    t_a = _prakriya.derive_form("rāmaḥ śete")
    t_b = _prakriya.derive_form("rāmaś śete")
    assert t_a is not None and t_b is not None
    assert t_a.to_dict() == t_b.to_dict()

    broken = _prakriya.derive_vibhasa_visarga()
    broken.branches = [broken.branches[0]]
    assert "AMBIGUOUS_DERIVATION_REQUIRES_MULTI_BRANCH" in _prakriya.validate_prakriya_trace(broken)
def test_additional_lakara_and_subanta_traces_and_validation():
    fut = _prakriya.derive_bhavisyati()
    assert fut.result_classification == "DETERMINISTIC_DERIVATION"
    assert fut.surface == "bhaviṣyati"
    assert fut.anuvrtti["lakara"] == "lṛṭ"
    assert "3.3.13" in fut.sutra_chain
    assert "3.1.33" in fut.sutra_chain
    assert "8.3.59" in fut.sutra_chain
    assert _prakriya.validate_prakriya_trace(fut) == []

    imp = _prakriya.derive_bhavatu()
    assert imp.result_classification == "DETERMINISTIC_DERIVATION"
    assert imp.surface == "bhavatu"
    assert imp.anuvrtti["lakara"] == "loṭ"
    assert "3.3.162" in imp.sutra_chain
    assert "3.4.86" in imp.sutra_chain
    assert _prakriya.validate_prakriya_trace(imp) == []

    acc = _prakriya.derive_ramam()
    assert acc.result_classification == "DETERMINISTIC_DERIVATION"
    assert acc.surface == "rāmam"
    assert "2.3.2" in acc.sutra_chain
    assert "6.1.107" in acc.sutra_chain
    assert _prakriya.validate_prakriya_trace(acc) == []

    loc = _prakriya.derive_rame()
    assert loc.result_classification == "DETERMINISTIC_DERIVATION"
    assert loc.surface == "rāme"
    assert "2.3.36" in loc.sutra_chain
    assert "6.1.87" in loc.sutra_chain
    assert _prakriya.validate_prakriya_trace(loc) == []

    for key in ("bhaviṣyati", "bhavishyati", "bhavatu", "rāmam", "ramam", "rāme", "rame"):
        assert _prakriya.derive_form(key) is not None
def test_engine_adapter_attaches_verified_prakriya_trace():
    from backend.engine.adapter import EngineAdapter

    adapter = EngineAdapter()

    for surface, expected_chain in (
        ("gacchati", ["3.2.123", "3.4.78", "1.4.101", "1.3.3", "1.3.9", "3.1.68", "1.3.8", "7.3.77", "1.4.14"]),
        ("bhavati", ["3.2.123", "3.4.78", "1.4.101", "1.3.3", "1.3.9", "3.1.68", "1.3.8", "7.3.84", "1.4.14"]),
        ("rāmaḥ", ["4.1.2", "2.3.46", "1.3.2", "1.3.9", "8.2.1", "8.2.66", "8.3.15", "1.4.14"]),
    ):
        env = adapter.parse(surface)
        assert len(env.candidates) >= 1
        cand = env.candidates[0]
        assert cand.result_classification == "DETERMINISTIC_DERIVATION"
        assert cand.sutra_chain == expected_chain
        assert cand.derivation_trace is not None
        assert cand.derivation_trace["surface"] == surface
        assert len(cand.derivation_trace["steps"]) >= 3

    unknown_env = adapter.parse("nonexistent_xyz_form")
    for cand in unknown_env.candidates:
        assert cand.derivation_trace is None
        assert cand.result_classification != "DETERMINISTIC_DERIVATION"
