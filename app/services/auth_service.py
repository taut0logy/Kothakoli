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
        

    async def create_user(self, email: str, password: str, name: str, role: str="USER") -> Dict:
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
                        "name": name,
                        "role": role
                    }
                )

                return {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role
                }

        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise

    async def authenticate_user(self, email: str, password: str, remember_me: bool = False) -> Optional[Dict]:
        """Authenticate a user and return a JWT token."""
        try:
            async with db.get_client() as client:
                # Find user
                user = await client.user.find_unique(where={"email": email})
                if not user or not verify_password(password, user.password):
                    return None

                # Set token expiration based on remember_me
                access_token = await self.create_access_token(user.id, user.role, expires_delta=timedelta(days=7 if remember_me else 1))

                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "expires_at": access_token.expires_at.isoformat(),
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "role": user.role,
                        "has_api_key": bool(user.apiKey)
                    }
                }

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise

    async def create_access_token(self, user_id: str, role: str, expires_delta: timedelta = None) -> str:
        """Create a JWT access token with role information."""
        try:
            if expires_delta is None:
                expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
            expiration = datetime.utcnow() + expires_delta
            
            # Include role in token payload
            data = {
                "sub": str(user_id),
                "role": role,
                "exp": expiration
            }
            
            access_token = jwt.encode(
                claims=data,
                key=settings.JWT_SECRET,
                algorithm=settings.JWT_ALGORITHM
            )

            # Store token in database
            async with db.get_client() as client:
                await client.token.create(
                    data={
                        "userId": user_id,
                        "token": access_token,
                        "expiresAt": expiration
                    }
                )

            return access_token
        except Exception as e:
            logger.error(f"Failed to create access token: {str(e)}")
            raise

    async def verify_token(self, token: str) -> Optional[Dict]:
        """Verify a token and return the user data."""
        try:
            async with db.get_client() as client:
                # Check if token exists and is not expired
                db_token = await client.token.find_first(
                    where={
                        "token": token,
                        "expiresAt": {"gt": datetime.utcnow()}
                    },
                    include={
                        "user": True
                    }
                )
                
                if not db_token:
                    return None

                # Verify JWT
                try:
                    payload = jwt.decode(
                        token=token,
                        key=settings.JWT_SECRET,
                        algorithms=[settings.JWT_ALGORITHM]
                    )
                except (JWTError, jwt.ExpiredSignatureError):
                    # Delete expired token
                    await client.token.delete_many(
                        where={"token": token}
                    )
                    return None

                return {
                    "id": db_token.user.id,
                    "email": db_token.user.email,
                    "name": db_token.user.name,
                    "role": db_token.user.role,
                    "isVerified": db_token.user.isVerified
                }

        except Exception as e:
            logger.error(f"Token verification error: {str(e)}")
            return None

    async def cleanup_expired_tokens(self):
        """Clean up expired tokens from database."""
        try:
            async with db.get_client() as client:
                await client.token.delete_many(
                    where={
                        "expiresAt": {"lt": datetime.utcnow()}
                    }
                )
        except Exception as e:
            logger.error(f"Token cleanup error: {str(e)}")

    async def logout_user(self, token: str) -> bool:
        """Logout user by removing their token."""
        try:
            async with db.get_client() as client:
                await client.token.delete_many(
                    where={"token": token}
                )
                return True
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
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
                    "has_api_key": bool(user.apiKey),
                    "role": user.role,
                    "created_at": user.createdAt
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

    async def create_password_reset_token(self, email: str) -> Optional[Dict]:
        """Create a password reset token."""
        try:
            async with db.get_client() as client:
                user = await client.user.find_unique(where={"email": email})
                if not user:
                    raise ValueError("No account found with this email address")

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
                
                return {
                    "token": token,
                    "email": email,
                    "name": user.name
                }
        except Exception as e:
            logger.error(f"Failed to create password reset token: {str(e)}")
            raise

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