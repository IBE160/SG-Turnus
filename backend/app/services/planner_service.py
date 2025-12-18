from backend.app.models.planner import NextStep, AIModule, InteractionPatternType
from backend.app.services.nlp_service import Intent, UserState

class PlannerService:
    def select_next_step(self, intent: Intent, user_state: UserState, confidence: float) -> NextStep:
        """
        Selects the next step based on the intent, user state, and confidence.
        """
        if intent == Intent.SUMMARIZATION:
            return NextStep(
                ai_module=AIModule.SUMMARIZATION,
                interaction_pattern=InteractionPatternType.MICRO_EXPLANATION,
                parameters={"detail_level": "brief"}
            )
        elif intent == Intent.ACTIVE_RECALL:
            if user_state == UserState.CONFUSED:
                return NextStep(
                    ai_module=AIModule.QUIZ_GENERATION,
                    interaction_pattern=InteractionPatternType.CALIBRATION_QUESTION,
                    parameters={}
                )
            else:
                return NextStep(
                    ai_module=AIModule.FLASHCARD_GENERATION,
                    interaction_pattern=InteractionPatternType.CONCEPT_SNAPSHOT,
                    parameters={}
                )
        elif intent == Intent.CLARIFICATION:
            return NextStep(
                ai_module=AIModule.QA,
                interaction_pattern=InteractionPatternType.ANCHOR_QUESTION,
                parameters={}
            )
        else:
            return NextStep(
                ai_module=AIModule.SUMMARIZATION,
                interaction_pattern=InteractionPatternType.MICRO_EXPLANATION,
                parameters={"detail_level": "normal"}
            )
