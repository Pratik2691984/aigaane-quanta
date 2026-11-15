import base64
import struct

from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)

RV_1_1_1_A = (
    "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"
    " "
    "\u092a\u0941\u0952\u0930\u094b\u0939\u093f\u0951\u0924\u092e\u094d"
)


def _render(tala_name=None, drone_on=True):
    payload = {
        "text": RV_1_1_1_A,
        "recension": "rgveda_sakala",
        "bpm": 60,
        "sa_hz": 240,
        "drone_on": drone_on,
        "sample_rate": 22050,
    }
    if tala_name:
        payload["tala_name"] = tala_name
    return client.post("/api/v3/vedic/render", json=payload)


def test_render_wav_header():
    r = _render()
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["rejected"] == []
    assert len(data["candidates"]) == 1
    cand = data["candidates"][0]
    wav = base64.b64decode(cand["wav_b64"])
    assert wav[:4] == b"RIFF"
    assert wav[8:12] == b"WAVE"
    assert len(wav) > 44


def test_render_determinism():
    r1 = _render()
    r2 = _render()
    assert r1.json()["candidates"][0]["sha256"] == r2.json()["candidates"][0]["sha256"]
    assert r1.json()["candidates"][0]["wav_b64"] == r2.json()["candidates"][0]["wav_b64"]


def test_render_duration_and_stats():
    r = _render()
    cand = r.json()["candidates"][0]
    assert cand["duration_sec"] > 1.0
    assert cand["peak_db"] <= -0.5
    assert -40.0 < cand["rms_db"] < -5.0
    assert cand["n_samples"] > 22050


def test_render_no_drone_differs():
    r_drone = _render(drone_on=True)
    r_dry = _render(drone_on=False)
    assert r_drone.json()["candidates"][0]["sha256"] != r_dry.json()["candidates"][0]["sha256"]


def test_render_with_tala_aligned():
    r = _render(tala_name="Tri\u015bra Dhruva")
    data = r.json()
    assert data["rejected"] == []
    cand = data["candidates"][0]
    assert cand["tala_meta"] is not None
    assert cand["tala_meta"]["cycle_length"] == 9


def test_render_unknown_tala_rejected():
    r = _render(tala_name="NotARealTala")
    data = r.json()
    assert data["candidates"] == []
    assert data["rejected"][0]["reason_code"] == "TALA_UNKNOWN"


def test_render_no_svara_marks_rejected():
    payload = {
        "text": "\u0905\u0917\u094d\u0928\u093f\u092e\u0940\u0933\u0947",
        "recension": "rgveda_sakala",
        "bpm": 60,
        "sa_hz": 240,
        "drone_on": True,
        "sample_rate": 22050,
    }
    r = client.post("/api/v3/vedic/render", json=payload)
    data = r.json()
    assert data["candidates"] == []
    assert data["rejected"][0]["reason_code"] == "NO_SVARA_MARKS"
