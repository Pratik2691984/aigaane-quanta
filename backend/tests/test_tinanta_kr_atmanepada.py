import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "lakara,purusha,vacana,expected",
    [
        ("laṭ", "prathama_purusha", "ekavacana",  "kurute"),
        ("laṭ", "uttama_purusha",   "ekavacana",  "kurve"),
        ("laṅ", "prathama_purusha", "ekavacana",  "akuruta"),
        ("laṅ", "uttama_purusha",   "bahuvacana", "akurmahi"),
        ("lṛṭ", "prathama_purusha", "ekavacana",  "kariṣyate"),
        ("lṛṭ", "uttama_purusha",   "ekavacana",  "kariṣye"),
        ("loṭ", "prathama_purusha", "ekavacana",  "kurutām"),
        ("loṭ", "madhyama_purusha", "ekavacana",  "kuruṣva"),
        ("loṭ", "uttama_purusha",   "ekavacana",  "karavai"),
    ],
)
def test_kr_atmanepada_table_paradigms(lakara, purusha, vacana, expected):
    res = _tinanta.conjugate("kṛ", lakara, purusha, vacana, "ātmanepada")
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0
