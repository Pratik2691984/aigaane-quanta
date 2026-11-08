"""
Regression tests for the Nyāya (syllogistic verifier) routes.
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_nyaya_verify_valid_proof(client):
    payload = {
        "candidate_id": "cand_01",
        "sutra_chain": ["1.1.1", "1.1.2"],
        "vigraha": "rāja-putraḥ",
        "samasa_type": "Tatpuruṣa"
    }
    r = client.post("/api/v3/nyaya/verify", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    
    # 5-step syllogism must be present
    for key in ("pratijna", "hetu", "udaharana", "upanaya", "nigamana"):
        assert key in data, f"Missing {key} in Nyāya proof"
        assert isinstance(data[key], str)
        assert len(data[key]) > 0
        
    assert data["is_valid"] is True
    assert data["validation_notes"] == []

def test_nyaya_verify_invalid_proof(client):
    # Empty sutra chain should fail validation
    payload = {
        "candidate_id": "cand_bad",
        "sutra_chain": [],
    }
    r = client.post("/api/v3/nyaya/verify", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["is_valid"] is False
    assert len(data["validation_notes"]) > 0

def test_nyaya_dual_mount(client):
    # Ensure both /api/v1 and /api/v3 are available
    payload = {"candidate_id": "cand_01", "sutra_chain": ["1.1.1"]}
    r_v3 = client.post("/api/v3/nyaya/verify", json=payload)
    r_v1 = client.post("/api/v1/nyaya/verify", json=payload)
    assert r_v3.status_code == 200
    assert r_v1.status_code == 200
    assert r_v3.json()["pratijna"] == r_v1.json()["pratijna"]