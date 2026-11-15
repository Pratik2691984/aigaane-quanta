"""
Guard: every /api/v1/{domain} must have either:
  (a) a matching /api/v3/{domain} router mount, OR
  (b) an intentional @app.<verb>("/api/v1/{domain}/...") legacy alias.

v1-only router mounts with no v3 twin AND no app-level alias fail.
"""
import re
from pathlib import Path

from fastapi.routing import APIRoute
from backend.api.main import app

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / "backend" / "api" / "main.py"


EXPECTED_DUAL = [
    "/api/v1/quanta", "/api/v3/quanta",
    "/api/v1/aigaane", "/api/v3/aigaane",
    "/api/v1/corpus", "/api/v3/corpus",
    "/api/v1/samasa", "/api/v3/samasa",
    "/api/v1/sandhi", "/api/v3/sandhi",
    "/api/v1/morphology", "/api/v3/morphology",
    "/api/v1/chandas", "/api/v3/chandas",
    "/api/v1/lexicon", "/api/v3/lexicon",
    "/api/v1/studio3", "/api/v3/studio3",
    "/api/v1/nyaya", "/api/v3/nyaya",
    "/api/v1/vedic", "/api/v3/vedic",
]


def _app_paths():
    return {r.path for r in app.routes if isinstance(r, APIRoute)}


def _domains(paths, prefix):
    return {
        p.split("/")[3]
        for p in paths
        if p.startswith(prefix) and p.count("/") >= 3
    }


def _is_intentional_alias(domain: str) -> bool:
    """True if main.py has an @app.<verb>("/api/v1/{domain}...") decorator."""
    src = MAIN.read_text(encoding="utf-8-sig")
    pattern = rf'@app\.\w+\("/api/v1/{re.escape(domain)}(?:/|\?|"|\))'
    return bool(re.search(pattern, src))


def test_all_v1_domains_have_v3_twin_or_legacy_alias():
    paths = _app_paths()
    v1 = _domains(paths, "/api/v1/")
    v3 = _domains(paths, "/api/v3/")

    missing_v3 = v1 - v3
    real_bugs = [d for d in missing_v3 if not _is_intentional_alias(d)]

    assert not real_bugs, (
        f"v1-only domains with NO v3 twin AND NO @app alias: {sorted(real_bugs)}\n"
        f"Either mount: app.include_router(<router>.router, prefix='/api/v3/<domain>')"
        f" OR add: @app.<verb>('/api/v1/<domain>/...') if intentional alias."
    )


def test_expected_dual_mounts_present():
    paths = _app_paths()
    present = set()
    for p in paths:
        for expected in EXPECTED_DUAL:
            if p == expected or p.startswith(expected + "/"):
                present.add(expected)
    missing = set(EXPECTED_DUAL) - present
    assert not missing, f"missing expected mounts: {sorted(missing)}"


def test_main_py_has_no_single_side_router_inclusions():
    """Static: every app.include_router(...) appears at least twice (v1 + v3),
    except pipeline_routes which is intentionally asymmetric."""
    src = MAIN.read_text(encoding="utf-8-sig")
    includes = re.findall(
        r'app\.include_router\(\s*(\w+)\.router,\s*prefix="([^"]+)"',
        src,
    )
    by_router = {}
    for router_name, prefix in includes:
        by_router.setdefault(router_name, []).append(prefix)
    singles = {r: ps for r, ps in by_router.items() if len(ps) < 2}
    singles.pop("pipeline_routes", None)
    assert not singles, f"routers mounted only once: {singles}"


def test_vedic_routes_dual_mounted():
    paths = _app_paths()
    v1 = {p for p in paths if p.startswith("/api/v1/vedic/")}
    v3 = {p for p in paths if p.startswith("/api/v3/vedic/")}
    assert v1, "no /api/v1/vedic/* routes registered"
    assert v3, "no /api/v3/vedic/* routes registered"
    v1_tails = {p[len("/api/v1/vedic"):] for p in v1}
    v3_tails = {p[len("/api/v3/vedic"):] for p in v3}
    missing = v1_tails - v3_tails
    assert not missing, f"/api/v1/vedic has routes v3 is missing: {sorted(missing)}"


def test_v1_only_domains_actually_respond():
    """For every v1-only domain (detected from registered routes), the domain's
    actual registered paths must respond without 404 when called with their
    own method. No guessing which subpath or verb is registered."""
    from fastapi.testclient import TestClient
    client = TestClient(app)
    routes = [r for r in app.routes if isinstance(r, APIRoute)]

    paths = _app_paths()
    v1 = _domains(paths, "/api/v1/")
    v3 = _domains(paths, "/api/v3/")
    v1_only = sorted(v1 - v3)
    assert v1_only, "expected at least one v1-only domain (parse, sruti, etc.)"

    for domain in v1_only:
        # Every registered path under this domain
        matching = [r for r in routes if r.path.startswith(f"/api/v1/{domain}")]
        assert matching, f"domain {domain!r} listed but no registered route"
        # At least ONE of its paths must not 404 when called with its own method
        responded = False
        errors = []
        for r in matching:
            if "{" in r.path:
                continue  # skip dynamic-path routes; can't trivially test
            method = sorted(r.methods)[0] if r.methods else "GET"
            try:
                if method == "GET":
                    resp = client.get(r.path)
                elif method == "POST":
                    resp = client.post(r.path, json={})
                else:
                    resp = client.request(method, r.path)
            except Exception as e:
                errors.append(f"{method} {r.path}: exception {e}")
                continue
            if resp.status_code != 404:
                responded = True
                break
            errors.append(f"{method} {r.path}: 404")
        assert responded, (
            f"domain {domain!r} is detected but every registered path 404s:\n  "
            + "\n  ".join(errors)
        )
