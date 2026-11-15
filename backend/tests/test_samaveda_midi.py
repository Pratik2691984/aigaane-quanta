import base64

from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)


def test_samaveda_midi_export_returns_valid_midi():
    payload = {
        "swaras": ["S", "R2", "G2", "M1", "P", "D1", "N2", "S"],
        "sa_hz": 240.0,
        "sa_midi_note": 60,
        "tempo_bpm": 76.0,
        "include_tanpura": False,
        "verse_title": "Samaveda route test",
    }
    r = client.post("/api/v3/studio3/midi/export", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    midi_b64 = None
    for key in ("midi_base64", "midi_b64", "midi"):
        if key in data:
            midi_b64 = data[key]
            break
    assert midi_b64 is not None, f"no MIDI field in {list(data.keys())}"
    midi_bytes = base64.b64decode(midi_b64)
    assert midi_bytes[:4] == b"MThd", f"not MIDI header: {midi_bytes[:8]!r}"
    assert len(midi_bytes) > 50, f"MIDI too short: {len(midi_bytes)} bytes"


def test_samaveda_midi_route_available_via_v1_and_v3():
    payload = {"swaras": ["S", "P"], "sa_hz": 240.0, "sa_midi_note": 60, "tempo_bpm": 76.0}
    r3 = client.post("/api/v3/studio3/midi/export", json=payload)
    r1 = client.post("/api/v1/studio3/midi/export", json=payload)
    assert r3.status_code == 200, r3.text
    assert r1.status_code == 200, r1.text
