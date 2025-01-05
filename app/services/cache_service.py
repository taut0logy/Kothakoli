import json
import logging
from typing import Any, Optional
import redis
from ..core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                ssl=True
            )
            logger.info("Cache Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis connection: {str(e)}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get from cache: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a value in cache with optional TTL."""
        try:
            data = json.dumps(value)
            await self.redis.set(key, data, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Failed to set cache: {str(e)}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete from cache: {str(e)}")
            return False

    async def increment(self, key: str, ttl: int = None) -> Optional[int]:
        """Increment a counter and set TTL if not exists."""
        try:
            pipe = self.redis.pipeline()
            await pipe.incr(key)
            if ttl is not None:
                await pipe.expire(key, ttl)
            results = await pipe.execute()
            return results[0]
        except Exception as e:
            logger.error(f"Failed to increment counter: {str(e)}")
            return None

    async def get_counter(self, key: str) -> Optional[int]:
        """Get the current value of a counter."""
        try:
            value = await self.redis.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"Failed to get counter: {str(e)}")
            return None

    def get_rate_limit_key(self, user_id: str) -> str:
        """Generate a rate limit key for a user."""
        return f"rate_limit:{user_id}"

    async def check_rate_limit(self, user_id: str) -> bool:
        """Check if a user has exceeded their rate limit."""
        key = self.get_rate_limit_key(user_id)
        try:
            count = await self.increment(key, settings.RATE_LIMIT_WINDOW)
            if count is None:
                return False
            return count <= settings.RATE_LIMIT_REQUESTS
        except Exception as e:
            logger.error(f"Failed to check rate limit: {str(e)}")
            return False

cache_service = CacheService() 