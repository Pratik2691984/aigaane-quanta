"""
Regression tests for the chandas (meter) routes.

Endpoints exercised:
  POST /api/v3/chandas/scan     — full scansion (weights, matra, meter)
  POST /api/v3/chandas/analyze  — meter classification only
  GET  /api/v3/chandas/probe    — module availability discovery

Notes on the implementation:
  - scan and analyze are conditional on `_chhandas` / `_chhandas_scanner`
    imports. If those failed on startup, endpoints return 503. Tests
    branch on /probe first so we exercise whichever path is live.
  - scan() has graceful degradation: if scanner/analyzer throw, it returns
    200 with `errors` populated instead of 500. We verify that contract.
  - Empty-after-strip input → 400 on both endpoints.
"""
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def probe_state(client):
    """Fetch /probe once — tells us whether modules are actually loaded."""
    r = client.get("/api/v3/chandas/probe")
    assert r.status_code == 200, r.text
    return r.json()


# ------------------------------------------------------------------ #
#   /probe                                                            #
# ------------------------------------------------------------------ #

def test_probe_returns_expected_keys(probe_state):
    for key in (
        "chhandas_ok",
        "scanner_ok",
        "script_ok",
        "has_analyze_verse",
        "has_scan_iast",
    ):
        assert key in probe_state, f"probe missing key: {key}"
        assert isinstance(probe_state[key], bool), f"{key} must be bool"


# ------------------------------------------------------------------ #
#   POST /scan                                                        #
# ------------------------------------------------------------------ #

def test_scan_rejects_empty(client):
    r = client.post("/api/v3/chandas/scan", json={"text": ""})
    assert r.status_code == 422  # pydantic min_length=1


def test_scan_rejects_whitespace_only(client, probe_state):
    """Whitespace passes pydantic but fails the .strip() guard inside handler."""
    if not probe_state["scanner_ok"] and not probe_state["chhandas_ok"]:
        pytest.skip("chandas modules unavailable")
    r = client.post("/api/v3/chandas/scan", json={"text": "   "})
    assert r.status_code == 400


def test_scan_iast_verse_returns_weights_and_matras(client, probe_state):
    if not probe_state["scanner_ok"]:
        pytest.skip("scanner module unavailable")

    # Anuṣṭubh-compatible line — Rāmāyaṇa opening
    verse = "tapasvādhyāyanirataṃ tapasvī vāgvidāṃ varam"
    r = client.post("/api/v3/chandas/scan", json={"text": verse})
    assert r.status_code == 200, r.text

    data = r.json()
    # Required keys
    for k in ("surface", "iast", "weights", "syllable_count",
              "matra_sum", "meter", "errors"):
        assert k in data, f"scan response missing: {k}"

    # Weights should be a list of 'L'/'G'
    assert isinstance(data["weights"], list)
    assert all(w in ("L", "G") for w in data["weights"]), \
        f"unexpected weights: {data['weights']}"

    # Math consistency: syllable_count == len(weights)
    assert data["syllable_count"] == len(data["weights"])

    # Math consistency: matra_sum == L*1 + G*2
    expected_matra = sum(1 if w == "L" else 2 for w in data["weights"])
    assert data["matra_sum"] == expected_matra


def test_scan_devanagari_input_is_transliterated(client, probe_state):
    if not probe_state["scanner_ok"] or not probe_state["script_ok"]:
        pytest.skip("scanner or script module unavailable")

    deva = "तपस्वाध्यायनिरतं तपस्वी वाग्विदां वरम्"
    r = client.post("/api/v3/chandas/scan", json={"text": deva})
    assert r.status_code == 200, r.text

    data = r.json()
    assert data["surface"] == deva
    # `iast` should differ from surface if script module transliterated it.
    # We don't assert exact content (transliteration can vary), just that
    # the field is non-empty when transliteration is available.
    assert isinstance(data["iast"], str)
    assert data["iast"]  # non-empty


def test_scan_meter_is_dict_or_none(client, probe_state):
    if not probe_state["scanner_ok"]:
        pytest.skip("scanner module unavailable")
    r = client.post("/api/v3/chandas/scan", json={"text": "agnimīḷe purohitaṃ"})
    assert r.status_code == 200
    meter = r.json()["meter"]
    assert meter is None or isinstance(meter, dict)


# ------------------------------------------------------------------ #
#   POST /analyze                                                     #
# ------------------------------------------------------------------ #

def test_analyze_rejects_empty(client):
    r = client.post("/api/v3/chandas/analyze", json={"text": ""})
    assert r.status_code == 422


def test_analyze_rejects_whitespace_only(client, probe_state):
    if not probe_state["chhandas_ok"]:
        pytest.skip("chandas module unavailable")
    r = client.post("/api/v3/chandas/analyze", json={"text": "   "})
    assert r.status_code == 400


def test_analyze_returns_found_and_meter(client, probe_state):
    if not probe_state["chhandas_ok"]:
        pytest.skip("chandas module unavailable")

    verse = "tapasvādhyāyanirataṃ tapasvī vāgvidāṃ varam"
    r = client.post("/api/v3/chandas/analyze", json={"text": verse})
    assert r.status_code == 200, r.text

    data = r.json()
    for k in ("surface", "iast", "found", "meter"):
        assert k in data, f"analyze response missing: {k}"
    assert isinstance(data["found"], bool)
    if data["found"]:
        assert data["meter"] is not None


# ------------------------------------------------------------------ #
#   Cross-endpoint consistency                                        #
# ------------------------------------------------------------------ #

def test_scan_and_analyze_agree_on_surface_and_iast(client, probe_state):
    """Both endpoints process the same input the same way."""
    if not (probe_state["scanner_ok"] and probe_state["chhandas_ok"]):
        pytest.skip("need both scanner and chhandas modules")

    verse = "agnimīḷe purohitaṃ yajñasya devamṛtvijam"
    scan = client.post("/api/v3/chandas/scan", json={"text": verse}).json()
    anly = client.post("/api/v3/chandas/analyze", json={"text": verse}).json()

    assert scan["surface"] == anly["surface"]
    assert scan["iast"] == anly["iast"]


# ------------------------------------------------------------------ #
#   Fallback 503 path (only when modules are genuinely missing)       #
# ------------------------------------------------------------------ #

def test_scan_503_if_both_modules_missing(client, probe_state):
    """If neither module loaded, /scan must 503, not 500."""
    if probe_state["scanner_ok"] or probe_state["chhandas_ok"]:
        pytest.skip("both modules loaded — 503 path not applicable")
    r = client.post("/api/v3/chandas/scan", json={"text": "any"})
    assert r.status_code == 503


def test_analyze_503_if_chhandas_missing(client, probe_state):
    """If _chhandas failed to import, /analyze must 503."""
    if probe_state["chhandas_ok"]:
        pytest.skip("chhandas module loaded — 503 path not applicable")
    r = client.post("/api/v3/chandas/analyze", json={"text": "any"})
    assert r.status_code == 503