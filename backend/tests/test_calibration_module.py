# backend/tests/test_calibration_module.py

import pytest
from unittest.mock import MagicMock
from backend.app.core.ai.calibration_module import CalibrationModule
from langchain_core.messages import AIMessage


def test_generate_question_with_context(calibration_module, mock_llm_response):
    """
    Tests that generate_question calls the LLM with the correct prompt
    and returns the LLM's response when context is provided.
    """
    user_input = "What about the kernel?"
    context = {"key_term": "kernel", "topic": "Operating Systems"}
    
    expected_mock_response = mock_llm_response.format(key_term=context["key_term"], topic=context["topic"])
    
    question = calibration_module.generate_question(user_input, context)

    assert isinstance(question, str)
    assert question == expected_mock_response
    # Verify that the LLM's invoke method was called
    calibration_module.llm.invoke.assert_called_once()
    # You can further assert on the call arguments if needed
    call_args = calibration_module.llm.invoke.call_args[0][0]
    assert call_args["user_input"] == user_input
    assert call_args["key_term"] == context["key_term"]
    assert call_args["topic"] == context["topic"]

def test_generate_question_missing_key_term(calibration_module):
    """
    Tests the fallback behavior when 'key_term' is missing from the context.
    """
    user_input = "Tell me more."
    context = {"topic": "Computer Science"}
    question = calibration_module.generate_question(user_input, context)
    assert question == "Could you please provide more context or clarify your question?"
    # Ensure LLM was NOT called for fallback scenario
    calibration_module.llm.invoke.assert_not_called()

def test_generate_question_missing_topic(calibration_module):
    """
    Tests the fallback behavior when 'topic' is missing from the context.
    """
    user_input = "What is a mutex?"
    context = {"key_term": "mutex"}
    question = calibration_module.generate_question(user_input, context)
    assert question == "Could you please provide more context or clarify your question?"
    # Ensure LLM was NOT called for fallback scenario
    calibration_module.llm.invoke.assert_not_called()

def test_generate_question_empty_context(calibration_module):
    """
    Tests the fallback behavior when the context dictionary is empty.
    """
    user_input = "Explain."
    context = {}
    question = calibration_module.generate_question(user_input, context)
    assert question == "Could you please provide more context or clarify your question?"
    # Ensure LLM was NOT called for fallback scenario
    calibration_module.llm.invoke.assert_not_called()