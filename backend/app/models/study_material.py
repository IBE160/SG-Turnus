from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.app.database import Base
from backend.app.models.user import User # Import User for relationship
import datetime

class StudyMaterial(Base):
    __tablename__ = "study_materials"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    processing_status = Column(String, default="pending") # e.g., 'pending', 'processing', 'complete', 'failed'

    # Relationship to User
    owner = relationship("User", back_populates="study_materials")