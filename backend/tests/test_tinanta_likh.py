import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "lakara,purusha,vacana,expected",
    [
        ("laṭ", "prathama_purusha", "ekavacana",  "likhati"),
        ("laṭ", "uttama_purusha",   "ekavacana",  "likhāmi"),
        ("laṅ", "prathama_purusha", "ekavacana",  "alikhat"),
        ("laṅ", "uttama_purusha",   "bahuvacana", "alikhāma"),
        ("lṛṭ", "prathama_purusha", "ekavacana",  "lekhiṣyati"),
        ("lṛṭ", "uttama_purusha",   "ekavacana",  "lekhiṣyāmi"),
        ("loṭ", "madhyama_purusha", "ekavacana",  "likha"),
        ("loṭ", "prathama_purusha", "bahuvacana", "likhantu"),
    ],
)
def test_likh_parasmaipada_table_paradigms(lakara, purusha, vacana, expected):
    res = _tinanta.conjugate("likh", lakara, purusha, vacana, "parasmaipada")
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0
