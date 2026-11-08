"""
Regression tests for sandhi (phonological combination) routes.

Endpoints:
  POST /api/v3/sandhi/split   — split surface form into sandhi boundaries
  GET  /api/v3/sandhi/probe   — module availability

Notes on the implementation:
  - Accepts SLP1 / IAST / Devanagari; transliterates to IAST internally.
  - Two engines contribute candidates: `_sandhi_gen.invert_sandhi` (primary)
    and `_sandhi.split_surface` (legacy). Results deduplicated by split tuple.
  - Empty input after strip → 400. Missing both modules → 503.
  - Errors from individual engines are collected in response `errors` but
    do NOT cause 500 — graceful degradation.
"""
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def probe_state(client):
    r = client.get("/api/v3/sandhi/probe")
    assert r.status_code == 200, r.text
    return r.json()


# ------------------------------------------------------------------ #
#   /probe                                                            #
# ------------------------------------------------------------------ #

def test_probe_returns_expected_keys(probe_state):
    for key in ("sandhi_ok", "sandhi_gen_ok", "script_ok", "has_to_canonical_iast"):
        assert key in probe_state, f"probe missing: {key}"
        assert isinstance(probe_state[key], bool)


# ------------------------------------------------------------------ #
#   POST /split                                                       #
# ------------------------------------------------------------------ #

def test_split_rejects_empty(client):
    r = client.post("/api/v3/sandhi/split", json={"text": ""})
    assert r.status_code == 422


def test_split_rejects_whitespace_only(client, probe_state):
    if not (probe_state["sandhi_ok"] or probe_state["sandhi_gen_ok"]):
        pytest.skip("no sandhi module available")
    r = client.post("/api/v3/sandhi/split", json={"text": "   "})
    assert r.status_code == 400


def test_split_rejects_oversized_max_candidates(client):
    r = client.post(
        "/api/v3/sandhi/split",
        json={"text": "devālayaḥ", "max_candidates": 100},
    )
    assert r.status_code == 422  # pydantic le=50


def test_split_iast_returns_expected_shape(client, probe_state):
    if not probe_state["sandhi_gen_ok"]:
        pytest.skip("_sandhi_gen unavailable — primary engine required for shape test")
    r = client.post("/api/v3/sandhi/split", json={"text": "devālayaḥ"})
    assert r.status_code == 200, r.text

    data = r.json()
    for k in ("surface", "iast", "count", "candidates", "errors"):
        assert k in data, f"split response missing: {k}"
    assert isinstance(data["candidates"], list)
    assert data["count"] == len(data["candidates"])
    # Each candidate must have the documented shape
    for cand in data["candidates"]:
        for k in ("split", "rule", "sutra", "score"):
            assert k in cand, f"candidate missing: {k}"
        assert isinstance(cand["split"], list)
        assert isinstance(cand["score"], (int, float))


def test_split_respects_max_candidates(client, probe_state):
    if not probe_state["sandhi_gen_ok"]:
        pytest.skip("_sandhi_gen unavailable")
    r = client.post(
        "/api/v3/sandhi/split",
        json={"text": "devālayaḥ", "max_candidates": 1},
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data["candidates"]) <= 1


def test_split_candidates_sorted_by_score_descending(client, probe_state):
    if not probe_state["sandhi_gen_ok"]:
        pytest.skip("_sandhi_gen unavailable")
    r = client.post("/api/v3/sandhi/split", json={"text": "devālayaḥ"})
    assert r.status_code == 200
    scores = [c["score"] for c in r.json()["candidates"]]
    assert scores == sorted(scores, reverse=True), "candidates must be score-sorted"


def test_split_preserves_surface(client, probe_state):
    if not probe_state["sandhi_gen_ok"]:
        pytest.skip("_sandhi_gen unavailable")
    input_text = "devālayaḥ"
    r = client.post("/api/v3/sandhi/split", json={"text": input_text})
    assert r.status_code == 200
    assert r.json()["surface"] == input_text


# ------------------------------------------------------------------ #
#   503 fallback                                                      #
# ------------------------------------------------------------------ #

def test_split_503_if_all_modules_missing(client, probe_state):
    if probe_state["sandhi_ok"] or probe_state["sandhi_gen_ok"]:
        pytest.skip("at least one sandhi module loaded — 503 path not applicable")
    r = client.post("/api/v3/sandhi/split", json={"text": "devālayaḥ"})
    assert r.status_code == 503