"""
Tiṅanta (finite verb) generation engine — Q4-B.

Table-first, generation-fallback approach:
  1. Try verified paradigm tables (_tinanta_data.PARADIGMS).
  2. If missing, fall back to a simple generative rule for regular roots.
  3. Every response has a "source" field ("table" | "generated") and
     "confidence" (1.0 for table, 0.5 for generated).
"""

from __future__ import annotations
from typing import Optional

from _lexicon import _DHATUPATHA
from _tinanta_data import PARADIGMS, _LOT_PARASMAI, _LOT_ATMANE

SUPPORTED_LAKARAS = ["laṭ", "laṅ", "lṛṭ", "loṭ"]
SUPPORTED_PADAS = ["parasmaipada", "ātmanepada"]
PURUSHAS = ["prathama_purusha", "madhyama_purusha", "uttama_purusha"]
VACANAS = ["ekavacana", "dvivacana", "bahuvacana"]

_LAT_PARASMAI = [
    ("ti",  "ekavacana",  "prathama_purusha"),
    ("taḥ", "dvivacana",  "prathama_purusha"),
    ("anti","bahuvacana", "prathama_purusha"),
    ("si",  "ekavacana",  "madhyama_purusha"),
    ("thaḥ","dvivacana",  "madhyama_purusha"),
    ("tha", "bahuvacana", "madhyama_purusha"),
    ("mi",  "ekavacana",  "uttama_purusha"),
    ("vaḥ", "dvivacana",  "uttama_purusha"),
    ("maḥ", "bahuvacana", "uttama_purusha"),
]

_LAT_ATMANE = [
    ("te",   "ekavacana",  "prathama_purusha"),
    ("ete",  "dvivacana",  "prathama_purusha"),
    ("ante", "bahuvacana", "prathama_purusha"),
    ("se",   "ekavacana",  "madhyama_purusha"),
    ("ethe", "dvivacana",  "madhyama_purusha"),
    ("dhve", "bahuvacana", "madhyama_purusha"),
    ("e",    "ekavacana",  "uttama_purusha"),
    ("vahe", "dvivacana",  "uttama_purusha"),
    ("mahe", "bahuvacana", "uttama_purusha"),
]

_LAN_PARASMAI = [
    ("t", "ekavacana",  "prathama_purusha"),
    ("tām","dvivacana", "prathama_purusha"),
    ("n", "bahuvacana", "prathama_purusha"),
    ("ḥ", "ekavacana",  "madhyama_purusha"),
    ("tam","dvivacana", "madhyama_purusha"),
    ("ta","bahuvacana", "madhyama_purusha"),
    ("am","ekavacana",  "uttama_purusha"),
    ("va","dvivacana",  "uttama_purusha"),
    ("ma","bahuvacana", "uttama_purusha"),
]

_LAN_ATMANE = [
    ("ta",   "ekavacana",  "prathama_purusha"),
    ("etām", "dvivacana",  "prathama_purusha"),
    ("anta", "bahuvacana", "prathama_purusha"),
    ("thāḥ", "ekavacana",  "madhyama_purusha"),
    ("ethām","dvivacana",  "madhyama_purusha"),
    ("dhvam","bahuvacana", "madhyama_purusha"),
    ("i",    "ekavacana",  "uttama_purusha"),
    ("vahi", "dvivacana",  "uttama_purusha"),
    ("mahi", "bahuvacana", "uttama_purusha"),
]

ENDING_TABLES = {
    ("laṭ", "parasmaipada"): _LAT_PARASMAI,
    ("laṭ", "ātmanepada"):   _LAT_ATMANE,
    ("laṅ", "parasmaipada"): _LAN_PARASMAI,
    ("laṅ", "ātmanepada"):   _LAN_ATMANE,
    ("loṭ", "parasmaipada"): _LOT_PARASMAI,
    ("loṭ", "ātmanepada"):   _LOT_ATMANE,
    ("lṛṭ", "parasmaipada"): _LAT_PARASMAI,
    ("lṛṭ", "ātmanepada"):   _LAT_ATMANE,
}


def _lookup_table(dhatu, lakara, pada, purusha, vacana):
    """Return the verified surface form from the paradigm table, or None."""
    root = PARADIGMS.get(dhatu)
    if not root:
        return None
    lak = root.get(lakara)
    if not lak:
        return None
    pad = lak.get(pada)
    if not pad:
        return None
    return pad.get((purusha, vacana))


def _ending(lakara, pada, purusha, vacana):
    for surface, v, p in ENDING_TABLES.get((lakara, pada), []):
        if p == purusha and v == vacana:
            return surface
    return None


