# app/crud/crud_token.py
from sqlalchemy.orm import Session
from app.models.models import BlacklistedToken
from datetime import datetime

class CRUDToken:
    def is_token_blacklisted(self, db: Session, token: str) -> bool:
        """Check if token is blacklisted"""
        blacklisted = db.query(BlacklistedToken).filter(
            BlacklistedToken.token == token
        ).first()
        return blacklisted is not None

    def blacklist_token(self, db: Session, token: str, token_type: str = "access", reason: str = "logout") -> bool:
        """Add token to blacklist"""
        from app.core.security import verify_token
        
        # Decode token to get expiration
        payload = verify_token(token)
        if not payload:
            return False
        
        expires_at = datetime.fromtimestamp(payload['exp'])
        
        # Check if already blacklisted
        if self.is_token_blacklisted(db, token):
            return True
        
        blacklisted_token = BlacklistedToken(
            token=token,
            token_type=token_type,
            expires_at=expires_at,
            reason=reason
        )
        
        db.add(blacklisted_token)
        db.commit()
        return True

    def cleanup_expired_tokens(self, db: Session) -> int:
        """Remove expired blacklisted tokens"""
        result = db.query(BlacklistedToken).filter(
            BlacklistedToken.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        return result

    def get_blacklisted_tokens(self, db: Session, skip: int = 0, limit: int = 100):
        """Get all blacklisted tokens (for admin purposes)"""
        return db.query(BlacklistedToken).order_by(
            BlacklistedToken.blacklisted_at.desc()
        ).offset(skip).limit(limit).all()

crud_token = CRUDToken()