import json
import unicodedata

from fastapi.testclient import TestClient

from backend.api.main import app
from backend.engine._svara import generate_vedic_contour

client = TestClient(app)

RV_1_1_1_A = "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947 \u092a\u0941\u0952\u0930\u094b\u0939\u093f\u0951\u0924\u092e\u094d"


def test_nfc_round_trip_and_akshara_segmentation():
    env = generate_vedic_contour(RV_1_1_1_A, recension="rgveda_sakala")
    assert env.rejected == []
    assert len(env.candidates) == 1
    events = env.candidates[0].contour_events
    assert len(events) == 9, f"expected 8 got {len(events)}"
    assert events[0].svara == "anudatta"
    assert events[0].svara_source == "marked"


def test_jatyа_enclitic_svarita_and_pracaya_derivation():
    env = generate_vedic_contour(RV_1_1_1_A, recension="rgveda_sakala")
    events = env.candidates[0].contour_events
    assert events[2].svara == "udatta"
    assert events[2].svara_source == "marked"
    assert events[3].svara == "svarita"
    assert events[3].svara_source == "derived"
    assert events[3].pitch.start_ratio != events[3].pitch.end_ratio
    assert events[3].pitch.glide_cents < 0
    assert events[6].svara == "udatta"
    assert events[7].svara == "svarita"
    assert events[7].svara_source == "derived"


def test_recension_divergence_rgveda_vs_taittiriya():
    rg = generate_vedic_contour(RV_1_1_1_A, recension="rgveda_sakala")
    ty = generate_vedic_contour(RV_1_1_1_A, recension="taittiriya")
    assert rg.candidates[0].contour_events[0].pitch.start_ratio != ty.candidates[0].contour_events[0].pitch.start_ratio
    assert rg.candidates[0].contour_events[0].srutis == [6]
    assert ty.candidates[0].contour_events[0].srutis == [4]


def test_samaveda_explicit_rejection_routing():
    env = generate_vedic_contour(RV_1_1_1_A, recension="samaveda")
    assert env.candidates == []
    assert len(env.rejected) == 1
    assert env.rejected[0].reason_code == "SAMAVEDA_ROUTE"
    assert env.rejected[0].fallback_endpoint == "/api/v3/studio3/midi/export"


def test_unmarked_mantra_rejected_fail_closed():
    env = generate_vedic_contour("\u0905\u0917\u094d\u0928\u093f\u092e\u0940\u0933\u0947", recension="rgveda_sakala")
    assert env.candidates == []
    assert env.rejected[0].reason_code == "NO_SVARA_MARKS"


def test_determinism_byte_identical_json():
    e1 = generate_vedic_contour(RV_1_1_1_A, recension="rgveda_sakala").model_dump()
    e2 = generate_vedic_contour(RV_1_1_1_A, recension="rgveda_sakala").model_dump()
    assert json.dumps(e1, sort_keys=True) == json.dumps(e2, sort_keys=True)


def test_dual_mount_api_routes():
    payload = {"text": RV_1_1_1_A, "recension": "rgveda_sakala", "sa_hz": 240.0}
    r1 = client.post("/api/v1/vedic/contour", json=payload)
    r3 = client.post("/api/v3/vedic/contour", json=payload)
    assert r1.status_code == 200, r1.text
    assert r3.status_code == 200, r3.text
    assert r1.json() == r3.json()


DANDA_BASE = "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"


def test_single_danda_sets_rest_after_matras():
    env = generate_vedic_contour(DANDA_BASE + " \u0964", recension="rgveda_sakala")
    assert env.rejected == []
    events = env.candidates[0].contour_events
    assert events[-1].rest_after_matras == 2.0
    for ev in events[:-1]:
        assert ev.rest_after_matras == 0.0


def test_double_danda_sets_rest_after_matras():
    env = generate_vedic_contour(DANDA_BASE + " \u0965", recension="rgveda_sakala")
    assert env.rejected == []
    events = env.candidates[0].contour_events
    assert events[-1].rest_after_matras == 4.0


def test_no_danda_no_rest():
    env = generate_vedic_contour(DANDA_BASE, recension="rgveda_sakala")
    events = env.candidates[0].contour_events
    for ev in events:
        assert ev.rest_after_matras == 0.0


def test_rest_fields_present_on_models():
    from backend.engine._svara import ContourEvent
    from backend.engine._rhythm import RhythmEvent
    assert "rest_after_matras" in ContourEvent.model_fields
    assert "rest_after_sec" in RhythmEvent.model_fields



