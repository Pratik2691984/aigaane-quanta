import sys
from pathlib import Path
import pytest

ENGINE_DIR = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import _tinanta


def test_labh_dhatupatha_metadata():
    entry = _tinanta._DHATUPATHA.get("labh")
    assert isinstance(entry, dict)
    assert entry["gana"] == 1
    assert entry["meaning"] == "to obtain"
    assert entry["pada"] == "ātmanepada"
    assert entry["stem_pres"] == "labha"
    assert entry["stem_fut"] == "lapsya"
    assert entry["stem_perf"] == "lebh"


@pytest.mark.parametrize(
    "lakara,purusha,vacana,expected",
    [
        ("laṭ", "prathama_purusha", "ekavacana",  "labhate"),
        ("laṭ", "prathama_purusha", "dvivacana",  "labhete"),
        ("laṭ", "prathama_purusha", "bahuvacana", "labhante"),
        ("laṭ", "madhyama_purusha", "ekavacana",  "labhase"),
        ("laṭ", "uttama_purusha",   "ekavacana",  "labhe"),
        ("laṭ", "uttama_purusha",   "bahuvacana", "labhāmahe"),
        ("laṅ", "prathama_purusha", "ekavacana",  "alabhata"),
        ("laṅ", "uttama_purusha",   "bahuvacana", "alabhāmahi"),
        ("lṛṭ", "prathama_purusha", "ekavacana",  "lapsyate"),
        ("lṛṭ", "uttama_purusha",   "ekavacana",  "lapsye"),
        ("loṭ", "prathama_purusha", "ekavacana",  "labhatām"),
        ("loṭ", "madhyama_purusha", "ekavacana",  "labhasva"),
    ],
)
def test_labh_atmanepada_paradigm_source_and_confidence(lakara, purusha, vacana, expected):
    res = _tinanta.conjugate("labh", lakara, purusha, vacana, "ātmanepada")
    assert "error" not in res, f"Unexpected error for labh ({lakara}, {purusha}, {vacana}): {res}"
    assert res["dhatu"] == "labh"
    assert res["pada"] == "ātmanepada"
    assert res["surface"] == expected
    assert res["source"] == "table"
    assert res["confidence"] == 1.0