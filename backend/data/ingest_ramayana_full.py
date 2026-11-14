"""
Ingest remaining 6 kāṇḍas of Vālmīki Rāmāyaṇa (Ayodhyā, Araṇya, Kiṣkindhā, Sundara, Yuddha, Uttara)
into canon.db. Bālakāṇḍa already ingested (see ingest_ramayana_bala.py).

Total additions: ~21,074 verses. After this run, canon.db contains all 23,291 Rāmāyaṇa verses.

Source: backend/data/valmiki_ramayana_shlokas.json (full dataset, git-ignored)
"""
import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

SOURCE_JSON = Path("backend/data/valmiki_ramayana_shlokas.json")
TARGET_DB = Path("backend/data/canon.db")
FRONTEND_DB = Path("frontend/public/sqlite/canon.db")

SOURCE_NAME = "github.com/Ashutosh-Vijay/Valmiki_Ramayan_Dataset"
CABINET = "CABINET_SMRITI_ITIHASA"

# Per-kāṇḍa mapping: kanda field value -> (book display name, room name, prefix, envelope subpath)
KANDA_MAP = {
    "Ayodhya Kanda":   ("Vālmīki Rāmāyaṇa (Ayodhyākāṇḍa)",   "RAMAYANA_AYODHYA",   "AYO", "ayodhya"),
    "Aranya Kanda":    ("Vālmīki Rāmāyaṇa (Araṇyakāṇḍa)",    "RAMAYANA_ARANYA",    "ARA", "aranya"),
    "Kishkindha Kanda":("Vālmīki Rāmāyaṇa (Kiṣkindhākāṇḍa)", "RAMAYANA_KISHKINDHA","KIS", "kishkindha"),
    "Sundara Kanda":   ("Vālmīki Rāmāyaṇa (Sundarakāṇḍa)",   "RAMAYANA_SUNDARA",   "SUN", "sundara"),
    "Yuddha Kanda":    ("Vālmīki Rāmāyaṇa (Yuddhakāṇḍa)",    "RAMAYANA_YUDDHA",    "YUD", "yuddha"),
    "Uttara Kanda":    ("Vālmīki Rāmāyaṇa (Uttarakāṇḍa)",    "RAMAYANA_UTTARA",    "UTT", "uttara"),
}


def ingest(dry_run: bool = True):
    if not SOURCE_JSON.exists():
        print(f"ERROR: source missing: {SOURCE_JSON}")
        return

    all_verses = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    print(f"Loaded {len(all_verses)} total verses from full dataset")

    conn = sqlite3.connect(str(TARGET_DB))
    cur = conn.cursor()

    for kanda_field, (book_name, room, prefix, subpath) in KANDA_MAP.items():
        subset = [v for v in all_verses if v.get("kanda") == kanda_field]
        if not subset:
            print(f"  [SKIP] {kanda_field}: no verses in dataset")
            continue

        # Idempotency check
        cur.execute("SELECT COUNT(*) FROM verses WHERE source = ? AND book = ?", (SOURCE_NAME, book_name))
        existing = cur.fetchone()[0]
        if existing > 0:
            print(f"  [WARN] {kanda_field}: {existing} verses already present, will REPLACE")

        inserted = 0
        skipped = 0
        max_chapter = 0

        for v in subset:
            chapter = v.get("sarga")
            verse = v.get("shloka")
            deva = (v.get("shloka_text") or "").strip()
            iast = (v.get("transliteration") or "").strip()

            if not chapter or not verse or not deva or not iast:
                skipped += 1
                continue

            record_id = f"AIGAANE-{prefix}-{subpath.upper()[:3]}-{int(chapter):03d}.{int(verse):03d}"
            envelope_path = f"corpus/itihasa/ramayana/{subpath}/chapter_{int(chapter):03d}/verse_{int(verse):03d}.json"

            if not dry_run:
                cur.execute(
                    "INSERT OR REPLACE INTO verses "
                    "(record_id, book, chapter, verse, text, iast, meter, source, envelope_path) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (record_id, book_name, int(chapter), int(verse),
                     deva, iast, "Anuṣṭubh", SOURCE_NAME, envelope_path)
                )
            inserted += 1
            max_chapter = max(max_chapter, int(chapter))

        if not dry_run and inserted > 0:
            now = datetime.now(timezone.utc).isoformat()
            cur.execute(
                "INSERT OR REPLACE INTO texts "
                "(book, cabinet, room, total_verses, total_chapters, last_updated) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (book_name, CABINET, room, inserted, max_chapter, now)
            )

        print(f"  [{'DRY' if dry_run else 'OK':3}] {kanda_field:20} {inserted:>5} verses, {skipped} skipped, chapters 1-{max_chapter}")

    if not dry_run:
        print("\nRebuilding FTS5...")
        cur.execute("INSERT INTO verses_fts(verses_fts) VALUES('rebuild')")
        conn.commit()

        # Copy to frontend
        if FRONTEND_DB.parent.exists():
            shutil.copy2(TARGET_DB, FRONTEND_DB)
            print(f"Copied {TARGET_DB} -> {FRONTEND_DB}")

        # Final stats
        cur.execute("SELECT COUNT(*) FROM verses")
        print(f"\nTotal verses now: {cur.fetchone()[0]}")

    conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Insert for real")
    args = parser.parse_args()
    ingest(dry_run=not args.apply)