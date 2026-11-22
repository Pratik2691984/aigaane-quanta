"""
P0-1 Architectural Gate: Strict Mode 1 (Vedic Oral Recitation) Isolation.
Verifies that Mode 1 recitation has zero direct or transitive dependencies on
musical tuning (_sruti) or Carnatic rhythm (_tala / _rhythm), both statically
(AST + fresh subprocess sys.modules) and dynamically (runtime monkeypatch).
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

MODE1_PATH = Path("backend/engine/vedic/_mode1.py")
FORBIDDEN_MODULES = {"_sruti", "_tala", "_rhythm"}


def test_mode1_module_exists():
    assert MODE1_PATH.exists(), (
        "P0-1: backend/engine/vedic/_mode1.py not yet created (Option A Mode 1 seam)."
    )


def test_mode1_ast_has_no_forbidden_imports():
    if not MODE1_PATH.exists():
        pytest.skip("Mode 1 module not yet created")
    tree = ast.parse(MODE1_PATH.read_text(encoding="utf-8-sig"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[-1])
            for alias in node.names:
                imported.add(alias.name)
    overlap = imported & FORBIDDEN_MODULES
    assert not overlap, f"Mode 1 AST directly imports forbidden musical modules: {overlap}"


def test_mode1_subprocess_no_transitive_sruti_or_tala():
    if not MODE1_PATH.exists():
        pytest.skip("Mode 1 module not yet created")
    code = (
        "import sys, backend.engine.vedic._mode1 as m1; "
        "leaked = [m for m in sys.modules if any(f in m for f in ('_sruti', '_tala', '_rhythm'))]; "
        "assert not leaked, f'Transitive leak: {leaked}'"
    )
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr or res.stdout


def test_mode1_runtime_never_calls_sruti_or_tala(monkeypatch):
    if not MODE1_PATH.exists():
        pytest.skip("Mode 1 module not yet created")
    import backend.engine._sruti as sruti
    import backend.engine._tala as tala
    import backend.engine.vedic._mode1 as mode1

    def _boom(*_args, **_kwargs):
        raise AssertionError("Mode 1 runtime touched forbidden musical module")

    monkeypatch.setattr(sruti, "get_sruti_table", _boom)
    monkeypatch.setattr(sruti, "lookup_svara", _boom)
    monkeypatch.setattr(tala, "lookup_tala", _boom)
    monkeypatch.setattr(tala, "check_congruence", _boom)

    rv_1_1_1 = "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947 \u092a\u0941\u0952\u0930\u094b\u0939\u093f\u0951\u0924\u092e\u094d"
    result = mode1.render_oral_recitation(rv_1_1_1, recension="rgveda_sakala")
    assert result.wav_bytes[:4] == b"RIFF"


def test_mode1_rejects_samaveda_and_unverified_recensions():
    import pytest
    from backend.engine.vedic._mode1 import render_oral_recitation

    sample = "\u0905\u0952\u0917\u094d\u0928\u093f"
    for recension in ("samaveda", "samaveda_kauthuma", "parishishta_tei", "unknown_recension"):
        with pytest.raises(ValueError):
            render_oral_recitation(sample, recension=recension)
