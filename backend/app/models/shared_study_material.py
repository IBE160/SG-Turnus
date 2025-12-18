from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from backend.app.database import Base
import datetime

class SharedStudyMaterial(Base):
    __tablename__ = "shared_study_materials"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    study_material_id = Column(Integer, ForeignKey("study_materials.id"), nullable=False)
    shared_with_user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # For direct shares
    share_token = Column(String, unique=True, index=True, nullable=True) # For public links
    permissions = Column(String, nullable=False, default="view_only") # e.g., "view_only", "edit"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    owner = relationship("User", foreign_keys=[owner_user_id], back_populates="owned_shares")
    shared_with = relationship("User", foreign_keys=[shared_with_user_id], back_populates="received_shares")
    study_material = relationship("StudyMaterial", back_populates="shares")