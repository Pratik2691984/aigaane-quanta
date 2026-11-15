import json

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.engine import _tala
from backend.engine._rhythm import align_to_tala
from backend.engine._svara import generate_vedic_contour

client = TestClient(app)

RV_1_1_1_A = (
    "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"
    " "
    "\u092a\u0941\u0952\u0930\u094b\u0939\u093f\u0951\u0924\u092e\u094d"
)


def _tala_name(cycle: int, needle: str) -> str:
    for t in _tala.list_talas():
        if t["cycle_length"] == cycle and needle in t["name"]:
            return t["name"]
    raise RuntimeError(f"No tala cycle={cycle} containing {needle!r}")


TALA_9 = _tala_name(9, "Dhruva")


def _events():
    env = generate_vedic_contour(RV_1_1_1_A, recension="rgveda_sakala")
    assert env.candidates, f"contour failed: {env.rejected}"
    return env.candidates[0].contour_events


def test_align_monotonic_onsets():
    events = _events()
    rhythm, _meta = align_to_tala(events, TALA_9, bpm=60)
    assert len(rhythm) == len(events) == 8
    for i in range(1, len(rhythm)):
        assert rhythm[i].onset_sec > rhythm[i - 1].onset_sec


def test_align_sam_accent_only_on_slot_zero():
    events = _events()
    rhythm, _meta = align_to_tala(events, TALA_9, bpm=60)
    for ev in rhythm:
        assert ev.sam_accent == (ev.akshara_in_avarta == 0)


def test_align_slot_and_avarta_consistent():
    events = _events()
    rhythm, _meta = align_to_tala(events, TALA_9, bpm=60)
    for ev in rhythm:
        assert 0 <= ev.akshara_in_avarta < 9
        assert ev.avarta_index >= 0
        expected_onset = (ev.avarta_index * 9 + ev.akshara_in_avarta) * 1.0
        assert abs(ev.onset_sec - expected_onset) < 0.001


def test_align_unknown_tala_raises():
    events = _events()
    try:
        align_to_tala(events, "NotARealTala", bpm=60)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_align_api_endpoint():
    payload = {
        "text": RV_1_1_1_A,
        "recension": "rgveda_sakala",
        "tala_name": TALA_9,
        "bpm": 60,
        "sa_hz": 240,
    }
    r = client.post("/api/v3/vedic/align", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["rejected"] == []
    assert len(data["candidates"]) == 1
    cand = data["candidates"][0]
    assert len(cand["contour_events"]) == 8
    assert len(cand["rhythm_events"]) == 8
    assert cand["tala_meta"]["cycle_length"] == 9


def test_align_api_unknown_tala_returns_rejected():
    payload = {
        "text": RV_1_1_1_A,
        "recension": "rgveda_sakala",
        "tala_name": "NotARealTala",
        "bpm": 60,
        "sa_hz": 240,
    }
    r = client.post("/api/v3/vedic/align", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["candidates"] == []
    assert data["rejected"][0]["reason_code"] == "TALA_UNKNOWN"


def test_align_determinism():
    events = _events()
    r1, m1 = align_to_tala(events, TALA_9, bpm=60)
    r2, m2 = align_to_tala(events, TALA_9, bpm=60)
    j1 = [e.model_dump() for e in r1]
    j2 = [e.model_dump() for e in r2]
    assert json.dumps(j1, sort_keys=True) == json.dumps(j2, sort_keys=True)
    assert m1 == m2
