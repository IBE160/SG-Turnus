import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.planner_service import PlannerService
from backend.app.core.ai.uncertainty_resolution_module import UncertaintyResolutionModule
from backend.app.core.ai.exploratory_module import ExploratoryModule
from backend.app.core.ai.micro_explanation_module import MicroExplanationModule
import random

@pytest.fixture(autouse=True)
def mock_chat_openai_per_module(mocker):
    """
    Mocks ChatOpenAI within calibration_module, exploratory_module and micro_explanation_module
    to prevent API key validation during tests.
    """
    mocker.patch('backend.app.core.ai.uncertainty_resolution_module.ChatOpenAI', autospec=True)
    mocker.patch('backend.app.core.ai.exploratory_module.ChatOpenAI', autospec=True)
    mocker.patch('backend.app.core.ai.micro_explanation_module.ChatOpenAI', autospec=True)


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

@pytest.mark.parametrize("user_input, inferred_context, intent_confidence, state_confidence, expected_action, expected_content_substring, expected_uncertainty_type", [
    ("User query", {"key_term": "test", "topic": "tests"}, 0.9, 0.85, "direct_response", "Proceeding with direct response.", None),   # High confidence for both
    ("User query", {"key_term": "test", "topic": "tests"}, 0.7, 0.8, "direct_response", "Proceeding with direct response.", None),    # Intent at threshold, state high
    ("User query", {"key_term": "test", "topic": "tests"}, 0.8, 0.7, "direct_response", "Proceeding with direct response.", None),    # State at threshold, intent high
    ("Low intent query", {"key_term": "low intent", "topic": "AI"}, 0.69, 0.8, "uncertainty_handling", "low intent", "calibration_question"), # Intent just below threshold, test calibration
    ("Low intent query", {"key_term": "low intent", "topic": "AI"}, 0.69, 0.8, "uncertainty_handling", "low intent", "exploratory_phrasing"), # Intent just below threshold, test exploratory
    ("Low intent query", {"key_term": "low intent", "topic": "AI"}, 0.69, 0.8, "uncertainty_handling", "low intent", "micro_explanation"), # Intent just below threshold, test micro-explanation
    ("Low state query", {"key_term": "low state", "topic": "AI"}, 0.8, 0.69, "uncertainty_handling", "low state", "calibration_question"), # State just below threshold, test calibration
    ("Low state query", {"key_term": "low state", "topic": "AI"}, 0.8, 0.69, "uncertainty_handling", "low state", "exploratory_phrasing"), # State just below threshold, test exploratory
    ("Low state query", {"key_term": "low state", "topic": "AI"}, 0.8, 0.69, "uncertainty_handling", "low state", "micro_explanation"), # State just below threshold, test micro-explanation
    ("Very low intent query", {"key_term": "very low", "topic": "AI"}, 0.5, 0.9, "uncertainty_handling", "very low", "calibration_question"), # Low intent confidence, test calibration
    ("Very low intent query", {"key_term": "very low", "topic": "AI"}, 0.5, 0.9, "uncertainty_handling", "very low", "exploratory_phrasing"), # Low intent confidence, test exploratory
    ("Very low intent query", {"key_term": "very low", "topic": "AI"}, 0.5, 0.9, "uncertainty_handling", "very low", "micro_explanation"), # Low intent confidence, test micro-explanation
    ("Very low state query", {"key_term": "another low", "topic": "AI"}, 0.9, 0.4, "uncertainty_handling", "another low", "calibration_question"), # Low state confidence, test calibration
    ("Very low state query", {"key_term": "another low", "topic": "AI"}, 0.9, 0.4, "uncertainty_handling", "another low", "exploratory_phrasing"), # Low state confidence, test exploratory
    ("Very low state query", {"key_term": "another low", "topic": "AI"}, 0.9, 0.4, "uncertainty_handling", "another low", "micro_explanation"), # Low state confidence, test micro-explanation
    ("Both low query", {"key_term": "both low", "topic": "AI"}, 0.2, 0.3, "uncertainty_handling", "both low", "calibration_question"), # Low confidence for both, test calibration
    ("Both low query", {"key_term": "both low", "topic": "AI"}, 0.2, 0.3, "uncertainty_handling", "both low", "exploratory_phrasing"), # Low confidence for both, test exploratory
    ("Both low query", {"key_term": "both low", "topic": "AI"}, 0.2, 0.3, "uncertainty_handling", "both low", "micro_explanation"), # Low confidence for both, test micro-explanation
])
def test_plan_next_step_default_threshold(default_planner, user_input, inferred_context, intent_confidence, state_confidence, expected_action, expected_content_substring, expected_uncertainty_type, mocker):
    """
    Tests the plan_next_step method with the default confidence threshold,
    including checking the content for uncertainty handling.
    """
    if expected_action == "uncertainty_handling":
        mock_cal_gen_q = mocker.patch('backend.app.core.ai.uncertainty_resolution_module.UncertaintyResolutionModule.return_value.generate_question')
        mock_cal_gen_q.return_value = "Mocked calibration: " + expected_content_substring

        mock_exp_gen_p = mocker.patch('backend.app.core.ai.exploratory_module.ExploratoryModule.return_value.generate_phrasing')
        mock_exp_gen_p.return_value = "Mocked exploratory: " + expected_content_substring

        mock_micro_exp_gen_me = mocker.patch('backend.app.core.ai.micro_explanation_module.MicroExplanationModule.return_value.generate_micro_explanation')
        mock_micro_exp_gen_me.return_value = "Mocked micro-explanation: " + expected_content_substring
        
        # Patch random.choice to always return the expected_uncertainty_type
        mocker.patch('random.choice', return_value=expected_uncertainty_type)

    plan = default_planner.plan_next_step(user_input, inferred_context, intent_confidence, state_confidence)
    assert plan["action"] == expected_action
    if expected_action == "direct_response":
        assert expected_content_substring in plan["content"]
    else: # uncertainty_handling
        assert isinstance(plan["content"], dict)
        assert "type" in plan["content"]
        if plan["content"]["type"] == "calibration_question":
            assert "question" in plan["content"]
            assert expected_content_substring in plan["content"]["question"]
        elif plan["content"]["type"] == "exploratory_phrasing":
            assert "phrasing" in plan["content"]
            assert expected_content_substring in plan["content"]["phrasing"]
        elif plan["content"]["type"] == "micro_explanation":
            assert "explanation" in plan["content"]
            assert expected_content_substring in plan["content"]["explanation"]


