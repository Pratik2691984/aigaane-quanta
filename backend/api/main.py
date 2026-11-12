from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import (
    quanta_routes, aigaane_routes, corpus_routes, samasa_routes,
    sandhi_routes, morphology_routes, chandas_routes, lexicon_routes,
    studio3_routes, nyaya_routes, pipeline_routes,
)
APP_VERSION = "2.3.0-legacy-ui-bridge"

app = FastAPI(
    title="Quanta-Aigaane Neuro-Symbolic API",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://aigaane.in",
        "https://www.aigaane.in",
        "https://api.aigaane.in",
        "https://aigaane-api.web.app",
        "https://aigaane-engine-2026.web.app",
        "https://aigaane-engine-2026.firebaseapp.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dual-mount: /api/v1 (deprecated) and /api/v3 (canonical)
app.include_router(quanta_routes.router, prefix="/api/v1/quanta", tags=["quanta"])
app.include_router(quanta_routes.router, prefix="/api/v3/quanta", tags=["quanta"])

app.include_router(aigaane_routes.router, prefix="/api/v1/aigaane", tags=["aigaane"])
app.include_router(aigaane_routes.router, prefix="/api/v3/aigaane", tags=["aigaane"])

app.include_router(corpus_routes.router, prefix="/api/v1/corpus", tags=["corpus"])
app.include_router(corpus_routes.router, prefix="/api/v3/corpus", tags=["corpus"])
app.include_router(samasa_routes.router, prefix="/api/v1/samasa", tags=["samasa"])
app.include_router(samasa_routes.router, prefix="/api/v3/samasa", tags=["samasa"])
app.include_router(sandhi_routes.router, prefix="/api/v1/sandhi", tags=["sandhi"])
app.include_router(sandhi_routes.router, prefix="/api/v3/sandhi", tags=["sandhi"])
app.include_router(morphology_routes.router, prefix="/api/v1/morphology", tags=["morphology"])
app.include_router(morphology_routes.router, prefix="/api/v3/morphology", tags=["morphology"])
app.include_router(chandas_routes.router, prefix="/api/v1/chandas", tags=["chandas"])
app.include_router(chandas_routes.router, prefix="/api/v3/chandas", tags=["chandas"])
app.include_router(lexicon_routes.router, prefix="/api/v1/lexicon", tags=["lexicon"])
app.include_router(lexicon_routes.router, prefix="/api/v3/lexicon", tags=["lexicon"])
app.include_router(studio3_routes.router, prefix="/api/v1/studio3", tags=["studio3"])
app.include_router(studio3_routes.router, prefix="/api/v3/studio3", tags=["studio3"])

# ============================================================
# LEGACY UI COMPATIBILITY LAYER (for aigaane-master frontend)
# ============================================================
from fastapi import Body
from backend.engine._sruti import get_sruti_table

@app.post("/api/v1/parse")
def legacy_parse(payload: dict = Body(...)):
    """Legacy alias: redirects to /api/v3/aigaane/parse"""
    from fastapi import HTTPException
    from backend.engine.adapter import EngineAdapter
    from backend.critic.gatekeeper import CegarGatekeeper
    try:
        adapter = EngineAdapter()
        gk = CegarGatekeeper()
        envelope = adapter.parse(payload.get("text", ""))
        return gk.verify(envelope).model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sruti")
def legacy_sruti(sa_hz: float = 240.0):
    """Legacy 22-sruti matrix endpoint."""
    try:
        table = get_sruti_table(sa_hz)
        return {"intervals": table, "sa_hz": sa_hz}
    except Exception as e:
        return {"intervals": [], "error": str(e)}

@app.post("/api/v1/pipeline")
def legacy_pipeline(payload: dict = Body(...)):
    """Legacy pipeline: parse + sruti in sequence."""
    text = payload.get("text", "")
    try:
        from backend.engine.adapter import EngineAdapter
        adapter = EngineAdapter()
        parse_result = adapter.parse(text)
        return {
            "studio_ii_verification": {"is_valid_inference": True, "mode": "Deterministic"},
            "studio_i_analysis": {"tokens": [t.dict() for t in (parse_result.candidates[0].parse if parse_result.candidates else [])]},
            "studio_iii_acoustics": {"meter_scansion": {"meter": "Anuṣṭubh"}},
            "sruti_table": get_sruti_table(240.0),
            "parse_envelope": parse_result.model_dump() if hasattr(parse_result, "model_dump") else None,
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/itihasa/search")
def legacy_itihasa_search(q: str, limit: int = 10):
    """Legacy alias for corpus search — forwards to corpus_routes.search_verses."""
    from backend.api.corpus_routes import search_verses as v3_search
    return v3_search(q=q, limit=limit)

app.include_router(nyaya_routes.router, prefix="/api/v1/nyaya", tags=["nyaya"])
app.include_router(nyaya_routes.router, prefix="/api/v3/nyaya", tags=["nyaya"])


app.include_router(pipeline_routes.router, prefix="/api/v1/pipeline/v2", tags=["pipeline"])
app.include_router(pipeline_routes.router, prefix="/api/v3/pipeline", tags=["pipeline"])

@app.get("/health")
def health():
    return {
        "status": "ok",
        "architecture": "Neuro-Symbolic",
        "version": "2.3.0-legacy-ui-bridge",
    }

@app.get("/")
def root():
    return {
        "status": "online",
        "engine": "Aigaane-Quanta Neuro-Symbolic",
        "version": APP_VERSION,
        "docs": "/docs",
    }

# ============================================================
# DIAGNOSTIC ENDPOINT — Added to debug corpus expansion
# ============================================================
@app.get("/api/v1/diagnostics/db")
def diagnostics_db():
    """Report canon.db state from inside the running container."""
    import sqlite3
    from pathlib import Path
    
    db_path = Path(__file__).resolve().parent.parent / "data" / "canon.db"
    
    if not db_path.exists():
        return {
            "error": "canon.db NOT FOUND",
            "expected_path": str(db_path),
            "cwd": str(Path.cwd()),
        }
    
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        
        # Total verses
        cur.execute("SELECT COUNT(*) FROM verses")
        verse_count = cur.fetchone()[0]
        
        # Total FTS entries
        cur.execute("SELECT COUNT(*) FROM verses_fts")
        fts_count = cur.fetchone()[0]
        
        # Sources breakdown
        cur.execute("SELECT source, COUNT(*) FROM verses GROUP BY source ORDER BY COUNT(*) DESC")
        sources = [{"source": row[0], "count": row[1]} for row in cur.fetchall()]
        
        # Test search 'dharma'
        cur.execute(
            "SELECT COUNT(*) FROM verses_fts f JOIN verses v ON v.rowid = f.rowid "
            "WHERE verses_fts MATCH 'dharma*'"
        )
        dharma_matches = cur.fetchone()[0]
        
        # Sample non-Gita verse
        cur.execute(
            "SELECT record_id, book, verse, text FROM verses "
            "WHERE source NOT LIKE '%gita%' LIMIT 1"
        )
        sample = cur.fetchone()
        sample_verse = None
        if sample:
            sample_verse = {
                "record_id": sample[0],
                "book": sample[1],
                "verse": sample[2],
                "text_preview": sample[3][:80] if sample[3] else None,
            }
        
        conn.close()
        
        return {
            "db_path": str(db_path),
            "db_size_bytes": db_path.stat().st_size,
            "verse_count": verse_count,
            "fts_count": fts_count,
            "sources": sources,
            "dharma_search_matches": dharma_matches,
            "sample_non_gita_verse": sample_verse,
        }
    except Exception as e:
        return {
            "error": str(e),
            "db_path": str(db_path),
        }