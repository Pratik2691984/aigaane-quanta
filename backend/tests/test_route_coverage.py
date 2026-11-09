"""
Cross-cutting route coverage tests.

Verifies behaviors that every domain router must satisfy:
  1. Dual-mount equivalence: /api/v1/* responds identically to /api/v3/*
  2. CORS preflight: production origins are allowed
  3. Error handling: 4xx/5xx responses have consistent `detail` shape
  4. Health probe: /health returns the canonical envelope
"""
import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# ------------------------------------------------------------------ #
#   Dual-mount equivalence                                           #
# ------------------------------------------------------------------ #

DUAL_MOUNT_ENDPOINTS = [
    ("GET",  "/quanta/health"),
    ("GET",  "/samasa/categories"),
    ("GET",  "/sandhi/probe"),
    ("GET",  "/morphology/probe"),
    ("GET",  "/lexicon/probe"),
]


@pytest.mark.parametrize("method,path", DUAL_MOUNT_ENDPOINTS)
def test_dual_mount_equivalence(client, method, path):
    """Same path under /api/v1/* and /api/v3/* must produce the same status."""
    r1 = client.request(method, f"/api/v1{path}")
    r3 = client.request(method, f"/api/v3{path}")
    assert r1.status_code == r3.status_code, \
        f"{method} {path}: v1={r1.status_code} vs v3={r3.status_code}"


# ------------------------------------------------------------------ #
#   CORS preflight                                                   #
# ------------------------------------------------------------------ #

PROD_ORIGIN = "https://aigaane-engine-2026.web.app"


@pytest.mark.parametrize("path", [
    "/api/v3/quanta/health",
    "/api/v3/samasa/categories",
    "/api/v3/lexicon/probe",
])
def test_cors_preflight_allows_prod_origin(client, path):
    r = client.options(
        path,
        headers={
            "Origin": PROD_ORIGIN,
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.status_code in (200, 204), r.text
    assert r.headers.get("access-control-allow-origin") == PROD_ORIGIN


# ------------------------------------------------------------------ #
#   Error shape consistency                                          #
# ------------------------------------------------------------------ #

@pytest.mark.parametrize("path", [
    "/api/v3/samasa/split",
    "/api/v3/sandhi/split",
    "/api/v3/morphology/analyze",
    "/api/v3/lexicon/lookup",
])
def test_validation_error_has_detail(client, path):
    """All POST routes returning 422 must include a 'detail' field."""
    r = client.post(path, json={})  # missing required field
    assert r.status_code == 422, r.text
    assert "detail" in r.json()


# ------------------------------------------------------------------ #
#   Health probe                                                     #
# ------------------------------------------------------------------ #

def test_health_endpoint_returns_canonical_shape(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["architecture"] == "Neuro-Symbolic"
    assert "version" in data


def test_root_endpoint_advertises_docs(client):
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "online"
    assert data["docs"] == "/docs"
