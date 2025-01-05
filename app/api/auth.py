from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict, Optional, Any
from pydantic import BaseModel, EmailStr
from ..services.auth_service import auth_service
from ..services.cache_service import cache_service
from ..core.config import settings
import logging
from datetime import datetime
from ..services.email_service import email_service
from ..core.security import get_password_hash
from ..models.auth import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """Get the current authenticated user."""
    try:
        user_id = auth_service.verify_token(token)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await auth_service.get_user(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return user

    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
    """Create a new user account."""
    try:
        user = await auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        return {"message": "User created successfully", "user": user}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        error_message = str(e)
        if "duplicate key error" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already registered"
            )
        elif "validation failed" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input data. Please check your email and password format"
            )
        elif "connection" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to connect to the database. Please try again later"
            )
        logger.error(f"Error during signup: {error_message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later"
        )

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), remember_me: bool = Body(False)):
    """Authenticate a user and return a JWT token."""
    try:
        result = await auth_service.authenticate_user(
            email=form_data.username,
            password=form_data.password,
            remember_me=remember_me
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.post("/logout")
async def logout(
    current_user: Dict = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    """Logout a user by removing their token."""
    try:
        await auth_service.logout_user(token)
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me")
async def get_me(current_user: Dict = Depends(get_current_user)):
    """Get the current user's profile."""
    return current_user

@router.put("/me")
async def update_me(
    user_data: UserUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """Update the current user's profile."""
    try:
        if user_data.model_name and user_data.model_name not in settings.AVAILABLE_MODELS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid model name"
            )

        updated_user = await auth_service.update_user(
            user_id=current_user["id"],
            data=user_data.dict(exclude_unset=True)
        )
        return updated_user

    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user"
        )

@router.delete("/me")
async def delete_me(current_user: Dict = Depends(get_current_user)):
    """Delete the current user's account."""
    try:
        await auth_service.delete_user(current_user["id"])
        return {"message": "User deleted successfully"}

    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the user"
        )

@router.post("/verify-email")
async def verify_email(
    token: str = Body(..., embed=True)
) -> Dict[str, Any]:
    try:
        # Verify the token
        payload = email_service.verify_token(token, "email_verification")
        if not payload:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired verification token"
            )

        # Update user's email verification status
        email = payload.get("email")
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Invalid token payload"
            )

        # Mark email as verified
        success = await auth_service.verify_email(email)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to verify email"
            )

        return {
            "success": True,
            "message": "Email verified successfully"
        }

    except Exception as e:
        logger.error(f"Email verification failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )



@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset token to user's email."""
    try:
        # Create reset token
        result = await auth_service.create_password_reset_token(request.email)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account found with this email address"
            )

        # Send reset email
        await email_service.send_password_reset_email(email=request.email, name=result["name"], reset_token=result["token"])
        
        return {
            "message": "Password reset instructions have been sent to your email",
            "email": request.email
        }
    except Exception as e:
        logger.error(f"Failed to process forgot password request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset user's password using the reset token."""
    try:
        success = await auth_service.reset_password(
            token=request.token,
            new_password=request.new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
            
        return {"message": "Password has been reset successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to reset password: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )