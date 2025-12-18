from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.study_material import StudyMaterial
from backend.app.models.user import User
from backend.app.dependencies import get_current_user
from backend.app.api.schemas import (
    StudyMaterialCreate, 
    StudyMaterialResponse, 
    StudyMaterialUpdate, 
    SummarizeRequest, 
    FlashcardGenerateRequest, 
    QuizGenerateRequest,
    GeneratedSummaryResponse,        # New import
    GeneratedFlashcardSetResponse,   # New import
    GeneratedQuizResponse            # New import
)
from backend.app.services.nlp_service import NLPService # Import NLPService
import shutil
import os
import datetime

# For S3 integration, will be implemented later
# from backend.app.services.s3_service import upload_file_to_s3, delete_file_from_s3

router = APIRouter(
    prefix="/study-materials",
    tags=["study-materials"],
    dependencies=[Depends(get_current_user)], # All endpoints in this router require authentication
    responses={404: {"description": "Not found"}},
)

# Initialize NLPService as a dependency
def get_nlp_service(db: Session = Depends(get_db)): # Pass db session to NLPService
    return NLPService(db)

@router.post("/summarize", response_model=GeneratedSummaryResponse) # Changed response_model
async def summarize_text(
    study_material_id: int, # Added study_material_id
    request: SummarizeRequest,
    current_user: User = Depends(get_current_user),
    nlp_service: NLPService = Depends(get_nlp_service)
):
    """
    Generates a summary of the provided text using the NLPService and stores it persistently.
    """
    # Ensure the user owns the study material
    db_study_material = get_user_study_material(nlp_service.db, study_material_id, current_user.id)
    if not db_study_material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found or user does not own it")

    summary = nlp_service.get_summary(study_material_id, request.text, request.detail_level) # Pass study_material_id
    return summary

@router.post("/flashcards", response_model=GeneratedFlashcardSetResponse) # Changed response_model
async def generate_flashcards_api(
    study_material_id: int, # Added study_material_id
    request: FlashcardGenerateRequest,
    current_user: User = Depends(get_current_user),
    nlp_service: NLPService = Depends(get_nlp_service)
):
    """
    Generates flashcards from the provided text using the NLPService and stores them persistently.
    """
    # Ensure the user owns the study material
    db_study_material = get_user_study_material(nlp_service.db, study_material_id, current_user.id)
    if not db_study_material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found or user does not own it")

    flashcards_set = nlp_service.get_flashcards(study_material_id, request.text) # Pass study_material_id
    return flashcards_set

@router.post("/quiz", response_model=GeneratedQuizResponse) # Changed response_model
async def generate_quiz_api(
    study_material_id: int, # Added study_material_id
    request: QuizGenerateRequest,
    current_user: User = Depends(get_current_user),
    nlp_service: NLPService = Depends(get_nlp_service)
):
    """
    Generates a quiz from the provided text using the NLPService and stores it persistently.
    """
    # Ensure the user owns the study material
    db_study_material = get_user_study_material(nlp_service.db, study_material_id, current_user.id)
    if not db_study_material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found or user does not own it")

    quiz = nlp_service.get_quiz_questions(study_material_id, request.text) # Pass study_material_id
    return quiz

@router.get("/", response_model=List[StudyMaterialResponse])
def read_study_materials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a list of all study materials for the current user.
    """
    study_materials = db.query(StudyMaterial).filter(
        StudyMaterial.user_id == current_user.id
    ).all()
    return study_materials

@router.get("/updates", response_model=List[StudyMaterialResponse])
def get_updated_study_materials(
    since: datetime.datetime, # Expect datetime object
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve study materials for the current user that have been updated since a given timestamp.

    Args:
        since (datetime.datetime): The timestamp (e.g., ISO 8601 format) from which to retrieve updates.
                                   Only materials updated *after* this timestamp will be returned.

    Returns:
        List[StudyMaterialResponse]: A list of study materials that have been updated.
    """
    updated_materials = db.query(StudyMaterial).filter(
        StudyMaterial.user_id == current_user.id,
        StudyMaterial.updated_at > since
    ).all()
    return updated_materials

