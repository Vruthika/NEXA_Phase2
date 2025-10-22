from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
import re

class CustomerBase(BaseModel):
    phone_number: str
    full_name: str

class CustomerCreate(CustomerBase):
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

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    account_status: Optional[str] = None

class CustomerResponse(CustomerBase):
    customer_id: int
    account_status: str
    profile_picture_url: Optional[str]
    last_active_plan_date: Optional[datetime]
    days_inactive: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CustomerLogin(BaseModel):
    phone_number: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    customer_id: int

class TokenData(BaseModel):
    customer_id: Optional[int] = None