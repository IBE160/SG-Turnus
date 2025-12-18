from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base
import datetime
import uuid

class SharedStudyMaterial(Base):
    __tablename__ = "shared_study_materials"

    id = Column(Integer, primary_key=True, index=True)
    study_material_id = Column(Integer, ForeignKey("study_materials.id"), nullable=False)
    shared_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Nullable for public links
    share_token = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4())) # For public links
    permissions = Column(String, default="view") # e.g., "view", "edit"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True) # Optional expiration for links

    # Relationships
    study_material = relationship("StudyMaterial", back_populates="shares")
    shared_by = relationship("User", foreign_keys=[shared_by_user_id], back_populates="shares_made")
    shared_with = relationship("User", foreign_keys=[shared_with_user_id], back_populates="shares_received")
