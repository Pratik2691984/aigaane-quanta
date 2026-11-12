"""
Ingest 1,572 Upanishad verses from aigaane-master/raw_sources/gretil/*.json
into aigaane-quanta/backend/data/canon.db.

v3 (Priority 2, fix):
  - Auto-detect source script (IAST / SLP1 / ITRANS) and normalize to IAST
  - Transliterate IAST → Devanagari for text column
  - Store normalized IAST in iast column
  - Strip GRETIL colophon markers
  - Set meter='Prose' for Upanishad verses
"""

import json
import re
import sqlite3
import sys
from pathlib import Path

# Add engine to path for transliteration
_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

try:
    from _script import iast_to_devanagari, to_canonical_iast
    _TRANSLIT_OK = True
except Exception as e:
    print(f"[!] WARNING: script module not available: {e}")
    _TRANSLIT_OK = False


# Paths
SOURCE_DIR = Path(r"C:\aigaane-master\raw_sources\gretil")
TARGET_DB = Path("backend/data/canon.db")

# Map JSON files → (book name, record_id prefix, source)
CORPUS_REGISTRY = {
    "isup___u.json":       ("Isha Upanishad",         "ISU", "gretil.org/upanishads/isha"),
    "kena.json":           ("Kena Upanishad",          "KEN", "gretil.org/upanishads/kena"),
    "kathop_u.json":       ("Katha Upanishad",         "KAT", "gretil.org/upanishads/katha"),
    "prasup_u.json":       ("Prashna Upanishad",       "PRA", "gretil.org/upanishads/prashna"),
    "mundaka.json":        ("Mundaka Upanishad",       "MUN", "gretil.org/upanishads/mundaka"),
    "mandup_u.json":       ("Mandukya Upanishad",      "MAN", "gretil.org/upanishads/mandukya"),
    "aitup__u.json":       ("Aitareya Upanishad",      "AIT", "gretil.org/upanishads/aitareya"),
    "taittiriya.json":     ("Taittiriya Upanishad",    "TAI", "gretil.org/upanishads/taittiriya"),
    "chup___u.json":       ("Chandogya Upanishad",     "CHU", "gretil.org/upanishads/chandogya"),
    "brihadaranyaka.json": ("Brihadaranyaka Upanishad","BRI", "gretil.org/upanishads/brihadaranyaka"),
    "svetu_pu.json":       ("Shvetashvatara Upanishad","SVE", "gretil.org/upanishads/shvetashvatara"),
}


# ════════════════════════════════════════════════════════════════════
# COLOPHON STRIPPING
# ════════════════════════════════════════════════════════════════════

_COLOPHON_PATTERNS = [
    re.compile(r'\|\|\s*iti[^|]*\|\|', re.IGNORECASE),
    re.compile(r'OM\s+shAntiH\s+shAntiH\s+shAntiH.*$', re.IGNORECASE | re.DOTALL),
    re.compile(r'\|\|\s*iti\s+\w*pani[Ss]hat.*$', re.IGNORECASE | re.DOTALL),
    re.compile(r'From\s+Eight\s+Upanishads.*$', re.IGNORECASE | re.DOTALL),
    re.compile(r'var\s+indicates\s+variations.*$', re.IGNORECASE | re.DOTALL),
    re.compile(r'Please\s+send\s+corrections.*$', re.IGNORECASE | re.DOTALL),
    re.compile(r'Last\s+updated\s+https?://.*$', re.IGNORECASE | re.DOTALL),
    re.compile(r'\|\|[^|]*\|\|'),
    re.compile(r'\|+\s*$'),
]


def clean_verse_text(text: str) -> str:
    """Strip GRETIL colophon markers and editorial text from verse."""
    if not text:
        return ""
    result = text
    for pat in _COLOPHON_PATTERNS:
        result = pat.sub("", result)
    result = re.sub(r'\s+', ' ', result).strip()
    return result


