import secrets
from typing import Optional, Dict

from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.models.study_material import StudyMaterial
from backend.app.models.user import User
from backend.app.models.shared_study_material import SharedStudyMaterial
from backend.app.api.schemas import Permissions

class SharingService:
    def __init__(self, db: Session):
        self.db = db

    def generate_share_link(
        self, user_id: int, study_material_id: int, permissions: Permissions
    ) -> str:
        """
        Generates a unique share token for a study material and stores the sharing relationship.
        """
        # Ensure the user owns the study material
        study_material = (
            self.db.query(StudyMaterial)
            .filter(
                StudyMaterial.id == study_material_id,
                StudyMaterial.user_id == user_id
            )
            .first()
        )
        if not study_material:
            raise ValueError("Study material not found or user does not own it.")

        # Generate a unique share token
        share_token = secrets.token_urlsafe(16)

        # Create a new shared entry for the link
        db_shared_material = SharedStudyMaterial(
            shared_by_user_id=user_id,
            study_material_id=study_material_id,
            share_token=share_token,
            permissions=permissions.value,
            shared_with_user_id=None # This is a public link, not shared with a specific user
        )
        self.db.add(db_shared_material)
        self.db.commit()
        self.db.refresh(db_shared_material)

        return share_token

    def share_with_user(
        self, shared_by_user_id: int, study_material_id: int, target_user_email: str, permissions: Permissions
    ) -> SharedStudyMaterial:
        """
        Shares a study material with another user within the system by their email.
        """
        # Ensure the shared_by_user_id owns the study material
        study_material = (
            self.db.query(StudyMaterial)
            .filter(
                StudyMaterial.id == study_material_id,
                StudyMaterial.user_id == shared_by_user_id
            )
            .first()
        )
        if not study_material:
            raise ValueError("Study material not found or owner does not own it.")

        # Find the target user by email
        target_user = self.db.query(User).filter(User.email == target_user_email).first()
        if not target_user:
            raise ValueError("Target user with this email not found.")

        # Check if already shared with this user
        existing_share = (
            self.db.query(SharedStudyMaterial)
            .filter(
                SharedStudyMaterial.study_material_id == study_material_id,
                SharedStudyMaterial.shared_with_user_id == target_user.id
            )
            .first()
        )
        if existing_share:
            # Optionally update permissions or raise an error
            existing_share.permissions = permissions.value
            self.db.add(existing_share)
            self.db.commit()
            self.db.refresh(existing_share)
            return existing_share

        db_shared_material = SharedStudyMaterial(
            shared_by_user_id=shared_by_user_id,
            study_material_id=study_material_id,
            shared_with_user_id=target_user.id,
            permissions=permissions.value,
            share_token=None # Not a shareable link
        )
        self.db.add(db_shared_material)
        self.db.commit()
        self.db.refresh(db_shared_material)
        return db_shared_material

    def get_shared_material_by_token(
        self, share_token: str, current_user_id: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Retrieves shared material details by token.
        If current_user_id is provided, it also checks if the user is the owner or
        explicitly shared with, or if it's a public link.
        """
        shared_entry = (
            self.db.query(SharedStudyMaterial)
            .filter(SharedStudyMaterial.share_token == share_token)
            .first()
        )

        if not shared_entry:
            return None

        # Check permissions:
        # 1. If it's a direct share to a user, and current_user_id matches
        # 2. If it's a public link (shared_with_user_id is None)
        # 3. If current_user_id is the owner
        if (
            shared_entry.shared_with_user_id is not None
            and shared_entry.shared_with_user_id != current_user_id
            and shared_entry.shared_by_user_id != current_user_id
        ):
            return None # Not authorized to access this specific share

        study_material = (
            self.db.query(StudyMaterial)
            .filter(StudyMaterial.id == shared_entry.study_material_id)
            .first()
        )
        if not study_material:
            return None # Material might have been deleted

        return {
            "study_material_id": study_material.id,
            "file_name": study_material.file_name,
            "s3_key": study_material.s3_key,
            "permissions": shared_entry.permissions,
            "owner_id": study_material.user_id,
        }