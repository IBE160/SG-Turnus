import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.uncertainty_resolution_module import UncertaintyResolutionModule
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate

@pytest.fixture
def uncertainty_resolution_module_instance():
    """Returns an UncertaintyResolutionModule instance with ChatOpenAI mocked, and the mock LLM."""
    with patch('backend.app.core.ai.uncertainty_resolution_module.ChatOpenAI') as mock_chat_openai_class:
        mock_llm_instance = MagicMock()
        mock_chat_openai_class.return_value = mock_llm_instance
        module = UncertaintyResolutionModule()
        return module, mock_llm_instance


def test_calibration_module_init(uncertainty_resolution_module_instance):
    """Tests that the UncertaintyResolutionModule can be initialized."""
    module, _ = uncertainty_resolution_module_instance
    assert module is not None
    assert hasattr(module, 'llm')
    assert hasattr(module, 'prompt')
    assert isinstance(module.prompt, ChatPromptTemplate)

def test_generate_question_with_valid_context(uncertainty_resolution_module_instance):
    """
    Tests that a calibration question is generated with valid context by mocking
    the LLM's invoke method directly.
    """
    module, mock_llm_instance = uncertainty_resolution_module_instance
    user_input = "Explain this concept."
    inferred_context = {"key_term": "concept", "topic": "understanding"}
    
    mock_llm_instance.invoke.return_value = AIMessage(content="Mocked calibration question: What do you mean by 'concept' in 'understanding'?")

    question = module.generate_question(user_input, inferred_context)
    
    assert question == "Mocked calibration question: What do you mean by 'concept' in 'understanding'?"
    mock_llm_instance.invoke.assert_called_once()
    # Verify that the prompt was called with the correct arguments
    call_args = mock_llm_instance.invoke.call_args[0][0]
    assert call_args["user_input"] == user_input
    assert call_args["key_term"] == inferred_context["key_term"]
    assert call_args["topic"] == inferred_context["topic"]
def test_generate_question_with_missing_key_term(uncertainty_resolution_module_instance):
    module, _ = uncertainty_resolution_module_instance
    """Tests fallback behavior when key_term is missing from context."""
    user_input = "Explain this concept."
    inferred_context = {"topic": "understanding"}
    
    question = module.generate_question(user_input, inferred_context)
    
    assert question == "Could you please provide more context or clarify your question?"

def test_generate_question_with_missing_topic(uncertainty_resolution_module_instance):
    module, _ = uncertainty_resolution_module_instance
    """Tests fallback behavior when topic is missing from context."""
    user_input = "Explain this concept."
    inferred_context = {"key_term": "concept"}
    
    question = module.generate_question(user_input, inferred_context)
    
    assert question == "Could you please provide more context or clarify your question?"

def test_generate_question_with_empty_context(uncertainty_resolution_module_instance):
    module, _ = uncertainty_resolution_module_instance
    """Tests fallback behavior with empty context."""
    user_input = "What is it?"
    inferred_context = {}
    
    question = module.generate_question(user_input, inferred_context)
    
    assert question == "Could you please provide more context or clarify your question?"
