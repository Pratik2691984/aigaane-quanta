import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "lakara,purusha,vacana,expected",
    [
        ("laṭ", "prathama_purusha", "ekavacana",  "tiṣṭhati"),
        ("laṭ", "uttama_purusha",   "ekavacana",  "tiṣṭhāmi"),
        ("laṅ", "prathama_purusha", "ekavacana",  "atiṣṭhat"),
        ("laṅ", "uttama_purusha",   "bahuvacana", "atiṣṭhāma"),
        ("lṛṭ", "prathama_purusha", "ekavacana",  "sthāsyati"),
        ("lṛṭ", "uttama_purusha",   "ekavacana",  "sthāsyāmi"),
        ("loṭ", "madhyama_purusha", "ekavacana",  "tiṣṭha"),
        ("loṭ", "prathama_purusha", "bahuvacana", "tiṣṭhantu"),
    ],
)
def test_stha_parasmaipada_table_paradigms(lakara, purusha, vacana, expected):
    res = _tinanta.conjugate("sthā", lakara, purusha, vacana, "parasmaipada")
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0
