from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import auth_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, require_verified: bool = True):
        super().__init__(auto_error=auto_error)
        self.require_verified = require_verified

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        try:
            credentials: HTTPAuthorizationCredentials = await super().__call__(request)
            if not credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization code"
                )

            # Verify token and get user
            user = await auth_service.verify_token(credentials.credentials)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token or expired token"
                )

            # Check if email verification is required and user is verified
            if self.require_verified and not user.get("isVerified"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Email verification required"
                )

            # Attach user to request state
            request.state.user = user
            request.state.token = credentials.credentials
            return credentials

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )

# Create instances for different authentication requirements
auth_required = JWTBearer(require_verified=True)
auth_optional = JWTBearer(auto_error=False, require_verified=True)
unverified_allowed = JWTBearer(require_verified=False)