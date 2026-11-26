import sys
from pathlib import Path
import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from engine._chhandas import PINGALA_GANAS, encode_ganas, scan_verse
from engine._tala import check_tihai_congruence


def test_all_eight_pingala_ganas():
    weights = [
        "G", "G", "G",  # ma (111)
        "L", "G", "G",  # ya (011)
        "G", "L", "G",  # ra (101)
        "L", "L", "G",  # sa (001)
        "G", "G", "L",  # ta (110)
        "L", "G", "L",  # ja (010)
        "G", "L", "L",  # bha (100)
        "L", "L", "L",  # na (000)
    ]
    res = encode_ganas(weights)
    assert res["binary_string"] == "111011101001110010100000"
    assert [g["gana"] for g in res["ganas"]] == [
        "ma", "ya", "ra", "sa", "ta", "ja", "bha", "na"
    ]
    assert set(PINGALA_GANAS.keys()) == {
        "111", "011", "101", "001", "110", "010", "100", "000"
    }
    assert res["remainder_bits"] == ""
    assert res["remainder_vector"] == []


def test_encode_ganas_remainder_and_scan_verse():
    res = encode_ganas(["G", "G", "G", "L", "L", "L", "G"])
    assert [g["gana"] for g in res["ganas"]] == ["ma", "na"]
    assert res["remainder_bits"] == "1"
    assert res["remainder_vector"] == [1]

    scanned = scan_verse("dharmakṣetre kurukṣetre")
    assert "ganas" in scanned
    assert scanned["ganas"]["binary_string"] == "11110111"
    assert len(scanned["ganas"]["ganas"]) == 2


def test_check_tihai_congruence_valid_and_invalid():
    ok = check_tihai_congruence(phrase_matras=5, gap_matras=1, cycle_length=16, t_start=0, sam_anchor=17)
    assert ok["congruent"] is True
    assert ok["tihai_span_matras"] == 17
    assert ok["total_matras"] == 17
    assert ok["residue"] == ok["target"] == 1

    off = check_tihai_congruence(phrase_matras=4, gap_matras=1, cycle_length=16, t_start=0, sam_anchor=17)
    assert off["congruent"] is False
    assert off["tihai_span_matras"] == 14

    with pytest.raises(ValueError):
        check_tihai_congruence(phrase_matras=-1, gap_matras=0, cycle_length=16)
    with pytest.raises(ValueError):
        check_tihai_congruence(phrase_matras=4, gap_matras=1, cycle_length=0)


def test_studio3_tala_tihai_route():
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)

    r_ok = client.post(
        "/api/v3/studio3/tala/tihai",
        json={"phrase_matras": 5, "gap_matras": 1, "cycle_length": 16, "t_start": 0, "sam_anchor": 17},
    )
    assert r_ok.status_code == 200
    body_ok = r_ok.json()
    assert body_ok["congruent"] is True
    assert body_ok["tihai_span_matras"] == 17

    r_off = client.post(
        "/api/v3/studio3/tala/tihai",
        json={"phrase_matras": 4, "gap_matras": 1, "cycle_length": 16},
    )
    assert r_off.status_code == 200
    assert r_off.json()["congruent"] is False

    r_probe = client.get("/api/v3/studio3/probe")
    assert r_probe.status_code == 200
    assert r_probe.json().get("has_check_tihai_congruence") is True
