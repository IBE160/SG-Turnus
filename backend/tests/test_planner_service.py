# backend/tests/test_planner_service.py

import pytest
from backend.app.core.planner_service import PlannerService
from backend.app.core.ai.calibration_module import CalibrationModule

# Test data: a list of (user_input, inferred_context, intent_confidence, state_confidence, expected_action, expected_content_substring)
PLANNER_TEST_CASES = [
    ("User query", {"key_term": "test", "topic": "tests"}, 0.9, 0.85, "direct_response", "Proceeding with direct response."),   # High confidence for both
    ("User query", {"key_term": "test", "topic": "tests"}, 0.7, 0.8, "direct_response", "Proceeding with direct response."),    # Intent at threshold, state high
    ("User query", {"key_term": "test", "topic": "tests"}, 0.8, 0.7, "direct_response", "Proceeding with direct response."),    # State at threshold, intent high
    ("Low intent query", {"key_term": "low intent", "topic": "AI"}, 0.69, 0.8, "uncertainty_handling", "low intent"), # Intent just below threshold
    ("Low state query", {"key_term": "low state", "topic": "AI"}, 0.8, 0.69, "uncertainty_handling", "low state"), # State just below threshold
    ("Very low intent query", {"key_term": "very low", "topic": "AI"}, 0.5, 0.9, "uncertainty_handling", "very low"), # Low intent confidence
    ("Very low state query", {"key_term": "another low", "topic": "AI"}, 0.9, 0.4, "uncertainty_handling", "another low"), # Low state confidence
    ("Both low query", {"key_term": "both low", "topic": "AI"}, 0.2, 0.3, "uncertainty_handling", "both low"), # Low confidence for both
]

@pytest.fixture
def default_planner():
    """Returns a PlannerService with the default threshold (0.7)."""
    return PlannerService()

def test_is_confidence_below_threshold_default(default_planner):
    """
    Tests the is_confidence_below_threshold method with the default threshold.
    """
    assert default_planner.is_confidence_below_threshold(0.6) is True
    assert default_planner.is_confidence_below_threshold(0.69) is True
    assert default_planner.is_confidence_below_threshold(0.7) is False
    assert default_planner.is_confidence_below_threshold(0.71) is False
    assert default_planner.is_confidence_below_threshold(0.9) is False
    assert default_planner.is_confidence_below_threshold(1.0) is False
    assert default_planner.is_confidence_below_threshold(0.0) is True

def test_is_confidence_below_threshold_custom():
    """
    Tests the is_confidence_below_threshold method with a custom threshold.
    """
    custom_planner = PlannerService(confidence_threshold=0.8)
    assert custom_planner.is_confidence_below_threshold(0.7) is True
    assert custom_planner.is_confidence_below_threshold(0.79) is True
    assert custom_planner.is_confidence_below_threshold(0.8) is False
    assert custom_planner.is_confidence_below_threshold(0.81) is False

@pytest.mark.parametrize("user_input, inferred_context, intent_confidence, state_confidence, expected_action, expected_content_substring", PLANNER_TEST_CASES)
def test_plan_next_step_default_threshold(default_planner, user_input, inferred_context, intent_confidence, state_confidence, expected_action, expected_content_substring):
    """
    Tests the plan_next_step method with the default confidence threshold,
    including checking the content for uncertainty handling.
    """
    plan = default_planner.plan_next_step(user_input, inferred_context, intent_confidence, state_confidence)
    assert plan["action"] == expected_action
    assert expected_content_substring in plan["content"]

def test_plan_next_step_custom_threshold():
    """
    Tests the plan_next_step method with a custom confidence threshold.
    """
    custom_planner = PlannerService(confidence_threshold=0.9)
    user_input = "Custom low confidence"
    inferred_context = {"key_term": "custom low", "topic": "testing"}

    # With a 0.9 threshold, this should now be "uncertainty_handling"
    plan = custom_planner.plan_next_step(user_input, inferred_context, intent_confidence=0.85, state_confidence=0.95)
    assert plan["action"] == "uncertainty_handling"
    assert inferred_context["key_term"] in plan["content"]

    # With a 0.9 threshold, this should still be "direct_response"
    plan = custom_planner.plan_next_step(user_input, inferred_context, intent_confidence=0.91, state_confidence=0.92)
    assert plan["action"] == "direct_response"
    assert "Proceeding with direct response." in plan["content"]
