from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import re

class AdminBase(BaseModel):
    name: str
    phone_number: str
    email: EmailStr

class AdminCreate(AdminBase):
    password: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        return v

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v

class AdminUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class AdminResponse(AdminBase):
    admin_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminToken(BaseModel):
    access_token: str
    token_type: str
    admin_id: int