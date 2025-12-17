from backend.app.services.nlp_service import Intent, UserState
from backend.app.api.schemas import NextStep, ClarityResponse, InteractionPatternType

class ClarityService:
    def __init__(self):
        pass

    def select_next_step(
        self,
        detected_intent: Intent,
        intent_confidence: float,
        inferred_user_state: UserState,
        user_state_confidence: float,
        # Add original_text, tokens, etc. if needed for more complex logic
    ) -> ClarityResponse: # Changed return type
        """
        Selects the single most helpful next step based on detected intent, user state,
        and confidence levels. This is a rule-based system for the initial implementation.
        """
        explanation = ""
        pattern_type = InteractionPatternType.NONE
        pattern_data = {}

        # --- High-confidence intent-based decisions ---
        if intent_confidence > 0.8:
            if detected_intent == Intent.CLARIFICATION:
                if inferred_user_state == UserState.CONFUSED:
                    explanation = "High confidence in clarification intent and user confusion."
                    pattern_type = InteractionPatternType.MICRO_EXPLANATION_PATTERN
                    pattern_data = {"concept": "the concept you are confused about"} # Placeholder
                    return ClarityResponse(next_step=NextStep.PROVIDE_MICRO_EXPLANATION, explanation=explanation, pattern_type=pattern_type, pattern_data=pattern_data)
                else:
                    explanation = "High confidence in clarification intent."
                    pattern_type = InteractionPatternType.ANCHOR_QUESTION_PATTERN
                    pattern_data = {"question": "What specifically are you trying to clarify?"} # Placeholder
                    return ClarityResponse(next_step=NextStep.ASK_FOR_CLARIFICATION_QUESTION, explanation=explanation, pattern_type=pattern_type, pattern_data=pattern_data)

            elif detected_intent == Intent.SUMMARIZATION:
                if inferred_user_state == UserState.TIME_LIMITED:
                    explanation = "High confidence in summarization intent and user being time-limited."
                    return ClarityResponse(next_step=NextStep.GENERATE_BRIEF_SUMMARY, explanation=explanation)
                else:
                    explanation = "High confidence in summarization intent."
                    return ClarityResponse(next_step=NextStep.ASK_FOR_SUMMARY_LENGTH, explanation=explanation)

            elif detected_intent == Intent.PROBLEM_SOLVING:
                explanation = "High confidence in problem-solving intent."
                pattern_type = InteractionPatternType.PROBLEM_DECOMPOSITION_PATTERN
                pattern_data = {"problem_statement": "Your problem here"} # Placeholder
                return ClarityResponse(next_step=NextStep.BREAK_DOWN_PROBLEM, explanation=explanation, pattern_type=pattern_type, pattern_data=pattern_data)

            elif detected_intent == Intent.ACTIVE_RECALL:
                explanation = "High confidence in active recall intent."
                return ClarityResponse(next_step=NextStep.CREATE_PRACTICE_QUIZ, explanation=explanation)

            elif detected_intent == Intent.CONCEPT_LINKING:
                explanation = "High confidence in concept linking intent."
                return ClarityResponse(next_step=NextStep.EXPLAIN_CONNECTION, explanation=explanation)

            elif detected_intent == Intent.MISCONCEPTION_CORRECTION:
                explanation = "High confidence in misconception correction intent."
                return ClarityResponse(next_step=NextStep.PROVIDE_CORRECT_INFORMATION, explanation=explanation)

        # --- Lower confidence or general state-based decisions ---
        if inferred_user_state == UserState.CONFUSED and user_state_confidence > 0.6:
            explanation = "User appears confused."
            pattern_type = InteractionPatternType.CALIBRATION_QUESTION_PATTERN
            pattern_data = {"question": "What parts are unclear?"} # Placeholder
            return ClarityResponse(next_step=NextStep.SUGGEST_DEFINITION_LOOKUP, explanation=explanation, pattern_type=pattern_type, pattern_data=pattern_data)

        if inferred_user_state == UserState.OVERLOADED and user_state_confidence > 0.6:
            explanation = "User appears overloaded."
            return ClarityResponse(next_step=NextStep.GENERATE_BRIEF_SUMMARY, explanation=explanation)

        if inferred_user_state == UserState.UNCERTAIN and user_state_confidence > 0.5:
            explanation = "User appears uncertain."
            return ClarityResponse(next_step=NextStep.ACKNOWLEDGE_AND_REPHRASE, explanation=explanation)
            
        # --- Fallback for unknown intent or low confidence ---
        if detected_intent == Intent.UNKNOWN and intent_confidence < 0.3:
            explanation = "Low confidence in intent detection, asking for more context."
            pattern_type = InteractionPatternType.ANCHOR_QUESTION_PATTERN
            pattern_data = {"question": "Can you tell me more about what you need help with?"} # Placeholder
            return ClarityResponse(next_step=NextStep.ASK_OPEN_ENDED_QUESTION, explanation=explanation, pattern_type=pattern_type, pattern_data=pattern_data)
        
        # Default fallback
        explanation = "Default next step due to lack of specific signals."
        return ClarityResponse(next_step=NextStep.PROVIDE_GENERAL_GUIDANCE, explanation=explanation)