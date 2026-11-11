"""
Ingest 1,572 Upanishad verses from aigaane-master/raw_sources/gretil/*.json
into aigaane-quanta/backend/data/canon.db.

Source: pre-parsed JSON files with {file, count, verses: [{num, text}]}
Target: backend/data/canon.db (verses table with record_id, book, chapter,
        verse, text, iast, meter, source, envelope_path)

Note: The JSON "text" field contains IAST, not Devanagari. We store IAST in
both `text` and `iast` columns (search still works; user sees IAST). To
provide Devanagari, we'd need an iast_to_deva transliterator — not yet
available in _script.py.
"""

import json
import sqlite3
from pathlib import Path

# Paths
SOURCE_DIR = Path(r"C:\aigaane-master\raw_sources\gretil")
TARGET_DB = Path("backend/data/canon.db")

# Map JSON files → (book name, record_id prefix, source)
CORPUS_REGISTRY = {
    "isup___u.json":       ("Isha Upanishad",        "ISU", "gretil.org/upanishads/isha"),
    "kena.json":           ("Kena Upanishad",         "KEN", "gretil.org/upanishads/kena"),
    "kathop_u.json":       ("Katha Upanishad",        "KAT", "gretil.org/upanishads/katha"),
    "prasup_u.json":       ("Prashna Upanishad",      "PRA", "gretil.org/upanishads/prashna"),
    "mundaka.json":        ("Mundaka Upanishad",      "MUN", "gretil.org/upanishads/mundaka"),
    "mandup_u.json":       ("Mandukya Upanishad",     "MAN", "gretil.org/upanishads/mandukya"),
    "aitup__u.json":       ("Aitareya Upanishad",     "AIT", "gretil.org/upanishads/aitareya"),
    "taittiriya.json":     ("Taittiriya Upanishad",   "TAI", "gretil.org/upanishads/taittiriya"),
    "chup___u.json":       ("Chandogya Upanishad",    "CHU", "gretil.org/upanishads/chandogya"),
    "brihadaranyaka.json": ("Brihadaranyaka Upanishad","BRI", "gretil.org/upanishads/brihadaranyaka"),
    "svetu_pu.json":       ("Shvetashvatara Upanishad","SVE", "gretil.org/upanishads/shvetashvatara"),
}


def make_record_id(prefix: str, chapter: int, verse: int) -> str:
    """Generate a stable record_id like 'AIGAANE-UPN-ISU-01.001'."""
    return f"AIGAANE-UPN-{prefix}-{chapter:02d}.{verse:03d}"


def parse_num(num: str) -> tuple[int, int]:
    """Parse a verse number like '1', '1.2', or '1.2.3' into (chapter, verse)."""
    parts = num.replace("-", ".").split(".")
    if len(parts) == 1:
        return 1, int(parts[0])
    elif len(parts) == 2:
        return int(parts[0]), int(parts[1])
    else:
        return int(parts[0]), int(parts[-1])


def ingest_all(dry_run: bool = True):
    """Ingest all Upanishad JSON files into canon.db."""
    conn = sqlite3.connect(str(TARGET_DB))
    cur = conn.cursor()

    # Verify schema matches expectations
    cur.execute("PRAGMA table_info(verses)")
    existing_cols = {row[1] for row in cur.fetchall()}
    required_cols = {"record_id", "book", "chapter", "verse", "text", "iast", "meter", "source", "envelope_path"}
    missing = required_cols - existing_cols
    if missing:
        print(f"[!] Schema missing columns: {missing}")
        print(f"    Existing: {existing_cols}")
        return

    print(f"Target schema OK: {sorted(existing_cols)}\n")

    total_inserted = 0
    total_skipped = 0

    for filename, (book, prefix, source) in CORPUS_REGISTRY.items():
        json_path = SOURCE_DIR / filename
        if not json_path.exists():
            print(f"[!] Missing: {json_path}")
            continue

        data = json.loads(json_path.read_text(encoding="utf-8"))
        verses = data.get("verses", [])
        inserted = 0
        skipped = 0

        for v in verses:
            iast_text = (v.get("text") or "").strip()
            num = (v.get("num") or "").strip()
            if not iast_text or not num:
                skipped += 1
                continue

            try:
                chapter, verse_num = parse_num(num)
            except (ValueError, IndexError):
                chapter, verse_num = 1, inserted + 1

            record_id = make_record_id(prefix, chapter, verse_num)
            envelope_path = f"corpus/stotra/upanishads/{prefix.lower()}/chapter_{chapter:02d}/verse_{verse_num:03d}.json"

            if dry_run:
                inserted += 1
            else:
                cur.execute(
                    "INSERT OR REPLACE INTO verses "
                    "(record_id, book, chapter, verse, text, iast, meter, source, envelope_path) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (record_id, book, chapter, verse_num,
                     iast_text, iast_text, None, source, envelope_path)
                )
                inserted += 1

        if not dry_run:
            conn.commit()

        print(f"[{'DRY' if dry_run else 'OK':3}] {book:30} {inserted:>5} verses ({skipped} skipped)")
        total_inserted += inserted
        total_skipped += skipped

    conn.close()
    print(f"\n{'[DRY RUN]' if dry_run else '[DONE]'} "
          f"Total: {total_inserted} verses inserted, {total_skipped} skipped")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Actually insert into DB (default: dry-run)")
    args = parser.parse_args()
    ingest_all(dry_run=not args.apply)