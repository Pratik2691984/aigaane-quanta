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
        from backend.api.search_normalizer import build_fts5_match_query

        match_expr = build_fts5_match_query(q)
        if not match_expr:
            conn.close()
            return {
                "query": q,
                "count": 0,
                "verses": [],
                "results": [],
                "total": 0,
            }

        # Fetch MORE than needed (limit * 10) so we can diversify across sources.
        # Without this, FTS5 returns matches in rowid order — always Gita first.
        cur.execute(
            "SELECT v.chapter, v.verse, v.text, v.iast, v.meter, v.source "
            "FROM verses_fts f JOIN verses v ON v.rowid = f.rowid "
            "WHERE verses_fts MATCH ? "
            "ORDER BY f.rank "
            "LIMIT ?",
            (match_expr, limit * 10)
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

    from backend.api.search_normalizer import build_verse_gloss, detect_themes

    verses = []
    for r in selected:
        themes = detect_themes(q, text=r[2] or "", iast=r[3] or "", source=r[5] or "")
        gloss = build_verse_gloss(themes, source=r[5] or "", meter=r[4] or "")
        verses.append(
            {
                "chapter": r[0],
                "verse": r[1],
                "text": r[2],
                "iast": r[3],
                "transliteration": r[3],  # frontend-compat alias
                "meter": r[4],
                "source": r[5],
                "matched_themes": themes,
                "gloss": gloss,
            }
        )

    return {
        "query": q,
        "count": len(verses),
        "verses": verses,
        # Backward-compat aliases for the legacy frontend
        "results": verses,
        "total": len(verses),
    }

@router.get("/browse")
def browse_verses(
    source: str | None = Query(default=None, min_length=1),
    parvan: int | None = Query(default=None, ge=1, le=18),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Browse canonical verses by optional source or Mahābhārata Parvan (1–18) with real total count."""
    if not CANON_DB_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail=f"canon.db not found at {CANON_DB_PATH}",
        )

    where_clauses: list[str] = []
    params: list[object] = []

    effective_source = source.strip() if isinstance(source, str) and source.strip() else None
    if effective_source is None and parvan is not None:
        effective_source = f"mahabharata_parvan_{parvan}"

    if effective_source is not None:
        where_clauses.append("source = ?")
        params.append(effective_source)

    where_sql = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    try:
        conn = sqlite3.connect(f"file:{CANON_DB_PATH.resolve().as_posix()}?mode=ro", uri=True)
        cur = conn.cursor()

        total = cur.execute(f"SELECT COUNT(*) FROM verses{where_sql}", params).fetchone()[0]

        query_sql = (
            "SELECT record_id, book, chapter, verse, text, iast, meter, source, recension, svara_text, text_clean "
            f"FROM verses{where_sql} "
            "ORDER BY rowid ASC "
            "LIMIT ? OFFSET ?"
        )
        rows = cur.execute(query_sql, [*params, limit, offset]).fetchall()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"corpus browse failed: {e}")

    items = [
        {
            "record_id": r[0],
            "book": r[1],
            "chapter": r[2],
            "verse": r[3],
            "text": r[4],
            "iast": r[5],
            "transliteration": r[5],
            "meter": r[6],
            "source": r[7],
            "recension": r[8],
            "svara_text": r[9],
            "text_clean": r[10],
        }
        for r in rows
    ]

    return {
        "count": len(items),
        "total": total,
        "limit": limit,
        "offset": offset,
        "filters": {
            "source": effective_source,
            "parvan": parvan,
        },
        "verses": items,
        "results": items,
    }
