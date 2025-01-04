from typing import List, Callable
from functools import wraps
from fastapi import HTTPException, status, Request
from ..core.config import settings
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def check_role(allowed_roles: List[str]) -> Callable:
    """Decorator to check if user has required role."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = datetime.now()
            log_data = {
                "timestamp": start_time.isoformat(),
                "function": func.__name__,
                "allowed_roles": allowed_roles,
                "status": "started"
            }

            # Find the request object
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                request = kwargs.get('request')

            try:
                if not request:
                    logger.error(f"Role check failed: {json.dumps({**log_data, 'error': 'Request object not found'})}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Could not validate role - Request object not found"
                    )

                # Get user from request state
                user = getattr(request.state, 'user', None)
                
                # Log request details
                log_data.update({
                    "path": str(request.url),
                    "method": request.method,
                    "client_ip": request.client.host if request.client else None,
                    "user_id": user.get('id') if user else None,
                    "user_email": user.get('email') if user else None,
                    "user_role": user.get('role') if user else None
                })

                logger.info(f"Role check started: {json.dumps(log_data)}")
                
                if not user:
                    logger.warning(f"Authentication failed: {json.dumps({**log_data, 'error': 'User not authenticated'})}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated"
                    )

                # Check if user role is in allowed roles
                user_role = user.get('role')
                if not user_role or user_role not in allowed_roles:
                    logger.warning(f"Permission denied: {json.dumps({**log_data, 'error': 'Invalid role', 'user_role': user_role})}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Not enough permissions. Required roles: {', '.join(allowed_roles)}"
                    )

                # Log successful role check
                logger.info(f"Role check passed: {json.dumps({**log_data, 'status': 'success'})}")

                # Execute the protected function
                response = await func(*args, **kwargs)

                # Log completion
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.info(f"Request completed: {json.dumps({
                    **log_data,
                    'status': 'completed',
                    'duration_seconds': duration
                })}")

                return response

            except HTTPException as http_ex:
                # Log HTTP exceptions
                logger.warning(f"HTTP Exception in role check: {json.dumps({
                    **log_data,
                    'status': 'failed',
                    'error_type': 'HTTPException',
                    'status_code': http_ex.status_code,
                    'detail': str(http_ex.detail)
                })}")
                raise

            except Exception as e:
                # Log unexpected exceptions
                logger.error(f"Unexpected error in role check: {json.dumps({
                    **log_data,
                    'status': 'failed',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                })}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error during role check"
                )

        return wrapper
    return decorator

# Role checker instances
require_admin = check_role(['ADMIN'])
require_user = check_role(['USER', 'ADMIN'])  # Admin can access user routes too

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