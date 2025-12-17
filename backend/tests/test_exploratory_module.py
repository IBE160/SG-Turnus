# backend/tests/test_exploratory_module.py

import pytest
from unittest.mock import MagicMock
from backend.app.core.ai.exploratory_module import ExploratoryModule
from langchain_core.messages import AIMessage


def test_generate_phrasing_with_context(exploratory_module, mock_llm_exploratory_response):
    """
    Tests that generate_phrasing calls the LLM with the correct prompt
    and returns the LLM's response when context is provided.
    """
    user_input = "I'm interested in this topic."
    context = {"key_term": "this topic", "topic": "general knowledge"}
    
    expected_mock_response = mock_llm_exploratory_response.format(key_term=context["key_term"], topic=context["topic"])
    
    phrasing = exploratory_module.generate_phrasing(user_input, context)

    assert isinstance(phrasing, str)
    assert phrasing == expected_mock_response
    # Verify that the LLM's invoke method was called
    exploratory_module.llm.invoke.assert_called_once()
    # You can further assert on the call arguments if needed
    call_args = exploratory_module.llm.invoke.call_args[0][0]
    assert call_args["user_input"] == user_input
    assert call_args["key_term"] == context["key_term"]
    assert call_args["topic"] == context["topic"]

def test_generate_phrasing_missing_key_term(exploratory_module):
    """
    Tests the fallback behavior when 'key_term' is missing from the context.
    """
    user_input = "Tell me more about it."
    context = {"topic": "Science"}
    phrasing = exploratory_module.generate_phrasing(user_input, context)
    assert phrasing == "It seems I need a bit more information. Could you clarify what you're looking for?"
    # Ensure LLM was NOT called for fallback scenario
    exploratory_module.llm.invoke.assert_not_called()

def test_generate_phrasing_missing_topic(exploratory_module):
    """
    Tests the fallback behavior when 'topic' is missing from the context.
    """
    user_input = "What is this thing?"
    context = {"key_term": "this thing"}
    phrasing = exploratory_module.generate_phrasing(user_input, context)
    assert phrasing == "It seems I need a bit more information. Could you clarify what you're looking for?"
    # Ensure LLM was NOT called for fallback scenario
    exploratory_module.llm.invoke.assert_not_called()

def test_generate_phrasing_empty_context(exploratory_module):
    """
    Tests the fallback behavior when the context dictionary is empty.
    """
    user_input = "Explain."
    context = {}
    phrasing = exploratory_module.generate_phrasing(user_input, context)
    assert phrasing == "It seems I need a bit more information. Could you clarify what you're looking for?"
    # Ensure LLM was NOT called for fallback scenario
    exploratory_module.llm.invoke.assert_not_called()