import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.summarization_module import SummarizationModule
import os

@pytest.fixture
def mock_chain_invoke():
    with patch('langchain_core.runnables.base.RunnableSequence.invoke') as mock_invoke:
        yield mock_invoke

@pytest.fixture(autouse=True)
def set_openai_api_key_env():
    """Ensure OPENAI_API_KEY is set for tests that require it."""
    original_api_key = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    yield
    if original_api_key:
        os.environ["OPENAI_API_KEY"] = original_api_key
    else:
        del os.environ["OPENAI_API_KEY"]

def test_summarization_module_initialization():
    """Test that the summarization module initializes correctly."""
    summarizer = SummarizationModule()
    assert summarizer.llm is None
    assert summarizer.output_parser is not None
    assert summarizer.summary_prompt_template is not None
    assert summarizer.brief_summary_prompt_template is not None

def test_generate_normal_summary(mock_chain_invoke):
    """Test generating a normal summary."""
    summarizer = SummarizationModule()
    mock_chain_invoke.return_value = "This is a normal summary."

    text = "A very long text that needs to be summarized."
    summary = summarizer.generate_summary(text, detail_level="normal")

    assert summary == "This is a normal summary."
    mock_chain_invoke.assert_called_once_with({"text": text})

def test_generate_brief_summary(mock_chain_invoke):
    """Test generating a brief summary."""
    summarizer = SummarizationModule()
    mock_chain_invoke.return_value = "Brief summary."

    text = "A very long text that needs to be summarized briefly."
    summary = summarizer.generate_summary(text, detail_level="brief")

    assert summary == "Brief summary."
    mock_chain_invoke.assert_called_once_with({"text": text})

def test_generate_summary_missing_api_key():
    """Test error handling when OPENAI_API_KEY is not set."""
    original_api_key = os.environ.pop("OPENAI_API_KEY", None)
    
    summarizer = SummarizationModule()
    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set."):
        summarizer.generate_summary("some text")

    if original_api_key:
        os.environ["OPENAI_API_KEY"] = original_api_key
