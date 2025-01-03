from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, List, Optional
from ..services.content_service import content_service
from ..api.auth import get_current_user
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(prefix="/content", tags=["content"])

class ContentResponse(BaseModel):
    id: str
    type: str
    title: str
    content: str
    filename: Optional[str] = None
    fileUrl: Optional[str] = None
    metadata: Optional[Dict] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

@router.get("/", response_model=List[ContentResponse])
async def get_user_content(
    content_type: Optional[str] = Query(None, description="Filter by content type (CHAT, PDF, VOICE, FILE)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict = Depends(get_current_user)
):
    """Get user's generated content with optional filtering."""
    try:
        contents = await content_service.get_user_content(
            user_id=current_user["id"],
            content_type=content_type,
            limit=limit,
            offset=offset
        )
        return contents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Get specific content by ID."""
    try:
        content = await content_service.get_content_by_id(content_id)
        if not content or content["userId"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        return content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{content_id}")
async def delete_content(
    content_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Delete specific content."""
    try:
        success = await content_service.delete_content(
            content_id=content_id,
            user_id=current_user["id"]
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        return {"message": "Content deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 