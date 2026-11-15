import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)
FIXTURE = Path(__file__).parent / "fixtures" / "vedic_golden.json"

def _load_cases():
    if not FIXTURE.exists():
        pytest.skip(f"missing {FIXTURE}; run python -m backend.tests._generate_vedic_goldens")
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["cases"]

@pytest.mark.parametrize("case", _load_cases(), ids=lambda c: c["id"])
def test_golden_render_sha(case):
    r = client.post("/api/v3/vedic/render", json=case["input"])
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["rejected"] == [], data["rejected"]
    cand = data["candidates"][0]
    assert cand["sha256"] == case["sha256"], (
        f"sha256 drift for {case['id']}:\n  expected {case['sha256']}\n  got      {cand['sha256']}\n"
        f"If intentional: python -m backend.tests._generate_vedic_goldens"
    )
    assert cand["duration_sec"] == case["duration_sec"]
    assert cand["peak_db"] == case["peak_db"]
    assert cand["rms_db"] == case["rms_db"]
    assert cand["n_samples"] == case["n_samples"]
