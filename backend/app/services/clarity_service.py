from backend.app.services.nlp_service import NLPService
from backend.app.services.planner_service import PlannerService
from backend.app.models.planner import NextStep
from sqlalchemy.orm import Session # Import Session

class ClarityService:
    def __init__(self, db: Session): # Accept db session
        self.nlp_service = NLPService(db) # Pass db session to NLPService
        self.planner_service = PlannerService()
        self.db = db # Store db session

    def get_next_step(self, text: str) -> NextStep:
        """
        Determines the next step based on the input text.
        """
        # 1. Process the text to get signals
        signals = self.nlp_service.process_text(self.db, text) # Pass db session

        # 2. Extract intent and user state
        intent = signals["detected_intent"]
        user_state = signals["inferred_user_state"]
        intent_confidence = signals["intent_confidence"]

        # 3. Select the next step using the PlannerService
        next_step = self.planner_service.select_next_step(intent, user_state, intent_confidence)

        return next_step