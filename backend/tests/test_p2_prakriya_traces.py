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
