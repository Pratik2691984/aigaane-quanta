from backend.engine import _samasa
from backend.engine.vedic._patha_grammar import transform_patha, pada_to_samhita


def test_recursive_split_compound_multitoken_depth():
    node = _samasa.recursive_split_compound("rājaputravadhaḥ")
    assert node is not None
    assert node["depth"] == 1
    assert node["left_stem"] == "rāja"
    assert node["sub_tree"] is not None
    assert node["sub_tree"]["depth"] == 2
    assert node["sub_tree"]["left_stem"] == "putra"
    assert _samasa.is_compound("rājaputravadhaḥ") is True


def test_patha_vikriti_preserves_accents_and_samhita_is_deterministic():
    ghana_res = transform_patha(["अ॒ग्निम्", "ई॒ळे"], patha="ghana")
    assert "॒" in ghana_res.rendered_text
    assert ghana_res.parigraha_indices == [1]

    iast_out = pada_to_samhita(["agnim", "īḷe"])
    assert isinstance(iast_out, str)
    assert len(iast_out.strip()) > 0
