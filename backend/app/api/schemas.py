from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional, Dict
import datetime

class UserRegistration(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    token: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class InteractionPatternType(str, Enum):
    """
    Defines the types of first interaction patterns the AI can use.
    """
    ANCHOR_QUESTION = "anchor_question"
    MICRO_EXPLANATION = "micro_explanation"
    CALIBRATION_QUESTION = "calibration_question"
    PROBLEM_DECOMPOSITION = "problem_decomposition"
    CONCEPT_SNAPSHOT = "concept_snapshot"
    # Add other patterns as they are defined

class NextStep(BaseModel): # Renamed from NextStepContent
    """
    Base model for the content of a next step, allowing for different types
    of responses (e.g., text, structured data for a question).
    """
    type: str
    data: Dict

class ClarityResponse(BaseModel):
    """
    Represents the AI's response after processing a user's query,
    including the action to be taken and the content of the response.
    """
    action: str # e.g., "direct_response", "uncertainty_handling", "generate_materials"
    content: str # This will hold the direct string response for now,
                 # but could be a more complex object (e.g., NextStep)

class StudyMaterialCreate(BaseModel):
    file_name: str
    s3_key: str

class StudyMaterialResponse(BaseModel):
    id: int
    user_id: int
    file_name: str
    s3_key: str
    upload_date: datetime.datetime
    processing_status: str

    class Config:
        orm_mode = True # Enable ORM mode for automatic mapping

class StudyMaterialUpdate(BaseModel):
    file_name: Optional[str] = None
    s3_key: Optional[str] = None
    processing_status: Optional[str] = None

class NLPRequest(BaseModel):
    text: str

class NLPSignalsResponse(BaseModel):
    lexical_signals: Dict
    structural_signals: Dict
    content_density: Dict