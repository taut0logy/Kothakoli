from typing import Optional
from pydantic import BaseModel
from app.services.cache_service import cache_service
import json

class RedisOTP(BaseModel):
    email: str
    otp: str
    purpose: str
    attempts: int = 0
    expiry: float

    @classmethod
    async def get(cls, key: str) -> Optional['RedisOTP']:
        """Get an OTP by its key."""
        try:
            data = await cache_service.get(f"otp:{key}")
            if data:
                return cls(**json.loads(data))
            return None
        except Exception:
            return None

    async def save(self) -> None:
        """Save the OTP with expiry."""
        key = self.get_key()
        data = json.dumps(self.dict())
        ttl = 3600  # 1 hour
        await cache_service.set(f"otp:{key}", data, ttl)

    async def delete(self) -> None:
        """Delete the OTP."""
        key = self.get_key()
        await cache_service.delete(f"otp:{key}")

    def get_key(self) -> str:
        """Get the Redis key for this OTP."""
        return f"{self.email}:{self.purpose}"
