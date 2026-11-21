import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.api.search_normalizer import build_fts5_match_query, sanitize_fts_tokens

client = TestClient(app)
CANON_DB = Path("backend/data/canon.db")


def test_search_normalizer_sangeeta_and_music():
    assert sanitize_fts_tokens("Sangeeta") == ["sangita"]
    assert sanitize_fts_tokens("sa\u1e45g\u012bta") == ["sangita"]
    assert build_fts5_match_query("Sangeeta") == '"sangita"*'
    assert build_fts5_match_query("sa\u1e45g\u012bta") == '"sangita"*'
    music_tokens = sanitize_fts_tokens("music")
    assert "sangita" in music_tokens
    assert "svara" in music_tokens


def test_corpus_search_endpoint_sangeeta_diacritics_and_operators():
    for q in ["Sangeeta", "sa\u1e45g\u012bta", "music", "dharma", "AND OR NOT * ? \"quotes\""]:
        r = client.get("/api/v3/corpus/search", params={"q": q, "limit": 5})
        assert r.status_code == 200, f"{q}: {r.text}"
        body = r.json()
        assert body["count"] >= 1, f"Expected >=1 match for {q!r}"


def test_canon_db_ingested_sources_and_fts_count():
    assert CANON_DB.exists()
    conn = sqlite3.connect(f"file:{CANON_DB.resolve().as_posix()}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        total_verses = cur.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
        total_fts = cur.execute("SELECT COUNT(*) FROM verses_fts").fetchone()[0]
        assert total_verses >= 40474
        assert total_fts == total_verses

        avp_cnt = cur.execute(
            "SELECT COUNT(*) FROM verses WHERE record_id LIKE 'AIGAANE-AVP-%'"
        ).fetchone()[0]
        sv_cnt = cur.execute(
            "SELECT COUNT(*) FROM verses WHERE record_id LIKE 'AIGAANE-SV-K-%'"
        ).fetchone()[0]
        assert avp_cnt == 2718
        assert sv_cnt == 2247
    finally:
        conn.close()
def test_corpus_search_returns_matched_themes_and_gloss():
    r = client.get("/api/v3/corpus/search", params={"q": "music", "limit": 5})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["count"] >= 1
    first = body["verses"][0]
    assert "matched_themes" in first and isinstance(first["matched_themes"], list)
    assert "music" in first["matched_themes"]
    assert isinstance(first.get("gloss"), str) and len(first["gloss"]) > 0
