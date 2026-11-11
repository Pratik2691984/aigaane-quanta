import sys
from pathlib import Path
import logging

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

try:
    import legacy_engine
    _LEGACY_OK = True
except Exception as _e:
    legacy_engine = None
    _LEGACY_OK = False
    logging.warning(f"Legacy engine not loaded: {_e}")

from backend.engine.pydantic_models import (
    KernelEnvelope, Candidate, RejectedCandidate,
    OrthographicTriad, Authority, ParseToken
)

logger = logging.getLogger(__name__)


class EngineAdapter:
    def __init__(self):
        self.version = "1.0.9-adapter"  # bumped: now normalizes input to IAST

    def _triad(self, legacy: dict, fallback_input: str, original_input: str = None) -> OrthographicTriad:
        """
        Build the input_triad (SLP1, Devanagari, IAST) for the response.

        `fallback_input` is what the engine was fed (likely IAST after normalization).
        `original_input` is what the caller originally sent (SLP1, IAST, or Devanagari).
        If original_input is provided, it's used verbatim as the `slp1` field to
        preserve round-trip fidelity for SLP1 inputs.
        """
        tl = legacy.get("transliteration") or {}

        # Fallback SLP1 -> IAST map for basic display
        iast_fallback = fallback_input.replace("H", "ḥ").replace("M", "ṃ").replace("A", "ā").replace("I", "ī").replace("U", "ū").replace("R", "ṛ").replace("S", "ṣ")

        deva = tl.get("devanagari") or iast_fallback
        iast = tl.get("iast") or iast_fallback

        # Prefer original_input (SLP1) if given; else fall back to legacy surface or fallback
        slp1 = original_input or legacy.get("surface") or fallback_input
        return OrthographicTriad(slp1=slp1, devanagari=deva, iast=iast)

    def parse(self, slp1_input: str) -> KernelEnvelope:
        if not _LEGACY_OK or not hasattr(legacy_engine, "parse"):
            return KernelEnvelope(
                input_triad=OrthographicTriad(slp1=slp1_input, devanagari=slp1_input, iast=slp1_input),
                candidates=[], rejected=[], engine_version=self.version + "-no-legacy"
            )

        # Normalize any script (SLP1 / Devanagari / IAST) to IAST before passing
        # to legacy_engine, which consumes IAST (post SLP1 fix in _script.py).
        try:
            from _script import to_canonical_iast
            _, iast_input = to_canonical_iast(slp1_input)
        except Exception as _e:
            logger.debug(f"Script normalization failed for {slp1_input!r}: {_e}")
            iast_input = slp1_input  # graceful fallback

        try:
            legacy = legacy_engine.parse(iast_input)

            # If the legacy engine returned a samasa_tree with multiple children
            # but only 1 token, expand the tokens from the compound tree.
            samasa_tree = legacy.get("samasa_tree") or {}
            children = samasa_tree.get("children") or []
            tokens = legacy.get("tokens") or []

            # Fallback: if samasa_tree is empty AND tokens has only 1 entry,
            # try _samasa.generate_compound_tree() directly.
            if len(children) < 2 and len(tokens) <= 1:
                try:
                    import _samasa
                    logger.info(f"[DEBUG] Attempting compound rescue for {iast_input}")
                    dyn_tree = _samasa.generate_compound_tree(iast_input)
                    logger.info(f"[DEBUG] dyn_tree = {dyn_tree}")
                    if dyn_tree and dyn_tree.get("children") and len(dyn_tree["children"]) >= 2:
                        samasa_tree = dyn_tree
                        children = dyn_tree["children"]
                        legacy["samasa_tree"] = dyn_tree
                        logger.info(f"Adapter rescued compound {iast_input} via generate_compound_tree")
                except Exception as e:
                    logger.warning(f"Adapter compound rescue failed for {iast_input}: {e}")

            if len(children) >= 2 and len(tokens) <= 1:
                expanded_tokens = []
                for idx, child in enumerate(children):
                    is_last = (idx == len(children) - 1)
                    expanded_tokens.append({
                        "token_id": f"T{idx}",
                        "pada": child.get("component_surface", ""),
                        "stem": child.get("component_surface", ""),
                        "pos": "subhanta" if is_last else "samasa_purvapada",
                        "vibhakti": "prathama" if is_last else "lupta",
                        "vacana": "ekavacana",
                        "linga": "pullinga",
                        "confidence": child.get("confidence", 0.90),
                    })
                legacy["tokens"] = expanded_tokens
                logger.info(f"Expanded compound {iast_input} into {len(expanded_tokens)} tokens from samasa_tree")
        except Exception as e:
            logger.error(f"Legacy parse failed on {iast_input}: {e}")
            return KernelEnvelope(
                input_triad=OrthographicTriad(slp1=slp1_input, devanagari=slp1_input, iast=slp1_input),
                candidates=[], rejected=[], engine_version=self.version + "-error"
            )

        if legacy is None:
            return KernelEnvelope(
                input_triad=OrthographicTriad(slp1=slp1_input, devanagari=slp1_input, iast=slp1_input),
                candidates=[],
                rejected=[RejectedCandidate(
                    parse=[ParseToken(surface=slp1_input, stem="UNKNOWN", role="unknown")],
                    reason_code="UNATTESTED_STEM"
                )],
                engine_version=self.version
            )

        # Pass both the normalized IAST (fallback) and the original input (for triad round-trip)
        triad = self._triad(legacy, iast_input, original_input=slp1_input)
        candidates = []

        primary = self._adapt_primary(legacy)
        if primary is not None:
            candidates.append(primary)

        for amb in legacy.get("ambiguous_parses") or []:
            adapted = self._adapt_ambiguous(amb, rank=len(candidates) + 1)
            if adapted is not None:
                candidates.append(adapted)

        rejected = []
        if not candidates:
            rejected.append(RejectedCandidate(
                parse=[ParseToken(surface=slp1_input, stem="UNPARSED", role="unknown")],
                reason_code="UNATTESTED_STEM"
            ))

        candidates.sort(key=lambda c: c.score, reverse=True)
        for idx, cand in enumerate(candidates):
            cand.candidate_id = f"cand_{idx + 1:02d}"

        return KernelEnvelope(
            input_triad=triad,
            candidates=candidates,
            rejected=rejected,
            engine_version=self.version
        )

    def _adapt_primary(self, legacy: dict) -> Candidate | None:
        tokens = legacy.get("tokens") or []
        if not tokens:
            return None

        parse_tokens = []
        for tok in tokens:
            parse_tokens.append(ParseToken(
                surface=tok.get("pada") or tok.get("surface") or "unknown",
                stem=tok.get("stem") or "unknown",
                role=self._role_from_token(tok)
            ))

        samasa_tree = legacy.get("samasa_tree") or {}
        samasa_type = samasa_tree.get("type") if samasa_tree else None
        vigraha = samasa_tree.get("vigraha") if samasa_tree else None
        sutra_chain = self._extract_sutra_chain(legacy, samasa_type)

        provenance = legacy.get("provenance") or []
        engine_ver = next((p.split("=", 1)[1] for p in provenance if p.startswith("engine=")), "unknown")

        authority = Authority(
            recension="Kasika_Vrtti",
            primary_source=f"Aṣṭādhyāyī ({engine_ver})",
            authority_notes="; ".join(provenance) or None,
            disputed_alternatives=[]
        )

        score = float(legacy.get("confidence") or 0.0)
        score = max(0.0, min(1.0, score))

        return Candidate(
            candidate_id="cand_01",
            parse=parse_tokens,
            samasa_type=samasa_type,
            vigraha=vigraha,
            sutra_chain=sutra_chain,
            authority=authority,
            score=score
        )

    def _adapt_ambiguous(self, amb: dict, rank: int) -> Candidate | None:
        tokens = amb.get("tokens") or []
        if not tokens:
            return None

        parse_tokens = []
        for tok in tokens:
            parse_tokens.append(ParseToken(
                surface=tok.get("pada") or tok.get("surface") or "unknown",
                stem=tok.get("stem") or "unknown",
                role=self._role_from_token(tok)
            ))

        sutra_chain = ["1.4.14"]
        score = float(amb.get("confidence") or 0.0)
        score = max(0.0, min(1.0, score))
        ambiguity_type = amb.get("ambiguity_type") or "unspecified"

        authority = Authority(
            recension="Kasika_Vrtti",
            primary_source=f"Ambiguous reading ({ambiguity_type})",
            authority_notes=f"ambiguity_type={ambiguity_type}",
            disputed_alternatives=[]
        )

        return Candidate(
            candidate_id=f"cand_{rank + 1:02d}",
            parse=parse_tokens,
            samasa_type=None,
            vigraha=None,
            sutra_chain=sutra_chain,
            authority=authority,
            score=score
        )

    def _role_from_token(self, tok: dict) -> str:
        pos = tok.get("pos")
        vibhakti = tok.get("vibhakti")
        if pos == "subhanta":
            return f"subanta:{vibhakti}" if vibhakti else "subanta"
        if pos == "tinanta":
            return "tinanta"
        return pos or "token"

    def _extract_sutra_chain(self, legacy: dict, samasa_type: str | None) -> list[str]:
        canon_refs = legacy.get("canon_refs") or []
        if canon_refs:
            refs = []
            for ref in canon_refs:
                if isinstance(ref, str):
                    refs.append(ref)
                elif isinstance(ref, dict) and "sutra" in ref:
                    refs.append(str(ref["sutra"]))
            if refs:
                return refs

        samasa_to_sutra = {
            "tatpurusha": ["2.1.22", "2.2.8"],
            "karmadharaya": ["2.1.57"],
            "bahuvrihi": ["2.2.24"],
            "dvandva": ["2.2.29"],
            "avyayibhava": ["2.1.5"],
            "dvigu": ["2.1.52"],
        }
        if samasa_type and samasa_type in samasa_to_sutra:
            return samasa_to_sutra[samasa_type]

        return ["2.1.1"]