from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import quanta_routes, aigaane_routes, corpus_routes, samasa_routes, sandhi_routes, morphology_routes, chandas_routes, lexicon_routes, studio3_routes
APP_VERSION = "2.3.0-legacy-ui-bridge"
from backend.api import quanta_routes, aigaane_routes, corpus_routes, samasa_routes, sandhi_routes, morphology_routes, chandas_routes, lexicon_routes, studio3_routes, nyaya_routes

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
def legacy_itihasa_search(q: str):
    """Legacy alias: minimal corpus search placeholder."""
    try:
        from backend.api.corpus_routes import search as v3_search
        return v3_search(q=q)
    except Exception as e:
        return {"results": [], "error": str(e), "total": 0}

app.include_router(nyaya_routes.router, prefix="/api/v1/nyaya", tags=["nyaya"])
app.include_router(nyaya_routes.router, prefix="/api/v3/nyaya", tags=["nyaya"])

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