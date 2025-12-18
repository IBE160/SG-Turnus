from pydantic import BaseModel, EmailStr
from enum import Enum
from typing import Optional, Dict, Union, List
import datetime
from backend.app.core.ai.flashcard_generation_module import Flashcard
from backend.app.core.ai.quiz_generation_module import QuizQuestion
from backend.app.models.planner import NextStep

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

class CalibrationQuestionResponse(BaseModel):
    """
    Structured response for a calibration question.
    """
    type: str = "calibration_question"
    question: str

class ExploratoryPhrasingResponse(BaseModel):
    """
    Structured response for an exploratory phrasing.
    """
    type: str = "exploratory_phrasing"
    phrasing: str

class ClarityResponse(BaseModel):
    """
    Represents the AI's response after processing a user's query,
    including the action to be taken and the content of the response.
    The 'content' field can be a direct string or a structured object
    like CalibrationQuestionResponse or ExploratoryPhrasingResponse.
    """
    action: str # e.g., "direct_response", "uncertainty_handling", "generate_materials"
    content: Union[str, CalibrationQuestionResponse, ExploratoryPhrasingResponse, NextStep]

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

class SummarizeRequest(BaseModel):
    text: str
    detail_level: Optional[str] = "normal"

class SummarizeResponse(BaseModel):
    summary: str



class FlashcardGenerateRequest(BaseModel):
    text: str
    # Optional fields like num_flashcards or difficulty can be added later

class FlashcardGenerateResponse(BaseModel):
    flashcards: List[Flashcard]

class QuizGenerateRequest(BaseModel):
    text: str

class QuizGenerateResponse(BaseModel):
    questions: List[QuizQuestion]

# New schemas for persistent generated materials
class GeneratedSummaryResponse(BaseModel):
    id: int
    study_material_id: int
    content: str
    detail_level: Optional[str]
    generated_at: datetime.datetime

    class Config:
        orm_mode = True

class GeneratedFlashcardResponse(BaseModel):
    question: str
    answer: str

class GeneratedFlashcardSetResponse(BaseModel):
    id: int
    study_material_id: int
    content: List[GeneratedFlashcardResponse]
    generated_at: datetime.datetime

    class Config:
        orm_mode = True

class GeneratedQuizQuestionResponse(BaseModel):
    question: str
    options: List[str]
    correct_answer: str

class GeneratedQuizResponse(BaseModel):
    id: int
    study_material_id: int
    content: List[GeneratedQuizQuestionResponse]
    generated_at: datetime.datetime

    class Config:
        orm_mode = True

class Permissions(str, Enum):
    view_only = "view_only"
    edit = "edit"

class ShareLinkCreateRequest(BaseModel):
    permissions: Permissions = Permissions.view_only

class ShareLinkGenerateResponse(BaseModel):
    share_token: str

class ShareWithUserRequest(BaseModel):
    target_user_email: EmailStr
    permissions: Permissions = Permissions.view_only

class ShareWithUserResponse(BaseModel):
    shared_id: int
    study_material_id: int
    shared_with_user_id: int
    permissions: Permissions

    class Config:
        orm_mode = True

class SharedStudyMaterialResponse(BaseModel):
    study_material_id: int
    file_name: str
    s3_key: str
    permissions: Permissions
    owner_id: int


class FeedbackCreate(BaseModel):
    material_id: int
    material_type: str
    rating: int
    comments: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    material_id: int
    material_type: str
    rating: int
    comments: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        orm_mode = True