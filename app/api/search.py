from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.api.auth import get_current_user
from app.services.search_service import SearchService
from app.schemas.common import PaginatedResponse
from enum import Enum
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class Role(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

class ContentType(str, Enum):
    CHAT = "CHAT"
    PDF = "PDF"
    VOICE = "VOICE"
    FILE = "FILE"

# Search Response Models
class UserSearchResult(BaseModel):
    id: str = Field(..., alias="_id")
    email: str
    name: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    role: Role

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PDFCreator(BaseModel):
    id: str = Field(..., alias="_id")
    name: Optional[str] = None
    email: str

    class Config:
        from_attributes = True
        populate_by_name = True

class PDFSearchResult(BaseModel):
    id: str = Field(..., alias="_id")
    type: ContentType
    title: str
    filename: Optional[str] = None
    prompt: Optional[str] = None
    content: str
    fileUrl: Optional[str] = None
    metadata: Optional[Dict] = None
    userId: str
    user: PDFCreator
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserSearchResponse(PaginatedResponse):
    items: List[UserSearchResult]

class PDFSearchResponse(PaginatedResponse):
    items: List[PDFSearchResult]

# Change the prefix to match the API structure
router = APIRouter(prefix="/search", tags=["search"])

@router.get("/users", response_model=UserSearchResponse)
async def search_users(
    request: Request,
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """
    Search for users by name or email.
    Available to both regular users and admins.
    """
    logger.info(f"User search request received from user {current_user.get('id')} - Query: {query}")
    logger.debug(f"Search parameters - Page: {page}, Limit: {limit}")
    logger.debug(f"Request headers: {dict(request.headers)}")

    try:
        search_service = SearchService()
        results = await search_service.search_users(
            query=query,
            page=page,
            limit=limit
        )
        logger.info(f"User search completed successfully - Found {results.total} total results")
        logger.debug(f"Returning {len(results.items)} items for page {page}")
        return results
    except Exception as e:
        logger.error(f"User search failed: {str(e)}", exc_info=True)
        logger.error(f"Failed search parameters - Query: {query}, Page: {page}, Limit: {limit}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search users: {str(e)}"
        )

@router.get("/pdfs", response_model=PDFSearchResponse)
async def search_pdfs(
    request: Request,
    query: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Dict = Depends(get_current_user)
):
    """
    Search for PDFs by title or content.
    Available to both regular users and admins.
    """
    logger.info(f"PDF search request received from user {current_user.get('id')} - Query: {query}")
    logger.debug(f"Search parameters - Page: {page}, Limit: {limit}")
    logger.debug(f"Request headers: {dict(request.headers)}")

    try:
        search_service = SearchService()
        results = await search_service.search_pdfs(
            query=query,
            page=page,
            limit=limit
        )
        logger.info(f"PDF search completed successfully - Found {results.total} total results")
        logger.debug(f"Returning {len(results.items)} items for page {page}")
        return results
    except Exception as e:
        logger.error(f"PDF search failed: {str(e)}", exc_info=True)
        logger.error(f"Failed search parameters - Query: {query}, Page: {page}, Limit: {limit}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search PDFs: {str(e)}"
        ) 