from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.dependencies import get_current_user
from backend.app.api.schemas import ShareCreateRequest, SharedMaterialResponse, SharedLinkResponse
from backend.app.services.sharing_service import SharingService

router = APIRouter(
    prefix="/sharing",
    tags=["sharing"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate-link", response_model=SharedLinkResponse, status_code=status.HTTP_201_CREATED)
async def generate_link(
    share_request: ShareCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates a shareable link for a study material.
    """
    sharing_service = SharingService(db)
    try:
        share_token = sharing_service.generate_share_link(
            user_id=current_user.id,
            study_material_id=share_request.study_material_id,
            permissions=share_request.permissions
        )
        return SharedLinkResponse(share_token=share_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/share-with-user", response_model=SharedMaterialResponse, status_code=status.HTTP_201_CREATED)
async def share_with_user_endpoint(
    share_request: ShareCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Shares a study material with another user.
    """
    if not share_request.shared_with_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email of the user to share with is required."
        )
    sharing_service = SharingService(db)
    try:
        shared_material = sharing_service.share_with_user(
            shared_by_user_id=current_user.id,
            study_material_id=share_request.study_material_id,
            target_user_email=share_request.shared_with_email,
            permissions=share_request.permissions
        )
        return shared_material
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/shared/{share_token}", response_model=SharedMaterialResponse)
def get_shared_material_by_token_endpoint(
    share_token: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Allows access to a shared material via a public share token.
    """
    sharing_service = SharingService(db)
    user_id = current_user.id if current_user else None
    shared_material = sharing_service.get_shared_material_by_token(share_token, user_id)
    if not shared_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared material not found, link may have expired, or you may not have permission to view it."
        )
    return SharedMaterialResponse(**shared_material)

@router.get("/my-shares", response_model=List[SharedMaterialResponse])
def get_my_shares(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a list of study materials shared by the current user.
    """
    shares = db.query(SharedStudyMaterial).filter(
        SharedStudyMaterial.shared_by_user_id == current_user.id
    ).all()

    response_list = []
    for share in shares:
        db_study_material = db.query(StudyMaterial).filter(StudyMaterial.id == share.study_material_id).first()
        if db_study_material:
            response_data = share.__dict__
            response_data['file_name'] = db_study_material.file_name
            response_data['s3_key'] = db_study_material.s3_key
            response_list.append(SharedMaterialResponse(**response_data))
    return response_list

@router.get("/shared-with-me", response_model=List[SharedMaterialResponse])
def get_shared_with_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a list of study materials shared with the current user.
    """
    shares = db.query(SharedStudyMaterial).filter(
        SharedStudyMaterial.shared_with_user_id == current_user.id
    ).all()

    response_list = []
    for share in shares:
        db_study_material = db.query(StudyMaterial).filter(StudyMaterial.id == share.study_material_id).first()
        if db_study_material:
            response_data = share.__dict__
            response_data['file_name'] = db_study_material.file_name
            response_data['s3_key'] = db_study_material.s3_key
            response_list.append(SharedMaterialResponse(**response_data))
    return response_list

@router.delete("/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_share(
    share_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revokes a specific share, effectively making the material no longer shared.
    Only the owner of the share can revoke it.
    """
    db_share = db.query(SharedStudyMaterial).filter(
        SharedStudyMaterial.id == share_id,
        SharedStudyMaterial.shared_by_user_id == current_user.id
    ).first()

    if not db_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share not found or user is not the owner"
        )
    
    db.delete(db_share)
    db.commit()
    return