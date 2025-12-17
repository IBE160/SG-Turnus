# backend/app/core/ai/calibration_module.py

import random

class CalibrationModule:
    """
    Module responsible for generating calibration questions when the AI's
    confidence is low.
    """

    def __init__(self):
        """
        Initializes the CalibrationModule with a set of question templates.
        """
        self.templates = [
            "Just to be sure, when you mention '{term}', are you referring to its definition in the context of {topic}?",
            "I'm seeing a couple of ways to interpret '{term}'. Could you clarify what you mean by it?",
            "To give you the best answer, could you tell me more about what you're looking for regarding '{term}'?",
            "What do you think the most important aspect of '{term}' is in this context?",
            "Help me understand your perspective better: how does '{term}' relate to the main subject?"
        ]

    def generate_question(self, user_input: str, inferred_context: dict) -> str:
        """
        Generates a calibration question based on the user input and context.

        For this initial version, it randomly selects a template and populates
        it with a term from the context. A more advanced version would use
        LangChain and a proper LLM.

        Args:
            user_input: The original input from the user.
            inferred_context: A dictionary containing inferred information,
                              such as key terms and the topic. Expected keys:
                              'key_term' and 'topic'.

        Returns:
            A formatted calibration question.
        """
        if not inferred_context.get("key_term") or not inferred_context.get("topic"):
            # Fallback if context is missing
            return "Could you please provide more context or clarify your question?"

        template = random.choice(self.templates)
        question = template.format(
            term=inferred_context["key_term"],
            topic=inferred_context["topic"]
        )
        return question

# Example of how this might be used
if __name__ == '__main__':
    calibration_module = CalibrationModule()
    user_query = "Tell me about memory management in operating systems."
    context = {"key_term": "memory management", "topic": "operating systems"}

    for _ in range(3):
        question = calibration_module.generate_question(user_query, context)
        print(question)

    # Example with missing context
    no_context_question = calibration_module.generate_question("What is it?", {})
    print(f"\nNo context scenario: {no_context_question}")
