# backend/tests/conftest.py

import pytest
from unittest.mock import MagicMock, PropertyMock
from backend.app.core.ai.uncertainty_resolution_module import UncertaintyResolutionModule
from backend.app.core.ai.exploratory_module import ExploratoryModule
from langchain_core.messages import AIMessage

@pytest.fixture
def mock_llm_response():
    """Fixture to provide a consistent mocked LLM response."""
    return "Mocked calibration question about {key_term} in {topic}."

@pytest.fixture
def uncertainty_resolution_module(mocker, mock_llm_response):
    """
    Returns an instance of the UncertaintyResolutionModule with a mocked LLM.
    The LLM's invoke method is mocked to return a predefined response.
    """
    mock_chat_openai_class = mocker.patch('backend.app.core.ai.uncertainty_resolution_module.ChatOpenAI')
    mock_llm_instance = MagicMock()
    
    mock_returned_value = MagicMock()
    type(mock_returned_value).content = PropertyMock(return_value=mock_llm_response)
    mock_llm_instance.invoke.return_value = mock_returned_value
    
    mock_chat_openai_class.return_value = mock_llm_instance
    return UncertaintyResolutionModule()

@pytest.fixture
def mock_llm_exploratory_response():
    """Fixture to provide a consistent mocked LLM response for exploratory phrasing."""
    return "Mocked exploratory phrasing about {key_term} in {topic}."

@pytest.fixture
def exploratory_module(mocker, mock_llm_exploratory_response):
    """
    Returns an instance of the ExploratoryModule with a mocked LLM.
    The LLM's invoke method is mocked to return a predefined response.
    """
    mock_chat_openai_class = mocker.patch('backend.app.core.ai.exploratory_module.ChatOpenAI')
    mock_llm_instance = MagicMock()
    
    mock_returned_value = MagicMock()
    type(mock_returned_value).content = PropertyMock(return_value=mock_llm_exploratory_response)
    mock_llm_instance.invoke.return_value = mock_returned_value
    
    mock_chat_openai_class.return_value = mock_llm_instance
    return ExploratoryModule()