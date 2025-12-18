import os
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from typing import List
from pydantic import BaseModel

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str

class QuizGenerationModule:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.5):
        """
        Initializes the QuizGenerationModule with an LLM and prompt templates.
        Args:
            model_name: The name of the OpenAI model to use.
            temperature: The sampling temperature for the LLM.
        """
        self.llm = None
        self.model_name = model_name
        self.temperature = temperature
        self.output_parser = JsonOutputParser()

        self.quiz_prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an expert in creating educational content. Your task is to generate a multiple-choice quiz from a given text. Each question should be a dictionary with 'question', 'options' (a list of 4 strings), and 'correct_answer' keys. Return a JSON list of these questions."),
                ("user", "Generate a quiz for the following text:\n\n{text}\n\nQuiz:")
            ]
        )

    def generate_quiz(self, text: str) -> List[QuizQuestion]:
        """
        Generates a quiz from the provided text using an LLM.
        Args:
            text: The input text to generate a quiz from.
        Returns:
            A list of QuizQuestion objects.
        """
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        if self.llm is None:
            self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)

        chain = self.quiz_prompt_template | self.llm | self.output_parser
        result = chain.invoke({"text": text})
        
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except json.JSONDecodeError:
                return []
        
        questions = [QuizQuestion(**item) for item in result]
        return questions

if __name__ == "__main__":
    if "OPENAI_API_KEY" not in os.environ:
        print("Please set the OPENAI_API_KEY environment variable.")
    else:
        quiz_generator = QuizGenerationModule()
        sample_text = """
        The Roman Empire was a vast and powerful civilization that ruled much of Europe and North Africa for over 1000 years.
        It was founded in 27 BC when Octavian became the first Roman Emperor, Augustus. The Empire was characterized by its
        strong military, advanced engineering, and sophisticated legal system. Its capital, Rome, was a thriving metropolis
        with impressive architecture, including the Colosseum and the Pantheon. The Pax Romana, a period of relative peace
        and stability, allowed the Empire to flourish and expand its influence. However, internal strife, economic problems,
        and external pressures from barbarian tribes eventually led to the decline and fall of the Western Roman Empire in 476 AD.
        The Eastern Roman Empire, also known as the Byzantine Empire, continued for another thousand years.
        """
        print("--- Generated Quiz ---")
        questions = quiz_generator.generate_quiz(sample_text)
        for i, question in enumerate(questions):
            print(f"Question {i+1}: {question.question}")
            for j, option in enumerate(question.options):
                print(f"  {chr(97+j)}) {option}")
            print(f"Correct Answer: {question.correct_answer}")
            print()