from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Literal

ResultClassification = Literal[
    "DETERMINISTIC_DERIVATION",
    "AMBIGUOUS_DERIVATION",
    "HEURISTIC_UNVERIFIED",
    "UNRESOLVED",
]


class OrthographicTriad(BaseModel):
    devanagari: str
    iast: str
    slp1: str


class Authority(BaseModel):
    recension: Literal[
        "Kasika_Vrtti", "Mahabhasya", "Siddhantakaumudi",
        "Vulgate", "Critical_Edition"
    ]
    primary_source: str
    authority_notes: Optional[str] = None
    disputed_alternatives: List[str] = []


class ParseToken(BaseModel):
    surface: str
    stem: str
    role: str


class Candidate(BaseModel):
    candidate_id: str
    parse: List[ParseToken]
    samasa_type: Optional[str] = None
    vigraha: Optional[str] = None
    sutra_chain: List[str]
    authority: Authority
    result_classification: Optional[ResultClassification] = None
    derivation_trace: Optional[Dict[str, Any]] = None
    score: float = Field(ge=0.0, le=1.0)


class RejectedCandidate(BaseModel):
    parse: List[ParseToken]
    reason_code: Literal[
        "UNATTESTED_STEM", "UNATTESTED_PADA_BOUNDARY", "SUTRA_CONFLICT_ASIDDHA",
        "INVALID_SAMASA_ADHIKARA", "CHANDAS_MATRA_MISMATCH", "TIHAI_SAM_VIOLATION"
    ]
    violated_sutra: Optional[str] = None


class KernelEnvelope(BaseModel):
    input_triad: OrthographicTriad
    candidates: List[Candidate]
    rejected: List[RejectedCandidate]
    engine_version: str