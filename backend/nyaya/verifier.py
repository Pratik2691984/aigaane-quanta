from typing import List
from .schemas import NyayaProof, NyayaVerifyRequest
from backend.engine._prakriya import validate_sutra_chain


class NyayaVerifier:
    """
    Implements the 5-step syllogistic verification.
    Checks if a grammatical derivation (Candidate) is logically and Paninian-sound.
    """

    def verify(self, req: NyayaVerifyRequest) -> NyayaProof:
        # 1. Pratijna (Proposition)
        prop = f"Candidate {req.candidate_id} is a valid grammatical form."

        # 2. Hetu (Reason)
        reason = f"Because it is derived via the sutra chain: {' -> '.join(req.sutra_chain)}."

        # 3. Udaharana (Example)
        example = f"Just as other forms derived by {' -> '.join(req.sutra_chain)} are valid."

        # 4. Upanaya (Application)
        application = "This candidate applies the exact same sutra sequence."

        # 5. Nigamana (Conclusion)
        conclusion = f"Therefore, {req.candidate_id} is logically and grammatically valid."

        # Logical + Paninian validation
        has_chain = bool(req.sutra_chain) and all(bool((s or "").strip()) for s in req.sutra_chain)
        cls = (req.result_classification or "").strip()
        is_heuristic = cls == "HEURISTIC_UNVERIFIED"
        is_known_non_deterministic = cls in ("AMBIGUOUS_DERIVATION", "UNRESOLVED")
        notes: List[str] = []

        if not has_chain:
            notes.append("Hetu is empty or contains blank sutra entries.")
        if is_heuristic:
            notes.append("Candidate is HEURISTIC_UNVERIFIED; heuristic output cannot be certified as a deterministic proof.")
        if is_known_non_deterministic:
            notes.append(f"Candidate classification is {cls}; insufficient derivation evidence for valid proof.")
        if not cls:
            notes.append("Missing result_classification; unverified classification cannot establish a valid proof.")

        chain_violations: List[str] = []
        if has_chain:
            chain_violations = validate_sutra_chain(
                req.sutra_chain,
                require_registered=req.strict_registry,
            )
            for v in chain_violations:
                notes.append(f"Paninian chain violation: {v}")

        if req.derivation_steps is not None and len(req.derivation_steps) == 0:
            chain_violations.append("EMPTY_DERIVATION_STEPS")
            notes.append("Provided derivation_steps list is empty; cannot certify deterministic proof.")

        is_valid = bool(
            has_chain
            and cls == "DETERMINISTIC_DERIVATION"
            and len(chain_violations) == 0
        )

        return NyayaProof(
            pratijna=prop,
            hetu=reason,
            udaharana=example,
            upanaya=application,
            nigamana=conclusion,
            is_valid=is_valid,
            validation_notes=notes,
        )
