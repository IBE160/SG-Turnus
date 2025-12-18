import pytest
import os
from unittest.mock import MagicMock, patch
from backend.app.core.ai.flashcard_generation_module import FlashcardGenerationModule, Flashcard, FlashcardList

# Mock the ChatOpenAI to prevent actual API calls during testing
@pytest.fixture
def mock_chat_openai():
    with patch('langchain_openai.ChatOpenAI') as MockChatOpenAI:
        mock_llm = MockChatOpenAI.return_value
        yield mock_llm

@pytest.fixture
def flashcard_generator(mock_chat_openai):
    # Ensure OPENAI_API_KEY is set for the module initialization to pass
    os.environ["OPENAI_API_KEY"] = "fake_key" 
    generator = FlashcardGenerationModule()
    del os.environ["OPENAI_API_KEY"] # Clean up
    return generator

def test_flashcard_generation_success(flashcard_generator, mock_chat_openai):
    """
    Test successful flashcard generation with a valid text input.
    """
    sample_text = "Photosynthesis is the process by which plants convert light energy into chemical energy."
    mock_llm.invoke.return_value = '[{"question": "What is photosynthesis?", "answer": "The process by which plants convert light energy into chemical energy."}]'

    flashcards = flashcard_generator.generate_flashcards(sample_text)

    assert isinstance(flashcards, list)
    assert len(flashcards) == 1
    assert isinstance(flashcards[0], Flashcard)
    assert flashcards[0].question == "What is photosynthesis?"
    assert flashcards[0].answer == "The process by which plants convert light energy into chemical energy."
    mock_llm.invoke.assert_called_once()
    assert mock_llm.invoke.call_args.kwargs['text'] == sample_text

def test_flashcard_generation_multiple_flashcards(flashcard_generator, mock_chat_openai):
    """
    Test generation of multiple flashcards.
    """
    sample_text = "DNA is a double helix. RNA is single-stranded."
    mock_llm.invoke.return_value = '''
    [
        {"question": "What is the structure of DNA?", "answer": "A double helix."},
        {"question": "What is the structure of RNA?", "answer": "Single-stranded."}
    ]
    '''

    flashcards = flashcard_generator.generate_flashcards(sample_text)

    assert isinstance(flashcards, list)
    assert len(flashcards) == 2
    assert flashcards[0].question == "What is the structure of DNA?"
    assert flashcards[1].answer == "Single-stranded."

def test_flashcard_generation_empty_text(flashcard_generator, mock_chat_openai):
    """
    Test flashcard generation with empty text input.
    The LLM should ideally return an empty list or handle it gracefully.
    """
    empty_text = ""
    mock_llm.invoke.return_value = '[]' # LLM returns empty list for empty input

    flashcards = flashcard_generator.generate_flashcards(empty_text)
    
    assert isinstance(flashcards, list)
    assert len(flashcards) == 0
    mock_llm.invoke.assert_called_once()
    assert mock_llm.invoke.call_args.kwargs['text'] == empty_text

def test_flashcard_generation_invalid_json_output(flashcard_generator, mock_chat_openai):
    """
    Test error handling when LLM returns invalid JSON.
    """
    sample_text = "Some text."
    mock_llm.invoke.return_value = '{"question": "invalid json"' # Malformed JSON

    with pytest.raises(ValueError, match="Failed to parse flashcards from LLM output. Invalid JSON format."):
        flashcard_generator.generate_flashcards(sample_text)

def test_flashcard_generation_missing_openai_key():
    """
    Test that a ValueError is raised if OPENAI_API_KEY is not set.
    """
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"] # Ensure it's not set
    
    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set."):
        FlashcardGenerationModule()

    # Restore environment if it was set before
    # (This is more robust if other tests rely on it)
    # os.environ["OPENAI_API_KEY"] = "original_key" # if we had one
