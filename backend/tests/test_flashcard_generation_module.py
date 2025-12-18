import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.flashcard_generation_module import FlashcardGenerationModule, Flashcard
import os

# Mock the ChatOpenAI to prevent actual API calls during testing
@pytest.fixture
def mock_openai_chat_completion():
    with patch('backend.app.core.ai.flashcard_generation_module.ChatOpenAI') as mock_chat_openai_class:
        mock_llm_instance = MagicMock()
        mock_chat_openai_class.return_value = mock_llm_instance
        yield mock_llm_instance

@pytest.fixture(autouse=True)
def set_openai_api_key_env():
    """Ensure OPENAI_API_KEY is set for tests that require it."""
    original_api_key = os.environ.get("OPENAI_API_KEY")
    os.environ["OPENAI_API_KEY"] = "sk-test-key-flashcard"  # Set a dummy key
    yield
    if original_api_key:
        os.environ["OPENAI_API_KEY"] = original_api_key
    else:
        del os.environ["OPENAI_API_KEY"]

def test_flashcard_generation_module_initialization():
    """Test that the flashcard generation module initializes correctly."""
    generator = FlashcardGenerationModule()
    assert generator.llm is not None
    assert generator.output_parser is not None
    assert generator.flashcard_prompt is not None

def test_generate_flashcards_success(mock_openai_chat_completion):
    """Test successful flashcard generation."""
    generator = FlashcardGenerationModule()
    
    mock_flashcards_data = [
        {"question": "What is Photosynthesis?", "answer": "Process by which plants convert light energy into chemical energy."},
        {"question": "What is Chlorophyll?", "answer": "A green pigment essential for photosynthesis."}
    ]
    mock_openai_chat_completion.invoke.return_value = [
        Flashcard(question=fc["question"], answer=fc["answer"]) for fc in mock_flashcards_data
    ]

    text = "Photosynthesis is the process by which green plants and some other organisms convert light energy into chemical energy. Chlorophyll, a green pigment, is essential for photosynthesis."
    flashcards = generator.generate_flashcards(text)

    assert len(flashcards) == 2
    assert flashcards[0].question == "What is Photosynthesis?"
    assert flashcards[0].answer == "Process by which plants convert light energy into chemical energy."
    assert flashcards[1].question == "What is Chlorophyll?"
    assert flashcards[1].answer == "A green pigment essential for photosynthesis."
    mock_openai_chat_completion.invoke.assert_called_once()

def test_generate_flashcards_empty_text(mock_openai_chat_completion):
    """Test flashcard generation with empty input text."""
    generator = FlashcardGenerationModule()
    mock_openai_chat_completion.invoke.return_value = []

    text = ""
    flashcards = generator.generate_flashcards(text)

    assert len(flashcards) == 0
    mock_openai_chat_completion.invoke.assert_called_once()

def test_generate_flashcards_missing_api_key():
    """Test error handling when OPENAI_API_KEY is not set."""
    original_api_key = os.environ.pop("OPENAI_API_KEY", None)
    
    generator = FlashcardGenerationModule()
    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set."):
        generator.generate_flashcards("some text")

    if original_api_key:
        os.environ["OPENAI_API_KEY"] = original_api_key
