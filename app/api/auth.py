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
from ..services.otp_service import otp_service
from ..core.security import get_password_hash
from ..models.auth import (
    VerifyEmailRequest,
    ResendVerificationRequest,
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
        # Check if token is blacklisted
        is_blacklisted = await cache_service.get(f"blacklist:{token}")
        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated",
                headers={"WWW-Authenticate": "Bearer"},
            )

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
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user"
        )

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    json_data: LoginRequest = None
):
    """Authenticate a user and return a JWT token."""
    try:
        email = form_data.username if form_data else json_data.email
        password = form_data.password if form_data else json_data.password

        result = await auth_service.authenticate_user(
            email=email,
            password=password
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return result

    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/logout")
async def logout(current_user: Dict = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    """Logout a user by blacklisting their token."""
    try:
        # Add token to blacklist with expiry matching token expiry
        token_exp = auth_service.decode_token(token).get("exp")
        if token_exp:
            ttl = token_exp - datetime.utcnow().timestamp()
            await cache_service.set(f"blacklist:{token}", "true", int(ttl))
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during logout"
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

@router.post("/resend-verification")
async def resend_verification(request: ResendVerificationRequest):
    """Resend verification email to the user."""
    try:
        user = await auth_service.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.isVerified:
            return {"message": "Email already verified"}

        # Send verification email
        await email_service.send_verification_email(user.email)
        return {"message": "Verification email sent"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Send password reset OTP to user's email."""
    try:
        user = await auth_service.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Generate and send OTP
        otp = await otp_service.create_otp(user.email, 'password_reset')
        await email_service.send_password_reset_email(user.email, otp)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset user's password using OTP."""
    try:
        user = await auth_service.get_user_by_email(request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify OTP
        is_valid = await otp_service.verify_otp(
            request.email,
            request.otp,
            'password_reset'
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )

        # Update password
        hashed_password = get_password_hash(request.password)
        await auth_service.update_user(user.id, {"password": hashed_password})

        # Invalidate OTP
        await otp_service.invalidate_otp(request.email, 'password_reset')
        return {"message": "Password reset successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 