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
