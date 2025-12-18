import os
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

class Flashcard(BaseModel):
    """Represents a single flashcard with a question and an answer."""
    question: str = Field(..., description="The question side of the flashcard.")
    answer: str = Field(..., description="The answer side of the flashcard.")

class FlashcardGenerationModule:
    def __init__(self, model_name: str = "gpt-4o", temperature: float = 0.5):
        """
        Initializes the FlashcardGenerationModule with an LLM and prompt template.
        Args:
            model_name: The name of the OpenAI model to use.
            temperature: The sampling temperature for the LLM (lower for more factual/less creative).
        """
        self.llm = None
        self.model_name = model_name
        self.temperature = temperature
        # Using StrOutputParser for initial output, will parse string into Flashcard objects
        self.output_parser = StrOutputParser() 

        self.flashcard_prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", 
                 "You are an expert in generating concise and clear flashcards (question-answer pairs) from text. "
                 "For the given text, identify key concepts, terms, and facts, and formulate them into flashcards. "
                 "Each flashcard should consist of a single question and a direct, concise answer. "
                 "Format your output as a numbered list, where each item is 'Question: [Your Question]\nAnswer: [Your Answer]'.\n"
                 "Ensure to generate at least 3-5 flashcards, focusing on distinct concepts.\n"
                 "Example:\n1. Question: What is photosynthesis?\nAnswer: The process by which green plants and some other organisms use sunlight to synthesize foods.\n"
                 "2. Question: Where does photosynthesis occur?\nAnswer: In the chloroplasts of plant cells."),
                ("user", "Generate flashcards from the following text:\n\n{text}\n\nFlashcards:")
            ]
        )

    def generate_flashcards(self, text: str) -> List[Flashcard]:
        """
        Generates a list of flashcards from the provided text using an LLM.
        Args:
            text: The input text from which to generate flashcards.
        Returns:
            A list of Flashcard objects.
        """
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")

        if self.llm is None:
            self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)

        chain = self.flashcard_prompt_template | self.llm | self.output_parser
        llm_output = chain.invoke({"text": text})
        
        return self._parse_llm_output_to_flashcards(llm_output)

    def _parse_llm_output_to_flashcards(self, llm_output: str) -> List[Flashcard]:
        """
        Parses the LLM's raw string output into a list of Flashcard objects.
        Assumes the format: "1. Question: ...\nAnswer: ...\n2. Question: ..."
        """
        flashcards = []
        # Split by "Question:" to handle each flashcard entry
        entries = llm_output.split("Question:")
        
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            
            
            # Remove any leading numbering or "Question:" prefix
            # Use regex to handle potential variations in numbering (e.g., "1.", "2)", "1-")
            match_num = re.match(r"^\d+[\.\)]?\s*", entry)
            if match_num:
                entry = entry[match_num.end():].strip()
            
            # Now, ensure we only take the part after "Question:" for the question
            question_prefix_idx = entry.lower().find("question:")
            if question_prefix_idx != -1:
                question_start = question_prefix_idx + len("question:")
                remaining_entry = entry[question_start:].strip()
            else:
                remaining_entry = entry # Assume the entry directly starts with the question if no "Question:" prefix found

            answer_start_idx = remaining_entry.lower().find("answer:")
            if answer_start_idx == -1:
                continue
            
            question = remaining_entry[:answer_start_idx].strip()
            answer = remaining_entry[answer_start_idx:].replace("Answer:", "", 1).strip() # Replace only the first occurrence

            if question and answer:
                flashcards.append(Flashcard(question=question, answer=answer))
        
        return flashcards

if __name__ == "__main__":
    # Example usage (requires OPENAI_API_KEY environment variable to be set)
    if "OPENAI_API_KEY" not in os.environ:
        print("Please set the OPENAI_API_KEY environment variable.")
    else:
        generator = FlashcardGenerationModule()
        sample_text = """
        Photosynthesis is a process used by plants and other organisms to convert light energy into chemical energy that,
        through cellular respiration, can later be released to fuel the organism's metabolic activities. This chemical
        energy is stored in carbohydrate molecules, such as sugars, which are synthesized from carbon dioxide and water.
        In most cases, oxygen is released as a waste product. Most plants, algae, and cyanobacteria perform photosynthesis;
        such organisms are called photoautotrophs. Photosynthesis is largely responsible for producing and maintaining
        the oxygen content of the Earth's atmosphere, and supplies all organic compounds and most of the energy necessary
        for life on Earth.
        """
        print("--- Generated Flashcards ---")
        generated_flashcards = generator.generate_flashcards(sample_text)
        for i, fc in enumerate(generated_flashcards):
            print(f"{i+1}. Question: {fc.question}")
            print(f"   Answer: {fc.answer}")
