import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)
CANON_DB = Path("backend/data/canon.db")


def _db_count(where_sql: str = "", params: tuple = ()) -> int:
    assert CANON_DB.exists(), f"canon.db missing at {CANON_DB}"
    conn = sqlite3.connect(f"file:{CANON_DB.resolve().as_posix()}?mode=ro", uri=True)
    try:
        return conn.execute(f"SELECT COUNT(*) FROM verses{where_sql}", params).fetchone()[0]
    finally:
        conn.close()


def test_browse_without_query_returns_paginated_verses():
    expected_total = _db_count()
    r = client.get("/api/v3/corpus/browse", params={"limit": 5, "offset": 0})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["count"] == 5
    assert body["total"] == expected_total
    assert body["limit"] == 5
    assert body["offset"] == 0
    assert len(body["verses"]) == 5
    assert body["results"] == body["verses"]


def test_browse_parvan_filter_matches_db_count():
    expected_total = _db_count(" WHERE source = ?", ("mahabharata_parvan_13",))
    r = client.get("/api/v3/corpus/browse", params={"parvan": 13, "limit": 4, "offset": 0})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == expected_total
    assert body["count"] == min(4, expected_total)
    for item in body["verses"]:
        assert item["source"] == "mahabharata_parvan_13"


def test_browse_pagination_and_empty_results():
    page1 = client.get("/api/v3/corpus/browse", params={"source": "mahabharata_parvan_13", "limit": 3, "offset": 0})
    page2 = client.get("/api/v3/corpus/browse", params={"source": "mahabharata_parvan_13", "limit": 3, "offset": 3})
    assert page1.status_code == 200 and page2.status_code == 200
    p1_ids = [v["record_id"] for v in page1.json()["verses"]]
    p2_ids = [v["record_id"] for v in page2.json()["verses"]]
    assert len(p1_ids) == 3 and len(p2_ids) == 3
    assert set(p1_ids).isdisjoint(set(p2_ids))

    empty = client.get("/api/v3/corpus/browse", params={"source": "nonexistent_source_check", "limit": 10, "offset": 0})
    assert empty.status_code == 200
    assert empty.json()["count"] == 0
    assert empty.json()["total"] == 0
    assert empty.json()["verses"] == []
