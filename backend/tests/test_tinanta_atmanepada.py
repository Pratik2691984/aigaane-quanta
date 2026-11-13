"""
Q4-C regression tests: Ātmanepada paradigm tables.
189 verified cells across 6 roots; dā loṭ explicitly unverified.
"""
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.engine import _tinanta

client = TestClient(app)


@pytest.mark.parametrize(
    "dhatu,lakara,purusha,vacana,expected",
    [
        # kṛ — new lṛṭ + loṭ ātmanepada
        ("kṛ", "lṛṭ", "prathama_purusha", "ekavacana",  "kariṣyate"),
        ("kṛ", "lṛṭ", "uttama_purusha",   "bahuvacana", "kariṣyāmahe"),
        ("kṛ", "loṭ", "prathama_purusha", "ekavacana",  "kurutām"),
        ("kṛ", "loṭ", "madhyama_purusha", "ekavacana",  "kuruṣva"),
        ("kṛ", "loṭ", "uttama_purusha",   "ekavacana",  "karavai"),
        # labh
        ("labh", "laṭ", "prathama_purusha", "ekavacana", "labhate"),
        ("labh", "laṅ", "prathama_purusha", "ekavacana", "alabhata"),
        ("labh", "lṛṭ", "prathama_purusha", "ekavacana", "lapsyate"),
        ("labh", "loṭ", "madhyama_purusha", "ekavacana", "labhasva"),
        # dā — verified lakāras only
        ("dā", "laṭ", "prathama_purusha", "ekavacana", "datte"),
        ("dā", "laṭ", "madhyama_purusha", "ekavacana", "datse"),
        ("dā", "laṅ", "prathama_purusha", "ekavacana", "adatta"),
        ("dā", "lṛṭ", "prathama_purusha", "ekavacana", "dāsyate"),
        # cur
        ("cur", "laṭ", "prathama_purusha", "ekavacana", "corayate"),
        ("cur", "lṛṭ", "prathama_purusha", "ekavacana", "corayiṣyate"),
        # vah
        ("vah", "laṭ", "prathama_purusha", "ekavacana", "vahate"),
        ("vah", "lṛṭ", "prathama_purusha", "ekavacana", "vakṣyate"),
        # jñā
        ("jñā", "laṭ", "prathama_purusha", "ekavacana", "jānīte"),
        ("jñā", "laṭ", "madhyama_purusha", "ekavacana", "jānīṣe"),
        ("jñā", "laṅ", "prathama_purusha", "ekavacana", "ajānīta"),
        ("jñā", "lṛṭ", "prathama_purusha", "ekavacana", "jñāsyate"),
        ("jñā", "loṭ", "prathama_purusha", "ekavacana", "jānītām"),
    ],
)
def test_golden_atmanepada_forms(dhatu, lakara, purusha, vacana, expected):
    r = client.get(
        "/api/v3/morphology/tinanta",
        params={
            "dhatu": dhatu, "lakara": lakara,
            "purusha": purusha, "vacana": vacana,
            "pada": "ātmanepada",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["surface"] == expected
    assert body["source"] == "table"


def test_da_lot_atmanepada_unverified():
    r = client.get(
        "/api/v3/morphology/tinanta",
        params={
            "dhatu": "dā", "lakara": "loṭ",
            "purusha": "prathama_purusha", "vacana": "ekavacana",
            "pada": "ātmanepada",
        },
    )
    assert r.status_code == 400
    assert "not yet verified" in r.json()["detail"]


def test_usage_notes_for_cur_vah():
    for root in ("cur", "vah", "dā"):
        r = client.get(
            "/api/v3/morphology/tinanta/paradigm",
            params={"dhatu": root, "lakara": "laṭ", "pada": "ātmanepada"},
        )
        assert r.status_code == 200
        assert "usage_note" in r.json()


def test_no_usage_note_for_verified_roots():
    for root in ("kṛ", "labh", "jñā"):
        r = client.get(
            "/api/v3/morphology/tinanta/paradigm",
            params={"dhatu": root, "lakara": "laṭ", "pada": "ātmanepada"},
        )
        assert r.status_code == 200
        assert "usage_note" not in r.json()