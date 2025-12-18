import pytest
from unittest.mock import MagicMock, patch
from backend.app.core.ai.quiz_generation_module import QuizGenerationModule, QuizQuestion
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

def test_quiz_generation_module_initialization():
    """Test that the quiz generation module initializes correctly."""
    quiz_generator = QuizGenerationModule()
    assert quiz_generator.llm is None
    assert quiz_generator.output_parser is not None
    assert quiz_generator.quiz_prompt_template is not None

def test_generate_quiz(mock_chain_invoke):
    """Test generating a quiz."""
    mock_chain_invoke.return_value = [
        {
            "question": "What was the capital of the Roman Empire?",
            "options": ["Athens", "Carthage", "Rome", "Alexandria"],
            "correct_answer": "Rome"
        },
        {
            "question": "Who was the first Roman Emperor?",
            "options": ["Julius Caesar", "Nero", "Augustus", "Constantine"],
            "correct_answer": "Augustus"
        }
    ]
    quiz_generator = QuizGenerationModule()
    
    text = "Some text to generate a quiz from."
    questions = quiz_generator.generate_quiz(text)

    assert len(questions) == 2
    assert isinstance(questions[0], QuizQuestion)
    assert questions[0].question == "What was the capital of the Roman Empire?"
    assert questions[0].options == ["Athens", "Carthage", "Rome", "Alexandria"]
    assert questions[0].correct_answer == "Rome"
    
    mock_chain_invoke.assert_called_once_with({"text": text})

def test_generate_quiz_with_string_output(mock_chain_invoke):
    """Test generating a quiz when the LLM returns a JSON string."""
    
    mock_chain_result_str = json.dumps([
        {
            "question": "What is 2 * 3?",
            "options": ["5", "6", "7", "8"],
            "correct_answer": "6"
        }
    ])
    mock_chain_invoke.return_value = mock_chain_result_str

    quiz_generator = QuizGenerationModule()
    
    text = "Another text."
    questions = quiz_generator.generate_quiz(text)

    assert len(questions) == 1
    assert isinstance(questions[0], QuizQuestion)
    assert questions[0].question == "What is 2 * 3?"
    assert questions[0].correct_answer == "6"

def test_generate_quiz_invalid_json_string(mock_chain_invoke):
    """Test handling of invalid JSON string from LLM."""
    mock_chain_invoke.return_value = "This is not valid JSON"

    quiz_generator = QuizGenerationModule()
    questions = quiz_generator.generate_quiz("some text")

    assert questions == []

def test_generate_quiz_missing_api_key():
    """Test error handling when OPENAI_API_KEY is not set."""
    original_api_key = os.environ.pop("OPENAI_API_KEY", None)
    
    quiz_generator = QuizGenerationModule()
    with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable is not set."):
        quiz_generator.generate_quiz("some text")

    if original_api_key:
        os.environ["OPENAI_API_KEY"] = original_api_key
