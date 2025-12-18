import io
from typing import Tuple, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

# Import generated material models
from backend.app.models.generated_summary import GeneratedSummary
from backend.app.models.generated_flashcard_set import GeneratedFlashcardSet
from backend.app.models.generated_quiz import GeneratedQuiz

# Import document generation libraries
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from docx import Document
import csv

class ExportService:
    def __init__(self, db: Session):
        self.db = db

    async def export_material(
        self, user_id: int, material_type: str, material_id: int, format: str
    ) -> Tuple[Any, str, str]:
        """
        Fetches the specified generated material, converts it to the requested format,
        and returns the file content, media type, and filename.
        """
        material = None
        file_name_prefix = ""

        if material_type == "summary":
            material = (
                self.db.query(GeneratedSummary)
                .filter(GeneratedSummary.id == material_id)
                .join(GeneratedSummary.study_material)
                .filter(GeneratedSummary.study_material.has(user_id=user_id))
                .first()
            )
            file_name_prefix = "summary"
        elif material_type == "flashcard_set":
            material = (
                self.db.query(GeneratedFlashcardSet)
                .filter(GeneratedFlashcardSet.id == material_id)
                .join(GeneratedFlashcardSet.study_material)
                .filter(GeneratedFlashcardSet.study_material.has(user_id=user_id))
                .first()
            )
            file_name_prefix = "flashcards"
        elif material_type == "quiz":
            material = (
                self.db.query(GeneratedQuiz)
                .filter(GeneratedQuiz.id == material_id)
                .join(GeneratedQuiz.study_material)
                .filter(GeneratedQuiz.study_material.has(user_id=user_id))
                .first()
            )
            file_name_prefix = "quiz"
        else:
            raise ValueError("Invalid material type provided for export.")

        if not material:
            raise ValueError("Generated material not found or unauthorized access.")

        # Generate base file name
        base_file_name = f"{file_name_prefix}_{material.study_material.file_name.split('.')[0]}"

        if format == "pdf":
            return self._generate_pdf(material, base_file_name), "application/pdf", f"{base_file_name}.pdf"
        elif format == "docx":
            return self._generate_docx(material, base_file_name), "application/vnd.openxmlformats-officedocument.wordprocessingml.document", f"{base_file_name}.docx"
        elif format == "csv":
            if material_type not in ["flashcard_set", "quiz"]:
                raise ValueError("CSV export is only supported for flashcard sets and quizzes.")
            return self._generate_csv(material, base_file_name, material_type), "text/csv", f"{base_file_name}.csv"
        else:
            raise ValueError("Unsupported export format.")

    def _generate_pdf(self, material: Any, base_file_name: str) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph(f"<h1>{base_file_name.replace('_', ' ').title()}</h1>", styles['h1']))
        story.append(Spacer(1, 0.2 * 10))

        if isinstance(material, GeneratedSummary):
            story.append(Paragraph(material.content, styles['Normal']))
        elif isinstance(material, GeneratedFlashcardSet):
            story.append(Paragraph("<h3>Flashcards:</h3>", styles['h3']))
            for i, flashcard in enumerate(material.content):
                story.append(Paragraph(f"<b>Q{i+1}:</b> {flashcard['question']}", styles['Normal']))
                story.append(Paragraph(f"<b>A{i+1}:</b> {flashcard['answer']}", styles['Normal']))
                story.append(Spacer(1, 0.1 * 10))
        elif isinstance(material, GeneratedQuiz):
            story.append(Paragraph("<h3>Quiz:</h3>", styles['h3']))
            for i, question in enumerate(material.content):
                story.append(Paragraph(f"<b>Q{i+1}:</b> {question['question']}", styles['Normal']))
                if 'options' in question and question['options']:
                    for opt_idx, option in enumerate(question['options']):
                        story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{chr(97+opt_idx)}. {option}", styles['Normal']))
                story.append(Paragraph(f"<b>Correct Answer:</b> {question['correct_answer']}", styles['Normal']))
                story.append(Spacer(1, 0.1 * 10))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _generate_docx(self, material: Any, base_file_name: str) -> bytes:
        document = Document()
        document.add_heading(base_file_name.replace('_', ' ').title(), level=1)

        if isinstance(material, GeneratedSummary):
            document.add_paragraph(material.content)
        elif isinstance(material, GeneratedFlashcardSet):
            document.add_heading("Flashcards:", level=3)
            for i, flashcard in enumerate(material.content):
                document.add_paragraph(f"Q{i+1}: {flashcard['question']}", style='List Number')
                document.add_paragraph(f"A{i+1}: {flashcard['answer']}")
        elif isinstance(material, GeneratedQuiz):
            document.add_heading("Quiz:", level=3)
            for i, question in enumerate(material.content):
                document.add_paragraph(f"Q{i+1}: {question['question']}", style='List Number')
                if 'options' in question and question['options']:
                    for opt_idx, option in enumerate(question['options']):
                        document.add_paragraph(f"  {chr(97+opt_idx)}. {option}")
                document.add_paragraph(f"Correct Answer: {question['correct_answer']}")
        
        buffer = io.BytesIO()
        document.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def _generate_csv(self, material: Any, base_file_name: str, material_type: str) -> bytes:
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        if material_type == "flashcard_set":
            writer.writerow(["Question", "Answer"])
            for flashcard in material.content:
                writer.writerow([flashcard['question'], flashcard['answer']])
        elif material_type == "quiz":
            writer.writerow(["Question", "Option A", "Option B", "Option C", "Option D", "Correct Answer"])
            for question in material.content:
                options = question.get('options', [])
                row = [question['question']] + options + [''] * (4 - len(options)) # Pad to 4 options
                row.append(question['correct_answer'])
                writer.writerow(row)
        
        return buffer.getvalue().encode('utf-8')
