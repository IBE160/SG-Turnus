from fastapi import APIRouter, Depends
from backend.app.services.nlp_service import NLPService, Intent, UserState
from backend.app.services.clarity_service import ClarityService
from backend.app.api.schemas import NLPRequest, ClarityResponse

router = APIRouter()

# Initialize services
nlp_service = NLPService()
clarity_service = ClarityService()

@router.post("/next-step", response_model=ClarityResponse)
async def get_next_step(request: NLPRequest):
    """
    Analyzes user input and determines the most helpful next step.
    """
    # Process text using NLP service to get intent and user state
    nlp_signals = nlp_service.process_text(request.text)

    detected_intent = Intent(nlp_signals["detected_intent"])
    intent_confidence = nlp_signals["intent_confidence"]
    inferred_user_state = UserState(nlp_signals["inferred_user_state"])
    user_state_confidence = nlp_signals["user_state_confidence"]

    # Select the next step using the Clarity service
    next_step, explanation = clarity_service.select_next_step(
        detected_intent=detected_intent,
        intent_confidence=intent_confidence,
        inferred_user_state=inferred_user_state,
        user_state_confidence=user_state_confidence,
    )

    return ClarityResponse(next_step=next_step, explanation=explanation)
