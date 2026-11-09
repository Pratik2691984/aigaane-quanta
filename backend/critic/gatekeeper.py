"""
CEGAR Gatekeeper -- Two-Tier Stem Attestation (v1.4.1).

Tier 1: `_lexicon.lookup()` -- primary source, ~2,500-5,000 curated stems
Tier 2: `canon.db` FTS5 -- secondary source, 701 Gita verses

Fail-closed design:
  - If `_lexicon` cannot be imported, backend refuses to start
  - If `canon.db` is missing, Tier 2 is skipped (with a warning)
  - Any exception during lookup = UNATTESTED (fail-closed)
"""

import logging
import sqlite3
import sys
import re
from pathlib import Path

_ENGINE_DIR = Path(__file__).resolve().parent.parent / "engine"
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))

try:
    import _lexicon as legacy_lexicon
    _LEXICON_OK = True
except Exception as e:
    legacy_lexicon = None
    _LEXICON_OK = False
    logging.error(f"FATAL: _lexicon not importable from {_ENGINE_DIR}: {e}")

try:
    from _lexicon_supplement import SUPPLEMENT_STEMS
    _SUPPLEMENT_OK = True
except Exception:
    SUPPLEMENT_STEMS = {}
    _SUPPLEMENT_OK = False

try:
    from _tala import check_congruence, lookup_tala
    _TALA_OK = True
except Exception as e:
    check_congruence = None
    lookup_tala = None
    _TALA_OK = False
    logging.warning(f"_tala not importable: {e}")

from backend.engine.pydantic_models import (
    KernelEnvelope,
    RejectedCandidate,
    Candidate,
)

logger = logging.getLogger(__name__)

CANON_DB_PATH = Path("C:/aigaane-master/frontend/public/sqlite/canon.db")

_ENDINGS_TO_STRIP = [
    "āḥ", "aḥ", "āṇi", "āni",
    "āya", "āt", "asya",
    "oḥ", "au", "īḥ", "ūḥ",
    "ā", "ī", "ū", "ḥ", "m",
    "aH", "AH", "iH", "IH", "uH", "UH",
    "aM", "AM",
    "H", "M",
]


def _candidate_forms(stem: str):
    seen = set()
    if stem and stem not in seen:
        seen.add(stem)
        yield stem
    for ending in _ENDINGS_TO_STRIP:
        if stem.endswith(ending) and len(stem) > len(ending) + 1:
            base = stem[: -len(ending)]
            if base not in seen:
                seen.add(base)
                yield base
            with_a = base + "a"
            if with_a not in seen:
                seen.add(with_a)
                yield with_a
            with_aa = base + "ā"
            if with_aa not in seen:
                seen.add(with_aa)
                yield with_aa


