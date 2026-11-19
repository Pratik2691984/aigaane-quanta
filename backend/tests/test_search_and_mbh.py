import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.api.search_normalizer import build_fts5_match_query, sanitize_fts_tokens

client = TestClient(app)
CANON_DB = Path("backend/data/canon.db")


def test_search_normalizer_transliteration_and_music():
    assert sanitize_fts_tokens("Sangeeta") == ["sangita"]
    assert sanitize_fts_tokens("sa\u1e45g\u012bta") == ["sangita"]
    music_tokens = sanitize_fts_tokens("music")
    assert "sangita" in music_tokens
    assert "svara" in music_tokens
    assert build_fts5_match_query("dharma-karma") == '"darma"* OR "karma"*'


def test_corpus_search_endpoint_handles_variants_and_punctuation():
    for q in ["Sangeeta", "sa\u1e45g\u012bta", "music", "dharma-karma", "((agni))"]:
        r = client.get("/api/v3/corpus/search", params={"q": q, "limit": 5})
        assert r.status_code == 200, f"{q}: {r.text}"
        body = r.json()
        assert body["count"] >= 1, f"Expected >=1 result for {q!r}"


def test_mahabharata_seed_rows_and_fts_sync():
    assert CANON_DB.exists()
    conn = sqlite3.connect(f"file:{CANON_DB.as_posix()}?mode=ro", uri=True)
    cur = conn.cursor()
    mbh_rows = cur.execute(
        "SELECT record_id, text_clean FROM verses WHERE source LIKE 'mahabharata%'"
    ).fetchall()
    assert len(mbh_rows) >= 5
    for record_id, text_clean in mbh_rows:
        assert text_clean and len(text_clean.strip()) > 0, f"Empty text_clean for {record_id}"

    fts_hit = cur.execute(
        "SELECT COUNT(*) FROM verses_fts WHERE verses_fts MATCH ?",
        ('"narayanam"*',),
    ).fetchone()[0]
    conn.close()
    assert fts_hit >= 1