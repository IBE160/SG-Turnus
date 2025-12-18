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
    return NLPService()

def test_nlp_service_initialization(nlp_service, patch_spacy_load):
    """Test that NLPService initializes and loads the spaCy model."""
    patch_spacy_load.assert_called_once_with("en_core_web_sm")
    assert nlp_service.nlp is not None

@pytest.mark.parametrize("text_input, expected_intent, expected_confidence", [
    ("summarize this text", Intent.SUMMARIZATION, 0.9),
    ("Can you give me a summary?", Intent.SUMMARIZATION, 0.9),
    ("What is a noun?", Intent.CLARIFICATION, 0.8),
    ("Explain the concept of gravity.", Intent.CLARIFICATION, 0.8),
    ("How do I solve this problem?", Intent.PROBLEM_SOLVING, 0.7),
    ("Solve for x in 2x + 5 = 10.", Intent.PROBLEM_SOLVING, 0.7),
    ("Quiz me on this chapter.", Intent.ACTIVE_RECALL, 0.7),
    ("Test my knowledge on history.", Intent.ACTIVE_RECALL, 0.7),
    ("Relate this to biology.", Intent.CONCEPT_LINKING, 0.6),
    ("Connect these ideas.", Intent.CONCEPT_LINKING, 0.6),
    ("Is it true that the earth is flat?", Intent.MISCONCEPTION_CORRECTION, 0.6),
    ("I think I'm wrong about this.", Intent.MISCONCEPTION_CORRECTION, 0.6),
    ("Just some random text.", Intent.UNKNOWN, 0.1),
])
def test_detect_intent(nlp_service, text_input, expected_intent, expected_confidence):
    """Test the intent detection logic."""
    doc = nlp_service.nlp(text_input)
    tokens = [token.text for token in doc]
    question_words = ["who", "what", "where", "when", "why", "how", "which", "whom", "whose"]
    found_question_words = [token.text.lower() for token in doc if token.text.lower() in question_words]

    intent, confidence = nlp_service.detect_intent(text_input, tokens, found_question_words)
    assert intent == expected_intent
    assert confidence == expected_confidence

@pytest.mark.parametrize("text_input, detected_intent, expected_state, expected_confidence", [
    ("I am confused about this topic.", Intent.UNKNOWN, UserState.CONFUSED, 0.8),
    ("What is the capital of France? I don't understand.", Intent.CLARIFICATION, UserState.CONFUSED, 0.8),
    ("Tell me more about quantum physics.", Intent.UNKNOWN, UserState.CURIOUS, 0.7),
    ("This is too much information, simplify it.", Intent.UNKNOWN, UserState.OVERLOADED, 0.7),
    ("Can you explain this quickly?", Intent.UNKNOWN, UserState.TIME_LIMITED, 0.6),
    ("Maybe this is wrong?", Intent.UNKNOWN, UserState.UNCERTAIN, 0.6),
    ("Just some neutral text.", Intent.UNKNOWN, UserState.NEUTRAL, 0.1),
])
def test_infer_user_state(nlp_service, text_input, detected_intent, expected_state, expected_confidence):
    """Test the user state inference logic."""
    doc = nlp_service.nlp(text_input)
    tokens = [token.text for token in doc]
    state, confidence = nlp_service.infer_user_state(text_input, tokens, detected_intent)
    assert state == expected_state
    assert confidence == expected_confidence


