"""
P0-4 Corpus Provenance Migration (vedic_metadata table in canon.db).
Adds per-record provenance columns (edition, shakha, accent_convention,
audio_ref, alignment_status, textgrid_ref, license, verified_by) without
mutating existing verses columns or FTS5 triggers.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DDL = """
CREATE TABLE IF NOT EXISTS vedic_metadata (
    record_id TEXT PRIMARY KEY,
    edition TEXT NOT NULL,
    shakha TEXT NOT NULL,
    accent_convention TEXT NOT NULL,
    audio_ref TEXT,
    alignment_status TEXT NOT NULL DEFAULT 'none'
        CHECK (alignment_status IN ('none', 'auto', 'expert_verified')),
    textgrid_ref TEXT,
    license TEXT NOT NULL DEFAULT 'unknown',
    verified_by TEXT,
    FOREIGN KEY (record_id) REFERENCES verses(record_id)
);
CREATE INDEX IF NOT EXISTS idx_vedic_meta_shakha_align
    ON vedic_metadata(shakha, alignment_status);
"""


def migrate_canon_db(db_path: Path = Path("backend/data/canon.db")) -> int:
    con = sqlite3.connect(str(db_path))
    try:
        con.executescript(DDL)
        rows = con.execute(
            """
            SELECT record_id, source, COALESCE(recension, 'unknown')
            FROM verses
            WHERE svara_text IS NOT NULL AND svara_text != ''
            """
        ).fetchall()
        inserted = 0
        for record_id, source, recension in rows:
            edition = "RV-D-UTF8.html" if source == "rigveda_corpus" else str(source)
            convention = "paninian_udatta_anudatta_marks"
            cur = con.execute(
                """
                INSERT OR IGNORE INTO vedic_metadata
                    (record_id, edition, shakha, accent_convention, alignment_status, license)
                VALUES (?, ?, ?, ?, 'none', 'CC-BY-NC-SA-4.0-pending-audit')
                """,
                (record_id, edition, recension, convention),
            )
            inserted += cur.rowcount
        con.commit()
        total = con.execute("SELECT COUNT(*) FROM vedic_metadata").fetchone()[0]
        return total
    finally:
        con.close()


if __name__ == "__main__":
    count = migrate_canon_db()
    print(f"[OK] vedic_metadata rows: {count}")
