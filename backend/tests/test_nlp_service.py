import pytest
from unittest.mock import MagicMock, patch
from backend.app.services.nlp_service import NLPService, Intent, UserState

@pytest.fixture
def mock_spacy_nlp():
    """Mocks the spaCy Language object."""
    mock_nlp = MagicMock()
    mock_doc = MagicMock()
    mock_nlp.return_value = mock_doc

    # Mock tokens and their properties
    mock_token1 = MagicMock(text="Hello", lemma_="hello", pos_="INTJ", is_alpha=True)
    mock_token2 = MagicMock(text=",", lemma_=",", pos_="PUNCT", is_alpha=False)
    mock_token3 = MagicMock(text="world", lemma_="world", pos_="NOUN", is_alpha=True)
    mock_token4 = MagicMock(text=".", lemma_="", pos_="PUNCT", is_alpha=False)
    mock_token5 = MagicMock(text="How", lemma_="how", pos_="ADV", is_alpha=True)
    mock_token6 = MagicMock(text="are", lemma_="be", pos_="AUX", is_alpha=True)
    mock_token7 = MagicMock(text="you", lemma_="you", pos_="PRON", is_alpha=True)
    mock_token8 = MagicMock(text="?", lemma_="?", pos_="PUNCT", is_alpha=False)

    mock_doc.configure_mock(
        **{
            "sents.__iter__.return_value": [
                MagicMock(text="Hello, world."),
                MagicMock(text="How are you?")
            ],
            "ents": [], # No named entities for this simple test case
            "__iter__.return_value": [mock_token1, mock_token2, mock_token3, mock_token4, mock_token5, mock_token6, mock_token7, mock_token8]
        }
    )
    # Mock for sentence tokenization in process_text calculations
    # This is a bit tricky because the NLPService re-processes sentences.
    # We need to mock nlp(sent) for each sentence.
    def mock_nlp_side_effect(text):
        if text == "Hello, world.":
            mock_sent_doc1 = MagicMock()
            mock_sent_doc1.__iter__.return_value = [mock_token1, mock_token2, mock_token3, mock_token4]
            return mock_sent_doc1
        elif text == "How are you?":
            mock_sent_doc2 = MagicMock()
            mock_sent_doc2.__iter__.return_value = [mock_token5, mock_token6, mock_token7, mock_token8]
            return mock_sent_doc2
        return MagicMock() # Default for other calls
    mock_nlp.side_effect = mock_nlp_side_effect


    # Mock specific calls for num_alphanumeric_tokens in sentences
    mock_sent_doc1 = MagicMock()
    mock_sent_doc1.__iter__.return_value = [mock_token1, mock_token2, mock_token3, mock_token4]
    
    mock_sent_doc2 = MagicMock()
    mock_sent_doc2.__iter__.return_value = [mock_token5, mock_token6, mock_token7, mock_token8]

    mock_nlp.return_value.sents.__iter__.return_value = [
        MagicMock(text="Hello, world.", doc=mock_sent_doc1),
        MagicMock(text="How are you?", doc=mock_sent_doc2)
    ]

    return mock_nlp

@pytest.fixture(autouse=True)
def patch_spacy_load(mock_spacy_nlp):
    """Patches spacy.load globally for all NLPService tests."""
    with patch('spacy.load', return_value=mock_spacy_nlp) as mock_load:
        yield mock_load

@pytest.fixture
def nlp_service():
    """Provides an instance of NLPService with mocked spaCy."""
    db_session = MagicMock()
    return NLPService(db=db_session)

def test_nlp_service_initialization(nlp_service, patch_spacy_load):
    """Test that NLPService initializes and loads the spaCy model."""
    patch_spacy_load.assert_called_once_with("en_core_web_sm")
    assert nlp_service.nlp is not None
    assert nlp_service.summarization_module is not None
    assert nlp_service.flashcard_generation_module is not None # Added assertion