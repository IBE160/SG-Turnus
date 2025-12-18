from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.dependencies import get_current_user
from backend.app.api.schemas import (
    ShareLinkGenerateResponse,
    ShareLinkCreateRequest,
    ShareWithUserRequest,
    ShareWithUserResponse,
    SharedStudyMaterialResponse
)
from backend.app.services.sharing_service import SharingService

router = APIRouter(
    prefix="/sharing",
    tags=["sharing"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

# Initialize SharingService as a dependency
def get_sharing_service(db: Session = Depends(get_db)):
    return SharingService(db)

@router.post("/{study_material_id}/generate-link", response_model=ShareLinkGenerateResponse)
async def generate_share_link(
    study_material_id: int,
    request: ShareLinkCreateRequest,
    current_user: User = Depends(get_current_user),
    sharing_service: SharingService = Depends(get_sharing_service)
):
    """
    Generates a shareable link for a specific study material.
    """
    share_token = sharing_service.generate_share_link(
        user_id=current_user.id,
        study_material_id=study_material_id,
        permissions=request.permissions
    )
    return ShareLinkGenerateResponse(share_token=share_token)

@router.post("/{study_material_id}/share-with-user", response_model=ShareWithUserResponse)
async def share_with_user(
    study_material_id: int,
    request: ShareWithUserRequest,
    current_user: User = Depends(get_current_user),
    sharing_service: SharingService = Depends(get_sharing_service)
):
    """
    Shares a study material with another user within the system.
    """
    shared_entry = sharing_service.share_with_user(
        owner_user_id=current_user.id,
        study_material_id=study_material_id,
        target_user_email=request.target_user_email,
        permissions=request.permissions
    )
    return ShareWithUserResponse(
        shared_id=shared_entry.id,
        study_material_id=shared_entry.study_material_id,
        shared_with_user_id=shared_entry.shared_with_user_id,
        permissions=shared_entry.permissions
    )

@router.get("/shared-material/{share_token}", response_model=SharedStudyMaterialResponse)
async def get_shared_study_material(
    share_token: str,
    current_user: User = Depends(get_current_user), # Assuming authenticated access for now
    sharing_service: SharingService = Depends(get_sharing_service)
):
    """
    Retrieves a shared study material using a share token.
    """
    shared_material_data = sharing_service.get_shared_material_by_token(share_token, current_user.id)
    if not shared_material_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared material not found or access denied")
    
    return SharedStudyMaterialResponse(
        study_material_id=shared_material_data["study_material_id"],
        file_name=shared_material_data["file_name"],
        s3_key=shared_material_data["s3_key"],
        permissions=shared_material_data["permissions"],
        owner_id=shared_material_data["owner_id"]
    )