def _simple_sandhi(stem, ending):
    """Simplified post-ending sandhi for generative fallback."""
    if not stem or not ending:
        return stem + ending
    lv, rv = stem[-1], ending[0]

    if lv in "aā" and rv in "aā":
        return stem[:-1] + "ā" + ending[1:]
    if lv in "aā" and rv in "iī":
        return stem[:-1] + "e" + ending[1:]
    if lv in "aā" and rv in "uū":
        return stem[:-1] + "o" + ending[1:]
    if lv in "iī" and rv in "aā":
        return stem[:-1] + "y" + ending
    if lv in "uū" and rv in "aā":
        return stem[:-1] + "v" + ending
    if lv in "aā" and rv in "e":
        return stem[:-1] + "a e" + ending[1:]
    if lv in "aā" and rv in "o":
        return stem[:-1] + "a o" + ending[1:]
    return stem + ending


def conjugate(
    dhatu: str,
    lakara: str = "laṭ",
    purusha: str = "prathama_purusha",
    vacana: str = "ekavacana",
    pada: Optional[str] = None,
) -> dict:
    if dhatu not in _DHATUPATHA:
        return {"error": f"dhātu '{dhatu}' not in _DHATUPATHA", "dhatu": dhatu}
    if lakara not in SUPPORTED_LAKARAS:
        return {"error": f"lakāra '{lakara}' not supported (use one of {SUPPORTED_LAKARAS})", "dhatu": dhatu}

    info = _DHATUPATHA[dhatu]
    if pada is None:
        pada = info.get("pada", "parasmaipada")
        if pada == "ubhayapada":
            pada = "parasmaipada"
    if pada not in SUPPORTED_PADAS:
        return {"error": f"pada '{pada}' not supported", "dhatu": dhatu}

    if purusha not in PURUSHAS or vacana not in VACANAS:
        return {"error": "invalid purusha/vacana", "dhatu": dhatu}

    verified = _lookup_table(dhatu, lakara, pada, purusha, vacana)
    if verified:
        return {
            "dhatu": dhatu,
            "lakara": lakara,
            "pada": pada,
            "purusha": purusha,
            "vacana": vacana,
            "surface": verified,
            "source": "table",
            "confidence": 1.0,
        }

    stem = None
    if lakara == "laṭ" or lakara == "loṭ":
        stem = info.get("stem_pres")
    elif lakara == "laṅ":
        base = info.get("stem_pres") or dhatu
        stem = "a" + base
    elif lakara == "lṛṭ":
        stem = info.get("stem_fut")

    if not stem:
        return {"error": f"cannot generate {lakara} for '{dhatu}'", "dhatu": dhatu}

    end = _ending(lakara, pada, purusha, vacana)
    if end is None:
        return {"error": "no ending available", "dhatu": dhatu}

    surface = _simple_sandhi(stem, end)

    return {
        "dhatu": dhatu,
        "lakara": lakara,
        "pada": pada,
        "purusha": purusha,
        "vacana": vacana,
        "surface": surface,
        "source": "generated",
        "confidence": 0.5,
    }


def paradigm(dhatu: str, lakara: str = "laṭ", pada: Optional[str] = None) -> dict:
    if dhatu not in _DHATUPATHA:
        return {"error": f"dhātu '{dhatu}' not in _DHATUPATHA"}

    info = _DHATUPATHA[dhatu]
    if pada is None:
        pada = info.get("pada", "parasmaipada")
        if pada == "ubhayapada":
            pada = "parasmaipada"

    out = {
        "dhatu": dhatu,
        "lakara": lakara,
        "pada": pada,
        "meaning": info.get("meaning", ""),
        "gana": info.get("gana"),
        "rows": [],
    }
    for pur in PURUSHAS:
        row = {"purusha": pur, "cells": []}
        for vac in VACANAS:
            r = conjugate(dhatu, lakara, pur, vac, pada)
            row["cells"].append({
                "vacana": vac,
                "surface": r.get("surface", "—"),
                "source": r.get("source", "error"),
            })
        out["rows"].append(row)
    return out


def list_dhatus():
    return [
        {"dhatu": name, "meaning": data.get("meaning", ""),
         "gana": data.get("gana"), "pada": data.get("pada")}
        for name, data in _DHATUPATHA.items()
    ]


if __name__ == "__main__":
    import json
    for dhatu in ["kṛ", "bhū", "gam", "as"]:
        for lakara in SUPPORTED_LAKARAS:
            par = paradigm(dhatu, lakara, "parasmaipada")
            print(f"\n=== {dhatu} · {lakara} · parasmaipada ===")
            for row in par["rows"]:
                cells = " | ".join(f"{c['surface']:14s}" for c in row["cells"])
                print(f"  {row['purusha']:20s} {cells}")