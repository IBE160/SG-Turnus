import pytest
from backend.app.services.planner_service import PlannerService
from backend.app.services.nlp_service import Intent, UserState
from backend.app.models.planner import AIModule, InteractionPatternType

@pytest.fixture
def planner_service():
    return PlannerService()

def test_select_next_step_summarization(planner_service):
    next_step = planner_service.select_next_step(Intent.SUMMARIZATION, UserState.NEUTRAL, 0.9)
    assert next_step.ai_module == AIModule.SUMMARIZATION
    assert next_step.interaction_pattern == InteractionPatternType.MICRO_EXPLANATION
    assert next_step.parameters == {"detail_level": "brief"}

def test_select_next_step_active_recall_confused(planner_service):
    next_step = planner_service.select_next_step(Intent.ACTIVE_RECALL, UserState.CONFUSED, 0.9)
    assert next_step.ai_module == AIModule.QUIZ_GENERATION
    assert next_step.interaction_pattern == InteractionPatternType.CALIBRATION_QUESTION

def test_select_next_step_active_recall_neutral(planner_service):
    next_step = planner_service.select_next_step(Intent.ACTIVE_RECALL, UserState.NEUTRAL, 0.9)
    assert next_step.ai_module == AIModule.FLASHCARD_GENERATION
    assert next_step.interaction_pattern == InteractionPatternType.CONCEPT_SNAPSHOT

def test_select_next_step_clarification(planner_service):
    next_step = planner_service.select_next_step(Intent.CLARIFICATION, UserState.NEUTRAL, 0.9)
    assert next_step.ai_module == AIModule.QA
    assert next_step.interaction_pattern == InteractionPatternType.ANCHOR_QUESTION

def test_select_next_step_unknown(planner_service):
    next_step = planner_service.select_next_step(Intent.UNKNOWN, UserState.NEUTRAL, 0.2)
    assert next_step.ai_module == AIModule.SUMMARIZATION
    assert next_step.interaction_pattern == InteractionPatternType.MICRO_EXPLANATION
    assert next_step.parameters == {"detail_level": "normal"}