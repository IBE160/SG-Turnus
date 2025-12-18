import os
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class QuizQuestion(BaseModel):
    """Represents a single quiz question with multiple-choice options and a correct answer."""
    question: str = Field(..., description="The quiz question.")
    options: List[str] = Field(..., description="A list of possible answers for the multiple-choice question.")
    correct_answer: str = Field(..., description="The correct answer among the options.")

class QuizGenerationModule:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.5):
        """
        Initializes the QuizGenerationModule with an LLM and prompt template.
        Args:
            model_name: The name of the OpenAI model to use.
            temperature: The sampling temperature for the LLM (lower for more factual/less creative).
        """
        self.llm = None
        self.model_name = model_name
        self.temperature = temperature
        self.output_parser = StrOutputParser()

        self.quiz_prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", 
                 "You are an expert in generating concise and clear multiple-choice quiz questions from text. "
                 "For the given text, identify key concepts, terms, and facts, and formulate them into quiz questions. "
                 "Each question should have a single correct answer and 3 plausible, but incorrect, distractor options. "
                 "Format your output as a numbered list, where each item is:\n"
                 "Question: [Your Question]\n"
                 "Options:\n"
                 "  A. [Option A]\n"
                 "  B. [Option B]\n"
                 "  C. [Option C]\n"
                 "  D. [Option D]\n"
                 "Correct Answer: [Letter of the correct option, e.g., A, B, C, or D]\n"
                 "Ensure to generate at least 2-3 questions.\n"
                 "Example:\n"
                 "1. Question: What is the capital of France?\n"
                 "Options:\n"
                 "  A. Berlin\n"
                 "  B. Madrid\n"
                 "  C. Paris\n"
                 "  D. Rome\n"
                 "Correct Answer: C\n"
                ),
                ("user", "Generate quiz questions from the following text:\n\n{text}\n\nQuiz Questions:")
            ]
        )

    def generate_quiz(self, text: str) -> List[QuizQuestion]:
        """
        Generates a list of quiz questions from the provided text using an LLM.
        Args:
            text: The input text from which to generate quiz questions.
        Returns:
            A list of QuizQuestion objects.
        """
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        if self.llm is None:
            self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)

        chain = self.quiz_prompt_template | self.llm | self.output_parser
        llm_output = chain.invoke({"text": text})
        
        return self._parse_llm_output_to_quiz_questions(llm_output)

    def _parse_llm_output_to_quiz_questions(self, llm_output: str) -> List[QuizQuestion]:
        """
        Parses the LLM's raw string output into a list of QuizQuestion objects.
        Assumes the format: "1. Question: ...\nOptions:\n  A. ...\n  B. ...\n  C. ...\n  D. ...\nCorrect Answer: ..."
        """
        quiz_questions = []
        question_blocks = llm_output.split("Question:")
        
        for block in question_blocks:
            block = block.strip()
            if not block:
                continue

            # Remove numbering like "1. "
            import re
            match_num = re.match(r"^\d+[\.\)]?\s*", block)
            if match_num:
                block = block[match_num.end():].strip()
            
            question_text = ""
            options = []
            correct_answer = ""

            # Split the block into lines and parse
            lines = block.split('\n')
            
            i = 0
            # Parse Question
            if lines[i].strip().endswith('?'): # Simple heuristic for question line
                question_text = lines[i].strip()
                i += 1
            
            # Parse Options
            if i < len(lines) and lines[i].strip() == "Options:":
                i += 1
                while i < len(lines) and re.match(r"^[A-D]\.\s", lines[i].strip()):
                    options.append(lines[i].strip()[3:].strip()) # Remove "A. ", "B. " etc.
                    i += 1
            
            # Parse Correct Answer
            if i < len(lines) and lines[i].strip().startswith("Correct Answer:"):
                correct_answer_raw = lines[i].strip()[len("Correct Answer:"):].strip()
                # Extract just the letter (e.g., "C" from "C. Paris")
                match_correct_letter = re.match(r"^[A-D]", correct_answer_raw)
                if match_correct_letter:
                    correct_answer = match_correct_letter.group(0)
                    
                    # Find the full correct answer from the options
                    for opt_idx, opt_text in enumerate(options):
                        if chr(65 + opt_idx) == correct_answer: # 'A' is ASCII 65
                            correct_answer = opt_text # Store the full text of the correct answer
                            break
                    
            if question_text and options and correct_answer:
                quiz_questions.append(QuizQuestion(question=question_text, options=options, correct_answer=correct_answer))
        
        return quiz_questions

if __name__ == "__main__":
    # Example usage (requires OPENAI_API_KEY environment variable to be set)
    if "OPENAI_API_KEY" not in os.environ:
        print("Please set the OPENAI_API_KEY environment variable.")
    else:
        generator = QuizGenerationModule()
        sample_text = """
The capital of France is Paris. Paris is known for its art, fashion, gastronomy, and culture.
It is home to the Eiffel Tower, the Louvre Museum, and Notre-Dame Cathedral. The river Seine
flows through Paris. France is a country located in Western Europe.
"""
        print("--- Generated Quiz Questions ---")
        generated_quiz = generator.generate_quiz(sample_text)
        for i, q in enumerate(generated_quiz):
            print(f"{i+1}. Question: {q.question}")
            print("   Options:")
            for j, opt in enumerate(q.options):
                print(f"     {chr(65 + j)}. {opt}")
            print(f"   Correct Answer: {q.correct_answer}")
            print("-" * 20)