@router.post("/", response_model=StudyMaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_study_material(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a new study material file.
    S3 integration will be added here later. For now, it creates a DB entry.
    """
    # Placeholder for S3 upload logic
    # s3_key = await upload_file_to_s3(file.file, file.filename, current_user.id)
    # For now, let's save the file locally for demonstration purposes (will remove later)
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # In a real scenario, this would be the s3_key
    s3_key = f"users/{current_user.id}/{file.filename}" 

    db_study_material = StudyMaterial(
        user_id=current_user.id,
        file_name=file.filename,
        s3_key=s3_key,
        processing_status="pending"
    )
    db.add(db_study_material)
    db.commit()
    db.refresh(db_study_material)
    
    # Clean up temp file (will be replaced by S3 cleanup)
    os.remove(temp_file_path)

    return db_study_material

@router.get("/{study_material_id}", response_model=StudyMaterialResponse)
def read_study_material(
    study_material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve details of a specific study material by ID.
    """
    db_study_material = get_user_study_material(db, study_material_id, current_user.id)
    if db_study_material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found")
    return db_study_material

@router.put("/{study_material_id}", response_model=StudyMaterialResponse)
def update_study_material(
    study_material_id: int,
    study_material_update: StudyMaterialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the metadata of an existing study material.

    Args:
        study_material_id (int): The ID of the study material to update.
        study_material_update (StudyMaterialUpdate): The Pydantic model containing the fields to update.
                                                     Only provided fields will be modified.

    Returns:
        StudyMaterialResponse: The updated study material object.
    """
    db_study_material = get_user_study_material(db, study_material_id, current_user.id)
    if db_study_material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found")

    update_data = study_material_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_study_material, key, value)
    
    db.add(db_study_material)
    db.commit()
    db.refresh(db_study_material)
    return db_study_material

@router.delete("/{study_material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_study_material(
    study_material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a study material. This will also delete the file from S3 later.
    """
    db_study_material = get_user_study_material(db, study_material_id, current_user.id)
    if db_study_material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found")
    
    # Placeholder for S3 delete logic
    # await delete_file_from_s3(db_study_material.s3_key)

    db.delete(db_study_material)
    db.commit()
    return

@router.get("/{study_material_id}/summaries", response_model=List[GeneratedSummaryResponse])
def get_summaries_for_study_material(
    study_material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a list of generated summaries for a specific study material.
    """
    db_study_material = get_user_study_material(db, study_material_id, current_user.id)
    if db_study_material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found or user does not own it")

    summaries = db.query(GeneratedSummary).filter(
        GeneratedSummary.study_material_id == study_material_id
    ).all()
    return summaries

@router.get("/{study_material_id}/flashcard-sets", response_model=List[GeneratedFlashcardSetResponse])
def get_flashcard_sets_for_study_material(
    study_material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a list of generated flashcard sets for a specific study material.
    """
    db_study_material = get_user_study_material(db, study_material_id, current_user.id)
    if db_study_material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found or user does not own it")

    flashcard_sets = db.query(GeneratedFlashcardSet).filter(
        GeneratedFlashcardSet.study_material_id == study_material_id
    ).all()
    return flashcard_sets

@router.get("/{study_material_id}/quizzes", response_model=List[GeneratedQuizResponse])
def get_quizzes_for_study_material(
    study_material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a list of generated quizzes for a specific study material.
    """
    db_study_material = get_user_study_material(db, study_material_id, current_user.id)
    if db_study_material is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study material not found or user does not own it")

    quizzes = db.query(GeneratedQuiz).filter(
        GeneratedQuiz.study_material_id == study_material_id
    ).all()
    return quizzes

def get_user_study_material(db: Session, study_material_id: int, user_id: int):
    """
    Retrieves a single study material by its ID, ensuring it belongs to the specified user.
    """
    db_study_material = db.query(StudyMaterial).filter(
        StudyMaterial.id == study_material_id,
        StudyMaterial.user_id == user_id
    ).first()
    return db_study_material