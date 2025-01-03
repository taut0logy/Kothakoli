from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, List
from ..services.auth_service import auth_service
from ..middleware.auth import auth_required
from ..middleware.role_checker import require_user
import logging
from pydantic import BaseModel
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

class UserResponse(BaseModel):
    _id: str
    name: str | None = None
    email: str

    class Config:
        from_attributes = True

    @classmethod
    def from_db(cls, db_user):
        data = dict(db_user)
        data['_id'] = data.pop('id')
        return cls(**data)

class ContentResponse(BaseModel):
    _id: str
    title: str
    content: str
    fileUrl: str | None = None
    createdAt: datetime
    user: UserResponse

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def from_db(cls, db_content):
        data = dict(db_content)
        data['_id'] = data.pop('id')
        if 'user' in data and data['user']:
            data['user'] = UserResponse.from_db(data['user'])
        return cls(**data)

@router.get("/search")
@require_user
async def search_users(
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: Dict = Depends(auth_required)
) -> Dict:
    """Search users by name with pagination."""
    try:
        skip = (page - 1) * limit
        users, total = await auth_service.search_users(
            query=query,
            current_user_id=current_user["id"],
            skip=skip,
            limit=limit
        )
        return {
            "users": users,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Failed to search users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search users"
        )

@router.get("/{user_id}/contents", response_model=List[ContentResponse])
@require_user
async def get_user_contents(
    user_id: str,
    current_user: Dict = Depends(auth_required)
):
    """Get user's generated content."""
    try:
        contents = await auth_service.get_user_contents(
            user_id=user_id,
            content_type="PDF"
        )
        return [ContentResponse.from_db(content) for content in contents]
    except Exception as e:
        logger.error(f"Failed to get user contents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user contents"
        ) 