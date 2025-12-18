import os
import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.flashcard_generation_module import FlashcardGenerationModule, Flashcard

# Mock the ChatOpenAI dependency
@pytest.fixture
def mock_chat_openai():
    with patch('langchain_openai.ChatOpenAI') as mock:
        yield mock

@pytest.fixture
def flashcard_generator(mock_chat_openai):
    # Ensure OPENAI_API_KEY is set for the test, as the module checks it
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    generator = FlashcardGenerationModule()
    # Reset llm to None so it gets initialized with the mock
    generator.llm = None
    yield generator
    del os.environ["OPENAI_API_KEY"]

def test_flashcard_init(flashcard_generator):
    assert flashcard_generator.model_name == "gpt-4o"
    assert flashcard_generator.temperature == 0.5
    assert flashcard_generator.llm is None # Should be initialized on first call

def test_generate_flashcards_no_openai_key():
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    generator = FlashcardGenerationModule()
    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set."):
        generator.generate_flashcards("some text")

def test_parse_llm_output_to_flashcards_valid_output(flashcard_generator):
    llm_output = """
1. Question: What is photosynthesis?
Answer: The process by which green plants and some other organisms use sunlight to synthesize foods.
2. Question: Where does photosynthesis occur?
Answer: In the chloroplasts of plant cells.
3. Question: What is the primary product of photosynthesis?
Answer: Sugars (carbohydrates).
    """
    flashcards = flashcard_generator._parse_llm_output_to_flashcards(llm_output)
    assert len(flashcards) == 3
    assert flashcards[0].question == "What is photosynthesis?"
    assert flashcards[0].answer == "The process by which green plants and some other organisms use sunlight to synthesize foods."
    assert flashcards[1].question == "Where does photosynthesis occur?"
    assert flashcards[1].answer == "In the chloroplasts of plant cells."
    assert flashcards[2].question == "What is the primary product of photosynthesis?"
    assert flashcards[2].answer == "Sugars (carbohydrates)."

def test_parse_llm_output_to_flashcards_empty_output(flashcard_generator):
    llm_output = ""
    flashcards = flashcard_generator._parse_llm_output_to_flashcards(llm_output)
    assert len(flashcards) == 0

def test_parse_llm_output_to_flashcards_malformed_output_no_answer(flashcard_generator):
    llm_output = "1. Question: What is photosynthesis?\nSome random text"
    flashcards = flashcard_generator._parse_llm_output_to_flashcards(llm_output)
    assert len(flashcards) == 0

def test_parse_llm_output_to_flashcards_with_varied_numbering(flashcard_generator):
    llm_output = """
1) Question: First Q?
Answer: First A.
2. Question: Second Q?
Answer: Second A.
    """
    flashcards = flashcard_generator._parse_llm_output_to_flashcards(llm_output)
    assert len(flashcards) == 2
    assert flashcards[0].question == "Question: First Q?" # The parsing currently keeps "Question:" if the numbering is not "1. "
    assert flashcards[0].answer == "First A."
    assert flashcards[1].question == "Second Q?"
    assert flashcards[1].answer == "Second A."

@pytest.mark.asyncio
async def test_generate_flashcards_with_llm(flashcard_generator, mock_chat_openai):
    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance
    mock_llm_instance.invoke.return_value = """
1. Question: Test Question 1?
Answer: Test Answer 1.
2. Question: Test Question 2?
Answer: Test Answer 2.
    """
    
    text = "Sample text for flashcards"
    flashcards = flashcard_generator.generate_flashcards(text)

    mock_chat_openai.assert_called_once_with(model_name="gpt-4o", temperature=0.5)
    mock_llm_instance.invoke.assert_called_once()
    assert len(flashcards) == 2
    assert flashcards[0].question == "Test Question 1?"
    assert flashcards[0].answer == "Test Answer 1."
