"""Temporary diagnostic — tells us what app.routes actually contains in CI."""
import sys
from fastapi.routing import APIRoute
from backend.api.main import app


def test_diagnostic_route_shape():
    print("\n=== ENV ===")
    print(f"Python: {sys.version}")
    try:
        import fastapi, starlette
        print(f"fastapi: {fastapi.__version__}")
        print(f"starlette: {starlette.__version__}")
    except Exception:
        pass

    print("\n=== app.routes ===")
    print(f"total routes: {len(app.routes)}")
    for r in app.routes:
        rtype = type(r).__name__
        rpath = getattr(r, "path", "<no-path>")
        is_api = isinstance(r, APIRoute)
        print(f"  {rtype:20s}  is_APIRoute={is_api}  path={rpath!r}")

    print("\n=== app.router.routes ===")
    print(f"total: {len(app.router.routes)}")

    print("\n=== openapi paths count ===")
    try:
        spec = app.openapi()
        paths = list(spec.get("paths", {}).keys())
        print(f"count: {len(paths)}")
        for p in paths[:20]:
            print(f"  {p}")
    except Exception as e:
        print(f"openapi() failed: {e}")

    # Don't actually assert anything — this is diagnostic
    assert True
