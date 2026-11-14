"""
Ingest Vālmīki Rāmāyaṇa Bālakāṇḍa (2,217 verses) into canon.db.

Source: github.com/Ashutosh-Vijay/Valmiki_Ramayan_Dataset
Pre-sliced file: backend/data/raw_sources/ramayana_bala.json
Schema: matches existing verses table (record_id, book, chapter, verse, text, iast, meter, source, envelope_path)

After insert: rebuilds verses_fts and copies backend/data/canon.db to frontend/public/sqlite/canon.db.
"""
import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

SOURCE_JSON = Path("backend/data/raw_sources/ramayana_bala.json")
TARGET_DB = Path("backend/data/canon.db")
FRONTEND_DB = Path("frontend/public/sqlite/canon.db")

SOURCE_NAME = "github.com/Ashutosh-Vijay/Valmiki_Ramayan_Dataset"
BOOK_NAME = "Vālmīki Rāmāyaṇa (Bālakāṇḍa)"
PREFIX = "RAM"
CABINET = "CABINET_SMRITI_ITIHASA"
ROOM = "RAMAYANA_BALA"


def make_record_id(chapter: int, verse: int) -> str:
    return f"AIGAANE-{PREFIX}-BALA-{chapter:03d}.{verse:03d}"


def ingest(dry_run: bool = True):
    if not SOURCE_JSON.exists():
        print(f"ERROR: source file missing: {SOURCE_JSON}")
        return
    if not TARGET_DB.exists():
        print(f"ERROR: target DB missing: {TARGET_DB}")
        return

    verses = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    print(f"Loaded {len(verses)} verses from {SOURCE_JSON}")

    conn = sqlite3.connect(str(TARGET_DB))
    cur = conn.cursor()

    # Idempotency check
    cur.execute("SELECT COUNT(*) FROM verses WHERE source = ?", (SOURCE_NAME,))
    existing = cur.fetchone()[0]
    if existing > 0:
        print(f"WARNING: {existing} Balakanda verses already in DB. Will REPLACE.")

    inserted = 0
    skipped = 0
    max_chapter = 0

    for v in verses:
        chapter = v.get("sarga")
        verse = v.get("shloka")
        deva = (v.get("shloka_text") or "").strip()
        iast = (v.get("transliteration") or "").strip()

        if not chapter or not verse or not deva or not iast:
            skipped += 1
            continue

        record_id = make_record_id(int(chapter), int(verse))
        envelope_path = f"corpus/itihasa/ramayana/bala/chapter_{int(chapter):03d}/verse_{int(verse):03d}.json"

        if dry_run:
            inserted += 1
        else:
            cur.execute(
                "INSERT OR REPLACE INTO verses "
                "(record_id, book, chapter, verse, text, iast, meter, source, envelope_path) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (record_id, BOOK_NAME, int(chapter), int(verse),
                 deva, iast, "Anuṣṭubh", SOURCE_NAME, envelope_path)
            )
            inserted += 1
        max_chapter = max(max_chapter, int(chapter))

    if not dry_run:
        now = datetime.now(timezone.utc).isoformat()
        cur.execute(
            "INSERT OR REPLACE INTO texts "
            "(book, cabinet, room, total_verses, total_chapters, last_updated) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (BOOK_NAME, CABINET, ROOM, inserted, max_chapter, now)
        )
        cur.execute("INSERT INTO verses_fts(verses_fts) VALUES('rebuild')")
        conn.commit()

        if FRONTEND_DB.parent.exists():
            shutil.copy2(TARGET_DB, FRONTEND_DB)
            print(f"Copied {TARGET_DB} -> {FRONTEND_DB}")

    conn.close()
    print(f"[{'DRY' if dry_run else 'OK'}] Inserted {inserted}, skipped {skipped}, chapters 1-{max_chapter}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Insert for real (default: dry run)")
    args = parser.parse_args()
    ingest(dry_run=not args.apply)