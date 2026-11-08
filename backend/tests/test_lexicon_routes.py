"""
Regression tests for lexicon (Kośa) routes.

Endpoints:
  POST /api/v3/lexicon/lookup   — dictionary lookup with strategy attribution
  POST /api/v3/lexicon/attest   — boolean stem attestation
  GET  /api/v3/lexicon/probe    — module availability + strategy list

Notes on the implementation:
  - lookup() tries up to 9 strategies: exact, then strip SLP1/IAST endings,
    then bare stem + 'a'. Response includes `strategies_tried` count.
  - Not-found returns 200 with `found: False`, NOT 404.
  - Both endpoints 503 if `_lexicon` failed to import.
"""
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def probe_state(client):
    r = client.get("/api/v3/lexicon/probe")
    assert r.status_code == 200, r.text
    return r.json()


# ------------------------------------------------------------------ #
#   /probe                                                            #
# ------------------------------------------------------------------ #

def test_probe_returns_expected_keys(probe_state):
    for key in ("lexicon_ok", "has_lookup", "has_lookup_classical_verb", "strategies"):
        assert key in probe_state, f"probe missing: {key}"
    assert isinstance(probe_state["lexicon_ok"], bool)
    assert isinstance(probe_state["strategies"], list)
    assert "exact" in probe_state["strategies"]


# ------------------------------------------------------------------ #
#   POST /lookup                                                      #
# ------------------------------------------------------------------ #

def test_lookup_rejects_empty(client):
    r = client.post("/api/v3/lexicon/lookup", json={"text": ""})
    assert r.status_code == 422  # pydantic min_length=1


def test_lookup_rejects_whitespace_only(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.post("/api/v3/lexicon/lookup", json={"text": "   "})
    assert r.status_code == 400


def test_lookup_response_has_required_shape(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    # Use a common Sanskrit stem: 'rāma' in IAST
    r = client.post("/api/v3/lexicon/lookup", json={"text": "rāma"})
    assert r.status_code == 200, r.text

    data = r.json()
    for k in ("surface", "found", "strategy", "strategies_tried", "analysis"):
        assert k in data, f"lookup response missing: {k}"
    assert isinstance(data["found"], bool)
    assert isinstance(data["strategies_tried"], int)
    assert data["strategies_tried"] >= 1


def test_lookup_attested_returns_analysis(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.post("/api/v3/lexicon/lookup", json={"text": "rāma"})
    assert r.status_code == 200
    data = r.json()
    if not data["found"]:
        pytest.skip("'rāma' not attested in this lexicon build")
    assert data["analysis"] is not None
    # Analysis shape
    for k in ("stem", "pos", "linga", "vibhakti", "vacana", "confidence"):
        assert k in data["analysis"], f"analysis missing: {k}"


def test_lookup_nonsense_still_returns_200(client, probe_state):
    """Not-found is 200 with found: False, not 404."""
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.post("/api/v3/lexicon/lookup", json={"text": "zzzqqqxyz"})
    assert r.status_code == 200
    data = r.json()
    assert data["found"] is False
    assert data["analysis"] is None
    assert data["strategy"] is None
    # Message should mention strategies tried
    assert "message" in data


# ------------------------------------------------------------------ #
#   POST /attest                                                      #
# ------------------------------------------------------------------ #

def test_attest_rejects_empty(client):
    r = client.post("/api/v3/lexicon/attest", json={"stem": ""})
    assert r.status_code == 422


def test_attest_rejects_whitespace_only(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.post("/api/v3/lexicon/attest", json={"stem": "   "})
    assert r.status_code == 400


def test_attest_response_shape(client, probe_state):
    if not probe_state["lexicon_ok"]:
        pytest.skip("lexicon module unavailable")
    r = client.post("/api/v3/lexicon/attest", json={"stem": "rāma"})
    assert r.status_code == 200
    data = r.json()
    for k in ("stem", "attested", "confidence"):
        assert k in data, f"attest response missing: {k}"
    assert isinstance(data["attested"], bool)
    assert isinstance(data["confidence"], (int, float))


# ------------------------------------------------------------------ #
#   503 fallback                                                      #
# ------------------------------------------------------------------ #

def test_lookup_503_if_module_missing(client, probe_state):
    if probe_state["lexicon_ok"]:
        pytest.skip("lexicon loaded — 503 path not applicable")
    r = client.post("/api/v3/lexicon/lookup", json={"text": "rāma"})
    assert r.status_code == 503


def test_attest_503_if_module_missing(client, probe_state):
    if probe_state["lexicon_ok"]:
        pytest.skip("lexicon loaded — 503 path not applicable")
    r = client.post("/api/v3/lexicon/attest", json={"stem": "rāma"})
    assert r.status_code == 503