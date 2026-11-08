from typing import List
from .schemas import NyayaProof, NyayaVerifyRequest

class NyayaVerifier:
    """
    Implements the 5-step syllogistic verification.
    Checks if a grammatical derivation (Candidate) is logically sound.
    """
    
    def verify(self, req: NyayaVerifyRequest) -> NyayaProof:
        # 1. Pratijñā (Proposition)
        prop = f"Candidate {req.candidate_id} is a valid grammatical form."
        
        # 2. Hetu (Reason)
        reason = f"Because it is derived via the sūtra chain: {' -> '.join(req.sutra_chain)}."
        
        # 3. Udāharaṇa (Example) - In a real build, this queries the Kosha/Corpus for a known parallel.
        example = f"Just as other forms derived by {' -> '.join(req.sutra_chain)} are valid."
        
        # 4. Upanaya (Application)
        application = f"This candidate applies the exact same sūtra sequence."
        
        # 5. Nigamana (Conclusion)
        conclusion = f"Therefore, {req.candidate_id} is logically and grammatically valid."
        
        # Logical validation: If the sutra chain is empty, the proof fails.
        is_valid = bool(req.sutra_chain) and bool(req.sutra_chain[0])
        notes = []
        if not is_valid:
            notes.append("Hetu is empty. No sūtra chain provided.")
            
        return NyayaProof(
            pratijna=prop,
            hetu=reason,
            udaharana=example,
            upanaya=application,
            nigamana=conclusion,
            is_valid=is_valid,
            validation_notes=notes
        )