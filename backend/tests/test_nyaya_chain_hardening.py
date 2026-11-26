from backend.engine import _prakriya
from backend.nyaya.schemas import NyayaVerifyRequest
from backend.nyaya.verifier import NyayaVerifier


def test_validate_sutra_chain_tripadi_and_purvatrasiddham():
    assert _prakriya.validate_sutra_chain(["3.2.123", "3.1.68", "7.3.84", "1.4.14"]) == []
    assert _prakriya.validate_sutra_chain(["8.2.39", "8.4.53"]) == []

    # Backward Tripadi order (8.4.53 before 8.2.39)
    v_tripadi = _prakriya.validate_sutra_chain(["8.4.53", "8.2.39"])
    assert any(v.startswith("TRIPADI_ORDER_VIOLATION:") for v in v_tripadi)

    # Sapadasaptadhyayee rule (7.3.84) after Tripadi rule (8.2.66)
    v_purva = _prakriya.validate_sutra_chain(["8.2.66", "7.3.84"])
    assert any(v.startswith("PURVATRASIDDHAM_VIOLATION:") for v in v_purva)

    # Out-of-range coordinate (8.9.99) and empty chain
    v_range = _prakriya.validate_sutra_chain(["8.9.99"])
    assert any(v.startswith("OUT_OF_RANGE_SUTRA:") for v in v_range)
    assert _prakriya.validate_sutra_chain([]) == ["EMPTY_SUTRA_CHAIN"]


def test_nyaya_verifier_rejects_invalid_tripadi_and_unregistered_when_strict():
    verifier = NyayaVerifier()

    ramah_trace = _prakriya.derive_ramah()
    ok_proof = verifier.verify(
        NyayaVerifyRequest(
            candidate_id="cand_ramah",
            sutra_chain=ramah_trace.sutra_chain,
            result_classification=ramah_trace.result_classification,
            strict_registry=True,
        )
    )
    assert ok_proof.is_valid is True
    assert ok_proof.validation_notes == []

    bad_tripadi = verifier.verify(
        NyayaVerifyRequest(
            candidate_id="cand_bad_tripadi",
            sutra_chain=["8.4.53", "8.2.39"],
            result_classification="DETERMINISTIC_DERIVATION",
        )
    )
    assert bad_tripadi.is_valid is False
    assert any("TRIPADI_ORDER_VIOLATION:" in n for n in bad_tripadi.validation_notes)

    bad_purva = verifier.verify(
        NyayaVerifyRequest(
            candidate_id="cand_bad_purva",
            sutra_chain=["8.2.66", "7.3.84"],
            result_classification="DETERMINISTIC_DERIVATION",
        )
    )
    assert bad_purva.is_valid is False
    assert any("PURVATRASIDDHAM_VIOLATION:" in n for n in bad_purva.validation_notes)

    strict_unreg = verifier.verify(
        NyayaVerifyRequest(
            candidate_id="cand_unreg",
            sutra_chain=["1.1.1"],
            result_classification="DETERMINISTIC_DERIVATION",
            strict_registry=True,
        )
    )
    assert strict_unreg.is_valid is False
    assert any("UNREGISTERED_SUTRA:1.1.1" in n for n in strict_unreg.validation_notes)
