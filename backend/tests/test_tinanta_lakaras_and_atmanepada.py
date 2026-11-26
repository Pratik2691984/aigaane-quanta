import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "dhatu,lakara,pada,purusha,vacana,expected",
    [
        ("bhū",  "laṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "bhavati"),
        ("kṛ",   "laṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "karoti"),
        ("kṛ",   "laṭ", "ātmanepada",   "prathama_purusha", "ekavacana",  "kurute"),
        ("labh", "laṭ", "ātmanepada",   "prathama_purusha", "ekavacana",  "labhate"),
        ("dā",   "loṭ", "ātmanepada",   "prathama_purusha", "ekavacana",  "dattām"),
        ("jñā",  "laṭ", "ātmanepada",   "prathama_purusha", "ekavacana",  "jānīte"),
    ],
)
def test_tinanta_table_forms_and_metadata(dhatu, lakara, pada, purusha, vacana, expected):
    res = _tinanta.conjugate(dhatu, lakara, purusha, vacana, pada)
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0


def test_extended_lakara_bhū_if_present():
    if not hasattr(_tinanta, "get_extended_conjugation"):
        pytest.skip("get_extended_conjugation not present in _tinanta")
    assert _tinanta.get_extended_conjugation("bhū", "vidhiliṅ", "prathama_purusha", "ekavacana", "parasmaipada") == "bhavet"
    assert _tinanta.get_extended_conjugation("bhū", "liṭ", "prathama_purusha", "ekavacana", "parasmaipada") == "babhūva"
