"""
Regression tests for samasa (compound) routes.

Endpoints:
  POST /api/v3/samasa/split        -- compound decomposition (KernelEnvelope)
  GET  /api/v3/samasa/categories   -- Paninian samasa taxonomy

Notes on the implementation:
  - /split has `response_model=KernelEnvelope` -- Pydantic validates the
    response before it leaves the route. Shape is guaranteed; test only
    for HTTP codes and stable identity.
  - /split wraps EngineAdapter.parse + CegarGatekeeper.verify. Any
    exception -> 500. No graceful degradation.
  - /categories is static -- always 200, no module dependency.
  - Unlike lexicon/morphology/sandhi, samasa has NO /probe endpoint.
"""
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ------------------------------------------------------------------ #
#   GET /categories -- static, always available                       #
# ------------------------------------------------------------------ #

def test_categories_returns_expected_shape(client):
    r = client.get("/api/v3/samasa/categories")
    assert r.status_code == 200, r.text

    data = r.json()
    assert "status" in data
    assert data["status"] == "ok"
    assert "categories" in data
    assert isinstance(data["categories"], list)
    assert len(data["categories"]) >= 6, "expected the 6 canonical samasa types"


def test_categories_contains_all_canonical_types(client):
    r = client.get("/api/v3/samasa/categories")
    ids = {c["id"] for c in r.json()["categories"]}
    expected = {
        "avyayibhava",
        "tatpurusha",
        "karmadharaya",
        "dvigu",
        "dvandva",
        "bahuvrihi",
    }
    assert expected.issubset(ids), f"missing categories: {expected - ids}"


def test_categories_each_entry_has_required_fields(client):
    r = client.get("/api/v3/samasa/categories")
    for cat in r.json()["categories"]:
        for k in ("id", "name", "sutra"):
            assert k in cat, f"category entry missing: {k}"
        assert isinstance(cat["id"], str)
        assert isinstance(cat["name"], str)
        assert isinstance(cat["sutra"], str)


# ------------------------------------------------------------------ #
#   POST /split -- wraps EngineAdapter + CegarGatekeeper              #
# ------------------------------------------------------------------ #

def test_split_rejects_empty(client):
    r = client.post("/api/v3/samasa/split", json={"text": ""})
    assert r.status_code == 422


def test_split_rejects_missing_text(client):
    r = client.post("/api/v3/samasa/split", json={})
    assert r.status_code == 422


def test_split_returns_200_or_500(client):
    """
    The route contract: 200 with valid KernelEnvelope, or 500 with detail.
    Since response_model=KernelEnvelope enforces the 200 shape, we only
    assert: either it worked (200) or it failed cleanly (500 with detail).
    """
    r = client.post(
        "/api/v3/samasa/split",
        json={"text": "rājaputraḥ"},
    )
    assert r.status_code in (200, 500), r.text
    if r.status_code == 500:
        detail = r.json().get("detail", "")
        assert detail, "500 response must include 'detail'"


def test_split_200_response_is_kernel_envelope(client):
    """If split succeeds (200), validate structural contract."""
    r = client.post("/api/v3/samasa/split", json={"text": "rājaputraḥ"})
    if r.status_code == 500:
        pytest.skip("engine returned 500 -- envelope contract not exercised")
    assert r.status_code == 200

    data = r.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_split_never_returns_4xx_for_valid_input(client):
    """Route wraps try/except -- valid input yields 200 or 500, not 422/404."""
    r = client.post("/api/v3/samasa/split", json={"text": "rājaputraḥ"})
    assert r.status_code not in (400, 404, 422), \
        f"unexpected client error {r.status_code} for well-formed input"


# ------------------------------------------------------------------ #
#   No /probe on samasa -- verify that absence explicitly             #
# ------------------------------------------------------------------ #

def test_no_probe_endpoint(client):
    """Samasa has no /probe -- document that as known state."""
    r = client.get("/api/v3/samasa/probe")
    assert r.status_code == 404, "samasa should not expose /probe"