@pytest.mark.parametrize("intent_confidence, state_confidence, expected_action, expected_uncertainty_type", [
    (0.85, 0.95, "uncertainty_handling", "calibration_question"), # Below threshold (0.9), test calibration
    (0.85, 0.95, "uncertainty_handling", "exploratory_phrasing"), # Below threshold (0.9), test exploratory
    (0.85, 0.95, "uncertainty_handling", "micro_explanation"), # Below threshold (0.9), test micro-explanation
    (0.91, 0.92, "direct_response", None) # Above threshold (0.9)
])
def test_plan_next_step_custom_threshold(intent_confidence, state_confidence, expected_action, expected_uncertainty_type, mocker):
    """
    Tests the plan_next_step method with a custom confidence threshold,
    including checking the content for uncertainty handling.
    """
    custom_planner = PlannerService(confidence_threshold=0.9)
    user_input = "Custom low confidence"
    inferred_context = {"key_term": "custom low", "topic": "testing"}

    if expected_action == "uncertainty_handling":
        mock_cal_gen_q = mocker.patch('backend.app.core.ai.uncertainty_resolution_module.UncertaintyResolutionModule.return_value.generate_question')
        mock_cal_gen_q.return_value = "Mocked calibration: custom low"

        mock_exp_gen_p = mocker.patch('backend.app.core.ai.exploratory_module.ExploratoryModule.return_value.generate_phrasing')
        mock_exp_gen_p.return_value = "Mocked exploratory: custom low"

        mock_micro_exp_gen_me = mocker.patch('backend.app.core.ai.micro_explanation_module.MicroExplanationModule.return_value.generate_micro_explanation')
        mock_micro_exp_gen_me.return_value = "Mocked micro-explanation: custom low"
        
        # Patch random.choice to always return the expected_uncertainty_type
        mocker.patch('random.choice', return_value=expected_uncertainty_type)

    plan = custom_planner.plan_next_step(user_input, inferred_context, intent_confidence, state_confidence)
    assert plan["action"] == expected_action
    if expected_action == "direct_response":
        assert "Proceeding with direct response." in plan["content"]
    else: # uncertainty_handling
        assert isinstance(plan["content"], dict)
        assert "type" in plan["content"]
        if plan["content"]["type"] == "calibration_question":
            assert "question" in plan["content"]
            assert inferred_context["key_term"] in plan["content"]["question"]
        elif plan["content"]["type"] == "exploratory_phrasing":
            assert "phrasing" in plan["content"]
            assert inferred_context["key_term"] in plan["content"]["phrasing"]
        elif plan["content"]["type"] == "micro_explanation":
            assert "explanation" in plan["content"]
            assert inferred_context["key_term"] in plan["content"]["explanation"]

