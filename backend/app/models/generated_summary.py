from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database import Base
import datetime

class GeneratedSummary(Base):
    __tablename__ = "generated_summaries"

    id = Column(Integer, primary_key=True, index=True)
    study_material_id = Column(Integer, ForeignKey("study_materials.id"), nullable=False)
    content = Column(Text, nullable=False)
    detail_level = Column(String, nullable=True) # e.g., 'normal', 'brief', 'detailed'
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationship to StudyMaterial
    study_material = relationship("StudyMaterial", back_populates="generated_summaries")