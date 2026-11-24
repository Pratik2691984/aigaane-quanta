import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "lakara,purusha,vacana,expected",
    [
        ('laṭ', 'prathama_purusha', 'ekavacana', 'nayati'),
        ('laṭ', 'uttama_purusha', 'ekavacana', 'nayāmi'),
        ('laṅ', 'prathama_purusha', 'ekavacana', 'anayat'),
        ('laṅ', 'uttama_purusha', 'bahuvacana', 'anayāma'),
        ('lṛṭ', 'prathama_purusha', 'ekavacana', 'neṣyati'),
        ('lṛṭ', 'uttama_purusha', 'ekavacana', 'neṣyāmi'),
        ('loṭ', 'madhyama_purusha', 'ekavacana', 'naya'),
        ('loṭ', 'prathama_purusha', 'bahuvacana', 'nayantu'),
    ],
)
def test_ni_parasmaipada_table_paradigms(lakara, purusha, vacana, expected):
    res = _tinanta.conjugate("nī", lakara, purusha, vacana, "parasmaipada")
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0
