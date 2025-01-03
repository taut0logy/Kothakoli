import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError
from ..core.config import settings
from ..core.security import get_password_hash, verify_password
from ..core.database import db

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        logger.info("Auth Service initialized")

    def decode_token(self, token: str) -> Optional[Dict]:
        """Decode a JWT token and return its payload."""
        try:
            payload = jwt.decode(
                token=token,
                key=settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except JWTError as e:
            logger.error(f"JWT decoding failed: {str(e)}")
            return None

    async def create_user(self, email: str, password: str, name: str) -> Dict:
        """Create a new user."""
        try:
            async with db.get_client() as client:
                # Check if user exists
                existing_user = await client.user.find_unique(where={"email": email})
                if existing_user:
                    raise ValueError("Email already registered")

                # Hash password
                hashed_password = get_password_hash(password)

                # Create user
                user = await client.user.create(
                    data={
                        "email": email,
                        "password": hashed_password,
                        "name": name
                    }
                )

                return {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name
                }

        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate a user and return a JWT token."""
        try:
            async with db.get_client() as client:
                # Find user
                user = await client.user.find_unique(where={"email": email})
                if not user:
                    return None

                # Verify password
                if not verify_password(password, user.password):
                    return None

                # Generate token
                access_token = self.create_access_token(user.id)

                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "has_api_key": bool(user.apiKey)
                    }
                }

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise

    def create_access_token(self, user_id: str) -> str:
        """Create a JWT access token."""
        try:
            expiration = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            data = {
                "sub": str(user_id),
                "exp": expiration
            }
            return jwt.encode(
                claims=data, 
                key=settings.JWT_SECRET, 
                algorithm=settings.JWT_ALGORITHM
            )
        except Exception as e:
            logger.error(f"Failed to create access token: {str(e)}")
            raise

    def verify_token(self, token: str) -> Optional[str]:
        """Verify a JWT token and return the user ID."""
        try:
            payload = jwt.decode(
                token=token, 
                key=settings.JWT_SECRET, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except JWTError as e:
            logger.error(f"JWT verification failed: {str(e)}")
            return None
        
    async def logout_user(self, user_id: str) -> bool:
        """Logout the current user."""
        try:
            async with db.get_client() as client:
                await client.user.update(where={"id": user_id}, data={"apiKey": None})
                return True
        except Exception as e:
            logger.error(f"Failed to logout user: {str(e)}")
            raise

    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        try:
            async with db.get_client() as client:
                user = await client.user.find_unique(where={"id": user_id})
                if not user:
                    return None

                return {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "has_api_key": bool(user.apiKey)
                }

        except Exception as e:
            logger.error(f"Failed to get user: {str(e)}")
            raise

    async def update_user(self, user_id: str, data: Dict) -> Dict:
        """Update user profile."""
        try:
            async with db.get_client() as client:
                update_data = {}
                if "name" in data:
                    update_data["name"] = data["name"]
                if "password" in data:
                    update_data["password"] = get_password_hash(data["password"])
                if "apiKey" in data:
                    update_data["apiKey"] = data["apiKey"]
                if "modelName" in data:
                    update_data["modelName"] = data["modelName"]

                user = await client.user.update(
                    where={"id": user_id},
                    data=update_data
                )

                return {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "has_api_key": bool(user.apiKey)
                }

        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            raise

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user account."""
        try:
            async with db.get_client() as client:
                await client.user.delete(where={"id": user_id})
                return True

        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            raise

    async def verify_email(self, email: str) -> bool:
        """Mark user's email as verified in the database."""
        try:
            async with db.get_client() as client:
                user = await client.user.update(
                    where={"email": email},
                    data={"emailVerified": True}
                )
                logger.info(f"Email verified for user: {email}")
                return bool(user)
        except Exception as e:
            logger.error(f"Failed to verify email: {str(e)}")
            raise

    async def is_email_verified(self, user_id: str) -> bool:
        """Check if user's email is verified."""
        try:
            async with db.get_client() as client:
                user = await client.user.find_unique(
                    where={"id": user_id}
                )
                return bool(user and user.emailVerified)
        except Exception as e:
            logger.error(f"Failed to check email verification: {str(e)}")
            raise

auth_service = AuthService() 