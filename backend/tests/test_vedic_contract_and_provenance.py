"""
P0-3 & P0-4 Acceptance Tests:
- 8-domain VedicPhoneticEvent v3.1 contract & Draft 2020-12 JSON Schema validation
- canon.db vedic_metadata provenance table audit
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import jsonschema

from backend.engine.vedic._events import VedicPhoneticEvent
from backend.engine.vedic._mode1 import render_oral_recitation

SCHEMA_PATH = Path("backend/schemas/vedic/vedic_phonetic_event.schema.json")
DB_PATH = Path("backend/data/canon.db")


def test_vedic_phonetic_event_v3_1_validates_against_draft_2020_12_schema():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8-sig"))
    jsonschema.Draft202012Validator.check_schema(schema)

    verse = "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"
    res = render_oral_recitation(verse, recension="rgveda_sakala")
    events = [VedicPhoneticEvent.from_oral_event(e, text_source="RV_1.1.1") for e in res.events]
    assert len(events) == 4

    for evt in events:
        payload = evt.model_dump()
        jsonschema.validate(instance=payload, schema=schema)
        assert payload["execution_mode"] == "vedic_oral_recitation"
        assert payload["musical_overlay"] is None
        assert payload["validation"]["expert_reviewed"] is False


def test_canon_db_vedic_metadata_provenance_populated():
    con = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    try:
        total = con.execute("SELECT COUNT(*) FROM vedic_metadata").fetchone()[0]
        assert total >= 10465, f"Expected at least 10465 rows, got {total}"
        unaligned = con.execute(
            "SELECT COUNT(*) FROM vedic_metadata WHERE alignment_status = 'none'"
        ).fetchone()[0]
        assert unaligned >= 10465, f"Expected at least 10465 unaligned rows, got {unaligned}"
    finally:
        con.close()
