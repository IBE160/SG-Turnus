from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.api.v1.study_materials import get_user_study_material # Re-using helper function
from backend.app.services.export_service import ExportService # Will create this next

router = APIRouter(
    prefix="/export",
    tags=["export"],
    dependencies=[Depends(get_current_user)],
    responses={404: {"description": "Not found"}},
)

def get_export_service(db: Session = Depends(get_db)):
    return ExportService(db)

@router.get("/{material_type}/{material_id}", response_class=StreamingResponse)
async def export_generated_material(
    material_type: str,
    material_id: int,
    format: str,
    current_user: User = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
    db: Session = Depends(get_db)
):
    """
    Exports a generated study material (summary, flashcard set, or quiz) in a specified format.
    """
    allowed_material_types = ["summary", "flashcard_set", "quiz"]
    if material_type not in allowed_material_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid material type. Must be one of: {', '.join(allowed_material_types)}")

    allowed_formats = ["pdf", "docx", "csv"]
    if format not in allowed_formats:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid export format. Must be one of: {', '.join(allowed_formats)}")

    # Fetch the generated material and check ownership
    # The export_service will handle ownership check internally when fetching the material
    try:
        file_content, media_type, file_name = await export_service.export_material(
            current_user.id,
            material_type,
            material_id,
            format
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during export: {str(e)}")

    return StreamingResponse(
        content=file_content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )
