import bcrypt
from cryptography.fernet import Fernet
from .config import settings

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(
        plain_password.encode(),
        hashed_password.encode()
    )

# Initialize Fernet cipher for API key encryption
cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key."""
    return cipher_suite.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key: str) -> str:
    """Decrypt an API key."""
    return cipher_suite.decrypt(encrypted_api_key.encode()).decode() 