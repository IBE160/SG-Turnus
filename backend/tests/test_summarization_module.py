import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.summarization_module import SummarizationModule
import os

# Mock the ChatOpenAI to prevent actual API calls during testing
@pytest.fixture
def mock_openai_chat_completion():
    with patch('backend.app.core.ai.summarization_module.ChatOpenAI') as mock_chat_openai_class:
        mock_llm_instance = MagicMock()
        mock_chat_openai_class.return_value = mock_llm_instance
        yield mock_llm_instance

@pytest.fixture(autouse=True)
def set_openai_api_key_env():
    """Ensure OPENAI_API_KEY is set for tests that require it."""
    original_api_key = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "sk-test-key"  # Set a dummy key
    yield
    if original_api_key:
        os.environ["OPENAI_API_KEY"] = original_api_key
    else:
        del os.environ["OPENAI_API_KEY"]

def test_summarization_module_initialization():
    """Test that the summarization module initializes correctly."""
    summarizer = SummarizationModule()
    assert summarizer.llm is not None
    assert summarizer.output_parser is not None
    assert summarizer.summary_prompt_template is not None
    assert summarizer.brief_summary_prompt_template is not None

def test_generate_normal_summary(mock_openai_chat_completion):
    """Test generating a normal summary."""
    summarizer = SummarizationModule()
    mock_openai_chat_completion.invoke.return_value = "This is a normal summary."

    text = "A very long text that needs to be summarized."
    summary = summarizer.generate_summary(text, detail_level="normal")

    assert summary == "This is a normal summary."
    mock_openai_chat_completion.invoke.assert_called_once()
    # You could add assertions here to check the prompt used,
    # but that might be overly coupled to LangChain internals.
    # A simpler check is that invoke was called.

def test_generate_brief_summary(mock_openai_chat_completion):
    """Test generating a brief summary."""
    summarizer = SummarizationModule()
    mock_openai_chat_completion.invoke.return_value = "Brief summary."

    text = "A very long text that needs to be summarized briefly."
    summary = summarizer.generate_summary(text, detail_level="brief")

    assert summary == "Brief summary."
    mock_openai_chat_completion.invoke.assert_called_once()
    # Check that it was called with the brief prompt

def test_generate_summary_missing_api_key():
    """Test error handling when OPENAI_API_KEY is not set."""
    # Temporarily remove API key for this specific test
    original_api_key = os.environ.pop("OPENAI_API_KEY", None)
    
    summarizer = SummarizationModule()
    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set."):
        summarizer.generate_summary("some text")

    # Restore API key
    if original_api_key:
        os.environ["OPENAI_API_KEY"] = original_api_key
