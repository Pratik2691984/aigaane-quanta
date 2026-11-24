import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "lakara,purusha,vacana,expected",
    [
        ('laṭ', 'prathama_purusha', 'ekavacana', 'carati'),
        ('laṭ', 'uttama_purusha', 'ekavacana', 'carāmi'),
        ('laṅ', 'prathama_purusha', 'ekavacana', 'acarat'),
        ('laṅ', 'uttama_purusha', 'bahuvacana', 'acarāma'),
        ('lṛṭ', 'prathama_purusha', 'ekavacana', 'cariṣyati'),
        ('lṛṭ', 'uttama_purusha', 'ekavacana', 'cariṣyāmi'),
        ('loṭ', 'madhyama_purusha', 'ekavacana', 'cara'),
        ('loṭ', 'prathama_purusha', 'bahuvacana', 'carantu'),
    ],
)
def test_car_parasmaipada_table_paradigms(lakara, purusha, vacana, expected):
    res = _tinanta.conjugate("car", lakara, purusha, vacana, "parasmaipada")
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0
