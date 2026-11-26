from backend.engine.vedic._patha_grammar import transform_patha


def test_vikriti_modes_krama_jata_ghana_are_deterministic():
    padas = ["अ॒ग्निम्", "ई॒ळे"]
    for mode in ("krama", "jata", "ghana"):
        r1 = transform_patha(padas, patha=mode)
        r2 = transform_patha(padas, patha=mode)
        assert r1.rendered_text == r2.rendered_text
        assert len(r1.rendered_text.strip()) > 0
