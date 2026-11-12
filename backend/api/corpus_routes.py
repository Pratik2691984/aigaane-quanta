"""
Corpus Search API — searches verses from Gita + 11 Upanishads via FTS5.

Backed by `canon.db` (1,748 verses, IAST + Devanagari + meter).
"""
from fastapi import APIRouter, Query, HTTPException
import sqlite3
from pathlib import Path
from collections import OrderedDict

router = APIRouter()

CANON_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "canon.db"

# Optional override for local testing / alternative deploy layouts
import os
if os.environ.get("AIGAANE_CANON_DB"):
    CANON_DB_PATH = Path(os.environ["AIGAANE_CANON_DB"])


@router.get("/search")
def search_verses(q: str = Query(..., min_length=2), limit: int = 10):
    """Search verses by Sanskrit term. FTS5 prefix match with source diversity."""
    if not CANON_DB_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=f"canon.db not found at {CANON_DB_PATH}"
        )
    try:
        conn = sqlite3.connect(str(CANON_DB_PATH))
        cur = conn.cursor()
        # Fetch MORE than needed (limit * 10) so we can diversify across sources.
        # Without this, FTS5 returns matches in rowid order — always Gita first.
        cur.execute(
            "SELECT v.chapter, v.verse, v.text, v.iast, v.meter, v.source "
            "FROM verses_fts f JOIN verses v ON v.rowid = f.rowid "
            "WHERE verses_fts MATCH ? "
            "ORDER BY f.rank "
            "LIMIT ?",
            (f"{q}*", limit * 10)
        )
        all_rows = cur.fetchall()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"corpus search failed: {e}")

    # Group by source
    by_source = OrderedDict()
    for r in all_rows:
        by_source.setdefault(r[5], []).append(r)

    # Round-robin: take 1 from each source, repeat until we hit `limit`
    selected = []
    while len(selected) < limit and any(by_source.values()):
        for src in list(by_source.keys()):
            if by_source[src] and len(selected) < limit:
                selected.append(by_source[src].pop(0))

    verses = [
        {
            "chapter": r[0],
            "verse": r[1],
            "text": r[2],
            "iast": r[3],
            "transliteration": r[3],  # frontend-compat alias
            "meter": r[4],
            "source": r[5],
        }
        for r in selected
    ]

    return {
        "query": q,
        "count": len(verses),
        "verses": verses,
        # Backward-compat aliases for the legacy frontend
        "results": verses,
        "total": len(verses),
    }