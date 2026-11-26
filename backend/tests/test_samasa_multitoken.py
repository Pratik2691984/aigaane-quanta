from backend.engine import _samasa


def test_multitoken_compound_rājaputravadhaḥ():
    tree = _samasa.build_tree("rājaputravadhaḥ")
    assert tree is not None
    assert tree["type"] == "tatpurusha"
    assert len(tree.get("children", [])) == 2
    assert tree["children"][0]["component_surface"] == "rājaputra"
    assert len(tree["children"][0].get("children", [])) == 2
    assert tree["children"][1]["component_surface"] == "vadhaḥ"


def test_known_compound_classification_types():
    assert _samasa.build_tree("nīlotpalam")["type"] == "karmadharaya"
    assert _samasa.build_tree("pītāmbaraḥ")["type"] == "bahuvrihi"
    assert _samasa.build_tree("rāmalakṣmaṇau")["type"] == "dvandva"
    assert _samasa.build_tree("yathāśakti")["type"] == "avyayibhava"
    assert _samasa.build_tree("saptarṣiḥ")["type"] == "dvigu"
