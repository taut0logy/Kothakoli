from typing import List
from functools import wraps
from fastapi import HTTPException, status
from ..core.config import settings

def check_role(allowed_roles: List[str]):
    """Decorator to check if user has required role."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = kwargs.get('request')
            if not request:
                for arg in args:
                    if hasattr(arg, 'scope'):  # FastAPI request object
                        request = arg
                        break
            
            if not request:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Could not validate role"
                )

            user = getattr(request.state, 'user', None)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )

            if user.get('role') not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Role checker instances
require_admin = check_role(['ADMIN'])
require_user = check_role(['USER', 'ADMIN'])  # Admin can access user routes too 