import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "lakara,purusha,vacana,expected",
    [
        ("laṭ", "prathama_purusha", "ekavacana",  "vadati"),
        ("laṭ", "uttama_purusha",   "ekavacana",  "vadāmi"),
        ("laṅ", "prathama_purusha", "ekavacana",  "avadat"),
        ("laṅ", "uttama_purusha",   "bahuvacana", "avadāma"),
        ("lṛṭ", "prathama_purusha", "ekavacana",  "vadiṣyati"),
        ("lṛṭ", "uttama_purusha",   "ekavacana",  "vadiṣyāmi"),
        ("loṭ", "madhyama_purusha", "ekavacana",  "vada"),
        ("loṭ", "prathama_purusha", "bahuvacana", "vadantu"),
    ],
)
def test_vad_parasmaipada_table_paradigms(lakara, purusha, vacana, expected):
    res = _tinanta.conjugate("vad", lakara, purusha, vacana, "parasmaipada")
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0
