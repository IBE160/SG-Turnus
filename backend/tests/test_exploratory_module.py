import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.exploratory_module import ExploratoryModule
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

@pytest.fixture
def exploratory_module_instance(mocker):
    """Returns an ExploratoryModule instance with ChatOpenAI mocked, and the mock LLM."""
    # We mock ChatOpenAI at the class level to avoid API key validation during instantiation
    with patch('backend.app.core.ai.exploratory_module.ChatOpenAI') as mock_chat_openai_class:
        mock_llm_instance = MagicMock()
        mock_chat_openai_class.return_value = mock_llm_instance
        module = ExploratoryModule()
        return module, mock_llm_instance


def test_generate_phrasing_with_valid_context(exploratory_module_instance):
    """
    Tests that an exploratory phrasing is generated with valid context by mocking
    the LLM's invoke method directly.
    """
    module, mock_llm_instance = exploratory_module_instance
    user_input = "Help me understand difficult concepts."
    inferred_context = {"key_term": "difficult concepts", "topic": "learning strategies"}
    
    # Mock the LLM's invoke method to return a specific AIMessage content
    mock_llm_instance.invoke.return_value = AIMessage(content="Mocked exploratory phrasing: Perhaps you're looking for strategies to tackle 'difficult concepts' in 'learning strategies'?")

    phrasing = module.generate_phrasing(user_input, inferred_context)
    
    assert phrasing == "Mocked exploratory phrasing: Perhaps you're looking for strategies to tackle 'difficult concepts' in 'learning strategies'?"
    mock_llm_instance.invoke.assert_called_once()
    # Verify that the prompt was called with the correct arguments
    call_args = mock_llm_instance.invoke.call_args[0][0]
    assert call_args["user_input"] == user_input
    assert call_args["key_term"] == inferred_context["key_term"]
    assert call_args["topic"] == inferred_context["topic"]

def test_generate_phrasing_with_missing_key_term(exploratory_module_instance):
    module, _ = exploratory_module_instance
    """Tests fallback behavior when key_term is missing from context."""
    user_input = "Explain this concept."
    inferred_context = {"topic": "understanding"}
    
    phrasing = module.generate_phrasing(user_input, inferred_context)
    
    assert phrasing == "It seems I need a bit more information. Could you clarify what you're looking for?"

def test_generate_phrasing_with_missing_topic(exploratory_module_instance):
    module, _ = exploratory_module_instance
    """Tests fallback behavior when topic is missing from context."""
    user_input = "Explain this concept."
    inferred_context = {"key_term": "concept"}
    
    phrasing = module.generate_phrasing(user_input, inferred_context)
    
    assert phrasing == "It seems I need a bit more information. Could you clarify what you're looking for?"

def test_generate_phrasing_with_empty_context(exploratory_module_instance):
    module, _ = exploratory_module_instance
    """Tests fallback behavior with empty context."""
    user_input = "What is it?"
    inferred_context = {}
    
    phrasing = module.generate_phrasing(user_input, inferred_context)
    
    assert phrasing == "It seems I need a bit more information. Could you clarify what you're looking for?"
