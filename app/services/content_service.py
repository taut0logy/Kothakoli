import logging
from typing import Optional, Dict, List
from datetime import datetime
from ..core.database import db
from ..core.config import settings
import json

logger = logging.getLogger(__name__)

class ContentService:
    def __init__(self):
        logger.info("Content Service initialized")

    async def save_content(
        self,
        user_id: str,
        content_type: str,
        title: str,
        content: str,
        isPublic: bool = True,
        prompt: Optional[str] = None,
        filename: Optional[str] = None,
        file_url: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Save generated content to the database."""
        try:
            async with db.get_client() as client:
                content = await client.generatedcontent.create(
                    data={
                        "userId": user_id,
                        "type": content_type,
                        "title": title,
                        "prompt": prompt,
                        "isPublic": isPublic,
                        "content": content,
                        "filename": filename,
                        "fileUrl": file_url,
                        "metadata": json.dumps(metadata) if metadata else None
                    }
                )
                return content
        except Exception as e:
            logger.error(f"Error saving content: {str(e)}")
            raise

    async def get_user_content(
        self,
        user_id: str,
        content_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        isPublic: Optional[bool] = None
    ) -> List[Dict]:
        """Get user's generated content with optional filtering by type."""
        try:
            async with db.get_client() as client:
                where = {"userId": user_id}
                if content_type:
                    where["type"] = content_type
                if isPublic:
                    where["isPublic"] = isPublic


                contents = await client.generatedcontent.find_many(
                    where=where,
                    order={"createdAt": "desc"},
                    skip=offset,
                    take=limit
                )
                return contents
        except Exception as e:
            logger.error(f"Error fetching content: {str(e)}")
            raise

    async def get_content_by_id(self, content_id: str, isPublic: Optional[bool] = None) -> Optional[Dict]:
        """Get specific content by ID."""
        try:
            async with db.get_client() as client:
                where = {"id": content_id}
                if isPublic:
                    where["isPublic"] = isPublic
                content = await client.generatedcontent.find_unique(
                    where=where
                )
                return content
        except Exception as e:
            logger.error(f"Error fetching content: {str(e)}")
            raise

    async def get_content_by_type(self, content_type: str, limit: int = 50, offset: int = 0, isPublic: Optional[bool] = None) -> List[Dict]:
        """Get content by type with optional filtering by public."""
        try:
            async with db.get_client() as client:
                where = {"type": content_type}
                if isPublic:
                    where["isPublic"] = isPublic
                contents = await client.generatedcontent.find_many(
                    where=where,
                    order={"createdAt": "desc"},
                    skip=offset,
                    take=limit
                )
                return contents
        except Exception as e:
            logger.error(f"Error fetching content: {str(e)}")
            raise

    async def delete_content(self, content_id: str, user_id: str) -> bool:
        """Delete specific content."""
        try:
            async with db.get_client() as client:
                content = await client.generatedcontent.delete(
                    where={
                        "id": content_id,
                        "userId": user_id
                    }
                )
                return bool(content)
        except Exception as e:
            logger.error(f"Error deleting content: {str(e)}")
            raise

content_service = ContentService() 