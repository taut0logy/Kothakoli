import random
import string
import logging
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import settings
from app.models.redis_models import RedisOTP

logger = logging.getLogger(__name__)

class OTPService:
    def __init__(self):
        self.otp_length = 6
        self.otp_expiry_minutes = 60
        self.max_attempts = 3

    def _generate_otp(self) -> str:
        """Generate a random numeric OTP of specified length."""
        return ''.join(random.choices(string.digits, k=self.otp_length))

    async def create_otp(self, email: str, purpose: str) -> str:
        """Create a new OTP for the given email and purpose."""
        try:
            otp = self._generate_otp()
            expiry = datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes)
            
            # Store OTP in Redis with expiry
            redis_otp = RedisOTP(
                email=email,
                otp=otp,
                purpose=purpose,
                attempts=0,
                expiry=expiry.timestamp()
            )
            await redis_otp.save()
            
            logger.info(f"OTP created for {email} with purpose: {purpose}")
            return otp
        except Exception as e:
            logger.error(f"Failed to create OTP: {str(e)}")
            raise

    async def verify_otp(self, email: str, otp: str, purpose: str) -> bool:
        """Verify the OTP for the given email and purpose."""
        try:
            # Get OTP from Redis
            redis_otp = await RedisOTP.get(f"{email}:{purpose}")
            if not redis_otp:
                logger.warning(f"No OTP found for {email} with purpose: {purpose}")
                return False

            # Check if OTP is expired
            if datetime.utcnow().timestamp() > redis_otp.expiry:
                logger.warning(f"OTP expired for {email}")
                await redis_otp.delete()
                return False

            # Check if max attempts exceeded
            if redis_otp.attempts >= self.max_attempts:
                logger.warning(f"Max attempts exceeded for {email}")
                await redis_otp.delete()
                return False

            # Increment attempts
            redis_otp.attempts += 1
            await redis_otp.save()

            # Verify OTP
            if redis_otp.otp != otp:
                logger.warning(f"Invalid OTP attempt for {email}")
                return False

            # Delete OTP after successful verification
            await redis_otp.delete()
            logger.info(f"OTP verified successfully for {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to verify OTP: {str(e)}")
            raise

    async def invalidate_otp(self, email: str, purpose: str) -> None:
        """Invalidate any existing OTP for the given email and purpose."""
        try:
            redis_otp = await RedisOTP.get(f"{email}:{purpose}")
            if redis_otp:
                await redis_otp.delete()
                logger.info(f"OTP invalidated for {email} with purpose: {purpose}")
        except Exception as e:
            logger.error(f"Failed to invalidate OTP: {str(e)}")
            raise

otp_service = OTPService()