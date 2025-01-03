import logging
from typing import Dict, Optional, List
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

                logger.info(f"Creating user with email: {email}, name: {name}")
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
                    logger.warning(f"Authentication failed: User not found for email {email}")
                    return None

                # Verify password
                if not verify_password(password, user.password):
                    logger.warning(f"Authentication failed: Invalid password for email {email}")
                    return None

                # Generate token
                access_token = self.create_access_token(user.id, user.role)
                logger.info(f"Generated access token for user {email}")

                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "role": user.role,
                        "has_api_key": bool(user.apiKey)
                    }
                }

        except Exception as e:
            logger.error(f"Authentication error for email {email}: {str(e)}")
            raise

    def create_access_token(self, user_id: str, role: str) -> str:
        """Create a JWT access token with role information."""
        try:
            expiration = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            data = {
                "sub": str(user_id),
                "role": role,
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
        
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email."""
        try:
            async with db.get_client() as client:
                user = await client.user.find_unique(where={"email": email})
                return user
        except Exception as e:
            logger.error(f"Failed to get user by email: {str(e)}")
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

    async def create_password_reset_token(self, email: str) -> Optional[str]:
        """Create a password reset token."""
        try:
            async with db.get_client() as client:
                user = await client.user.find_unique(where={"email": email})
                if not user:
                    return None

                # Create a token that expires in 15 minutes
                expiration = datetime.utcnow() + timedelta(minutes=15)
                token_data = {
                    "sub": str(user.id),
                    "email": email,
                    "type": "password_reset",
                    "exp": expiration
                }
                
                token = jwt.encode(
                    claims=token_data,
                    key=settings.JWT_SECRET,
                    algorithm=settings.JWT_ALGORITHM
                )
                
                return token
        except Exception as e:
            logger.error(f"Failed to create password reset token: {str(e)}")
            raise

    async def verify_reset_token(self, token: str) -> Optional[str]:
        """Verify a password reset token and return the user's email."""
        try:
            payload = jwt.decode(
                token=token,
                key=settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            if payload.get("type") != "password_reset":
                return None
                
            return payload.get("email")
        except jwt.ExpiredSignatureError:
            logger.warning("Reset token has expired")
            return None
        except JWTError as e:
            logger.error(f"Reset token verification failed: {str(e)}")
            return None

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user's password using a valid reset token."""
        try:
            # Verify and decode the token
            payload = jwt.decode(
                token=token,
                key=settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Check token type and expiration
            if payload.get("type") != "password_reset":
                logger.warning("Invalid token type for password reset")
                return False

            email = payload.get("email")
            if not email:
                logger.warning("No email in reset token")
                return False

            # Hash the new password
            hashed_password = get_password_hash(new_password)

            # Update the password in database
            async with db.get_client() as client:
                user = await client.user.update(
                    where={"email": email},
                    data={"password": hashed_password}
                )
                
                if user:
                    logger.info(f"Password reset successful for user: {email}")
                    return True
                return False

        except jwt.ExpiredSignatureError:
            logger.warning("Reset token has expired")
            return False
        except JWTError as e:
            logger.error(f"Invalid reset token: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to reset password: {str(e)}")
            raise

    async def search_users(self, query: str, current_user_id: str) -> List[Dict]:
        """Search users by name."""
        try:
            async with db.get_client() as client:
                users = await client.user.find_many(
                    where={
                        "name": {"contains": query, "mode": "insensitive"},
                        "id": {"not": current_user_id}  # Exclude current user
                    },
                    select={
                        "id": True,
                        "name": True,
                        "email": True,
                        "role": True,
                        "createdAt": True
                    }
                )
                return users
        except Exception as e:
            logger.error(f"Failed to search users: {str(e)}")
            raise

    async def get_user_contents(self, user_id: str) -> List[Dict]:
        """Get all contents generated by a user."""
        try:
            async with db.get_client() as client:
                contents = await client.generatedContent.find_many(
                    where={"userId": user_id},
                    include={
                        "user": {
                            "select": {
                                "name": True,
                                "email": True
                            }
                        }
                    },
                    order_by=[{"createdAt": "desc"}]
                )
                return contents
        except Exception as e:
            logger.error(f"Failed to get user contents: {str(e)}")
            raise

    async def get_all_users(self) -> List[Dict]:
        """Get all users (admin only)."""
        try:
            async with db.get_client() as client:
                users = await client.user.find_many(
                    select={
                        "id": True,
                        "name": True,
                        "email": True,
                        "role": True,
                        "createdAt": True,
                        "isVerified": True,
                        "_count": {
                            "select": {
                                "contents": True
                            }
                        }
                    },
                    order_by=[{"createdAt": "desc"}]
                )
                return users
        except Exception as e:
            logger.error(f"Failed to get all users: {str(e)}")
            raise

    async def get_all_contents(self) -> List[Dict]:
        """Get all contents (admin only)."""
        try:
            async with db.get_client() as client:
                contents = await client.generatedContent.find_many(
                    include={
                        "user": {
                            "select": {
                                "name": True,
                                "email": True
                            }
                        }
                    },
                    order_by=[{"createdAt": "desc"}]
                )
                return contents
        except Exception as e:
            logger.error(f"Failed to get all contents: {str(e)}")
            raise

auth_service = AuthService() 