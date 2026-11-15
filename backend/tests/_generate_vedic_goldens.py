"""
One-time golden fixture generator.
"""
import base64
import json
from pathlib import Path
from fastapi.testclient import TestClient
from backend.api.main import app

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "backend" / "tests" / "fixtures"
FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
OUT = FIXTURE_DIR / "vedic_golden.json"

RV_1_1_1_A = (
    "\u0905\u0952\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"
    " "
    "\u092a\u0941\u0952\u0930\u094b\u0939\u093f\u0951\u0924\u092e\u094d"
)

KAMPA_TEXT = (
    "\u0905\u0951\u0917\u094d\u0928\u093f\u092e\u0940\u0951\u0933\u0947"
)

CASES = [

    {"id": "rv_1_1_1_rgveda_free_drone",       "text": RV_1_1_1_A, "recension": "rgveda_sakala", "tala_name": None,               "bpm": 60, "sa_hz": 240, "drone_on": True,  "sample_rate": 22050},
    {"id": "rv_1_1_1_rgveda_free_dry",         "text": RV_1_1_1_A, "recension": "rgveda_sakala", "tala_name": None,               "bpm": 60, "sa_hz": 240, "drone_on": False, "sample_rate": 22050},
    {"id": "rv_1_1_1_rgveda_trisra_drone",     "text": RV_1_1_1_A, "recension": "rgveda_sakala", "tala_name": "Tri\u015bra Dhruva", "bpm": 60, "sa_hz": 240, "drone_on": True,  "sample_rate": 22050},
    {"id": "rv_1_1_1_rgveda_trisra_dry",       "text": RV_1_1_1_A, "recension": "rgveda_sakala", "tala_name": "Tri\u015bra Dhruva", "bpm": 60, "sa_hz": 240, "drone_on": False, "sample_rate": 22050},
    {"id": "rv_1_1_1_taittiriya_free_drone",   "text": RV_1_1_1_A, "recension": "taittiriya",    "tala_name": None,               "bpm": 60, "sa_hz": 240, "drone_on": True,  "sample_rate": 22050},
    {"id": "rv_1_1_1_taittiriya_trisra_drone", "text": RV_1_1_1_A, "recension": "taittiriya",    "tala_name": "Tri\u015bra Dhruva", "bpm": 60, "sa_hz": 240, "drone_on": True,  "sample_rate": 22050},
    {"id": "rv_1_1_1_kanva_free_drone",        "text": RV_1_1_1_A, "recension": "kanva",         "tala_name": None,               "bpm": 60, "sa_hz": 240, "drone_on": True,  "sample_rate": 22050},
    {"id": "rv_1_1_1_madhyandina_free_drone",  "text": RV_1_1_1_A, "recension": "madhyandina",   "tala_name": None,               "bpm": 60, "sa_hz": 240, "drone_on": True,  "sample_rate": 22050},
    {"id": "kampa_rgveda_free_dry",         "text": KAMPA_TEXT, "recension": "rgveda_sakala", "tala_name": None, "bpm": 60, "sa_hz": 240, "drone_on": False, "sample_rate": 22050},
    {"id": "kampa_kanva_free_dry",          "text": KAMPA_TEXT, "recension": "kanva",         "tala_name": None, "bpm": 60, "sa_hz": 240, "drone_on": False, "sample_rate": 22050},
    {"id": "kampa_taittiriya_free_dry",     "text": KAMPA_TEXT, "recension": "taittiriya",    "tala_name": None, "bpm": 60, "sa_hz": 240, "drone_on": False, "sample_rate": 22050},
    {"id": "kampa_madhyandina_free_dry",    "text": KAMPA_TEXT, "recension": "madhyandina",   "tala_name": None, "bpm": 60, "sa_hz": 240, "drone_on": False, "sample_rate": 22050},
]

def main():
    client = TestClient(app)
    out_cases = []
    for case in CASES:
        payload = {k: v for k, v in case.items() if k != "id"}
        r = client.post("/api/v3/vedic/render", json=payload)
        assert r.status_code == 200, f"{case['id']}: HTTP {r.status_code} {r.text}"
        data = r.json()
        assert data["rejected"] == [], f"{case['id']}: {data['rejected']}"
        cand = data["candidates"][0]
        wav = base64.b64decode(cand["wav_b64"])
        out_cases.append({
            "id": case["id"],
            "input": {k: v for k, v in case.items() if k != "id"},
            "sha256": cand["sha256"],
            "duration_sec": cand["duration_sec"],
            "peak_db": cand["peak_db"],
            "rms_db": cand["rms_db"],
            "n_samples": cand["n_samples"],
            "wav_bytes_len": len(wav),
        })
        print(f"  {case['id']:40s} sha={cand['sha256'][:12]} {cand['duration_sec']}s {len(wav)}B")

    fixture = {
        "version": "1.0",
        "engine": "aigaane-vedic-render",
        "note": "Any drift in sha256 means code changed output. Regenerate intentionally, commit.",
        "cases": out_cases,
    }
    OUT.write_text(json.dumps(fixture, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] wrote {OUT} ({len(out_cases)} cases)")

if __name__ == "__main__":
    main()
