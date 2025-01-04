from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import Dict, List
from ..services.auth_service import auth_service
from ..services.email_service import email_service
from ..middleware.auth import auth_required
from ..middleware.role_checker import require_admin
from ..models.auth import CreateAdminRequest
from ..api.auth import get_current_user
import logging
import secrets
import string
from app.core.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

async def check_admin(current_user: Dict = Depends(get_current_user)) -> Dict:
    """Check if the user is an admin."""
    try:
        async with db.get_client() as client:
            user = await client.db.users.find_one({"_id": current_user["id"]})
            if user["role"] != "ADMIN":
                raise HTTPException(status_code=403, detail="Forbidden")
            return user
    except Exception as e:
        logger.error(f"Failed to check admin: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to check admin")

@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """Get all users with their content counts."""
    await check_admin(current_user)
    try:
        skip = (page - 1) * limit
        users, total = await auth_service.get_all_users(skip=skip, limit=limit)
        return {
            "users": users,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Failed to get all users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.get("/contents")
async def get_all_contents(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: Dict = Depends(auth_required)
) -> Dict:
    """Get all generated contents across all users."""
    try:
        await check_admin(current_user)
        skip = (page - 1) * limit
        contents, total = await auth_service.get_all_contents(skip=skip, limit=limit)
        return {
            "contents": contents,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Failed to get all contents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get contents"
        )

@router.post("/create")
async def create_admin_user(
    data: CreateAdminRequest,
    current_user: Dict = Depends(auth_required)
) -> Dict:
    """Create a new admin user with a generated password."""
    try:
        await check_admin(current_user)
        # Generate a secure random password
        password = ''.join(secrets.choice(
            string.ascii_letters + string.digits + string.punctuation
        ) for _ in range(12))

        # Create the admin user
        user = await auth_service.create_user(
            email=data.email,
            password=password,
            name=data.name,
            role="ADMIN"
        )

        # Send email with credentials
        await email_service.send_admin_credentials(
            email=data.email,
            name=data.name,
            password=password
        )

        return {
            "message": "Admin user created successfully",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"]
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to create admin user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create admin user"
        ) 