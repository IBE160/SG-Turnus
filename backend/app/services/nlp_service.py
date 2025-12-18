import spacy
from enum import Enum
from backend.app.core.ai.summarization_module import SummarizationModule
from backend.app.core.ai.flashcard_generation_module import FlashcardGenerationModule, Flashcard # Import Flashcard and FlashcardGenerationModule
from typing import List

# Define Intent categories
class Intent(str, Enum):
    CLARIFICATION = "Clarification"
    SUMMARIZATION = "Summarization"
    ACTIVE_RECALL = "Active Recall"
    PROBLEM_SOLVING = "Problem Solving"
    CONCEPT_LINKING = "Concept Linking"
    MISCONCEPTION_CORRECTION = "Misconception Correction"
    UNKNOWN = "Unknown"

# Define User State categories
class UserState(str, Enum):
    CONFUSED = "Confused"
    CURIOUS = "Curious"
    OVERLOADED = "Overloaded"
    TIME_LIMITED = "Time Limited"
    UNCERTAIN = "Uncertain"
    NEUTRAL = "Neutral" # Default state if no specific state is inferred

class NLPService:
    def __init__(self):
        # Load the English spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        self.summarization_module = SummarizationModule()
        self.flashcard_generation_module = FlashcardGenerationModule() # Initialize FlashcardGenerationModule

    def detect_intent(self, text: str, tokens: list[str], found_question_words: list[str]) -> tuple[Intent, float]:
        """
        Placeholder for intent detection.
        Uses simple keyword matching to determine intent.
        """
        lower_tokens = [token.lower() for token in tokens]

        # Rule for Summarization
        if "summarize" in lower_tokens or "summary" in lower_tokens:
            return Intent.SUMMARIZATION, 0.9

        # Rule for Active Recall (e.g., "quiz", "test me", "flashcards")
        if "quiz" in lower_tokens or "test" in lower_tokens or "flashcards" in lower_tokens: # Added "flashcards"
            return Intent.ACTIVE_RECALL, 0.7

        # Rule for Clarification (e.g., "what is", "explain")
        if any(q_word in found_question_words for q_word in ["what", "how"]) or \
           "explain" in lower_tokens or "define" in lower_tokens:
            return Intent.CLARIFICATION, 0.8
        
        # Rule for Problem Solving (e.g., "solve", "how to")
        if "solve" in lower_tokens or ("how" in lower_tokens and "to" in lower_tokens):
            return Intent.PROBLEM_SOLVING, 0.7

        # Rule for Concept Linking (e.g., "relate", "connect")
        if "relate" in lower_tokens or "connect" in lower_tokens:
            return Intent.CONCEPT_LINKING, 0.6
        
        # Rule for Misconception Correction (e.g., "is it true", "wrong")
        if "true" in lower_tokens or "false" in lower_tokens or "wrong" in lower_tokens:
            return Intent.MISCONCEPTION_CORRECTION, 0.6

        return Intent.UNKNOWN, 0.1 # Default if no specific intent is found

    def infer_user_state(self, text: str, tokens: list[str], detected_intent: Intent) -> tuple[UserState, float]:
        """
        Placeholder for user state inference.
        Uses simple keyword matching and detected intent.
        """
        lower_text = text.lower()
        lower_tokens = [token.lower() for token in tokens]

        # Confused
        if "confused" in lower_text or "i don't understand" in lower_text or \
           (detected_intent == Intent.CLARIFICATION and "what" in lower_tokens):
            return UserState.CONFUSED, 0.8

        # Curious
        if "tell me more" in lower_text or "interested in" in lower_text or \
           detected_intent == Intent.CONCEPT_LINKING:
            return UserState.CURIOUS, 0.7

        # Overloaded
        if "too much information" in lower_text or "overwhelmed" in lower_text or \
           "simplify" in lower_tokens:
            return UserState.OVERLOADED, 0.7
        
        # Time Limited
        if "quickly" in lower_text or "in a nutshell" in lower_text or \
           "briefly" in lower_tokens:
            return UserState.TIME_LIMITED, 0.6

        # Uncertain
        if "maybe" in lower_text or "i think so" in lower_text or "not sure" in lower_text:
            return UserState.UNCERTAIN, 0.6

        return UserState.NEUTRAL, 0.1 # Default if no specific state is inferred


    def process_text(self, text: str) -> dict:
        doc = self.nlp(text)

        # 1. Lexical Indicators (keywords, question words)
        tokens = [token.text for token in doc]
        lemmas = [token.lemma_ for token in doc]
        pos_tags = [token.pos_ for token in doc]
        
        # Identify question words (simple heuristic)
        question_words = ["who", "what", "where", "when", "why", "how", "which", "whom", "whose"]
        found_question_words = [token.text.lower() for token in doc if token.text.lower() in question_words]

        # 2. Structural Elements (sentences/paragraphs)
        sentences = [sent.text for sent in doc.sents]
        num_sentences = len(sentences)
        num_paragraphs = text.count('\n\n') + 1 # Simple heuristic for paragraphs

        # 3. Content Density and Complexity
        # Number of alphanumeric tokens
        alphanumeric_tokens = [token for token in doc if token.is_alpha]
        num_alphanumeric_tokens = len(alphanumeric_tokens)
        
        # Number of unique words (ignoring case)
        unique_words = len(set([token.text.lower() for token in alphanumeric_tokens]))

        # Average word length
        total_word_length = sum(len(token.text) for token in alphanumeric_tokens)
        average_word_length = total_word_length / num_alphanumeric_tokens if num_alphanumeric_tokens > 0 else 0

        # Average sentence length (in words)
        sentence_lengths = [len([token for token in self.nlp(sent).doc if token.is_alpha]) for sent in sentences]
        average_sentence_length = sum(sentence_lengths) / num_sentences if num_sentences > 0 else 0
        
        # More advanced: Named Entity Recognition (NER)
        named_entities = [(ent.text, ent.label_) for ent in doc.ents]

        # Detect intent
        detected_intent, intent_confidence = self.detect_intent(text, tokens, found_question_words)

        # Infer user state
        inferred_user_state, user_state_confidence = self.infer_user_state(text, tokens, detected_intent)

        signals = {
            "original_text": text,
            "tokens": tokens,
            "lemmas": lemmas,
            "pos_tags": pos_tags,
            "found_question_words": list(set(found_question_words)), # Remove duplicates
            "sentences": sentences,
            "num_sentences": num_sentences,
            "num_paragraphs": num_paragraphs,
            "num_alphanumeric_tokens": num_alphanumeric_tokens,
            "unique_words": unique_words,
            "average_word_length": average_word_length,
            "average_sentence_length": average_sentence_length,
            "named_entities": named_entities,
            "detected_intent": detected_intent.value, # Store as string for Pydantic
            "intent_confidence": intent_confidence,
            "inferred_user_state": inferred_user_state.value, # Store as string for Pydantic
            "user_state_confidence": user_state_confidence
        }
        return signals

    def get_summary(self, text: str, detail_level: str = "normal") -> str:
        """
        Generates a summary of the given text using the SummarizationModule.
        """
        return self.summarization_module.generate_summary(text, detail_level)

    def get_flashcards(self, text: str) -> List[Flashcard]: # New method
        """
        Generates flashcards from the given text using the FlashcardGenerationModule.
        """
        return self.flashcard_generation_module.generate_flashcards(text)
