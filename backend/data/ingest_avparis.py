"""
Ingest Atharvaveda Pariśiṣṭas TEI XML (GRETIL) into canon.db.
Defaults to dry-run; pass --apply to write changes, rebuild verses_fts,
and sync frontend/public/sqlite/canon.db.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sqlite3
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

SOURCE_XML = Path(r"C:\aigaane-master\raw_sources\gretil\atharvaveda_parisistas.xml")
TARGET_DB = Path(r"C:\aigaane-quanta\backend\data\canon.db")
FRONTEND_DB = Path(r"C:\aigaane-quanta\frontend\public\sqlite\canon.db")

SOURCE_NAME = "gretil.org/atharvaveda_parisistas"
BOOK_NAME = "Atharvaveda Pariśiṣṭas"
CABINET = "CABINET_VEDA_PARISHISHTA"
ROOM = "ATHARVAVEDA_PARISHISHTAS"
RECENSION = "parishishta_tei"

MARKER_RE = re.compile(r"\(AVParis_([0-9]+),([0-9]+)\.([0-9]+)\)\s*(.+)")

DIA_FOLD: Dict[str, str] = {
    "\u0101": "a", "\u012b": "i", "\u016b": "u",
    "\u1e5b": "r", "\u1e5d": "r", "\u1e37": "l", "\u1e39": "l",
    "\u1e45": "n", "\u00f1": "n", "\u1e47": "n",
    "\u015b": "s", "\u1e63": "s",
    "\u1e43": "m", "\u1e21": "m", "\u1e25": "h",
}


def fold_text(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").lower()
    out: List[str] = []
    for ch in s:
        if unicodedata.combining(ch):
            continue
        out.append(DIA_FOLD.get(ch, ch))
    return "".join(out)


def clean_avp_text(raw_body: str) -> str:
    cleaned = re.sub(r"\(AVParis_[0-9]+,[0-9]+\.[0-9]+\)\s*", "", raw_body or "")
    cleaned = re.sub(r"\(Pariśiṣṭa_[^)]*\)\s*", "", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def parse_avparis_xml(xml_path: Path, include_zero_parishta: bool = True) -> Tuple[List[tuple], int]:
    if not xml_path.exists():
        raise FileNotFoundError(f"Source XML missing: {xml_path}")

    tree = ET.parse(xml_path)
    root = tree.getroot()
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    body = root.find("tei:body", ns)
    target = body if body is not None else root

    seen_ids: Counter[str] = Counter()
    rows: List[tuple] = []
    collisions = 0

    for elem in target.iter():
        if elem.tag.split("}")[-1] != "p":
            continue
        txt = " ".join("".join(elem.itertext()).split())
        match = MARKER_RE.search(txt)
        if not match:
            continue

        parishta = int(match.group(1))
        section = int(match.group(2))
        item = int(match.group(3))
        body_txt = match.group(4)

        if parishta == 0 and not include_zero_parishta:
            continue

        base_id = f"AIGAANE-AVP-{parishta:02d}-{section:02d}.{item:03d}"
        seen_ids[base_id] += 1
        occ = seen_ids[base_id]
        record_id = base_id if occ == 1 else f"{base_id}-v{occ}"
        if occ > 1:
            collisions += 1

        iast_clean = clean_avp_text(body_txt)
        if not iast_clean:
            continue

        text_clean = fold_text(iast_clean)
        envelope_path = (
            f"corpus/veda/atharvaveda/parisistas/"
            f"parishishta_{parishta:02d}/sec_{section:02d}_{record_id}.json"
        )
        rows.append(
            (
                record_id,
                BOOK_NAME,
                parishta,
                item,
                iast_clean,
                iast_clean,
                "Appendix/Kalpa",
                SOURCE_NAME,
                envelope_path,
                RECENSION,
                None,
                text_clean,
            )
        )

    return rows, collisions


def ingest_avparis(
    xml_path: Path = SOURCE_XML,
    db_path: Path = TARGET_DB,
    frontend_db: Path = FRONTEND_DB,
    include_zero_parishta: bool = True,
    apply: bool = False,
) -> None:
    rows, collisions = parse_avparis_xml(xml_path, include_zero_parishta=include_zero_parishta)
    chapters = {r[2] for r in rows}
    print(
        f"[{'APPLY' if apply else 'DRY-RUN'}] Parsed {len(rows)} AVParis rows "
        f"across {len(chapters)} parishishta numbers ({collisions} collision(s) disambiguated)"
    )

    if not apply:
        for sample in rows[:3]:
            print("  Sample:", sample[0], sample[2], sample[3], sample[5][:75])
        return

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    try:
        cur.executemany(
            """
            INSERT OR REPLACE INTO verses
            (record_id, book, chapter, verse, text, iast, meter, source,
             envelope_path, recension, svara_text, text_clean)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        now_iso = datetime.now(timezone.utc).isoformat()
        cur.execute(
            """
            INSERT OR REPLACE INTO texts
            (book, cabinet, room, total_verses, total_chapters, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (BOOK_NAME, CABINET, ROOM, len(rows), len(chapters), now_iso),
        )
        cur.execute("INSERT INTO verses_fts(verses_fts) VALUES('rebuild')")
        conn.commit()

        total_verses = cur.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
        total_fts = cur.execute("SELECT COUNT(*) FROM verses_fts").fetchone()[0]
        print(f"[OK] Committed {len(rows)} rows. Total verses={total_verses}, verses_fts={total_fts}")
    finally:
        conn.close()

    if frontend_db.parent.exists():
        shutil.copy2(db_path, frontend_db)
        print(f"[OK] Mirrored {db_path} -> {frontend_db}")
    print(f"[INFO] canon.db size: {db_path.stat().st_size / (1024 * 1024):.2f} MB")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest Atharvaveda Pariśiṣṭas into canon.db")
    parser.add_argument("--xml", type=Path, default=SOURCE_XML)
    parser.add_argument("--db", type=Path, default=TARGET_DB)
    parser.add_argument("--frontend-db", type=Path, default=FRONTEND_DB)
    parser.add_argument("--skip-zero-parishta", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    ingest_avparis(
        xml_path=args.xml,
        db_path=args.db,
        frontend_db=args.frontend_db,
        include_zero_parishta=not args.skip_zero_parishta,
        apply=args.apply,
    )


if __name__ == "__main__":
    main()