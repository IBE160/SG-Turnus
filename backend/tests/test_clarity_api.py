import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from backend.main import app
from backend.app.services.nlp_service import Intent, UserState
from backend.app.api.schemas import NextStep, ClarityResponse

# It's generally better to have a test client fixture for each test module
# to ensure isolation. Replicating essential parts from test_main.py.

# ----------------------------------------------------
# Test Client Setup
# ----------------------------------------------------

@pytest.fixture(scope="module")
def test_client():
    """Provides a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client

# ----------------------------------------------------
# Mocks for Services
# ----------------------------------------------------

@pytest.fixture(autouse=True)
def mock_services():
    """
    Mocks NLPService and ClarityService instances.
    """
    with patch('backend.app.api.v1.clarity.nlp_service') as mock_nlp_service, \
         patch('backend.app.api.v1.clarity.clarity_service') as mock_clarity_service:
        yield mock_nlp_service, mock_clarity_service

# ----------------------------------------------------
# Test Functions for Clarity API
# ----------------------------------------------------

def test_get_next_step_success(test_client: TestClient, mock_services):
    """
    Test the /api/v1/next-step endpoint for successful next step selection.
    """
    mock_nlp_service, mock_clarity_service = mock_services

    # Configure mock NLP service to return specific signals
    mock_nlp_service.process_text.return_value = {
        "detected_intent": Intent.CLARIFICATION.value,
        "intent_confidence": 0.85,
        "inferred_user_state": UserState.CONFUSED.value,
        "user_state_confidence": 0.7,
        "original_text": "What does this mean?",
        "tokens": ["What", "does", "this", "mean", "?"],
        "lemmas": ["what", "do", "this", "mean", "?"],
        "pos_tags": ["PRON", "AUX", "DET", "VERB", "PUNCT"],
        "found_question_words": ["what"],
        "sentences": ["What does this mean?"],
        "num_sentences": 1,
        "num_paragraphs": 1,
        "num_alphanumeric_tokens": 4,
        "unique_words": 4,
        "average_word_length": 4.0,
        "average_sentence_length": 4.0,
        "named_entities": []
    }

    # Configure mock Clarity service to return a specific next step
    expected_next_step = NextStep.PROVIDE_MICRO_EXPLANATION
    expected_explanation = "High confidence in clarification intent and user confusion."
    mock_clarity_service.select_next_step.return_value = (expected_next_step, expected_explanation)

    request_payload = {"text": "What does this mean?"}
    response = test_client.post("/api/v1/next-step", json=request_payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["next_step"] == expected_next_step.value
    assert response_data["explanation"] == expected_explanation

    # Verify that NLPService and ClarityService methods were called with correct arguments
    mock_nlp_service.process_text.assert_called_once_with(request_payload["text"])
    mock_clarity_service.select_next_step.assert_called_once_with(
        detected_intent=Intent.CLARIFICATION,
        intent_confidence=0.85,
        inferred_user_state=UserState.CONFUSED,
        user_state_confidence=0.7
    )

def test_get_next_step_unknown_intent_fallback(test_client: TestClient, mock_services):
    """
    Test the /api/v1/next-step endpoint for an unknown intent leading to a fallback next step.
    """
    mock_nlp_service, mock_clarity_service = mock_services

    # Configure mock NLP service for an unknown intent
    mock_nlp_service.process_text.return_value = {
        "detected_intent": Intent.UNKNOWN.value,
        "intent_confidence": 0.1,
        "inferred_user_state": UserState.NEUTRAL.value,
        "user_state_confidence": 0.1,
        "original_text": "Some random text.",
        "tokens": ["Some", "random", "text", "?"],
        "lemmas": ["some", "random", "text", "?"],
        "pos_tags": ["DET", "ADJ", "NOUN", "PUNCT"],
        "found_question_words": [],
        "sentences": ["Some random text."],
        "num_sentences": 1,
        "num_paragraphs": 1,
        "num_alphanumeric_tokens": 3,
        "unique_words": 3,
        "average_word_length": 4.0,
        "average_sentence_length": 3.0,
        "named_entities": []
    }

    # Configure mock Clarity service to return a specific next step for fallback
    expected_next_step = NextStep.ASK_OPEN_ENDED_QUESTION
    expected_explanation = "Low confidence in intent detection, asking for more context."
    mock_clarity_service.select_next_step.return_value = (expected_next_step, expected_explanation)

    request_payload = {"text": "Some random text."}
    response = test_client.post("/api/v1/next-step", json=request_payload)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["next_step"] == expected_next_step.value
    assert response_data["explanation"] == expected_explanation

    mock_nlp_service.process_text.assert_called_once_with(request_payload["text"])
    mock_clarity_service.select_next_step.assert_called_once_with(
        detected_intent=Intent.UNKNOWN,
        intent_confidence=0.1,
        inferred_user_state=UserState.NEUTRAL,
        user_state_confidence=0.1
    )

def test_get_next_step_invalid_input(test_client: TestClient):
    """
    Test the /api/v1/next-step endpoint with invalid input (e.g., missing 'text' field).
    """
    request_payload = {"invalid_field": "some value"} # Missing 'text' field
    response = test_client.post("/api/v1/next-step", json=request_payload)

    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation error
    assert "field required" in response.json()["detail"][0]["msg"]
