from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List
from app.models.models import AccountStatus

class CustomerLogin(BaseModel):
    phone_number: str
    password: str

class CustomerRegister(BaseModel):
    phone_number: str
    password: str
    full_name: str
    profile_picture_url: Optional[str] = None
    referral_code: Optional[str] = None  

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if not v.isdigit() or len(v) < 10:
            raise ValueError('Phone number must contain only digits and be at least 10 characters long')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
class Token(BaseModel):
    access_token: str
    token_type: str

class CustomerBase(BaseModel):
    phone_number: str
    full_name: str
    account_status: AccountStatus

class CustomerResponse(CustomerBase):
    customer_id: int
    profile_picture_url: Optional[str] = None
    last_active_plan_date: Optional[datetime] = None
    days_inactive: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CustomerDetailResponse(CustomerResponse):
    total_transactions: int = 0
    total_spent: float = 0.0
    active_subscriptions: int = 0
    queued_subscriptions: int = 0
    referral_code: Optional[str] = None

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    account_status: Optional[AccountStatus] = None

class CustomerFilter(BaseModel):
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    account_status: Optional[AccountStatus] = None
    days_inactive_min: Optional[int] = None
    days_inactive_max: Optional[int] = None

class CustomerStatsResponse(BaseModel):
    total_customers: int
    active_customers: int
    inactive_customers: int
    suspended_customers: int
    new_customers_today: int
    new_customers_this_week: int