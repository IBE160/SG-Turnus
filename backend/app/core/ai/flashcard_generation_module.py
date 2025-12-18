import os
import json
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field

# Define a Pydantic model for a Flashcard
class Flashcard(BaseModel):
    question: str = Field(description="The question for the flashcard")
    answer: str = Field(description="The answer to the flashcard question")

# Define a Pydantic model for the list of Flashcards
class FlashcardList(BaseModel):
    flashcards: List[Flashcard] = Field(description="A list of generated flashcards")

class FlashcardGenerationModule:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.5):
        """
        Initializes the FlashcardGenerationModule with an LLM and prompt templates.
        Args:
            model_name: The name of the OpenAI model to use.
            temperature: The sampling temperature for the LLM (lower for more factual/less creative).
        """
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature)
        # Using StrOutputParser for now, will process JSON string manually
        self.output_parser = StrOutputParser() 

        self.flashcard_prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", 
                 "You are an expert at generating flashcards from text. "
                 "Your task is to identify key concepts and facts from the provided text "
                 "and formulate them into concise question-answer pairs. "
                 "Ensure the questions are clear and the answers are direct and accurate. "
                 "Respond only with a JSON array of objects, where each object has a 'question' and an 'answer' key. "
                 "Example: [{ \"question\": \"What is X?\", \"answer\": \"Y\" }]"),
                ("user", "Generate flashcards from the following text:\n\n{text}\n\nFlashcards (JSON format):")
            ]
        )

    def generate_flashcards(self, text: str) -> List[Flashcard]:
        """
        Generates flashcards from the provided text using an LLM.
        Args:
            text: The input text from which to generate flashcards.
        Returns:
            A list of Flashcard objects.
        """
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        chain = self.flashcard_prompt_template | self.llm | self.output_parser
        json_string = chain.invoke({"text": text})

        try:
            # The LLM is instructed to return JSON, so we attempt to parse it.
            flashcard_data = json.loads(json_string)
            # Validate with Pydantic model
            flashcard_list = FlashcardList(flashcards=flashcard_data)
            return flashcard_list.flashcards
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM: {e}")
            print(f"LLM output: {json_string}")
            raise ValueError("Failed to parse flashcards from LLM output. Invalid JSON format.")
        except Exception as e:
            print(f"An unexpected error occurred during flashcard parsing: {e}")
            print(f"LLM output: {json_string}")
            raise

if __name__ == "__main__":
    # Example usage (requires OPENAI_API_KEY environment variable to be set)
    if "OPENAI_API_KEY" not in os.environ:
        print("Please set the OPENAI_API_KEY environment variable.")
    else:
        generator = FlashcardGenerationModule()
        sample_text = """
        Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that,
        through cellular respiration, can later be released to fuel the organism's metabolic activities. This chemical energy
        is stored in carbohydrate molecules, such as sugars, which are synthesized from carbon dioxide and water – hence the
        name photosynthesis, from the Greek φῶς, phōs, "light", and σύνθεσις, synthesis, "putting together".
        Most plants, algae, and cyanobacteria perform photosynthesis; such organisms are called photoautotrophs.
        Photosynthesis maintains atmospheric oxygen levels and supplies all of the organic compounds and most of the energy
        necessary for life on Earth.
        """
        print("--- Generating Flashcards ---")
        try:
            flashcards = generator.generate_flashcards(sample_text)
            for i, fc in enumerate(flashcards):
                print(f"Flashcard {i+1}:")
                print(f"  Q: {fc.question}")
                print(f"  A: {fc.answer}")
                print("-" * 20)
        except ValueError as e:
            print(f"Error: {e}")
