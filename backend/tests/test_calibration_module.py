# backend/tests/test_calibration_module.py

import pytest
from backend.app.core.ai.calibration_module import CalibrationModule

@pytest.fixture
def calibration_module():
    """Returns an instance of the CalibrationModule."""
    return CalibrationModule()

def test_generate_question_with_context(calibration_module):
    """
    Tests that generate_question returns a formatted string when context is provided.
    """
    user_input = "What about the kernel?"
    context = {"key_term": "kernel", "topic": "Operating Systems"}
    question = calibration_module.generate_question(user_input, context)

    assert isinstance(question, str)
    assert context["key_term"] in question
    # Check that it's not the fallback question
    assert "Could you please provide more context" not in question

def test_generate_question_missing_key_term(calibration_module):
    """
    Tests the fallback behavior when 'key_term' is missing from the context.
    """
    user_input = "Tell me more."
    context = {"topic": "Computer Science"}
    question = calibration_module.generate_question(user_input, context)
    assert question == "Could you please provide more context or clarify your question?"

def test_generate_question_missing_topic(calibration_module):
    """
    Tests the fallback behavior when 'topic' is missing from the context.
    """
    user_input = "What is a mutex?"
    context = {"key_term": "mutex"}
    question = calibration_module.generate_question(user_input, context)
    assert question == "Could you please provide more context or clarify your question?"

def test_generate_question_empty_context(calibration_module):
    """
    Tests the fallback behavior when the context dictionary is empty.
    """
    user_input = "Explain."
    context = {}
    question = calibration_module.generate_question(user_input, context)
    assert question == "Could you please provide more context or clarify your question?"

def test_generate_question_uses_templates(calibration_module):
    """
    Tests that the generated question is one of the available templates.
    """
    user_input = "What is polymorphism?"
    context = {"key_term": "polymorphism", "topic": "Object-Oriented Programming"}
    
    # Run it a few times to increase confidence that it's using the templates
    for _ in range(10):
        question = calibration_module.generate_question(user_input, context)
        # Check if the generated question, after substituting the context, matches any of the templates
        found_match = False
        for template in calibration_module.templates:
            expected_question = template.format(term=context["key_term"], topic=context["topic"])
            if question == expected_question:
                found_match = True
                break
        assert found_match, f"Generated question '{question}' does not match any template."
