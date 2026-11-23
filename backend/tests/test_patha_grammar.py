"""
Golden regression tests for Vedic Vikṛti Pāṭha grammar (_patha_grammar.py).
"""
import sys
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

import pytest
from backend.engine.vedic._patha_grammar import (
    SUPPORTED_PATHAS,
    generate_ghana,
    generate_jata,
    generate_krama,
    pada_to_samhita,
    samhita_to_padas,
    transform_patha,
)


RV_1_1_1_PADA_1_PADAS = ["agnim", "īḷe", "purohitam", "yajñasya", "devam", "ṛtvijam"]


def test_krama_golden_rv_1_1_1():
    res = generate_krama(RV_1_1_1_PADA_1_PADAS)
    assert res.patha == "krama"
    assert res.shakha == "rgveda_sakala"
    assert res.units == [
        ["agnim", "īḷe"],
        ["īḷe", "purohitam"],
        ["purohitam", "yajñasya"],
        ["yajñasya", "devam"],
        ["devam", "ṛtvijam"],
        ["ṛtvijam", "iti", "ṛtvijam"],
    ]
    assert res.rendered_text.endswith("ṛtvijam iti ṛtvijam ॥")


def test_jata_golden_three_padas():
    padas = ["agnim", "īḷe", "purohitam"]
    res = generate_jata(padas)
    assert res.units == [
        ["agnim", "īḷe", "īḷe", "agnim", "agnim", "īḷe"],
        ["īḷe", "purohitam", "purohitam", "īḷe", "īḷe", "purohitam"],
        ["purohitam", "iti", "purohitam"],
    ]


def test_ghana_golden_13_token_weave():
    padas = ["agnim", "īḷe", "purohitam"]
    res = generate_ghana(padas)
    # Canonical 13-token Ghana pattern: a b b a a b c c b a a b c
    assert res.units[0] == [
        "agnim", "īḷe", "īḷe", "agnim", "agnim", "īḷe",
        "purohitam", "purohitam", "īḷe", "agnim", "agnim", "īḷe", "purohitam",
    ]
    assert len(res.units[0]) == 13
    assert res.units[1] == ["īḷe", "purohitam", "purohitam", "īḷe", "īḷe", "purohitam"]
    assert res.units[2] == ["purohitam", "iti", "purohitam"]


def test_samhita_and_pada_roundtrip():
    samhita = pada_to_samhita(["deva", "indraḥ"])
    assert samhita == "devendraḥ"
    padas = samhita_to_padas("devendraḥ")
    assert padas == ["deva", "indraḥ"]


def test_vedic_accent_preservation_in_vikriti():
    accented = ["अ॒ग्निम्", "ई॒ळे", "पु॒रोहि॑तम्"]
    res = generate_jata(accented)
    assert res.units[0] == ["अ॒ग्निम्", "ई॒ळे", "ई॒ळे", "अ॒ग्निम्", "अ॒ग्निम्", "ई॒ळे"]
    assert "पु॒रोहि॑तम् iti पु॒रोहि॑तम् ॥" in res.rendered_text


def test_transform_patha_rejects_unknown_mode():
    with pytest.raises(ValueError, match="Unsupported patha"):
        transform_patha(["agnim", "īḷe"], patha="unknown_mode")
def test_pada_to_samhita_fallback_preserves_unmerged_accented_tokens():
    accented = ["अ॒ग्निम्", "ई॒ळे"]
    out = pada_to_samhita(accented)
    # When _sandhi_gen.combine_sandhi does not merge accented Devanagari inputs,
    # _join_pair_samhita falls back to spacing tokens and preserves accents.
    assert out == "अ॒ग्निम् ई॒ळे"
    assert "\u0952" in out


def test_vikriti_modes_preserve_accents_on_vedic_padas():
    accented = ["अ॒ग्निम्", "ई॒ळे", "पु॒रोहि॑तम्"]
    jata_out = generate_jata(accented).rendered_text
    samhita_out = pada_to_samhita(accented)
    assert "\u0951" in jata_out or "\u0952" in jata_out
    assert "\u0952" in samhita_out


def test_vedic_accents_covers_all_tone_categories_but_not_breath():
    from backend.engine.vedic._patha_grammar import _VEDIC_ACCENTS
    from backend.engine.vedic._vedic_unicode import VEDIC_MARK_REGISTRY

    tone_categories = {
        "udatta",
        "anudatta",
        "svarita",
        "svarita_double",
        "svarita_triple",
        "samaveda_tone",
    }
    for cp, spec in VEDIC_MARK_REGISTRY.items():
        if spec.accent_category in tone_categories:
            assert cp in _VEDIC_ACCENTS, f"Tone mark {spec.codepoint} missing from _VEDIC_ACCENTS"
        elif spec.accent_category == "nasal_or_breath":
            assert cp not in _VEDIC_ACCENTS, f"Breath mark {spec.codepoint} should not be stripped"


def test_pada_to_samhita_strips_candra_above_before_sandhi():
    out = pada_to_samhita(["deva\u1cf4", "indraḥ"])
    assert "\u1cf4" not in out
    assert out == "devendraḥ"
