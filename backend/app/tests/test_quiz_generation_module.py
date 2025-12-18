import os
import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.quiz_generation_module import QuizGenerationModule, QuizQuestion

# Mock the ChatOpenAI dependency
@pytest.fixture
def mock_chat_openai():
    with patch('langchain_openai.ChatOpenAI') as mock:
        yield mock

@pytest.fixture
def quiz_generator(mock_chat_openai):
    # Ensure OPENAI_API_KEY is set for the test, as the module checks it
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    generator = QuizGenerationModule()
    # Reset llm to None so it gets initialized with the mock
    generator.llm = None
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
    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance
    mock_llm_instance.invoke.return_value = """
1. Question: Mock Question 1?
Options:
  A. Mock Opt A1
  B. Mock Opt B1
Correct Answer: A

2. Question: Mock Question 2?
Options:
  A. Mock Opt A2
  B. Mock Opt B2
Correct Answer: B
    """
    
    text = "Sample text for quiz"
    questions = quiz_generator.generate_quiz(text)

    mock_chat_openai.assert_called_once_with(model_name="gpt-4o", temperature=0.5)
    mock_llm_instance.invoke.assert_called_once()
    assert len(questions) == 2
    assert questions[0].question == "Mock Question 1?"
    assert questions[0].correct_answer == "Mock Opt A1"
