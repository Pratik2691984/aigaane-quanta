from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def quanta_health():
    return {
        "status": "ok",
        "layer": "quanta",
        "pillars": ["deterministic", "cloud", "security"],
    }