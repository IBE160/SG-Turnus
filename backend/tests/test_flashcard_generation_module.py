import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.flashcard_generation_module import FlashcardGenerationModule, Flashcard
import os
import json

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

def test_flashcard_generation_module_initialization():
    """Test that the flashcard generation module initializes correctly."""
    flashcard_generator = FlashcardGenerationModule()
    assert flashcard_generator.llm is None
    assert flashcard_generator.output_parser is not None
    assert flashcard_generator.flashcard_prompt_template is not None

def test_generate_flashcards(mock_chain_invoke):
    """Test generating flashcards."""
    mock_chain_invoke.return_value = [
        {"question": "What is the capital of France?", "answer": "Paris"},
        {"question": "What is 2 + 2?", "answer": "4"}
    ]
    flashcard_generator = FlashcardGenerationModule()
    
    text = "Some text to generate flashcards from."
    flashcards = flashcard_generator.generate_flashcards(text)

    assert len(flashcards) == 2
    assert isinstance(flashcards[0], Flashcard)
    assert flashcards[0].question == "What is the capital of France?"
    assert flashcards[0].answer == "Paris"
    assert flashcards[1].question == "What is 2 + 2?"
    assert flashcards[1].answer == "4"
    
    mock_chain_invoke.assert_called_once_with({"text": text})

def test_generate_flashcards_with_string_output(mock_chain_invoke):
    """Test generating flashcards when the LLM returns a JSON string."""
    
    mock_chain_result_str = json.dumps([
        {"question": "What is the capital of Spain?", "answer": "Madrid"}
    ])
    mock_chain_invoke.return_value = mock_chain_result_str

    flashcard_generator = FlashcardGenerationModule()
    
    text = "Another text."
    flashcards = flashcard_generator.generate_flashcards(text)

    assert len(flashcards) == 1
    assert isinstance(flashcards[0], Flashcard)
    assert flashcards[0].question == "What is the capital of Spain?"
    assert flashcards[0].answer == "Madrid"

def test_generate_flashcards_invalid_json_string(mock_chain_invoke):
    """Test handling of invalid JSON string from LLM."""
    mock_chain_invoke.return_value = "This is not valid JSON"

    flashcard_generator = FlashcardGenerationModule()
    flashcards = flashcard_generator.generate_flashcards("some text")

    assert flashcards == []

def test_generate_flashcards_missing_api_key():
    """Test error handling when OPENAI_API_KEY is not set."""
    original_api_key = os.environ.pop("OPENAI_API_KEY", None)
    
    flashcard_generator = FlashcardGenerationModule()
    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set."):
        flashcard_generator.generate_flashcards("some text")

    if original_api_key:
        os.environ["OPENAI_API_KEY"] = original_api_key