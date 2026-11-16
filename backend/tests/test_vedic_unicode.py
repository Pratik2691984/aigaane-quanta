"""
P0-2 Acceptance Tests: Vedic Unicode Registry & Vowel-Nucleus Accent Attachment.
"""
from __future__ import annotations

from backend.engine.vedic._mode1 import render_oral_recitation
from backend.engine.vedic._vedic_unicode import (
    PLUTA_QUANTITY_CHAR,
    VEDIC_MARK_REGISTRY,
    extract_vowel_nucleus,
    is_tone_mark,
    segment_vedic_nuclei,
)


def test_registry_covers_vedic_extensions_and_excludes_digit_three():
    assert not is_tone_mark(PLUTA_QUANTITY_CHAR)
    assert PLUTA_QUANTITY_CHAR not in VEDIC_MARK_REGISTRY
    assert VEDIC_MARK_REGISTRY["\u0951"].accent_category == "udatta"
    assert VEDIC_MARK_REGISTRY["\u0952"].accent_category == "anudatta"
    assert VEDIC_MARK_REGISTRY["\u1cdc"].tradition == "kathaka"
    assert VEDIC_MARK_REGISTRY["\u1ce0"].tradition == "rgveda_kashmiri"
    assert VEDIC_MARK_REGISTRY["\u1ce1"].tradition == "atharvaveda"


def test_vowel_nucleus_extraction():
    # Independent vowel 'अ'
    assert extract_vowel_nucleus("\u0905") == "\u0905"
    # Consonant + matra 'मी' -> nucleus 'ई'
    assert extract_vowel_nucleus("\u092e\u0940") == "\u0908"
    # Consonant with inherent 'a' 'ळ' -> nucleus 'अ'
    assert extract_vowel_nucleus("\u0933") == "\u0905"
    # Halanta consonant 'म्' -> None (consonantal coda)
    assert extract_vowel_nucleus("\u092e\u094d") is None


def test_pluta_digit_three_sets_quantity_not_tone_mark():
    # 'अ३॑' -> pluta=True, tone mark='U+0951' (udatta)
    _, tokens = segment_vedic_nuclei("\u0905\u0969\u0951")
    assert len(tokens) == 1
    tok = tokens[0]
    assert tok["is_pluta"] is True
    assert tok["mark_hint"] == "udatta"
    assert tok["unicode_marks"] == ["U+0951"]
    assert tok["vowel_nucleus"] == "\u0905"


def test_mode1_events_expose_vowel_nucleus_and_unicode_marks():
    # अग्निमी॑ळे -> 4 aksharas: अ॒ (a) · ग्नि (gni) · मी॑ (mī) · ळे (ḷe)
    verse = "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"
    res = render_oral_recitation(verse, recension="rgveda_sakala")
    assert len(res.events) == 4
    # Akshara 0: 'अ॒' -> nucleus 'अ', mark U+0952
    assert res.events[0].vowel_nucleus == "\u0905"
    assert res.events[0].unicode_marks == ["U+0952"]
    assert res.events[0].svara == "anudatta"
    # Akshara 1: 'ग्नि' -> nucleus 'इ', unmarked baseline
    assert res.events[1].vowel_nucleus == "\u0907"
    assert res.events[1].unicode_marks == []
    # Akshara 2: 'मी॑' -> nucleus 'ई', mark U+0951
    assert res.events[2].vowel_nucleus == "\u0908"
    assert res.events[2].unicode_marks == ["U+0951"]
    assert res.events[2].svara == "udatta"
    # Akshara 3: 'ळे' -> nucleus 'ए', derived svarita (Panini 8.4.66)
    assert res.events[3].vowel_nucleus == "\u090f"
    assert res.events[3].svara == "svarita"
    assert res.events[3].svara_source == "derived"
