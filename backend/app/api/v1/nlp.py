from fastapi import APIRouter, Depends, HTTPException
from backend.app.services.nlp_service import NLPService
from backend.app.api.schemas import NLPRequest, NLPSignalsResponse

router = APIRouter()

# Dependency to get a single instance of NLPService
def get_nlp_service():
    return NLPService()

@router.post("/nlp/process", response_model=NLPSignalsResponse)
async def process_text_endpoint(
    request: NLPRequest,
    nlp_service: NLPService = Depends(get_nlp_service)
):
    try:
        signals = nlp_service.process_text(request.text)
        return NLPSignalsResponse(**signals)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))