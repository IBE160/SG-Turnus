# backend/tests/conftest.py

import pytest
from unittest.mock import MagicMock
from backend.app.core.ai.calibration_module import CalibrationModule
from langchain_core.messages import AIMessage

@pytest.fixture
def mock_llm_response():
    """Fixture to provide a consistent mocked LLM response."""
    return "Mocked calibration question about {key_term} in {topic}."

@pytest.fixture
def calibration_module(mocker, mock_llm_response):
    """
    Returns an instance of the CalibrationModule with a mocked LLM.
    The LLM's invoke method is mocked to return a predefined response.
    """
    mock_chat_openai_class = mocker.patch('backend.app.core.ai.calibration_module.ChatOpenAI')
    mock_llm_instance = MagicMock()
    
    # Create a mock for the AIMessage object that ChatOpenAI.invoke would return
    mock_ai_message = MagicMock(spec=AIMessage)
    mock_ai_message.content = mock_llm_response
    
    mock_llm_instance.invoke.return_value = mock_ai_message
    mock_chat_openai_class.return_value = mock_llm_instance
    return CalibrationModule()