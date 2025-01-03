from typing import Dict, List, Optional
from app.core.database import db
from app.schemas.common import PaginatedResponse
import logging
import json

logger = logging.getLogger(__name__)

class SearchService:
    async def search_users(
        self,
        query: str,
        page: int = 1,
        limit: int = 10
    ) -> PaginatedResponse:
        """
        Search for users by name or email.
        Returns paginated results.
        """
        try:
            logger.info(f"Starting user search with query: {query}, page: {page}, limit: {limit}")
            skip = (page - 1) * limit
            
            async with db.get_client() as prisma:
                # Get total count for pagination
                where_condition = {
                    "OR": [
                        {"name": {"contains": query, "mode": "insensitive"}},
                        {"email": {"contains": query, "mode": "insensitive"}}
                    ],
                }
                logger.debug(f"User search where condition: {json.dumps(where_condition, indent=2)}")

                total_count = await prisma.user.count(where=where_condition)
                logger.info(f"Found {total_count} total matching users")

                # Get paginated results
                users = await prisma.user.find_many(
                    where=where_condition,
                    skip=skip,
                    take=limit,
                    order={"name": "asc"}
                )
                logger.info(f"Retrieved {len(users)} users for current page")
                logger.debug(f"User IDs retrieved: {[user.id for user in users]}")

                response = PaginatedResponse(
                    items=users,
                    total=total_count,
                    page=page,
                    limit=limit,
                    total_pages=(total_count + limit - 1) // limit
                )
                logger.info(f"Returning paginated response with {len(response.items)} items")
                return response

        except Exception as e:
            logger.error(f"Error searching users: {str(e)}", exc_info=True)
            logger.error(f"Search parameters - query: {query}, page: {page}, limit: {limit}")
            raise

    async def search_pdfs(
        self,
        query: str,
        page: int = 1,
        limit: int = 10
    ) -> PaginatedResponse:
        """
        Search for PDFs by title or content.
        Returns paginated results.
        """
        try:
            logger.info(f"Starting PDF search with query: {query}, page: {page}, limit: {limit}")
            skip = (page - 1) * limit

            async with db.get_client() as prisma:
                # Get total count for pagination
                where_condition = {
                    "OR": [
                        {"title": {"contains": query, "mode": "insensitive"}},
                        {"content": {"contains": query, "mode": "insensitive"}}
                    ],
                    "type": "PDF"
                }
                logger.debug(f"PDF search where condition: {json.dumps(where_condition, indent=2)}")

                total_count = await prisma.generatedcontent.count(where=where_condition)
                logger.info(f"Found {total_count} total matching PDFs")

                # Get paginated results
                pdfs = await prisma.generatedcontent.find_many(
                    where=where_condition,
                    skip=skip,
                    take=limit,
                    order={"createdAt": "desc"},
                    include={
                        "user": True
                    }
                )
                

                response = PaginatedResponse(
                    items=pdfs,
                    total=total_count,
                    page=page,
                    limit=limit,
                    total_pages=(total_count + limit - 1) // limit
                )
                logger.info(f"Returning paginated response with {len(response.items)} items")
                return response

        except Exception as e:
            logger.error(f"Error searching PDFs: {str(e)}", exc_info=True)
            logger.error(f"Search parameters - query: {query}, page: {page}, limit: {limit}")
            raise 