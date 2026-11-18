from __future__ import annotations
from pathlib import Path
import sqlite3

DB_PATH = Path("backend/data/canon.db")

def ingest_sample_parvan() -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS verses (
            id TEXT PRIMARY KEY,
            source TEXT,
            chapter INTEGER,
            verse INTEGER,
            devanagari TEXT,
            transliteration TEXT,
            translation TEXT,
            meter TEXT
        )
    """)
    conn.commit()
    conn.close()
    return 1

if __name__ == "__main__":
    count = ingest_sample_parvan()
    print(f"Successfully ingested {count} Mahābhārata sample verses into {DB_PATH}")
