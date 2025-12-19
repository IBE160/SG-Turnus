# backend/tests/conftest.py

import pytest
from unittest.mock import MagicMock, PropertyMock
from backend.app.core.ai.uncertainty_resolution_module import UncertaintyResolutionModule
from backend.app.core.ai.exploratory_module import ExploratoryModule
from langchain_core.messages import AIMessage
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base, get_db
from fastapi.testclient import TestClient
from backend.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
def mock_openai_chat_completion_global(mocker, monkeypatch):
    """
    Globally patches ChatOpenAI for all AI modules and ensures a dummy API key is set.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

    mock_llm_instance = MagicMock()
    
    # Patch ChatOpenAI in summarization_module
    mocker.patch('backend.app.core.ai.summarization_module.ChatOpenAI', return_value=mock_llm_instance)
    # Patch ChatOpenAI in flashcard_generation_module
    mocker.patch('backend.app.core.ai.flashcard_generation_module.ChatOpenAI', return_value=mock_llm_instance)
    # Patch ChatOpenAI in uncertainty_resolution_module
    mocker.patch('backend.app.core.ai.uncertainty_resolution_module.ChatOpenAI', return_value=mock_llm_instance)
    # Patch ChatOpenAI in exploratory_module
    mocker.patch('backend.app.core.ai.exploratory_module.ChatOpenAI', return_value=mock_llm_instance)

    yield mock_llm_instance

@pytest.fixture
def mock_llm_response():
    """Fixture to provide a consistent mocked LLM response."""
    return "Mocked calibration question about {key_term} in {topic}."

@pytest.fixture
def uncertainty_resolution_module(mock_openai_chat_completion_global, mock_llm_response):
    """
    Returns an instance of the UncertaintyResolutionModule with a mocked LLM.
    The LLM's invoke method is mocked to return a predefined response.
    """
    mock_returned_value = MagicMock()
    type(mock_returned_value).content = PropertyMock(return_value=mock_llm_response)
    mock_openai_chat_completion_global.invoke.return_value = mock_returned_value
    
    return UncertaintyResolutionModule()

@pytest.fixture
def mock_llm_exploratory_response():
    """Fixture to provide a consistent mocked LLM response for exploratory phrasing."""
    return "Mocked exploratory phrasing about {key_term} in {topic}."

@pytest.fixture
def exploratory_module(mock_openai_chat_completion_global, mock_llm_exploratory_response):
    """
    Returns an instance of the ExploratoryModule with a mocked LLM.
    The LLM's invoke method is mocked to return a predefined response.
    """
    mock_returned_value = MagicMock()
    type(mock_returned_value).content = PropertyMock(return_value=mock_llm_exploratory_response)
    mock_openai_chat_completion_global.invoke.return_value = mock_returned_value
    
    return ExploratoryModule()
