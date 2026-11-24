import pytest
from backend.engine import _tinanta


@pytest.mark.parametrize(
    "lakara,purusha,vacana,expected",
    [
        ('laṭ', 'prathama_purusha', 'ekavacana', 'smarati'),
        ('laṭ', 'uttama_purusha', 'ekavacana', 'smarāmi'),
        ('laṅ', 'prathama_purusha', 'ekavacana', 'asmarat'),
        ('laṅ', 'uttama_purusha', 'bahuvacana', 'asmarāma'),
        ('lṛṭ', 'prathama_purusha', 'ekavacana', 'smariṣyati'),
        ('lṛṭ', 'uttama_purusha', 'ekavacana', 'smariṣyāmi'),
        ('loṭ', 'madhyama_purusha', 'ekavacana', 'smara'),
        ('loṭ', 'prathama_purusha', 'bahuvacana', 'smarantu'),
    ],
)
def test_smri_parasmaipada_table_paradigms(lakara, purusha, vacana, expected):
    res = _tinanta.conjugate("smṛ", lakara, purusha, vacana, "parasmaipada")
    assert "error" not in res
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0
