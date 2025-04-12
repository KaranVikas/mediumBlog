from datetime import datetime, timedelta
import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from fastapi.security import OAuth2PasswordBearer
from core.settings import settings

# Password hashing context
pwd_context = PasswordHash((BcryptHasher(),))

def get_password_hash(password: str) -> str:
    """Generate a password hash using pwdlib"""
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(password, hashed_password)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(user_id: str) -> str:
    """Create a JWT access token using pyjwt"""
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    return jwt.encode(
        payload,
        settings.SECRET_KEY.get_secret_value() if settings.SECRET_KEY else None,
        algorithm=settings.ALGORITHM
    )

