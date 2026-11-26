import pytest
from backend.engine import _tinanta
from backend.engine._lexicon import _DHATUPATHA


@pytest.mark.parametrize(
    "dhatu,lakara,pada,purusha,vacana,expected",
    [
        ("pā",  "laṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "pibati"),
        ("pā",  "laṅ", "parasmaipada", "prathama_purusha", "ekavacana",  "apibat"),
        ("pā",  "lṛṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "pāsyati"),
        ("pā",  "loṭ", "parasmaipada", "uttama_purusha",   "ekavacana",  "pibāni"),
        ("dā",  "laṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "dadāti"),
        ("dā",  "laṅ", "parasmaipada", "prathama_purusha", "bahuvacana", "adadhuḥ"),
        ("dā",  "lṛṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "dāsyati"),
        ("dā",  "loṭ", "parasmaipada", "madhyama_purusha", "ekavacana",  "dehi"),
        ("viś", "laṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "viśati"),
        ("viś", "laṅ", "parasmaipada", "prathama_purusha", "ekavacana",  "aviśat"),
        ("viś", "lṛṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "vekṣyati"),
        ("viś", "loṭ", "parasmaipada", "prathama_purusha", "bahuvacana", "viśantu"),
        ("vah", "laṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "vahati"),
        ("vah", "laṅ", "parasmaipada", "prathama_purusha", "ekavacana",  "avahat"),
        ("vah", "lṛṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "vakṣyati"),
        ("vah", "loṭ", "parasmaipada", "uttama_purusha",   "ekavacana",  "vahāni"),
        ("nī",  "laṭ", "ātmanepada",   "prathama_purusha", "ekavacana",  "nayate"),
        ("nī",  "laṅ", "ātmanepada",   "prathama_purusha", "ekavacana",  "anayata"),
        ("nī",  "lṛṭ", "ātmanepada",   "prathama_purusha", "ekavacana",  "neṣyate"),
        ("nī",  "loṭ", "ātmanepada",   "prathama_purusha", "ekavacana",  "nayatām"),
        ("hu",  "laṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "juhoti"),
        ("hu",  "laṅ", "parasmaipada", "prathama_purusha", "ekavacana",  "ajuhot"),
        ("hu",  "lṛṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "hoṣyati"),
        ("hu",  "loṭ", "parasmaipada", "madhyama_purusha", "ekavacana",  "juhudhi"),
        ("jñā", "laṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "jānāti"),
        ("jñā", "laṅ", "parasmaipada", "prathama_purusha", "ekavacana",  "ajānāt"),
        ("jñā", "lṛṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "jñāsyati"),
        ("jñā", "loṭ", "parasmaipada", "madhyama_purusha", "ekavacana",  "jānīhi"),
        ("cur", "laṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "corayati"),
        ("cur", "laṅ", "parasmaipada", "prathama_purusha", "ekavacana",  "acorayat"),
        ("cur", "lṛṭ", "parasmaipada", "prathama_purusha", "ekavacana",  "corayiṣyati"),
        ("cur", "loṭ", "parasmaipada", "uttama_purusha",   "ekavacana",  "corayāni"),
    ],
)
def test_remaining_dhatupatha_roots_table_paradigms(dhatu, lakara, pada, purusha, vacana, expected):
    res = _tinanta.conjugate(dhatu, lakara, purusha, vacana, pada)
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0


def test_all_twenty_dhatupatha_roots_present():
    assert len(_DHATUPATHA) == 20
    for root in (
        "bhū", "gam", "paṭh", "kṛ", "pā", "labh", "dā", "viś", "vah", "likh",
        "vad", "sthā", "nī", "dṛś", "smṛ", "car", "as", "hu", "jñā", "cur",
    ):
        assert root in _DHATUPATHA
