import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "lakara,purusha,vacana,expected",
    [
        ('laṭ', 'prathama_purusha', 'ekavacana', 'paśyati'),
        ('laṭ', 'uttama_purusha', 'ekavacana', 'paśyāmi'),
        ('laṅ', 'prathama_purusha', 'ekavacana', 'apaśyat'),
        ('laṅ', 'uttama_purusha', 'bahuvacana', 'apaśyāma'),
        ('lṛṭ', 'prathama_purusha', 'ekavacana', 'drakṣyati'),
        ('lṛṭ', 'uttama_purusha', 'ekavacana', 'drakṣyāmi'),
        ('loṭ', 'madhyama_purusha', 'ekavacana', 'paśya'),
        ('loṭ', 'prathama_purusha', 'bahuvacana', 'paśyantu'),
    ],
)
def test_dris_parasmaipada_table_paradigms(lakara, purusha, vacana, expected):
    res = _tinanta.conjugate("dṛś", lakara, purusha, vacana, "parasmaipada")
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0
