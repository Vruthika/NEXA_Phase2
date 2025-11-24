from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class LogoutResponse(BaseModel):
    message: str

class TokenBlacklistResponse(BaseModel):
    id: int
    token: str
    token_type: str
    expires_at: str
    blacklisted_at: str
    reason: str

    class Config:
        from_attributes = True