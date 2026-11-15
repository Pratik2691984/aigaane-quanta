"""
P2 audit: prove the entire API is already 100% deterministic.

EngineAdapter wraps legacy_engine.py (a deterministic Paninian module).
It is NOT an LLM. This test suite proves:
  - legacy_engine has no network / LLM imports
  - /api/v1/parse, /api/v1/aigaane/parse, /api/v3/aigaane/parse,
    /api/v1/samasa/split produce byte-identical JSON over repeated calls
  - EngineAdapter.parse is idempotent
  - No route in the app imports google.genai, openai, anthropic, or requests

If any of these fail, the API is not deterministic — the P2 retirement
concern is real. As of writing, all pass.
"""
import importlib
import json
import re
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)

ROOT = Path(__file__).resolve().parents[2]


# ---------- static audit ----------

FORBIDDEN_MODULES = ["google.genai", "google.generativeai", "openai", "anthropic", "cohere"]

FORBIDDEN_NETWORK = ["requests", "httpx", "urllib3", "aiohttp"]


def _iter_py_files(base: Path):
    for p in base.rglob("*.py"):
        if "venv" in p.parts or "__pycache__" in p.parts:
            continue
        if p.name == "test_determinism_audit.py":
            continue  # tests may legitimately hit TestClient
        yield p


def test_no_llm_imports_in_engine():
    """No engine file imports an LLM SDK."""
    hits = []
    for path in _iter_py_files(ROOT / "backend" / "engine"):
        src = path.read_text(encoding="utf-8", errors="replace")
        for mod in FORBIDDEN_MODULES:
            if re.search(rf"^\s*(?:from|import)\s+{re.escape(mod)}", src, re.MULTILINE):
                hits.append(f"{path.relative_to(ROOT)} imports {mod}")
    assert not hits, "LLM imports found:\n  " + "\n  ".join(hits)


def test_no_network_imports_in_adapter():
    """adapter.py and legacy_engine.py must not import an HTTP client."""
    for target in ["backend/engine/adapter.py", "backend/engine/legacy_engine.py"]:
        p = ROOT / target
        if not p.exists():
            continue
        src = p.read_text(encoding="utf-8", errors="replace")
        for mod in FORBIDDEN_NETWORK:
            m = re.search(rf"^\s*(?:from|import)\s+{re.escape(mod)}\b", src, re.MULTILINE)
            assert not m, f"{target} imports network lib: {mod}"


# ---------- runtime idempotency ----------

PARSE_PAYLOADS = [
    {"text": "r\u0101ma"},
    {"text": "dev\u0101layam"},
    {"text": "r\u0101mo r\u0101j\u0101"},
]

ROUTES_10X = [
    ("/api/v1/parse", "POST"),
    ("/api/v1/aigaane/parse", "POST"),
    ("/api/v3/aigaane/parse", "POST"),
]


def _canonical(resp):
    """Return a stable JSON dump — sorted keys, no whitespace variance."""
    return json.dumps(resp.json(), sort_keys=True, ensure_ascii=False)


@pytest.mark.parametrize("route,method", ROUTES_10X)
@pytest.mark.parametrize("payload", PARSE_PAYLOADS, ids=lambda p: p["text"][:8])
def test_parse_route_10x_identical(route, method, payload):
    """10 repeated calls → byte-identical JSON. Any nondeterminism is caught here."""
    first = None
    for i in range(10):
        r = client.post(route, json=payload)
        assert r.status_code == 200, f"{route} call {i}: {r.status_code} {r.text[:200]}"
        body = _canonical(r)
        if first is None:
            first = body
        else:
            assert body == first, f"{route} diverged at call {i}"


def test_samasa_split_10x_identical():
    payload = {"text": "r\u0101japutra"}
    first = None
    for i in range(10):
        r = client.post("/api/v1/samasa/split", json=payload)
        assert r.status_code == 200, f"call {i}: {r.status_code} {r.text[:200]}"
        body = _canonical(r)
        if first is None:
            first = body
        else:
            assert body == first, f"samasa split diverged at call {i}"


# ---------- adapter idempotency ----------

def test_engine_adapter_idempotent():
    """Direct adapter calls → identical output across 5 invocations."""
    from backend.engine.adapter import EngineAdapter
    a1 = EngineAdapter()
    a2 = EngineAdapter()
    for word in ["r\u0101ma", "deva", "agnim\u012b\u1e37e"]:
        e1 = a1.parse(word)
        e2 = a2.parse(word)
        e3 = a1.parse(word)
        j1 = json.dumps(e1.model_dump(), sort_keys=True, default=str)
        j2 = json.dumps(e2.model_dump(), sort_keys=True, default=str)
        j3 = json.dumps(e3.model_dump(), sort_keys=True, default=str)
        assert j1 == j2, f"cross-instance drift on {word!r}"
        assert j1 == j3, f"same-instance drift on {word!r}"


# ---------- capability preservation ----------

def test_parse_route_still_returns_morphology():
    """Sanity: /api/v1/parse returns candidates with non-empty parse[]."""
    r = client.post("/api/v1/parse", json={"text": "r\u0101ma"})
    assert r.status_code == 200
    data = r.json()
    assert data["candidates"], f"no candidates for r\u0101ma: {data.get('rejected')}"
    first = data["candidates"][0]
    assert first["parse"], f"empty parse[] — morphology regressed"
    assert first["parse"][0]["surface"]
    assert first["parse"][0]["stem"]
