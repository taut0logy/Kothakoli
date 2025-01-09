from fastapi import Request, HTTPException, status
from typing import Optional, Tuple, Callable
from ..services.cache_service import cache_service
import logging
from datetime import datetime
from ..core.config import settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter middleware using Redis."""
    
    def __init__(
        self,
        requests: int = settings.RATE_LIMIT_REQUESTS,
        window: int = settings.RATE_LIMIT_WINDOW,
        key_prefix: str = "rate_limit"
    ):
        self.requests = requests  # Number of requests allowed
        self.window = window    # Time window in seconds
        self.key_prefix = key_prefix
        
    def _get_key(self, identifier: str) -> str:
        """Generate Redis key for rate limiting."""
        return f"{self.key_prefix}:{identifier}"

    async def is_rate_limited(self, identifier: str) -> Tuple[bool, Optional[dict]]:
        """Check if the request should be rate limited."""
        try:
            key = self._get_key(identifier)
            
            # Get current count and TTL
            pipe = cache_service.redis.pipeline()
            pipe.incr(key)
            pipe.ttl(key)
            count, ttl = await pipe.execute()
            
            # Set expiry if this is the first request
            if ttl == -1:
                await cache_service.redis.expire(key, self.window)
                ttl = self.window
                
            # Check if limit exceeded
            if count > self.requests:
                return True, {
                    "limit": self.requests,
                    "remaining": 0,
                    "reset": ttl
                }
                
            return False, {
                "limit": self.requests,
                "remaining": self.requests - count,
                "reset": ttl
            }
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            return False, None

    def __call__(self) -> Callable:
        """Create a dependency that checks rate limits."""
        async def rate_limit_check(request: Request) -> None:
            try:
                # Get identifier (IP or user ID if authenticated)
                identifier = request.state.user["id"] if hasattr(request.state, "user") else request.client.host
                
                # Check rate limit
                is_limited, headers = await self.is_rate_limited(identifier)
                
                if headers:
                    # Add rate limit headers
                    request.state.rate_limit_headers = {
                        "X-RateLimit-Limit": str(headers["limit"]),
                        "X-RateLimit-Remaining": str(headers["remaining"]),
                        "X-RateLimit-Reset": str(headers["reset"])
                    }
                
                if is_limited:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded",
                        headers=request.state.rate_limit_headers
                    )
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Rate limit check failed: {str(e)}")
                # Don't block the request if rate limiting fails
                pass
            
        return rate_limit_check

# Create instances for different rate limits
default_limiter = RateLimiter()
strict_limiter = RateLimiter(requests=20, window=60)  # 20 requests per minute
lenient_limiter = RateLimiter(requests=1000, window=3600)  # 1000 requests per hour 