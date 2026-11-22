from backend.data.migrate_vedic_metadata import apply_vedic_metadata_governance
from backend.engine.vedic._vedic_unicode_audit import (
    audit_vedic_extensions_coverage,
    find_unclassified_vedic_marks,
)


def test_unclassified_vedic_mark_detection_and_pluta_separation():
    sample = "\u0905\u0951\u1cd0\u1ce1\u0969"
    unclassified = find_unclassified_vedic_marks(sample)
    assert any(item["codepoint"] == "U+1CE1" for item in unclassified)
    assert all(item["codepoint"] != "U+0969" for item in unclassified)

    report = audit_vedic_extensions_coverage(sample)
    assert report["pluta_u0969_count"] == 1
    assert report["has_unclassified"] is True


def test_vedic_metadata_governance_dry_run_safe():
    summary = apply_vedic_metadata_governance(dry_run=True)
    assert "vedic_metadata_present" in summary
