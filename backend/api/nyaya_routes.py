from fastapi import APIRouter, HTTPException
from backend.nyaya.schemas import NyayaVerifyRequest, NyayaProof
from backend.nyaya.verifier import NyayaVerifier

router = APIRouter(tags=["nyaya"])
verifier = NyayaVerifier()

@router.post("/verify", response_model=NyayaProof)
async def verify_proof(payload: NyayaVerifyRequest):
    """
    Takes a grammatical candidate and outputs a 5-step Nyāya syllogism 
    proving its validity.
    """
    try:
        proof = verifier.verify(payload)
        return proof
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))