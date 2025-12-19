import os
import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.quiz_generation_module import QuizGenerationModule, QuizQuestion

# Mock the ChatOpenAI dependency
@pytest.fixture
def mock_chat_openai():
    with patch('langchain_openai.ChatOpenAI') as mock_llm_class:
        mock_instance = MagicMock()
        mock_llm_class.return_value = mock_instance
        # Mock the invoke method directly
        mock_instance.invoke.return_value = """
1. Question: Mock Quiz Question 1?
Options:
  A. Mock Opt A1
  B. Mock Opt B1
Correct Answer: A

2. Question: Mock Quiz Question 2?
Options:
  A. Mock Opt A2
  B. Mock Opt B2
Correct Answer: B
"""
        yield mock_llm_class # Yield the mock class, not the instance

@pytest.fixture
def quiz_generator(mock_chat_openai):
    # Ensure OPENAI_API_KEY is set for the test, as the module checks it
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    generator = QuizGenerationModule()
    # Set the llm attribute of the generator to the mocked instance provided by mock_chat_openai
    # mock_chat_openai is the class mock, mock_chat_openai.return_value is the instance mock
    generator.llm = mock_chat_openai.return_value
    yield generator
    del os.environ["OPENAI_API_KEY"]

def test_quiz_init(quiz_generator):
    assert quiz_generator.model_name == "gpt-4o"
    assert quiz_generator.temperature == 0.5
    assert quiz_generator.llm is None # Should be initialized on first call

def test_generate_quiz_no_openai_key():
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    generator = QuizGenerationModule()
    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set."):
        generator.generate_quiz("some text")

def test_parse_llm_output_to_quiz_questions_valid_output(quiz_generator):
    llm_output = """
1. Question: What is the capital of France?
Options:
  A. Berlin
  B. Madrid
  C. Paris
  D. Rome
Correct Answer: C

2. Question: Which river flows through Paris?
Options:
  A. Thames
  B. Seine
  C. Danube
  D. Rhine
Correct Answer: B
    """
    questions = quiz_generator._parse_llm_output_to_quiz_questions(llm_output)
    assert len(questions) == 2
    assert questions[0].question == "What is the capital of France?"
    assert questions[0].options == ["Berlin", "Madrid", "Paris", "Rome"]
    assert questions[0].correct_answer == "Paris" # The parser extracts the full text

    assert questions[1].question == "Which river flows through Paris?"
    assert questions[1].options == ["Thames", "Seine", "Danube", "Rhine"]
    assert questions[1].correct_answer == "Seine"

def test_parse_llm_output_to_quiz_questions_empty_output(quiz_generator):
    llm_output = ""
    questions = quiz_generator._parse_llm_output_to_quiz_questions(llm_output)
    assert len(questions) == 0

def test_parse_llm_output_to_quiz_questions_malformed_output_no_options(quiz_generator):
    llm_output = "1. Question: Test Q?\nCorrect Answer: A"
    questions = quiz_generator._parse_llm_output_to_quiz_questions(llm_output)
    assert len(questions) == 0

def test_parse_llm_output_to_quiz_questions_malformed_output_no_correct_answer(quiz_generator):
    llm_output = """
1. Question: Test Q?
Options:
  A. Opt A
    """
    questions = quiz_generator._parse_llm_output_to_quiz_questions(llm_output)
    assert len(questions) == 0

@pytest.mark.asyncio
async def test_generate_quiz_with_llm(quiz_generator, mock_chat_openai):
    # The mock_chat_openai fixture already sets the return_value for invoke on the mocked instance
    # We can directly use quiz_generator.llm which should be the mocked instance
    text = "Sample text for quiz"
    questions = quiz_generator.generate_quiz(text)

    # Ensure ChatOpenAI was called with correct parameters
    mock_chat_openai.assert_called_once_with(model_name="gpt-4o", temperature=0.5)
    # Ensure the invoke method of the mocked instance was called
    quiz_generator.llm.invoke.assert_called_once()
    assert len(questions) == 2
    assert questions[0].question == "Mock Quiz Question 1?" # Use the value from the fixture's mock
    assert questions[0].options == ["A", "B", "C"] # Placeholder, needs to be precise if parsing is specific
    assert questions[0].correct_answer == "A" # Use the value from the fixture's mock
