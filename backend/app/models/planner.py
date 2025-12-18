from pydantic import BaseModel
from enum import Enum
from typing import Dict

class AIModule(str, Enum):
    SUMMARIZATION = "SummarizationModule"
    FLASHCARD_GENERATION = "FlashcardGenerationModule"
    QUIZ_GENERATION = "QuizGenerationModule"
    QA = "QAModule"
    # Add other modules as they are defined

class InteractionPatternType(str, Enum):
    """
    Defines the types of first interaction patterns the AI can use.
    """
    ANCHOR_QUESTION = "anchor_question"
    MICRO_EXPLANATION = "micro_explanation"
    CALIBRATION_QUESTION = "calibration_question"
    PROBLEM_DECOMPOSITION = "problem_decomposition"
    CONCEPT_SNAPSHOT = "concept_snapshot"
    # Add other patterns as they are defined

class NextStep(BaseModel):
    """
    Base model for the content of a next step, allowing for different types
    of responses (e.g., text, structured data for a question).
    """
    ai_module: AIModule
    interaction_pattern: InteractionPatternType
    parameters: Dict
