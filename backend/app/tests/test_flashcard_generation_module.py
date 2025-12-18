import os
import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.flashcard_generation_module import FlashcardGenerationModule, Flashcard

# Mock the ChatOpenAI dependency
@pytest.fixture
def mock_chat_openai():
    with patch('langchain_openai.ChatOpenAI') as mock_llm_class:
        mock_instance = MagicMock()
        mock_llm_class.return_value = mock_instance
        # Mock the invoke method directly
        mock_instance.invoke.return_value = """
1. Question: Mock Flashcard Question 1?
Answer: Mock Flashcard Answer 1.
2. Question: Mock Flashcard Question 2?
Answer: Mock Flashcard Answer 2.
"""
        yield mock_llm_class # Yield the mock class, not the instance

@pytest.fixture
def flashcard_generator(mock_chat_openai):
    # Ensure OPENAI_API_KEY is set for the test, as the module checks it
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    generator = FlashcardGenerationModule()
    # Set the llm attribute of the generator to the mocked instance provided by mock_chat_openai
    # mock_chat_openai is the class mock, mock_chat_openai.return_value is the instance mock
    generator.llm = mock_chat_openai.return_value 
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
    assert flashcards[0].question == "First Q?"
    assert flashcards[0].answer == "First A."
    assert flashcards[1].question == "Second Q?"
    assert flashcards[1].answer == "Second A."

@pytest.mark.asyncio
async def test_generate_flashcards_with_llm(flashcard_generator, mock_chat_openai):
    # The mock_chat_openai fixture already sets the return_value for invoke on the mocked instance
    # We can directly use flashcard_generator.llm which should be the mocked instance
    text = "Sample text for flashcards"
    flashcards = flashcard_generator.generate_flashcards(text)

    # Ensure ChatOpenAI was called with correct parameters
    mock_chat_openai.assert_called_once_with(model_name="gpt-4o", temperature=0.5)
    # Ensure the invoke method of the mocked instance was called
    flashcard_generator.llm.invoke.assert_called_once()
    assert len(flashcards) == 2
    assert flashcards[0].question == "Mock Flashcard Question 1?" # Use the value from the fixture's mock
    assert flashcards[0].answer == "Mock Flashcard Answer 1."
