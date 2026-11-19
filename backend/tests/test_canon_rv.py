"""Tests for Rigveda corpus in canon.db (Q7-RV extension)."""
import sqlite3
import unicodedata
from pathlib import Path

from backend.engine._svara import generate_vedic_contour

DB = Path(__file__).resolve().parents[2] / "backend" / "data" / "canon.db"


def _db():
    return sqlite3.connect(str(DB))


def test_rv_corpus_present():
    conn = _db()
    n = conn.execute(
        "SELECT COUNT(*) FROM verses WHERE book='Rigveda' AND source='rigveda_corpus'"
    ).fetchone()[0]
    conn.close()
    assert n >= 10000, f"expected >=10000 corpus rows, got {n}"


def test_rv_samples_preserved():
    conn = _db()
    n = conn.execute(
        "SELECT COUNT(*) FROM verses WHERE book='Rigveda' AND source='rigveda_svara_sample'"
    ).fetchone()[0]
    conn.close()
    assert n == 3, f"expected 3 Q7 samples preserved, got {n}"


def test_rv_1_1_1_present_with_svara_text():
    conn = _db()
    row = conn.execute(
        "SELECT svara_text, recension, source FROM verses "
        "WHERE record_id='AIGAANE-RIGVEDA-RIGVEDA-001.001.001'"
    ).fetchone()
    conn.close()
    assert row is not None, "RV 1.1.1 not found"
    svara_text, recension, source = row
    assert svara_text and "\u0951" in svara_text
    assert "\u0952" in svara_text
    assert recension == "rgveda_sakala"
    assert source == "rigveda_corpus"


def test_rv_1_1_1_parses_via_svara_engine():
    conn = _db()
    svara_text = conn.execute(
        "SELECT svara_text FROM verses WHERE record_id='AIGAANE-RIGVEDA-RIGVEDA-001.001.001'"
    ).fetchone()[0]
    conn.close()
    env = generate_vedic_contour(svara_text, recension="rgveda_sakala")
    assert env.rejected == [], f"rejected: {env.rejected}"
    assert env.candidates
    events = env.candidates[0].contour_events
    assert len(events) >= 16


def test_rv_corpus_all_svara_text_is_nfc():
    conn = _db()
    rows = conn.execute(
        "SELECT svara_text FROM verses WHERE book='Rigveda' AND svara_text IS NOT NULL LIMIT 200"
    ).fetchall()
    conn.close()
    assert len(rows) >= 100
    for (t,) in rows:
        assert unicodedata.normalize("NFC", t) == t


def test_rv_corpus_span_10_mandalas():
    conn = _db()
    mandalas = {r[0] for r in conn.execute(
        "SELECT DISTINCT chapter FROM verses WHERE book='Rigveda' AND source='rigveda_corpus'"
    ).fetchall()}
    conn.close()
    assert mandalas == set(range(1, 11))


def test_rv_corpus_sample_parses_across_mandalas():
    conn = _db()
    rows = conn.execute(
        "SELECT chapter, MIN(verse), svara_text FROM verses "
        "WHERE book='Rigveda' AND source='rigveda_corpus' AND svara_text IS NOT NULL "
        "GROUP BY chapter ORDER BY chapter"
    ).fetchall()
    conn.close()
    assert len(rows) == 10
    for ma, su, svara_text in rows:
        env = generate_vedic_contour(svara_text, recension="rgveda_sakala")
        assert not env.rejected, f"Mandala {ma} rejected: {env.rejected}"
        assert env.candidates


def test_rv_corpus_in_fts():
    conn = _db()
    n_verses = conn.execute("SELECT COUNT(*) FROM verses WHERE text IS NOT NULL").fetchone()[0]
    n_fts = conn.execute("SELECT COUNT(*) FROM verses_fts").fetchone()[0]
    conn.close()
    assert n_fts >= n_verses


