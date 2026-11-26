import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "dhatu,lakara,pada,purusha,vacana,expected",
    [
        ("bhū", "laṭ", "parasmaipada", "prathama_purusha", "ekavacana", "bhavati"),
        ("bhū", "laṅ", "parasmaipada", "prathama_purusha", "ekavacana", "abhavat"),
        ("bhū", "lṛṭ", "parasmaipada", "prathama_purusha", "ekavacana", "bhaviṣyati"),
        ("bhū", "loṭ", "parasmaipada", "prathama_purusha", "ekavacana", "bhavatu"),
        ("kṛ",  "laṭ", "ātmanepada",   "prathama_purusha", "ekavacana", "kurute"),
        ("kṛ",  "laṅ", "ātmanepada",   "prathama_purusha", "ekavacana", "akuruta"),
        ("kṛ",  "lṛṭ", "ātmanepada",   "prathama_purusha", "ekavacana", "kariṣyate"),
        ("kṛ",  "loṭ", "ātmanepada",   "prathama_purusha", "ekavacana", "kurutām"),
    ],
)
def test_primary_parasmaipada_and_atmanepada_table_cells(dhatu, lakara, pada, purusha, vacana, expected):
    res = _tinanta.conjugate(dhatu, lakara, purusha, vacana, pada)
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0


def test_extended_lakaras_bhu_and_kr_boundary():
    if not hasattr(_tinanta, "get_extended_conjugation"):
        pytest.skip("get_extended_conjugation not available in _tinanta")
    assert _tinanta.get_extended_conjugation("bhū", "vidhiliṅ", "prathama_purusha", "ekavacana", "parasmaipada") == "bhavet"
    assert _tinanta.get_extended_conjugation("bhū", "liṭ", "prathama_purusha", "ekavacana", "parasmaipada") == "babhūva"
    assert _tinanta.get_extended_conjugation("kṛ", "vidhiliṅ", "prathama_purusha", "ekavacana", "parasmaipada") is None
    assert _tinanta.get_extended_conjugation("kṛ", "liṭ", "prathama_purusha", "ekavacana", "parasmaipada") is None
