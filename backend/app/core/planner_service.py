# backend/app/core/planner_service.py

from .config import CONFIDENCE_THRESHOLD
from .ai.calibration_module import CalibrationModule

class PlannerService:
    """
    Service responsible for planning the AI's response, including evaluating
    confidence scores and selecting the overall strategy (e.g., direct response
    vs. uncertainty handling).
    """

    def __init__(self, confidence_threshold: float = CONFIDENCE_THRESHOLD):
        """
        Initializes the PlannerService.

        Args:
            confidence_threshold: The threshold to use for confidence evaluation.
        """
        self.confidence_threshold = confidence_threshold
        self.calibration_module = CalibrationModule()

    def is_confidence_below_threshold(self, confidence_score: float) -> bool:
        """
        Evaluates if the given confidence score is below the configured threshold.

        Args:
            confidence_score: The confidence score from an AI model (e.g., 
                              intent detection).

        Returns:
            True if the score is below the threshold, False otherwise.
        """
        return confidence_score < self.confidence_threshold

    def plan_next_step(self, user_input: str, inferred_context: dict, intent_confidence: float, state_confidence: float) -> dict:
        """
        Selects the next step based on confidence scores.

        Args:
            user_input: The original input from the user.
            inferred_context: A dictionary containing inferred information.
            intent_confidence: The confidence score for the detected intent.
            state_confidence: The confidence score for the inferred user state.

        Returns:
            A dictionary indicating the planned next step and its content.
        """
        if self.is_confidence_below_threshold(intent_confidence) or \
           self.is_confidence_below_threshold(state_confidence):
            calibration_question = self.calibration_module.generate_question(user_input, inferred_context)
            return {"action": "uncertainty_handling", "content": calibration_question}
        else:
            return {"action": "direct_response", "content": "Proceeding with direct response."}

# Example of how this might be used (will be integrated into the API layer)
if __name__ == '__main__':
    planner = PlannerService()

    user_query_high = "What is the capital of France?"
    context_high = {"key_term": "capital", "topic": "geography"}
    user_query_low_intent = "Tell me about this really complicated topic I vaguely understand."
    context_low_intent = {"key_term": "complicated topic", "topic": "unknown"}
    user_query_low_state = "I'm feeling lost about this concept."
    context_low_state = {"key_term": "concept", "topic": "learning"}
    user_query_custom = "Explain 'quantum entanglement' simply."
    context_custom = {"key_term": "quantum entanglement", "topic": "physics"}

    # Scenario 1: High confidence
    high_confidence_plan = planner.plan_next_step(user_query_high, context_high, intent_confidence=0.9, state_confidence=0.85)
    print(f"High confidence plan: {high_confidence_plan}") # Expected: direct_response

    # Scenario 2: Low intent confidence
    low_intent_confidence_plan = planner.plan_next_step(user_query_low_intent, context_low_intent, intent_confidence=0.6, state_confidence=0.9)
    print(f"Low intent confidence plan: {low_intent_confidence_plan}") # Expected: uncertainty_handling with a calibration question

    # Scenario 3: Low state confidence
    low_state_confidence_plan = planner.plan_next_step(user_query_low_state, context_low_state, intent_confidence=0.95, state_confidence=0.5)
    print(f"Low state confidence plan: {low_state_confidence_plan}") # Expected: uncertainty_handling with a calibration question

    # Scenario 4: Custom threshold
    custom_planner = PlannerService(confidence_threshold=0.8)
    custom_plan = custom_planner.plan_next_step(user_query_custom, context_custom, intent_confidence=0.75, state_confidence=0.9)
    print(f"Custom threshold plan: {custom_plan}") # Expected: uncertainty_handling with a calibration question
