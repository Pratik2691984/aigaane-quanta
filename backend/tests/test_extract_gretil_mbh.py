from pathlib import Path
import sys
import unicodedata

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend" / "data"))

from extract_gretil_mbh import extract_parvan_html


def test_extract_parvan_html_locator_grouping_and_normalization(tmp_path: Path) -> None:
    sample_html = "\n".join(
        [
            "<html><body>",
            "01,000.000*0001_01     front matter line ignored<BR>",
            "01,001.000a            n\u0101r\u0101ya\u1e47a\u1e03 namask\u1e5btya<BR>",
            "01,001.000c            dev\u012b\u1e03 sarasvat\u012b\u1e03 caiva<BR>",
            "01,001.003a            prathama   p\u0101da<BR>",
            "01,001.003b*0018_01    vulgate   first &amp; second<BR>",
            "01,001.003b*0018_02    <span>vulgate   third</span><BR>",
            "01,001.008             janamejayasya r\u0101jar\u1e63e\u1e25<BR>",
            "                       s\u016bta\u00a0\u00a0uv\u0101ca   a\u0301<BR>",
            "</body></html>",
        ]
    )
    html_file = tmp_path / "mbh_01_sample.htm"
    html_file.write_text(sample_html, encoding="utf-8")

    records, stats = extract_parvan_html(html_file, parvan_num=1)

    assert stats["verses_emitted"] == 3
    by_verse = {(r["chapter"], r["verse"]): r for r in records}

    # 1. Sub-padas 000a + 000c grouped into chapter=1, verse=0
    v0 = by_verse[(1, 0)]
    assert v0["parvan"] == 1
    assert v0["text"] == (
        "n\u0101r\u0101ya\u1e47a\u1e03 namask\u1e5btya"
        " / "
        "dev\u012b\u1e03 sarasvat\u012b\u1e03 caiva"
    )
    assert v0["iast"] == v0["text"]
    assert set(v0.keys()) == {"parvan", "chapter", "verse", "text", "iast", "meter"}

    # 2. Starred vulgate additions *0018_01 and *0018_02 appended to verse 3
    v3 = by_verse[(1, 3)]
    assert v3["text"] == "prathama p\u0101da / vulgate first & second / vulgate third"
    assert "<" not in v3["text"] and ">" not in v3["text"]

    # 3. Speaker/continuation line grouped into verse 8 + HTML stripped, NFC applied, whitespace collapsed
    v8 = by_verse[(1, 8)]
    expected_v8 = unicodedata.normalize("NFC", "janamejayasya r\u0101jar\u1e63e\u1e25 / s\u016bta uv\u0101ca a\u0301")
    assert v8["text"] == expected_v8
    assert "front matter" not in " ".join(r["text"] for r in records)


def test_extract_parvan_html_at_suffix_locator(tmp_path: Path) -> None:
    sample_html = "\n".join(
        [
            "<html><body>",
            "05,001.001a            prathama p\u0101da<BR>",
            "05,001.001d@001_0001   vulgate at p\u0101da one<BR>",
            "05,001.001d@001_0002   vulgate at p\u0101da two<BR>",
            "</body></html>",
        ]
    )
    html_file = tmp_path / "mbh_05_at_sample.htm"
    html_file.write_text(sample_html, encoding="utf-8")

    records, stats = extract_parvan_html(html_file, parvan_num=5)

    assert stats["verses_emitted"] == 1
    assert len(records) == 1
    v1 = records[0]
    assert v1["parvan"] == 5
    assert v1["chapter"] == 1
    assert v1["verse"] == 1
    assert v1["text"] == "prathama p\u0101da / vulgate at p\u0101da one / vulgate at p\u0101da two"
    assert v1["iast"] == v1["text"]
    assert "@" not in v1["text"] and "@" not in v1["iast"]
