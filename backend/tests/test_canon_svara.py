import sqlite3
from pathlib import Path

from backend.engine._svara import generate_vedic_contour

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "backend" / "data" / "canon.db"


def _db():
    assert DB.exists(), f"canon.db missing at {DB}"
    return sqlite3.connect(str(DB))


def test_verses_has_recension_and_svara_text_columns():
    conn = _db()
    cols = [r[1] for r in conn.execute("PRAGMA table_info(verses)").fetchall()]
    conn.close()
    assert "recension" in cols, f"missing recension; cols={cols}"
    assert "svara_text" in cols, f"missing svara_text; cols={cols}"


def test_sample_verses_present():
    conn = _db()
    n = conn.execute(
        "SELECT COUNT(*) FROM verses WHERE source='rigveda_svara_sample'"
    ).fetchone()[0]
    conn.close()
    assert n >= 3, f"expected >=3 sample rows, got {n}"


def test_three_recensions_present():
    conn = _db()
    recensions = {
        r[0] for r in conn.execute(
            "SELECT DISTINCT recension FROM verses WHERE source='rigveda_svara_sample'"
        ).fetchall()
    }
    conn.close()
    assert recensions == {"rgveda_sakala", "taittiriya", "kanva"}, recensions


def test_svara_text_is_nfc():
    import unicodedata
    conn = _db()
    rows = conn.execute(
        "SELECT svara_text FROM verses WHERE source='rigveda_svara_sample'"
    ).fetchall()
    conn.close()
    for (t,) in rows:
        assert t == unicodedata.normalize("NFC", t), f"not NFC: {t!r}"


def test_sample_verse_parses_via_svara_engine():
    conn = _db()
    rows = conn.execute(
        "SELECT svara_text, recension FROM verses WHERE source='rigveda_svara_sample'"
    ).fetchall()
    conn.close()
    assert len(rows) >= 1
    for svara_text, recension in rows:
        env = generate_vedic_contour(svara_text, recension=recension)
        assert env.rejected == [], f"{recension}: rejected {env.rejected}"
        assert env.candidates, f"{recension}: no candidates"
        evs = env.candidates[0].contour_events
        assert len(evs) == 9, f"{recension}: expected 9 akṣaras, got {len(evs)}"
        # Verify at least one derived svarita present
        derived = [e for e in evs if e.svara_source == "derived"]
        assert derived, f"{recension}: no derived svara events"


