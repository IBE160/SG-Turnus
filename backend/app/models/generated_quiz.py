from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.database import Base
import datetime

class GeneratedQuiz(Base):
    __tablename__ = "generated_quizzes"

    id = Column(Integer, primary_key=True, index=True)
    study_material_id = Column(Integer, ForeignKey("study_materials.id"), nullable=False)
    # Storing quiz as a JSON array of {question: string, options: string[], correct_answer: string}
    content = Column(JSON, nullable=False) 
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to StudyMaterial
    study_material = relationship("StudyMaterial", back_populates="generated_quizzes")