def test_process_text_basic_sentence(nlp_service, mock_spacy_nlp):
    """Test processing of a basic sentence, including intent and user state detection."""
    text = "Hello, world. How are you?"
    signals = nlp_service.process_text(text)

    # Assertions based on mocked spaCy output
    assert signals["original_text"] == text
    assert signals["tokens"] == ["Hello", ",", "world", ".", "How", "are", "you", "?"]
    assert signals["lemmas"] == ["hello", ",", "world", ".", "how", "be", "you", "?"]
    assert signals["pos_tags"] == ["INTJ", "PUNCT", "NOUN", "PUNCT", "ADV", "AUX", "PRON", "PUNCT"]
    assert sorted(signals["found_question_words"]) == sorted(["how"])
    assert signals["sentences"] == ["Hello, world.", "How are you?"]
    assert signals["num_sentences"] == 2
    assert signals["num_paragraphs"] == 1
    assert signals["num_alphanumeric_tokens"] == 5 # Hello, world, How, are, you
    assert signals["unique_words"] == 5 # hello, world, how, be, you
    # Manual calculation for average_word_length: (5 + 5 + 3 + 3 + 3) / 5 = 19/5 = 3.8
    assert signals["average_word_length"] == pytest.approx(3.8) 
    # Manual calculation for average_sentence_length: (2 words in "Hello, world." + 3 words in "How are you?") / 2 = 5/2 = 2.5
    assert signals["average_sentence_length"] == pytest.approx(2.5) 
    assert signals["named_entities"] == []
    assert signals["detected_intent"] == Intent.CLARIFICATION.value
    assert signals["intent_confidence"] == 0.8
    assert signals["inferred_user_state"] == UserState.NEUTRAL.value
    assert signals["user_state_confidence"] == 0.1


def test_process_text_empty_string(nlp_service):
    """Test processing an empty string, including intent and user state detection."""
    text = ""
    signals = nlp_service.process_text(text)
    assert signals["original_text"] == ""
    assert signals["tokens"] == []
    assert signals["num_sentences"] == 0
    assert signals["num_alphanumeric_tokens"] == 0
    assert signals["average_word_length"] == 0
    assert signals["average_sentence_length"] == 0
    assert signals["detected_intent"] == Intent.UNKNOWN.value
    assert signals["intent_confidence"] == 0.1
    assert signals["inferred_user_state"] == UserState.NEUTRAL.value
    assert signals["user_state_confidence"] == 0.1

