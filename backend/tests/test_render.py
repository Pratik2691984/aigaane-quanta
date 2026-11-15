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


def test_render_kampa_affects_output():
    """Kampa-triggering verse (udatta -> unmarked -> udatta pattern) must
    produce different WAV bytes across recensions whose kampa_default differs.
    Rgveda 5.5Hz/28c vs Kanva 5.0Hz/25c vs Taittiriya/Madhyandina None."""
    kampa_text = "\u0905\u0951\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"
    base = {"text": kampa_text, "bpm": 60, "sa_hz": 240, "drone_on": False, "sample_rate": 22050}
    r_rv = client.post("/api/v3/vedic/render", json={**base, "recension": "rgveda_sakala"})
    r_ty = client.post("/api/v3/vedic/render", json={**base, "recension": "taittiriya"})
    r_ka = client.post("/api/v3/vedic/render", json={**base, "recension": "kanva"})
    sha_rv = r_rv.json()["candidates"][0]["sha256"]
    sha_ty = r_ty.json()["candidates"][0]["sha256"]
    sha_ka = r_ka.json()["candidates"][0]["sha256"]
    assert sha_rv != sha_ty, "Rgveda (kampa) must differ from Taittiriya (no kampa)"
    assert sha_rv != sha_ka, "Rgveda 5.5Hz kampa must differ from Kanva 5.0Hz kampa"
    assert sha_ka != sha_ty, "Kanva (kampa) must differ from Taittiriya (no kampa)"


def test_pada_rest_extends_duration():
    base = "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"
    common = {"recension": "rgveda_sakala", "bpm": 60, "sa_hz": 240, "drone_on": False, "sample_rate": 22050}
    r_plain = client.post("/api/v3/vedic/render", json={**common, "text": base})
    r_single = client.post("/api/v3/vedic/render", json={**common, "text": base + " \u0964"})
    r_double = client.post("/api/v3/vedic/render", json={**common, "text": base + " \u0965"})
    assert r_plain.status_code == 200 and r_single.status_code == 200 and r_double.status_code == 200
    d_plain = r_plain.json()["candidates"][0]["duration_sec"]
    d_single = r_single.json()["candidates"][0]["duration_sec"]
    d_double = r_double.json()["candidates"][0]["duration_sec"]
    assert abs((d_single - d_plain) - 2.0) < 0.2, f"single delta={d_single - d_plain}"
    assert abs((d_double - d_plain) - 4.0) < 0.2, f"double delta={d_double - d_plain}"


def test_pada_rest_spectral_silence():
    import base64
    import io
    import math
    import struct
    import wave
    text = "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947 \u0964"
    payload = {"text": text, "recension": "rgveda_sakala", "bpm": 60, "sa_hz": 240, "drone_on": False, "sample_rate": 22050}
    r = client.post("/api/v3/vedic/render", json=payload)
    cand = r.json()["candidates"][0]
    wav_bytes = base64.b64decode(cand["wav_b64"])
    buf = io.BytesIO(wav_bytes)
    with wave.open(buf, "rb") as wf:
        n_frames = wf.getnframes()
        sr = wf.getframerate()
        raw = wf.readframes(n_frames)
    samples = [s / 32768.0 for s in struct.unpack(f"<{n_frames}h", raw)]
    tone_window = samples[:sr]
    rest_window = samples[-int(1.5 * sr):]
    def rms(xs):
        return math.sqrt(sum(s * s for s in xs) / len(xs)) if xs else 0.0
    tone_rms = rms(tone_window)
    rest_rms = rms(rest_window)
    assert tone_rms > 0.01, f"tone too quiet: {tone_rms}"
    assert rest_rms < tone_rms * 0.1, f"rest {rest_rms:.6f} vs tone {tone_rms:.6f}"
