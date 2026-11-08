"""
Golden corpus regression runner.
Reads backend/corpus/samasa_golden.json, replays each case against
the live /api/v3/samasa/split endpoint, and asserts the response
matches the expected envelope (for verified cases).
"""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app

GOLDEN_PATH = Path(__file__).resolve().parent.parent / "corpus" / "samasa_golden.json"

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def golden_cases():
    with open(GOLDEN_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["cases"]

@pytest.mark.parametrize("case", [
    pytest.param(c, id=c["case_id"]) for c in
    json.load(open(GOLDEN_PATH, encoding="utf-8"))["cases"]
])
def test_golden_case(client, case):
    """Replay a golden case against the live API."""
    # 1. Send the input to the split endpoint
    payload = {"text": case["input_triad"]["slp1"]}
    r = client.post("/api/v3/samasa/split", json=payload)
    
    # 2. Verified cases must return 200
    if case["status"] == "verified":
        assert r.status_code == 200, f"{case['case_id']} failed: {r.text}"
        response = r.json()
        expected = case["expected_envelope"]
        
        # 3. The input triad must round-trip
        assert response["input_triad"]["slp1"] == expected["input_triad"]["slp1"]
        
        # 4. There must be at least one candidate (or the case is intentionally all-rejected)
        expected_cand_ids = {c["candidate_id"] for c in expected["candidates"]}
        actual_cand_ids = {c["candidate_id"] for c in response["candidates"]}
        assert actual_cand_ids.issuperset(expected_cand_ids), \
            f"{case['case_id']}: missing candidates {expected_cand_ids - actual_cand_ids}"
        
        # 5. Each expected samasa_type must appear
        expected_types = {c.get("samasa_type") for c in expected["candidates"] if c.get("samasa_type")}
        actual_types = {c.get("samasa_type") for c in response["candidates"] if c.get("samasa_type")}
        assert expected_types.issubset(actual_types), \
            f"{case['case_id']}: missing samasa types {expected_types - actual_types}"

    elif case["status"] in ("rejected", "disputed"):
        # Rejected cases must still return 200 (envelope) but with zero candidates
        assert r.status_code == 200, f"{case['case_id']} rejected case failed: {r.text}"
        response = r.json()
        assert len(response["candidates"]) == 0, \
            f"{case['case_id']}: expected 0 candidates, got {len(response['candidates'])}"