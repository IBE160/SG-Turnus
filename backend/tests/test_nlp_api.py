import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app

# Import fixtures from test_main for client setup
from backend.tests.test_main import test_client, mock_external_services_and_singletons

@pytest.fixture(autouse=True)
def mock_spacy_load_for_api_tests():
    """
    Mocks spacy.load for API tests to prevent actual model loading
    and ensure deterministic behavior.
    """
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    mock_nlp.return_value = mock_doc

    # Minimal mocking for doc object to avoid errors during iteration or attribute access
    mock_token_hello = MagicMock(text="Hello", lemma_="hello", pos_="INTJ", is_alpha=True)
    mock_token_world = MagicMock(text="world", lemma_="world", pos_="NOUN", is_alpha=True)
    mock_token_period = MagicMock(text=".", lemma_=".", pos_="PUNCT", is_alpha=False)
    mock_token_question = MagicMock(text="?", lemma_="?", pos_="PUNCT", is_alpha=False)

    mock_doc.configure_mock(
        **{
            "sents.__iter__.return_value": [
                MagicMock(text="Hello world.", doc=MagicMock(__iter__=lambda s: [mock_token_hello, mock_token_world, mock_token_period])),
                MagicMock(text="How are you?", doc=MagicMock(__iter__=lambda s: [mock_token_hello, mock_token_world, mock_token_question]))
            ],
            "ents": [],
            "__iter__.return_value": [mock_token_hello, mock_token_world, mock_token_period, mock_token_question]
        }
    )
    mock_doc.sents = [
        MagicMock(text="Hello world.", doc=MagicMock(__iter__=lambda s: [mock_token_hello, mock_token_world, mock_token_period])),
        MagicMock(text="How are you?", doc=MagicMock(__iter__=lambda s: [mock_token_hello, mock_token_world, mock_token_question]))
    ]

    # Mock specific calls for num_alphanumeric_tokens in sentences within NLPService logic
    def mock_nlp_side_effect(text):
        if "Hello world." in text:
            mock_sent_doc = MagicMock()
            mock_sent_doc.__iter__.return_value = [
                MagicMock(text="Hello", is_alpha=True), MagicMock(text="world", is_alpha=True), MagicMock(text=".", is_alpha=False)
            ]
            return mock_sent_doc
        elif "How are you?" in text:
            mock_sent_doc = MagicMock()
            mock_sent_doc.__iter__.return_value = [
                MagicMock(text="How", is_alpha=True), MagicMock(text="are", is_alpha=True), MagicMock(text="you", is_alpha=True), MagicMock(text="?", is_alpha=False)
            ]
            return mock_sent_doc
        else:
            mock_doc_generic = MagicMock()
            mock_doc_generic.__iter__.return_value = []
            mock_doc_generic.sents = []
            mock_doc_generic.ents = []
            return mock_doc_generic

    mock_nlp.side_effect = mock_nlp_side_effect

    with patch('spacy.load', return_value=mock_nlp) as mock_load:
        yield mock_load

@pytest.mark.asyncio
async def test_process_text_endpoint_success(test_client: TestClient, mock_spacy_load_for_api_tests):
    """
    Test the /api/v1/nlp/process endpoint with a valid text input.
    """
    text_input = "Hello, world. How are you today?"
    response = test_client.post(
        "/api/v1/nlp/process",
        json={"text": text_input}
    )

    assert response.status_code == 200
    data = response.json()

    # Basic assertions for the structure and some content
    assert data["original_text"] == text_input
    assert isinstance(data["tokens"], list)
    assert "Hello" in data["tokens"]
    assert isinstance(data["sentences"], list)
    assert len(data["sentences"]) > 0
    assert data["num_sentences"] == 2
    assert "how" in data["found_question_words"]
    assert data["num_alphanumeric_tokens"] > 0
    assert data["unique_words"] > 0
    assert isinstance(data["average_word_length"], float)
    assert isinstance(data["average_sentence_length"], float)
    assert isinstance(data["named_entities"], list)

@pytest.mark.asyncio
async def test_process_text_endpoint_empty_input(test_client: TestClient, mock_spacy_load_for_api_tests):
    """
    Test the /api/v1/nlp/process endpoint with an empty text input.
    """
    text_input = ""
    response = test_client.post(
        "/api/v1/nlp/process",
        json={"text": text_input}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["original_text"] == ""
    assert data["tokens"] == []
    assert data["num_sentences"] == 0
    assert data["num_alphanumeric_tokens"] == 0
    assert data["unique_words"] == 0
    assert data["average_word_length"] == 0.0
    assert data["average_sentence_length"] == 0.0
    assert data["named_entities"] == []

@pytest.mark.asyncio
async def test_process_text_endpoint_invalid_input(test_client: TestClient):
    """
    Test the /api/v1/nlp/process endpoint with invalid input (e.g., missing 'text' key).
    """
    response = test_client.post(
        "/api/v1/nlp/process",
        json={"invalid_key": "some text"}
    )
    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation error