def test_rv_searchable_in_fts_iast():
    """Rigveda verses must be findable via IAST in FTS5."""
    conn = _db()
    n = conn.execute(
        "SELECT COUNT(*) FROM verses_fts WHERE verses_fts MATCH ?",
        ("agnimīḻe",)
    ).fetchone()[0]
    conn.close()
    assert n > 0, "RV 1.1.1 iast not searchable in FTS"


def test_rv_searchable_in_fts_prefix():
    """Prefix search 'agni*' must return Rigveda verses."""
    conn = _db()
    n = conn.execute(
        "SELECT COUNT(*) FROM verses_fts WHERE verses_fts MATCH ?",
        ("agni*",)
    ).fetchone()[0]
    conn.close()
    assert n > 10, f"expected >10 Rigveda matches for agni*, got {n}"


def test_rv_searchable_in_fts_devanagari_accented():
    """Accented Devanagari must match itself in FTS."""
    conn = _db()
    n = conn.execute(
        "SELECT COUNT(*) FROM verses_fts WHERE verses_fts MATCH ?",
        ("\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947",)
    ).fetchone()[0]
    conn.close()
    assert n > 0, "Accented Devanagari not searchable in FTS"


def test_fts_triggers_exist():
    """After fix, verses table should have ai/ad/au triggers for auto-sync."""
    conn = _db()
    triggers = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='trigger' AND tbl_name='verses'"
    ).fetchall()}
    conn.close()
    assert triggers, "no sync triggers on verses — future inserts will desync FTS"


def test_polish_text_clean_column_exists():
    """Polish: text_clean column added and populated."""
    conn = _db()
    cols = [r[1] for r in conn.execute("PRAGMA table_info(verses)").fetchall()]
    n = conn.execute("SELECT COUNT(*) FROM verses WHERE text_clean IS NOT NULL").fetchone()[0]
    total_with_text = conn.execute("SELECT COUNT(*) FROM verses WHERE text IS NOT NULL").fetchone()[0]
    conn.close()
    assert "text_clean" in cols
    assert n >= total_with_text * 0.95


def test_polish_unaccented_search_works():
    """Polish: unaccented Devanagari now matches accented content via text_clean."""
    conn = _db()
    n = conn.execute(
        "SELECT COUNT(*) FROM verses_fts WHERE verses_fts MATCH ?",
        ("\u0905\u0917\u094d\u0928\u093f\u092e\u0940\u0933\u0947",)
    ).fetchone()[0]
    conn.close()
    assert n >= 3, f"unaccented search returned {n}, expected >=3"


def test_polish_no_stray_devanagari_digits():
    """Polish: no non-pluta Devanagari digits in svara_text."""
    STRAY = "\u0966\u0967\u0968\u096a\u096b\u096c\u096d\u096e\u096f"
    conn = _db()
    rows = conn.execute(
        "SELECT COUNT(*) FROM verses WHERE svara_text IS NOT NULL AND svara_text GLOB ?",
        (f"*[{STRAY}]*",)
    ).fetchone()[0]
    conn.close()
    assert rows == 0, f"{rows} verses still contain stray digits"


def test_polish_rv_meter_backfilled():
    """Polish: Rigveda corpus has meter populated where _chhandas could classify."""
    conn = _db()
    total = conn.execute(
        "SELECT COUNT(*) FROM verses WHERE book='Rigveda' AND source='rigveda_corpus'"
    ).fetchone()[0]
    with_meter = conn.execute(
        "SELECT COUNT(*) FROM verses WHERE book='Rigveda' AND source='rigveda_corpus' AND meter IS NOT NULL"
    ).fetchone()[0]
    conn.close()
    assert total == 10462, f"corpus count changed: {total}"
    assert with_meter >= 100, f"only {with_meter}/{total} have meter — backfill failed"


def test_polish_fts_triggers_include_text_clean():
    """Polish: sync triggers include text_clean column."""
    conn = _db()
    triggers = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='trigger' AND tbl_name='verses'"
    ).fetchall()
    conn.close()
    assert len(triggers) == 3, f"expected 3 triggers, got {len(triggers)}"
    for (sql,) in triggers:
        assert "text_clean" in sql, f"trigger missing text_clean: {sql[:100]}"

