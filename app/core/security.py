from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings
from typing import Optional, Dict, Any
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None, user_type: str = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    
    # Add user type to token payload
    if user_type:
        to_encode.update({"user_type": user_type})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Refresh tokens typically last longer, e.g., 7 days
        expire = datetime.utcnow() + timedelta(days=7)
    
    # Add unique jti (JWT ID) for refresh token
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4())  # Unique identifier for this refresh token
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, db: Optional[Any] = None) -> Optional[Dict]:
    """
    Verify token and check if it's blacklisted
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # If db is provided, check if token is blacklisted
        if db:
            from app.models.models import BlacklistedToken
            blacklisted = db.query(BlacklistedToken).filter(
                BlacklistedToken.token == token
            ).first()
            if blacklisted:
                return None
        
        return payload
    except JWTError:
        return None

def is_token_blacklisted(db, token: str) -> bool:
    """Check if token is blacklisted"""
    from app.models.models import BlacklistedToken
    blacklisted = db.query(BlacklistedToken).filter(
        BlacklistedToken.token == token
    ).first()
    return blacklisted is not None

def blacklist_token(db, token: str, token_type: str = "access"):
    """Add token to blacklist"""
    from app.models.models import BlacklistedToken
    from app.core.security import verify_token
    
    # Decode token to get expiration
    payload = verify_token(token)
    if not payload:
        return False
    
    expires_at = datetime.fromtimestamp(payload['exp'])
    
    blacklisted_token = BlacklistedToken(
        token=token,
        token_type=token_type,
        expires_at=expires_at,
        reason='logout'
    )
    
    db.add(blacklisted_token)
    db.commit()
    return True