def test_plan_next_step_uncertainty_handling_selection(mocker):
    """
    Tests that when confidence is low, PlannerService correctly selects
    between calibration questions and exploratory phrasing.
    """
    # Mock CalibrationModule, ExploratoryModule, and MicroExplanationModule to return predictable responses
    mock_calibration_module = mocker.patch('backend.app.core.ai.uncertainty_resolution_module.UncertaintyResolutionModule')
    mock_calibration_module.return_value.generate_question.return_value = "Mocked calibration question."

    mock_exploratory_module = mocker.patch('backend.app.core.ai.exploratory_module.ExploratoryModule')
    mock_exploratory_module.return_value.generate_phrasing.return_value = "Mocked exploratory phrasing."

    mock_micro_explanation_module = mocker.patch('backend.app.core.ai.micro_explanation_module.MicroExplanationModule')
    mock_micro_explanation_module.return_value.generate_micro_explanation.return_value = "Mocked micro-explanation."

    planner = PlannerService()
    user_input = "Uncertain query"
    inferred_context = {"key_term": "uncertain", "topic": "unknown"}

    # Scenario 1: Mock random.choice to select calibration question
    mocker.patch('random.choice', return_value="calibration_question")
    plan_calibration = planner.plan_next_step(user_input, inferred_context, intent_confidence=0.5, state_confidence=0.6)
    assert plan_calibration["action"] == "uncertainty_handling"
    assert isinstance(plan_calibration["content"], dict)
    assert plan_calibration["content"]["type"] == "calibration_question"
    assert plan_calibration["content"]["question"] == "Mocked calibration question."
    mock_calibration_module.return_value.generate_question.assert_called_once_with(user_input, inferred_context)
    mock_exploratory_module.return_value.generate_phrasing.assert_not_called()
    mock_micro_explanation_module.return_value.generate_micro_explanation.assert_not_called()
    mock_calibration_module.return_value.generate_question.reset_mock() # Reset for next scenario
    mock_exploratory_module.return_value.generate_phrasing.reset_mock() # Reset for next scenario
    mock_micro_explanation_module.return_value.generate_micro_explanation.reset_mock() # Reset for next scenario


    # Scenario 2: Mock random.choice to select exploratory phrasing
    mocker.patch('random.choice', return_value="exploratory_phrasing")
    plan_exploratory = planner.plan_next_step(user_input, inferred_context, intent_confidence=0.5, state_confidence=0.6)
    assert plan_exploratory["action"] == "uncertainty_handling"
    assert isinstance(plan_exploratory["content"], dict)
    assert plan_exploratory["content"]["type"] == "exploratory_phrasing"
    assert plan_exploratory["content"]["phrasing"] == "Mocked exploratory phrasing."
    mock_exploratory_module.return_value.generate_phrasing.assert_called_once_with(user_input, inferred_context)
    mock_calibration_module.return_value.generate_question.assert_not_called()
    mock_micro_explanation_module.return_value.generate_micro_explanation.assert_not_called()
    mock_calibration_module.return_value.generate_question.reset_mock() # Reset for next scenario
    mock_exploratory_module.return_value.generate_phrasing.reset_mock() # Reset for next scenario
    mock_micro_explanation_module.return_value.generate_micro_explanation.reset_mock() # Reset for next scenario


    # Scenario 3: Mock random.choice to select micro-explanation
    mocker.patch('random.choice', return_value="micro_explanation")
    plan_micro_explanation = planner.plan_next_step(user_input, inferred_context, intent_confidence=0.5, state_confidence=0.6)
    assert plan_micro_explanation["action"] == "uncertainty_handling"
    assert isinstance(plan_micro_explanation["content"], dict)
    assert plan_micro_explanation["content"]["type"] == "micro_explanation"
    assert plan_micro_explanation["content"]["explanation"] == "Mocked micro-explanation."
    mock_micro_explanation_module.return_value.generate_micro_explanation.assert_called_once_with(user_input, inferred_context)
    mock_calibration_module.return_value.generate_question.assert_not_called()
    mock_exploratory_module.return_value.generate_phrasing.assert_not_called()