class CegarGatekeeper:
    def __init__(self):
        if not _LEXICON_OK or not hasattr(legacy_lexicon, "lookup"):
            raise RuntimeError(
                "FATAL: CegarGatekeeper cannot boot. "
                "_lexicon.lookup is unavailable. "
                "Fail-closed design requires the primary attestation source."
            )
        self.lookup_fn = legacy_lexicon.lookup
        self.supplement_stems = SUPPLEMENT_STEMS if isinstance(SUPPLEMENT_STEMS, dict) else {}

        if CANON_DB_PATH.exists():
            try:
                conn = sqlite3.connect(str(CANON_DB_PATH))
                conn.execute("SELECT 1 FROM verses_fts LIMIT 1").fetchone()
                conn.close()
                self.canon_db = str(CANON_DB_PATH)
            except Exception as e:
                logger.warning(f"canon.db present but unusable: {e}. Running with Tier 1 only.")
                self.canon_db = None
        else:
            self.canon_db = None

    def _attest_lexicon(self, stem: str) -> bool:
        for cand in _candidate_forms(stem):
            try:
                if self.lookup_fn(cand) is not None:
                    if cand != stem:
                        logger.info(f"Stem '{stem}' attested as '{cand}' (Tier 1a)")
                    return True
            except Exception as e:
                logger.warning(f"_lexicon.lookup('{cand}') raised: {e}")

            try:
                if cand.lower() != cand and self.lookup_fn(cand.lower()) is not None:
                    return True
            except Exception:
                pass

            try:
                capped = cand[0].upper() + cand[1:]
                if capped != cand and self.lookup_fn(capped) is not None:
                    return True
            except Exception:
                pass

            if cand in self.supplement_stems or cand.lower() in self.supplement_stems:
                return True

        return False

    def _attest_canon(self, stem: str) -> bool:
        if not self.canon_db:
            return False
        try:
            term = stem.lower().strip()
            if not term:
                return False
            query = f"{term}*"
            conn = sqlite3.connect(self.canon_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM verses_fts WHERE verses_fts MATCH ? LIMIT 1",
                (query,),
            )
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            logger.warning(f"canon.db FTS query for '{stem}' failed: {e} -- rejecting")
            return False

    def _attest_stem(self, stem: str) -> bool:
        if not stem or not isinstance(stem, str):
            return False
        if stem.lower() in {"unknown", "unparsed", "error"}:
            return False
        if self._attest_lexicon(stem):
            return True
        if self._attest_canon(stem):
            logger.info(f"Stem '{stem}' attested via canon.db (Tier 2)")
            return True
        return False

    def verify(self, envelope: KernelEnvelope) -> KernelEnvelope:
        kept: list[Candidate] = []
        rejected: list[RejectedCandidate] = list(envelope.rejected)

        for cand in envelope.candidates:
            # First: Tala congruence check (only if candidate declares a tala)
            tala_violation = None
            try:
                authority_notes = cand.authority.authority_notes or ""
                match = re.search(r"tala=(\w+)", authority_notes)
                if match and _TALA_OK and lookup_tala is not None:
                    tala_name = match.group(1)
                    spec = lookup_tala(tala_name)
                    if spec is not None:
                        pluta_count = 0
                        dirgha_count = 0
                        laghu_count = 0
                        for token in cand.parse:
                            surface = token.surface.lower()
                            if any(surface.endswith(v) for v in ["ā", "ī", "ū"]):
                                dirgha_count += 1
                            else:
                                laghu_count += 1
                        result = check_congruence(
                            pluta_count=pluta_count,
                            dirgha_count=dirgha_count,
                            laghu_count=laghu_count,
                            cycle_length=spec.cycle_length,
                            t_start=0,
                        )
                        if not result.congruent:
                            tala_violation = (
                                f"Tala {tala_name} congruence failed: "
                                f"residue={result.residue}, target={result.target}"
                            )
            except Exception as e:
                logger.warning(f"Tala check errored: {e}")

            if tala_violation:
                rejected.append(
                    RejectedCandidate(
                        parse=cand.parse,
                        reason_code="TIHAI_SAM_VIOLATION",
                        violated_sutra=None,
                    )
                )
                logger.info(f"Candidate {cand.candidate_id} rejected: {tala_violation}")
                continue

            # Second: stem attestation check
            bad_stem = None
            for token in cand.parse:
                if not self._attest_stem(token.stem):
                    bad_stem = token.stem
                    break

            if bad_stem is None:
                kept.append(cand)
            else:
                rejected.append(
                    RejectedCandidate(
                        parse=cand.parse,
                        reason_code="UNATTESTED_STEM",
                        violated_sutra=None,
                    )
                )
                logger.info(
                    f"Candidate {cand.candidate_id} rejected: "
                    f"stem '{bad_stem}' not attested"
                )

        kept.sort(key=lambda c: c.score, reverse=True)
        for idx, cand in enumerate(kept):
            cand.candidate_id = f"cand_{idx + 1:02d}"

        envelope.candidates = kept
        envelope.rejected = rejected

        return envelope
