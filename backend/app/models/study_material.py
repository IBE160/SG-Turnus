from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema: dict):
        field_schema.update(type="string")

class StudyMaterial(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(...)
    title: str = Field(...)
    content: str = Field(...)
    type: str = Field(...) # e.g., 'summary', 'flashcard', 'original_upload'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "user_id": "60a7d5b1b4c5d6e7f8a9b0c1",
                "title": "Introduction to Quantum Physics Summary",
                "content": "Quantum physics is a fundamental theory...",
                "type": "summary",
                "created_at": "2025-12-01T12:00:00Z",
                "updated_at": "2025-12-01T12:00:00Z",
            }
        }
