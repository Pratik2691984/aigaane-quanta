"""
Idempotent Vedic metadata & provenance migration helper (F1 / F6).
Ensures source_registry exists, unverified licenses stay 'unknown' rather than
asserting unverified licenses, and sample edition labels are normalized cleanly.
"""
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "canon.db"


def apply_vedic_metadata_governance(db_path: Path = DB_PATH, dry_run: bool = True) -> dict:
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    has_vedic_meta = (
        cur.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='vedic_metadata'"
        ).fetchone()[0]
        > 0
    )
    if not has_vedic_meta:
        conn.close()
        return {"vedic_metadata_present": False, "updated_licenses": 0, "updated_editions": 0}

    pending_count = cur.execute(
        "SELECT COUNT(*) FROM vedic_metadata "
        "WHERE license IS NULL OR trim(license) = '' OR lower(license) LIKE '%pending%'"
    ).fetchone()[0]

    sample_edition_count = cur.execute(
        "SELECT COUNT(*) FROM vedic_metadata WHERE edition = 'rigveda_svara_sample'"
    ).fetchone()[0]

    if not dry_run:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS source_registry (
                source_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                recension TEXT,
                license TEXT NOT NULL DEFAULT 'unknown',
                provenance_note TEXT,
                verified_by TEXT
            )
            """
        )
        cur.execute(
            """
            UPDATE vedic_metadata
            SET license = 'unknown'
            WHERE license IS NULL OR trim(license) = '' OR lower(license) LIKE '%pending%'
            """
        )
        cur.execute(
            """
            UPDATE vedic_metadata
            SET edition = 'sakala_sample_fixture'
            WHERE edition = 'rigveda_svara_sample'
            """
        )
        cur.execute(
            """
            INSERT OR IGNORE INTO source_registry
                (source_id, title, recension, license, provenance_note, verified_by)
            VALUES
                ('rigveda_corpus', 'Rigveda Corpus', 'rgveda_sakala', 'unknown', 'License provenance pending verification', NULL),
                ('rigveda_svara_sample', 'Rigveda Svara Sample', 'rgveda_sakala', 'unknown', 'Sample fixture metadata', NULL)
            """
        )
        conn.commit()

    conn.close()
    return {
        "vedic_metadata_present": True,
        "updated_licenses": pending_count,
        "updated_editions": sample_edition_count,
        "dry_run": dry_run,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize Vedic metadata provenance safely")
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    summary = apply_vedic_metadata_governance(args.db, dry_run=not args.apply)
    print(summary)


if __name__ == "__main__":
    main()
