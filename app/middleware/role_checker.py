from typing import List, Callable
from fastapi import HTTPException, status, Request, Depends
from ..core.config import settings
from .auth import JWTBearer
import logging
from jose import jwt
from functools import wraps

logger = logging.getLogger(__name__)

class RoleChecker:
    """Role checker middleware that verifies roles from JWT token."""
    
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles
        self.auth_scheme = JWTBearer()

    def verify_role(self, token: str) -> bool:
        """Verify role from JWT token."""
        try:
            # Decode token without verifying expiration (that's handled by auth middleware)
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_role = payload.get('role')
            return user_role in self.allowed_roles
        except Exception as e:
            logger.error(f"Role verification failed: {str(e)}")
            return False

    def __call__(self) -> Callable:
        """Create a dependency that checks user roles."""
        async def check_role(request: Request) -> dict:
            try:
                # Get token from request header
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Missing or invalid authorization header"
                    )

                token = auth_header.split(' ')[1]
                if not self.verify_role(token):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not enough permissions. Required roles: {', '.join(self.allowed_roles)}"
                    )

                return request.state.user

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Role check failed: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permission denied"
                )
        
        return Depends(check_role)

# Create role checker instances
require_admin = RoleChecker(['ADMIN'])()
require_user = RoleChecker(['USER', 'ADMIN'])()

def check_roles(allowed_roles: List[str]):
    """Create a role checker dependency."""
    return RoleChecker(allowed_roles)()

# Example usage in an endpoint:
"""
@router.get("/admin/users")
@require_admin
async def get_users(request: Request):
    # Only admins can access this endpoint
    pass

@router.get("/user/profile")
@require_user
async def get_profile(request: Request):
    # Both users and admins can access this endpoint
    pass
""" 