"""
Ingest Sāmaveda Saṃhitā (Kauthuma TEI XML, GRETIL) into canon.db.
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

SOURCE_XML = Path(r"C:\aigaane-master\raw_sources\gretil\sa_sAmavedasaMhitA.xml")
TARGET_DB = Path(r"C:\aigaane-quanta\backend\data\canon.db")
FRONTEND_DB = Path(r"C:\aigaane-quanta\frontend\public\sqlite\canon.db")

SOURCE_NAME = "gretil.org/samaveda_kauthuma"
BOOK_NAME = "Sāmaveda Saṃhitā (Kauthuma)"
CABINET = "CABINET_VEDA_SAMHITA"
ROOM = "SAMAVEDA_KAUTHUMA"
RECENSION = "samaveda_kauthuma"

CODE_RE = re.compile(r"\b(\d+)\s+(\d+)\s+(\d+)\s+(\d{2})(\d{2})([a-d])\b")

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


def parse_samaveda_xml(xml_path: Path) -> Tuple[List[tuple], int]:
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
        if "REFERENCE SYSTEM:" in txt or "Characters Used for the Transliteration" in txt:
            continue

        matches = list(CODE_RE.finditer(txt))
        for idx, m in enumerate(matches):
            start = m.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(txt)
            seg = re.sub(r"\s*\.\.\s*\d+\s*$", "", txt[start:end]).strip(" .")
            if not seg:
                continue

            b1, b2, b3, sec, itm, pada = m.groups()
            chapter = int(b2) if int(b2) > 0 else int(b1)
            verse_num = int(itm)

            base_id = (
                f"AIGAANE-SV-K-{int(b1):02d}-{int(b2):02d}-{int(b3):02d}-"
                f"{int(sec):02d}.{verse_num:03d}-{pada}"
            )
            seen_ids[base_id] += 1
            occ = seen_ids[base_id]
            record_id = base_id if occ == 1 else f"{base_id}-v{occ}"
            if occ > 1:
                collisions += 1

            text_clean = fold_text(seg)
            envelope_path = (
                f"corpus/veda/samaveda/kauthuma/"
                f"ch_{chapter:02d}/{record_id}.json"
            )
            rows.append(
                (
                    record_id,
                    BOOK_NAME,
                    chapter,
                    verse_num,
                    seg,
                    seg,
                    "Sāman/Ārcika",
                    SOURCE_NAME,
                    envelope_path,
                    RECENSION,
                    None,
                    text_clean,
                )
            )

    return rows, collisions


def ingest_samaveda(
    xml_path: Path = SOURCE_XML,
    db_path: Path = TARGET_DB,
    frontend_db: Path = FRONTEND_DB,
    apply: bool = False,
) -> None:
    rows, collisions = parse_samaveda_xml(xml_path)
    chapters = {r[2] for r in rows}
    print(
        f"[{'APPLY' if apply else 'DRY-RUN'}] Parsed {len(rows)} Sāmaveda segments "
        f"across {len(chapters)} sections ({collisions} collision(s) disambiguated)"
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
    parser = argparse.ArgumentParser(description="Ingest Sāmaveda Kauthuma into canon.db")
    parser.add_argument("--xml", type=Path, default=SOURCE_XML)
    parser.add_argument("--db", type=Path, default=TARGET_DB)
    parser.add_argument("--frontend-db", type=Path, default=FRONTEND_DB)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    ingest_samaveda(
        xml_path=args.xml,
        db_path=args.db,
        frontend_db=args.frontend_db,
        apply=args.apply,
    )


if __name__ == "__main__":
    main()