# ════════════════════════════════════════════════════════════════════
# INGESTION
# ════════════════════════════════════════════════════════════════════

def make_record_id(prefix: str, chapter: int, verse: int) -> str:
    return f"AIGAANE-UPN-{prefix}-{chapter:02d}.{verse:03d}"


def parse_num(num: str) -> tuple[int, int]:
    parts = num.replace("-", ".").split(".")
    if len(parts) == 1:
        return 1, int(parts[0])
    elif len(parts) == 2:
        return int(parts[0]), int(parts[1])
    else:
        return int(parts[0]), int(parts[-1])


def ingest_all(dry_run: bool = True):
    conn = sqlite3.connect(str(TARGET_DB))
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(verses)")
    existing_cols = {row[1] for row in cur.fetchall()}
    required_cols = {"record_id", "book", "chapter", "verse", "text", "iast", "meter", "source", "envelope_path"}
    missing = required_cols - existing_cols
    if missing:
        print(f"[!] Schema missing columns: {missing}")
        return

    print(f"Target schema OK: {sorted(existing_cols)}\n")

    total_inserted = 0
    total_skipped = 0
    total_cleaned = 0
    total_script_normalized = 0

    for filename, (book, prefix, source) in CORPUS_REGISTRY.items():
        json_path = SOURCE_DIR / filename
        if not json_path.exists():
            print(f"[!] Missing: {json_path}")
            continue

        data = json.loads(json_path.read_text(encoding="utf-8"))
        verses = data.get("verses", [])
        inserted = 0
        skipped = 0
        cleaned_count = 0
        script_normalized = 0

        for v in verses:
            text_raw = (v.get("text") or "").strip()
            num = (v.get("num") or "").strip()
            if not text_raw or not num:
                skipped += 1
                continue

            # Strip colophons
            text_cleaned = clean_verse_text(text_raw)
            if text_cleaned != text_raw:
                cleaned_count += 1

            if not text_cleaned:
                skipped += 1
                continue

            # Detect script and normalize to IAST
            if _TRANSLIT_OK:
                try:
                    detected_script, iast_clean = to_canonical_iast(text_cleaned)
                    if detected_script != "iast":
                        script_normalized += 1
                except Exception:
                    detected_script, iast_clean = "iast", text_cleaned
            else:
                detected_script, iast_clean = "iast", text_cleaned

            try:
                chapter, verse_num = parse_num(num)
            except (ValueError, IndexError):
                chapter, verse_num = 1, inserted + 1

            record_id = make_record_id(prefix, chapter, verse_num)
            envelope_path = f"corpus/stotra/upanishads/{prefix.lower()}/chapter_{chapter:02d}/verse_{verse_num:03d}.json"

            # Transliterate IAST → Devanagari
            if _TRANSLIT_OK:
                deva_text = iast_to_devanagari(iast_clean)
            else:
                deva_text = iast_clean

            meter = "Prose"

            if dry_run:
                inserted += 1
            else:
                cur.execute(
                    "INSERT OR REPLACE INTO verses "
                    "(record_id, book, chapter, verse, text, iast, meter, source, envelope_path) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (record_id, book, chapter, verse_num,
                     deva_text, iast_clean, meter, source, envelope_path)
                )
                inserted += 1

        if not dry_run:
            conn.commit()

        print(f"[{'DRY' if dry_run else 'OK':3}] {book:30} {inserted:>5} verses ({skipped} skipped, {cleaned_count} cleaned, {script_normalized} script-normalized)")
        total_inserted += inserted
        total_skipped += skipped
        total_cleaned += cleaned_count
        total_script_normalized += script_normalized

    conn.close()
    print(f"\n{'[DRY RUN]' if dry_run else '[DONE]'} "
          f"Total: {total_inserted} inserted, {total_skipped} skipped, "
          f"{total_cleaned} cleaned, {total_script_normalized} script-normalized")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Actually insert into DB (default: dry-run)")
    args = parser.parse_args()
    ingest_all(dry_run=not args.apply)