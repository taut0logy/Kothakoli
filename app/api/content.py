from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, List, Optional
from ..services.content_service import content_service
from ..api.auth import get_current_user
from pydantic import BaseModel, Field
from datetime import datetime
from app.core.database import db
import logging

router = APIRouter(prefix="/content", tags=["content"])
logger = logging.getLogger(__name__)

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

        
@router.get("/all", response_model=List[ContentResponse])
async def get_all_content(
    current_user: Dict = Depends(get_current_user)
):
    """Get all content."""
    try:
        contents = await content_service.get_all_content()
        return contents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

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

@router.get("/{user_id}", response_model=List[ContentResponse])
async def get_user_content(
    user_id: str,
    content_type: Optional[str] = Query(None, description="Filter by content type (CHAT, PDF, VOICE, FILE)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get user's generated content with optional filtering."""
    try:
        async with db.get_client() as client:
            user = client.user.find_unique(where={"id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        contents = await content_service.get_user_content(
                user_id=user_id,
                content_type=content_type,
                limit=limit,
                offset=offset
            )
        return contents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.get("/{user_id}/pdfs", response_model=List[ContentResponse])
async def get_user_content(
    user_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get user's generated content with optional filtering."""
    try:
        async with db.get_client() as client:
            user = client.user.find_unique(where={"id": user_id})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        contents = await content_service.get_user_content(
                user_id=user_id,
                content_type="PDF",
                limit=limit,
                offset=offset
            )
        return contents
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.get("/get/{content_id}", response_model=ContentResponse)
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

@router.post("/{content_id}/toggle-public")
async def toggle_content_public(
    content_id: str,
    current_user = Depends(get_current_user)
) -> Dict:
    """Toggle the public status of a content."""
    try:
        async with db.get_client() as client:
            # Get the content
            content = await client.generatedcontent.find_unique(
                where={"id": content_id}
            )
            
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found"
                )
                
            # Check if user owns the content
            if content.userId != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to modify this content"
                )
            
            # Toggle the isPublic status
            updated_content = await client.generatedcontent.update(
                where={"id": content_id},
                data={"isPublic": not content.isPublic}
            )
            
            return {
                "id": updated_content.id,
                "isPublic": updated_content.isPublic
            }
            
    except Exception as e:
        logger.error(f"Error toggling content public status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update content visibility"
        )

@router.get("/search")
async def search_content(
    query: str,
    page: int = 1,
    limit: int = 10,
    current_user = Depends(get_current_user)
) -> Dict:
    """Search for public PDFs."""
    try:
        skip = (page - 1) * limit
        
        async with db.get_client() as client:
            # Get public PDFs that match the query
            contents = await client.generatedcontent.find_many(
                where={
                    "type": "PDF",
                    "isPublic": True,
                    "OR": [
                        {"title": {"contains": query, "mode": "insensitive"}},
                        {"content": {"contains": query, "mode": "insensitive"}}
                    ]
                },
                skip=skip,
                take=limit,
                include={
                    "user": {
                        "select": {
                            "id": True,
                            "name": True,
                            "email": True
                        }
                    }
                }
            )
            
            # Get total count for pagination
            total = await client.generatedcontent.count(
                where={
                    "type": "PDF",
                    "isPublic": True,
                    "OR": [
                        {"title": {"contains": query, "mode": "insensitive"}},
                        {"content": {"contains": query, "mode": "insensitive"}}
                    ]
                }
            )
            
            return {
                "items": contents,
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
            
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search content"
        ) 