def test_process_text_with_named_entities(nlp_service, mock_spacy_nlp):
    """Test processing text with named entities, including intent and user state detection."""
    text = "Apple is a company. Steve Jobs founded Apple. Summarize this for me."
    
    mock_doc_with_entities = MagicMock()
    mock_ent1 = MagicMock(text="Apple", label_="ORG")
    mock_ent2 = MagicMock(text="Steve Jobs", label_="PERSON")
    mock_doc_with_entities.ents = [mock_ent1, mock_ent2]
    mock_doc_with_entities.sents.__iter__.return_value = [
        MagicMock(text="Apple is a company."),
        MagicMock(text="Steve Jobs founded Apple."),
        MagicMock(text="Summarize this for me.")
    ]
    
    mock_token1 = MagicMock(text="Apple", lemma_="apple", pos_="PROPN", is_alpha=True)
    mock_token2 = MagicMock(text="is", lemma_="be", pos_="AUX", is_alpha=True)
    mock_token3 = MagicMock(text="a", lemma_="a", pos_="DET", is_alpha=True)
    mock_token4 = MagicMock(text="company", lemma_="company", pos_="NOUN", is_alpha=True)
    mock_token5 = MagicMock(text=".", lemma_=".", pos_="PUNCT", is_alpha=False)
    mock_token6 = MagicMock(text="Steve", lemma_="steve", pos_="PROPN", is_alpha=True)
    mock_token7 = MagicMock(text="Jobs", lemma_="jobs", pos_="PROPN", is_alpha=True)
    mock_token8 = MagicMock(text="founded", lemma_="found", pos_="VERB", is_alpha=True)
    mock_token9 = MagicMock(text="Apple", lemma_="apple", pos_="PROPN", is_alpha=True)
    mock_token10 = MagicMock(text=". ", lemma_=".", pos_="PUNCT", is_alpha=False)
    mock_token11 = MagicMock(text="Summarize", lemma_="summarize", pos_="VERB", is_alpha=True)
    mock_token12 = MagicMock(text="this", lemma_="this", pos_="DET", is_alpha=True)
    mock_token13 = MagicMock(text="for", lemma_="for", pos_="ADP", is_alpha=True)
    mock_token14 = MagicMock(text="me", lemma_="me", pos_="PRON", is_alpha=True)
    mock_token15 = MagicMock(text=".", lemma_=".", pos_="PUNCT", is_alpha=False)

    mock_doc_with_entities.__iter__.return_value = [
        mock_token1,mock_token2,mock_token3,mock_token4,mock_token5,
        mock_token6,mock_token7,mock_token8,mock_token9,mock_token10,
        mock_token11,mock_token12,mock_token13,mock_token14,mock_token15
    ]

    # Mock side effect for sentence processing in average_sentence_length calculation
    def mock_nlp_side_effect_entities(text_input):
        if text_input == "Apple is a company.":
            mock_sent_doc = MagicMock()
            mock_sent_doc.__iter__.return_value = [
                MagicMock(text="Apple", is_alpha=True), MagicMock(text="is", is_alpha=True), MagicMock(text="a", is_alpha=True), MagicMock(text="company", is_alpha=True), MagicMock(text=".", is_alpha=False)
            ]
            return mock_sent_doc
        elif text_input == "Steve Jobs founded Apple.":
            mock_sent_doc = MagicMock()
            mock_sent_doc.__iter__.return_value = [
                MagicMock(text="Steve", is_alpha=True), MagicMock(text="Jobs", is_alpha=True), MagicMock(text="founded", is_alpha=True), MagicMock(text="Apple", is_alpha=True), MagicMock(text=".", is_alpha=False)
            ]
            return mock_sent_doc
        elif text_input == "Summarize this for me.":
            mock_sent_doc = MagicMock()
            mock_sent_doc.__iter__.return_value = [
                MagicMock(text="Summarize", is_alpha=True), MagicMock(text="this", is_alpha=True), MagicMock(text="for", is_alpha=True), MagicMock(text="me", is_alpha=True), MagicMock(text=".", is_alpha=False)
            ]
            return mock_sent_doc
        return MagicMock()
        
    mock_spacy_nlp.side_effect = mock_nlp_side_effect_entities

    # Now, override the mock_spacy_nlp behavior when called with the full text
    mock_spacy_nlp.return_value = mock_doc_with_entities


    signals = nlp_service.process_text(text)
    assert signals["named_entities"] == [("Apple", "ORG"), ("Steve Jobs", "PERSON")]
    assert signals["num_alphanumeric_tokens"] == 13 # Apple, is, a, company, Steve, Jobs, founded, Apple, Summarize, this, for, me
    assert signals["unique_words"] == 11 # apple, be, a, company, steve, jobs, found, summarize, this, for, me
    # Avg word length: (5+2+1+7+5+4+7+5+9+4+3+2)/12 = 54/12 = 4.5
    assert signals["average_word_length"] == pytest.approx(4.5)
    
    # Average sentence length: (4 words in "Apple is a company." + 4 words in "Steve Jobs founded Apple." + 4 words in "Summarize this for me.") / 3 = 12/3 = 4
    assert signals["average_sentence_length"] == pytest.approx(4.0)
    assert signals["detected_intent"] == Intent.SUMMARIZATION.value
    assert signals["intent_confidence"] == 0.9
    assert signals["inferred_user_state"] == UserState.NEUTRAL.value
    assert signals["user_state_confidence"] == 0.1

def test_process_text_multiple_paragraphs(nlp_service):
    """Test processing text with multiple paragraphs, including intent and user state detection."""
    text = "First paragraph.\n\nSecond paragraph. Explain this. I am confused."
    signals = nlp_service.process_text(text)
    assert signals["num_paragraphs"] == 2
    assert signals["detected_intent"] == Intent.CLARIFICATION.value
    assert signals["intent_confidence"] == 0.8
    assert signals["inferred_user_state"] == UserState.CONFUSED.value
    assert signals["user_state_confidence"] == 0.8

    text_single_newline = "First paragraph.\nSecond paragraph. Summarize this. I am interested in this."
    signals_single_newline = nlp_service.process_text(text_single_newline)
    assert signals_single_newline["num_paragraphs"] == 1 # Single newline is usually not a new paragraph.
    assert signals_single_newline["detected_intent"] == Intent.SUMMARIZATION.value
    assert signals_single_newline["intent_confidence"] == 0.9
    assert signals_single_newline["inferred_user_state"] == UserState.CURIOUS.value
    assert signals_single_newline["user_state_confidence"] == 0.7
