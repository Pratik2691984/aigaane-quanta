"""
Stage A extractor: GRETIL Unicode Mahābhārata HTML (mbh_NN_u.htm) -> JSON records.

Emits only parvan, chapter, verse, text, iast, and meter; Stage B
(ingest_mahabharata_full.py) owns source_id, PARVAN_META, text_clean, and FTS5.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_GRETIL_DIR = Path(
    r"C:\aigaane-master\mirror_tar\GRETIL-mirror-master\gretil.sub.uni-goettingen.de\gretil\1_sanskr\2_epic\mbh"
)

# Matches leading GRETIL locator such as:
#   01,001.000a
#   01,001.003b*0018_01
#   01,001.008
LOCATOR_RE = re.compile(
    r"^\s*(\d{2}),(\d{3})\.(\d{3})([a-zA-Z0-9*_@]+)?(?:\s+(.*)|(?:<[^>]+>|\s)*)$"
)
TAG_RE = re.compile(r"<[^>]+>")


def _clean_pada_line(raw_tail: str) -> str:
    txt = html.unescape(raw_tail or "")
    txt = TAG_RE.sub(" ", txt)
    txt = unicodedata.normalize("NFC", txt)
    # Collapse internal whitespace while keeping editorial markers readable
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


def extract_parvan_html(
    html_path: Path,
    parvan_num: int,
    meter_assumption: str = "anu\u1e63\u1e6dubh",
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    raw_lines = html_path.read_text(encoding="utf-8", errors="replace").splitlines()
    grouped: "OrderedDict[Tuple[int, int, int], List[str]]" = OrderedDict()
    current_key: Optional[Tuple[int, int, int]] = None
    in_front_matter = False
    locator_lines = 0
    continuation_lines = 0
    skipped_lines = 0

    for line in raw_lines:
        if not line.strip():
            skipped_lines += 1
            continue
        m = LOCATOR_RE.match(line)
        if m:
            p_num = int(m.group(1))
            ch_num = int(m.group(2))
            v_num = int(m.group(3))
            tail = _clean_pada_line(m.group(5) or "")

            if ch_num == 0 and v_num == 0:
                in_front_matter = True
                current_key = None
                skipped_lines += 1
                continue

            in_front_matter = False
            locator_lines += 1
            key = (p_num if p_num else parvan_num, ch_num, v_num)
            current_key = key
            if key not in grouped:
                grouped[key] = []
            if tail:
                grouped[key].append(tail)
        else:
            if in_front_matter or current_key is None:
                skipped_lines += 1
                continue
            cleaned = _clean_pada_line(line)
            if cleaned:
                continuation_lines += 1
                grouped[current_key].append(cleaned)
            else:
                skipped_lines += 1

    records: List[Dict[str, Any]] = []
    for (p_num, ch_num, v_num), padas in grouped.items():
        if not padas:
            continue
        joined = " / ".join(padas)
        records.append(
            {
                "parvan": p_num,
                "chapter": ch_num,
                "verse": v_num,
                "text": joined,
                "iast": joined,
                "meter": meter_assumption,
            }
        )

    stats = {
        "file": str(html_path),
        "total_lines": len(raw_lines),
        "locator_lines": locator_lines,
        "continuation_lines": continuation_lines,
        "skipped_lines": skipped_lines,
        "verses_emitted": len(records),
    }
    return records, stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract GRETIL Mahābhārata HTML to Stage A JSON")
    parser.add_argument("--parvan", type=int, required=True, help="Parvan number (1..18)")
    parser.add_argument("--html-path", type=Path, default=None, help="Path to mbh_NN_u.htm")
    parser.add_argument("--out", type=Path, required=True, help="Output JSON path")
    args = parser.parse_args()

    html_path = args.html_path or (DEFAULT_GRETIL_DIR / f"mbh_{args.parvan:02d}_u.htm")
    records, stats = extract_parvan_html(html_path, args.parvan)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
