from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session # Import Session
from backend.app.database import get_db # Import get_db
from backend.app.services.clarity_service import ClarityService
from backend.app.api.schemas import NLPRequest, NextStep

router = APIRouter()

# Dependency to get ClarityService
def get_clarity_service(db: Session = Depends(get_db)):
    return ClarityService(db)

@router.post("/next-step", response_model=NextStep)
async def get_next_step(
    request: NLPRequest,
    clarity_service: ClarityService = Depends(get_clarity_service) # Use dependency injection
):
    """
    Analyzes user input and determines the most helpful next step.
    """
    # Select the next step using the Clarity service
    next_step = clarity_service.get_next_step(request.text)

    return next_step
