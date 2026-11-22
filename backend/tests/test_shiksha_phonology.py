"""
Gate P1-2 Acceptance Tests: L6 Śikṣā Articulatory Phonology & Allophones.
"""
from __future__ import annotations

from backend.audio.vedic._allophones import realize_allophones, tokenize_iast_phonemes
from backend.audio.vedic._phoneme_inventory import VARNA_INVENTORY, is_svara, lookup_varna


def test_varna_inventory_articulatory_features():
    k = lookup_varna("k")
    assert k is not None
    assert (k.sthana, k.prayatna, k.ghosa, k.prana, k.matra_class) == (
        "kanthya", "sprsta", False, "alpaprana", "vyanjana"
    )

    bh = lookup_varna("bh")
    assert bh is not None
    assert (bh.sthana, bh.prayatna, bh.ghosa, bh.prana) == (
        "osthya", "sprsta", True, "mahaprana"
    )

    t_retro = lookup_varna("ṭ")
    t_dental = lookup_varna("t")
    assert t_retro is not None and t_retro.sthana == "murdhanya"
    assert t_dental is not None and t_dental.sthana == "dantya"

    assert is_svara("a") and is_svara("ā") and is_svara("ṛ") and is_svara("ai")
    assert not is_svara("k") and not is_svara("ḥ")


def test_zero_schwa_deletion_preserves_final_short_a():
    # Classical Sanskrit 'dharma' must retain word-final 'a' (never Hindi 'dharm')
    tokens = tokenize_iast_phonemes("dharma")
    assert tokens == ["dh", "a", "r", "m", "a"]
    realized = realize_allophones(tokens)
    assert realized[-1].surface_iast == "a"
    assert realized[-1].ipa == "ɐ"
    assert "no schwa deletion" in realized[-1].rule_ref


def test_contextual_visarga_jihvamuliya_upadhmaniya_and_echo():
    # 1. Jihvāmūlīya before 'k'
    r1 = realize_allophones(tokenize_iast_phonemes("rāmaḥ karoti"))
    vis1 = [t for t in r1 if t.surface_iast == "ḥ"][0]
    assert vis1.realized_allophone == "jihvamuliya"
    assert vis1.ipa == "x"

    # 2. Upadhmānīya before 'p'
    r2 = realize_allophones(tokenize_iast_phonemes("rāmaḥ patati"))
    vis2 = [t for t in r2 if t.surface_iast == "ḥ"][0]
    assert vis2.realized_allophone == "upadhmaniya"
    assert vis2.ipa == "ɸ"

    # 3. Echo-visarga at avasāna (।)
    r3 = realize_allophones(tokenize_iast_phonemes("kaviḥ ।"))
    vis3 = [t for t in r3 if t.surface_iast == "ḥ"][0]
    assert vis3.realized_allophone == "visarga_echo_i"
    assert vis3.ipa == "hi"


def test_contextual_anusvara_parasavarna_and_anunasika():
    # Before velar 'k' -> 'ṅ'
    r_velar = realize_allophones(tokenize_iast_phonemes("saṃkalpa"))
    anu_velar = [t for t in r_velar if t.surface_iast == "ṃ"][0]
    assert anu_velar.realized_allophone == "parasavarna_ṅ"
    assert anu_velar.ipa == "ŋ"

    # Before dental 't' -> 'n'
    r_dental = realize_allophones(tokenize_iast_phonemes("saṃtoṣa"))
    anu_dental = [t for t in r_dental if t.surface_iast == "ṃ"][0]
    assert anu_dental.realized_allophone == "parasavarna_n"
    assert anu_dental.ipa == "n̪"

    # Before sibilant 's' -> anunāsika glide
    r_sib = realize_allophones(tokenize_iast_phonemes("saṃsāra"))
    anu_sib = [t for t in r_sib if t.surface_iast == "ṃ"][0]
    assert anu_sib.realized_allophone == "anunasika_glide"
