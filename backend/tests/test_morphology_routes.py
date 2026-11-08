"""
Regression tests for morphology (subanta/tinanta) routes.

Endpoints:
  POST /api/v3/morphology/analyze             — full morphological analysis
  GET  /api/v3/morphology/paradigm/{stem}     — best-effort paradigm table
  GET  /api/v3/morphology/probe               — module availability

Notes on the implementation:
  - Both endpoints wrap `_lexicon.lookup()`. Same lexicon module as
    /api/v3/lexicon/* — if lexicon is down, all morphology routes 503.
  - /paradigm returns 200 with empty `forms: []` for unknown stems —
    no 404, no 500. It's a best-effort scan across common endings.
  - Not-found analyze → 200 with `found: False`.
"""
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def probe_state(client):
    r = client.get("/api/v3/morphology/probe")
    assert r.status_code == 200, r.text
    return r.json()


# ------------------------------------------------------------------ #
#   /probe                                                            #
# ------------------------------------------------------------------ #

def test_probe_returns_expected_keys(probe_state):
    for key in (
        "lexicon_ok",
        "has_lookup",
        "has_lookup_classical_verb",
        "has_analyze_subanta",
        "has_analyze_tinanta",
    ):
        assert key in probe_state, f"probe missing: {key}"
        assert isinstance(probe_state[key], bool)


# ------------------------------------------------------------------ #
#   POST /analyze                                                     #
# ------------------------------------------------------------------ #

def test_analyze_rejects_empty(client):
    r = client.post("/api/v3/morphology/analyze", json={"text": ""})
    assert r.status_code == 422


def test_analyze_rejects_whitespace_only(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.post("/api/v3/morphology/analyze", json={"text": "   "})
    assert r.status_code == 400


def test_analyze_response_has_required_shape(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.post("/api/v3/morphology/analyze", json={"text": "rāma"})
    assert r.status_code == 200, r.text

    data = r.json()
    for k in ("surface", "found", "analysis"):
        assert k in data, f"analyze response missing: {k}"
    assert isinstance(data["found"], bool)


def test_analyze_attested_returns_full_analysis(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.post("/api/v3/morphology/analyze", json={"text": "rāma"})
    assert r.status_code == 200
    data = r.json()
    if not data["found"]:
        pytest.skip("'rāma' not attested in this lexicon build")
    analysis = data["analysis"]
    for k in ("stem", "pos", "linga", "vibhakti", "vacana", "confidence"):
        assert k in analysis, f"analysis missing: {k}"


def test_analyze_nonsense_returns_found_false(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.post("/api/v3/morphology/analyze", json={"text": "zzzqqqxyz"})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is False
    assert data["analysis"] is None
    assert "message" in data


# ------------------------------------------------------------------ #
#   GET /paradigm/{stem}                                              #
# ------------------------------------------------------------------ #

def test_paradigm_returns_shape_for_known_stem(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.get("/api/v3/morphology/paradigm/rāma")
    assert r.status_code == 200, r.text
    data = r.json()
    for k in ("stem", "count", "forms"):
        assert k in data, f"paradigm response missing: {k}"
    assert data["stem"] == "rāma"
    assert data["count"] == len(data["forms"])
    assert isinstance(data["forms"], list)


def test_paradigm_returns_empty_for_unknown_stem(client, probe_state):
    """Unknown stem → 200 with empty forms, not 404 or 500."""
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.get("/api/v3/morphology/paradigm/zzzqqqxyz")
    assert r.status_code == 200
    data = r.json()
    assert data["stem"] == "zzzqqqxyz"
    assert data["count"] == 0
    assert data["forms"] == []


def test_paradigm_form_entries_have_expected_fields(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.get("/api/v3/morphology/paradigm/rāma")
    assert r.status_code == 200
    for form in r.json()["forms"]:
        for k in ("form", "vibhakti", "vacana", "linga"):
            assert k in form, f"form entry missing: {k}"


# ------------------------------------------------------------------ #
#   503 fallback                                                      #
# ------------------------------------------------------------------ #

def test_analyze_503_if_module_missing(client, probe_state):
    if probe_state["lexicon_ok"]:
        pytest.skip("lexicon loaded — 503 path not applicable")
    r = client.post("/api/v3/morphology/analyze", json={"text": "rāma"})
    assert r.status_code == 503


def test_paradigm_503_if_module_missing(client, probe_state):
    if probe_state["lexicon_ok"]:
        pytest.skip("lexicon loaded — 503 path not applicable")
    r = client.get("/api/v3/morphology/paradigm/rāma")
    assert r.status_code == 503