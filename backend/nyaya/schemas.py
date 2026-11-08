from pydantic import BaseModel, Field
from typing import List, Optional

class NyayaProof(BaseModel):
    pratijna: str = Field(..., description="Proposition: What is being claimed?")
    hetu: str = Field(..., description="Reason: Why is it true?")
    udaharana: str = Field(..., description="Example: Where else is it true?")
    upanaya: str = Field(..., description="Application: Does the example apply here?")
    nigamana: str = Field(..., description="Conclusion: Therefore, it is true.")
    
    is_valid: bool = False
    validation_notes: List[str] = []

class NyayaVerifyRequest(BaseModel):
    candidate_id: str
    sutra_chain: List[str]
    vigraha: Optional[str] = None
    samasa_type: Optional[str] = None