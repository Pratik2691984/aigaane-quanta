import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "lakara,purusha,vacana,expected",
    [
        ("laṭ", "prathama_purusha", "ekavacana",  "paṭhati"),
        ("laṭ", "uttama_purusha",   "ekavacana",  "paṭhāmi"),
        ("laṅ", "prathama_purusha", "ekavacana",  "apaṭhat"),
        ("laṅ", "uttama_purusha",   "bahuvacana", "apaṭhāma"),
        ("lṛṭ", "prathama_purusha", "ekavacana",  "paṭhiṣyati"),
        ("lṛṭ", "uttama_purusha",   "ekavacana",  "paṭhiṣyāmi"),
        ("loṭ", "madhyama_purusha", "ekavacana",  "paṭha"),
        ("loṭ", "prathama_purusha", "bahuvacana", "paṭhantu"),
    ],
)
def test_path_parasmaipada_table_paradigms(lakara, purusha, vacana, expected):
    res = _tinanta.conjugate("paṭh", lakara, purusha, vacana, "parasmaipada")
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0
