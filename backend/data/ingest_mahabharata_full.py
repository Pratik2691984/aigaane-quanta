"""
Mahābhārata Corpus Ingestion Pipeline (P2-2).
Ingests Mahābhārata Parvans into canon.db with text_clean normalization,
texts metadata updates, and FTS5 synchronization.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

DB_PATH = Path(__file__).resolve().parent / "canon.db"

DIA_FOLD = {
    "\u0101": "a", "\u012b": "i", "\u016b": "u",
    "\u1e5b": "r", "\u1e5d": "r", "\u1e37": "l", "\u1e39": "l",
    "\u1e45": "n", "\u00f1": "n", "\u1e47": "n",
    "\u015b": "s", "\u1e63": "s",
    "\u1e43": "m", "\u1e21": "m", "\u1e25": "h",
}

PARVAN_META: Dict[int, Tuple[str, str]] = {
    1: ("Mahābhārata Ādi Parva", "MAHABHARATA_ADI"),
    2: ("Mahābhārata Sabhā Parva", "MAHABHARATA_SABHA"),
    3: ("Mahābhārata Vana Parva", "MAHABHARATA_VANA"),
    4: ("Mahābhārata Virāṭa Parva", "MAHABHARATA_VIRATA"),
    5: ("Mahābhārata Udyoga Parva", "MAHABHARATA_UDYOGA"),
    6: ("Mahābhārata Bhīṣma Parva", "MAHABHARATA_BHISHMA"),
    7: ("Mahābhārata Droṇa Parva", "MAHABHARATA_DRONA"),
    8: ("Mahābhārata Karṇa Parva", "MAHABHARATA_KARNA"),
    9: ("Mahābhārata Śalya Parva", "MAHABHARATA_SHALYA"),
    10: ("Mahābhārata Sauptika Parva", "MAHABHARATA_SAUPTIKA"),
    11: ("Mahābhārata Strī Parva", "MAHABHARATA_STRI"),
    12: ("Mahābhārata Śānti Parva", "MAHABHARATA_SHANTI"),
    13: ("Mahābhārata Anuśāsana Parva", "MAHABHARATA_ANUSHASANA"),
    14: ("Mahābhārata Āśvamedhika Parva", "MAHABHARATA_ASHVAMEDHIKA"),
    15: ("Mahābhārata Āśramavāsika Parva", "MAHABHARATA_ASHRAMAVASIKA"),
    16: ("Mahābhārata Mausala Parva", "MAHABHARATA_MAUSALA"),
    17: ("Mahābhārata Mahāprasthānika Parva", "MAHABHARATA_MAHAPRASTHANIKA"),
    18: ("Mahābhārata Svargārohaṇa Parva", "MAHABHARATA_SVARGAROHANA"),
}

SEED_VERSES: List[Dict[str, Any]] = [
    {
        "parvan": 1,
        "chapter": 1,
        "verse": 1,
        "text": "\u0928\u093e\u0930\u093e\u092f\u0923\u0902 \u0928\u092e\u0938\u094d\u0915\u0943\u0924\u094d\u092f \u0928\u0930\u0902 \u091a\u0948\u0935 \u0928\u0930\u094b\u0924\u094d\u0924\u092e\u092e\u094d\u0964 \u0926\u0947\u0935\u0940\u0902 \u0938\u0930\u0938\u094d\u0935\u0924\u0940\u0902 \u091a\u0948\u0935 \u0924\u0924\u094b \u091c\u092f\u092e\u0941\u0926\u0940\u0930\u092f\u0947\u0924\u094d\u0965",
        "iast": "n\u0101r\u0101ya\u1e47a\u1e03 namask\u1e5btya nara\u1e03 caiva narottamam | dev\u012b\u1e03 sarasvat\u012b\u1e03 caiva tato jayam ud\u012brayet ||",
        "meter": "anu\u1e63\u1e6dubh",
    },
    {
        "parvan": 2,
        "chapter": 1,
        "verse": 1,
        "text": "\u0938\u092d\u093e\u092f\u093e\u0902 \u0930\u093e\u091c\u0938\u0924\u094d\u0915\u0943\u0924\u093e\u0903 \u092a\u093e\u0923\u094d\u0921\u0935\u093e\u0903 \u0915\u0941\u0930\u0941\u092a\u0941\u0902\u0917\u0935\u093e\u0903\u0964 \u0927\u0930\u094d\u092e\u0930\u093e\u091c\u0938\u094d\u092f \u0936\u0941\u0936\u0941\u091a\u0941\u0903 \u0938\u0924\u094d\u092f\u0938\u0902\u0927\u0938\u094d\u092f \u0927\u0940\u092e\u0924\u0903\u0965",
        "iast": "sabh\u0101y\u0101\u1e03 r\u0101jasatk\u1e5bt\u0101\u1e25 p\u0101\u1e47\u1e0dav\u0101\u1e25 kurupu\u1e03gav\u0101\u1e25 | dharmar\u0101jasya \u015bu\u015bucu\u1e25 satyasa\u1e03dhasya dh\u012bmata\u1e25 ||",
        "meter": "anu\u1e63\u1e6dubh",
    },
    {
        "parvan": 3,
        "chapter": 1,
        "verse": 1,
        "text": "\u0924\u0938\u094d\u092e\u093f\u0928\u094d \u0935\u0928\u0947 \u092e\u0939\u093e\u0930\u0923\u094d\u092f\u0947 \u092a\u093e\u0923\u094d\u0921\u0935\u093e\u0903 \u0938\u0939 \u0926\u094d\u0930\u094c\u092a\u0926\u094d\u092f\u093e\u0964 \u0928\u094d\u092f\u0935\u0938\u0928\u094d \u0926\u094d\u0935\u0948\u0924\u0935\u0928\u0947 \u0930\u092e\u094d\u092f\u0947 \u0927\u0930\u094d\u092e\u0930\u093e\u091c\u092a\u094d\u0930\u0936\u093e\u0938\u093f\u0924\u093e\u0903\u0965",
        "iast": "tasmin vane mah\u0101ra\u1e47ye p\u0101\u1e47\u1e0dav\u0101\u1e25 saha draupady\u0101 | nyavasan dvaitavane ramye dharmar\u0101japra\u015b\u0101sit\u0101\u1e25 ||",
        "meter": "anu\u1e63\u1e6dubh",
    },
    {
        "parvan": 4,
        "chapter": 1,
        "verse": 1,
        "text": "\u0924\u0924\u094b \u092f\u0941\u0927\u093f\u0937\u094d\u0920\u093f\u0930\u094b \u0930\u093e\u091c\u093e \u0935\u093f\u0930\u093e\u091f\u0938\u094d\u092f \u0928\u093f\u0935\u0947\u0936\u0928\u0947\u0964 \u0905\u091c\u094d\u091e\u093e\u0924\u0935\u093e\u0938\u092e\u0935\u0938\u0924\u094d \u0924\u0947\u0928\u0948\u0935 \u0938\u0939 \u092a\u093e\u0923\u094d\u0921\u0935\u0948\u0903\u0965",
        "iast": "tato yudhi\u1e63\u1e6diro r\u0101j\u0101 vir\u0101\u1e6dasya nive\u015bane | aj\u00f1\u0101tav\u0101sam avasat tenaiva saha p\u0101\u1e47\u1e0davai\u1e25 ||",
        "meter": "anu\u1e63\u1e6dubh",
    },
    {
        "parvan": 5,
        "chapter": 1,
        "verse": 1,
        "text": "\u0935\u093f\u0930\u093e\u091f\u0917\u0943\u0939\u0947 \u0924\u0941 \u0935\u093f\u092a\u094d\u0930\u0915\u0940\u0930\u094d\u0923\u093e\u0903 \u092a\u093e\u0923\u094d\u0921\u0935\u093e\u0903 \u0915\u0941\u0930\u0941\u092d\u093f\u0903 \u0938\u0939\u0964 \u0909\u0926\u094d\u092f\u094b\u0917\u092e\u0915\u0941\u0930\u094d\u0935\u0928\u094d\u0924 \u092f\u0941\u0926\u094d\u0927\u0947 \u0938\u092e\u0941\u092a\u0938\u094d\u0925\u093f\u0924\u0947\u0965",
        "iast": "vir\u0101\u1e6dag\u1e5bhe tu viprak\u012br\u1e47\u0101\u1e25 p\u0101\u1e47\u1e0dav\u0101\u1e25 kurubhi\u1e25 saha | udyogam akurvanta yuddhe samupasthite ||",
        "meter": "anu\u1e63\u1e6dubh",
    },
]


def fold_search_text(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").lower()
    chars: List[str] = []
    for ch in s:
        if unicodedata.combining(ch):
            continue
        chars.append(DIA_FOLD.get(ch, ch))
    return "".join(chars)


def _extract_parvan_num(item: Dict[str, Any]) -> Optional[int]:
    for key in ("parvan", "parva", "parvan_num", "parva_num", "kanda"):
        val = item.get(key)
        if val is None:
            continue
        if isinstance(val, int):
            return val
        digits = "".join(ch for ch in str(val) if ch.isdigit())
        if digits:
            return int(digits)
    return None


def _load_records(
    source_json: Optional[Path],
    parvans: Optional[Iterable[int]],
) -> List[Dict[str, Any]]:
    allowed = set(parvans) if parvans else None
    if not source_json:
        return [r for r in SEED_VERSES if allowed is None or r["parvan"] in allowed]

    raw = json.loads(source_json.read_text(encoding="utf-8"))
    entries = raw.get("verses", raw) if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise ValueError(f"Unsupported JSON root in {source_json}")

    out: List[Dict[str, Any]] = []
    for idx, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            continue
        parvan = _extract_parvan_num(entry) or 1
        if allowed is not None and parvan not in allowed:
            continue
        chapter = int(entry.get("chapter") or entry.get("adhyaya") or entry.get("sarga") or 1)
        verse = int(entry.get("verse") or entry.get("shloka") or idx)
        text_val = (entry.get("text") or entry.get("devanagari") or entry.get("shloka_text") or "").strip()
        iast_val = (entry.get("iast") or entry.get("transliteration") or "").strip()
        if not text_val and not iast_val:
            continue
        meter_val = (entry.get("meter") or "anu\u1e63\u1e6dubh").strip()
        out.append(
            {
                "parvan": parvan,
                "chapter": chapter,
                "verse": verse,
                "text": text_val or iast_val,
                "iast": iast_val or text_val,
                "meter": meter_val,
            }
        )
    return out


def ingest_mahabharata(
    db_path: Path = DB_PATH,
    source_json: Optional[Path] = None,
    parvans: Optional[List[int]] = None,
    dry_run: bool = True,
) -> int:
    records = _load_records(source_json, parvans)
    if not records:
        return 0

    if dry_run:
        return len(records)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    existing_cols = {row[1] for row in cur.execute("PRAGMA table_info(verses)").fetchall()}
    has_text_clean = "text_clean" in existing_cols

    touched_sources: Dict[str, Tuple[str, str]] = {}
    inserted = 0

    for rec in records:
        parvan = int(rec["parvan"])
        chapter = int(rec["chapter"])
        verse = int(rec["verse"])
        text_val = str(rec["text"])
        iast_val = str(rec["iast"])
        meter_val = str(rec["meter"])

        book_label, room_code = PARVAN_META.get(
            parvan, (f"Mah\u0101bh\u0101rata Parva {parvan}", f"MAHABHARATA_PARVAN_{parvan}")
        )
        source_name = f"mahabharata_parvan_{parvan}"
        record_id = f"AIGAANE-MBH-{parvan:02d}-{chapter:03d}.{verse:03d}"
        env_path = f"corpus/itihasa/mahabharata/parvan_{parvan:02d}/chapter_{chapter:03d}/verse_{verse:03d}.json"
        text_clean = f"{fold_search_text(iast_val)} {fold_search_text(text_val)}".strip()

        if has_text_clean:
            cur.execute(
                """
                INSERT OR REPLACE INTO verses
                (record_id, book, chapter, verse, text, iast, meter, source, envelope_path, text_clean)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (record_id, book_label, chapter, verse, text_val, iast_val, meter_val, source_name, env_path, text_clean),
            )
        else:
            cur.execute(
                """
                INSERT OR REPLACE INTO verses
                (record_id, book, chapter, verse, text, iast, meter, source, envelope_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (record_id, book_label, chapter, verse, text_val, iast_val, meter_val, source_name, env_path),
            )
        inserted += 1
        touched_sources[source_name] = (book_label, room_code)

    now_iso = datetime.now(timezone.utc).isoformat()
    for src_name, (book_label, room_code) in touched_sources.items():
        cnt, ch_cnt = cur.execute(
            "SELECT COUNT(*), COUNT(DISTINCT chapter) FROM verses WHERE source = ?",
            (src_name,),
        ).fetchone()
        cur.execute(
            """
            INSERT OR REPLACE INTO texts (book, cabinet, room, total_verses, total_chapters, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (book_label, "CABINET_SMRITI_ITIHASA", room_code, cnt, ch_cnt, now_iso),
        )

    cur.execute("INSERT INTO verses_fts(verses_fts) VALUES('rebuild')")
    conn.commit()
    conn.close()
    return inserted


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Mahābhārata Parvans into canon.db")
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--source-json", type=Path, default=None)
    parser.add_argument("--parvans", type=str, default=None, help="Comma-separated Parvan numbers, e.g. 1,2")
    parser.add_argument("--apply", action="store_true", help="Write changes to canon.db (default is dry-run)")
    args = parser.parse_args()

    parvan_list = (
        [int(x.strip()) for x in args.parvans.split(",") if x.strip()]
        if args.parvans
        else None
    )
    count = ingest_mahabharata(
        db_path=args.db,
        source_json=args.source_json,
        parvans=parvan_list,
        dry_run=not args.apply,
    )
    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"[{mode}] Processed {count} Mahābhārata verses on {args.db}")


if __name__ == "__main__":
    main()