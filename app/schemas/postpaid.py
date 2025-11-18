from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional
from app.models.models import PostpaidStatus, AddonStatus

# ==========================================================
# POSTPAID SCHEMAS
# ==========================================================

class PostpaidPlanResponse(BaseModel):
    plan_id: int
    plan_name: str
    price: float
    description: str
    data_allowance_gb: Optional[float] = None
    talktime_allowance_minutes: Optional[int] = None
    sms_allowance: Optional[int] = None
    benefits: Optional[List[str]] = None

    class Config:
        from_attributes = True

class SecondaryNumberResponse(BaseModel):
    secondary_id: int
    phone_number: str
    added_date: datetime

    class Config:
        from_attributes = True

class DataAddonResponse(BaseModel):
    addon_id: int
    addon_name: str
    data_amount_gb: float
    addon_price: float
    purchased_date: datetime
    valid_until: datetime
    status: AddonStatus

    class Config:
        from_attributes = True

class PostpaidActivationRequest(BaseModel):
    plan_id: int
    primary_number: str

    @validator('primary_number')
    def validate_phone_number(cls, v):
        if not v.isdigit() or len(v) < 10:
            raise ValueError('Phone number must contain only digits and be at least 10 characters long')
        return v

class PostpaidActivationResponse(BaseModel):
    activation_id: int
    plan_name: str
    primary_number: str
    billing_cycle_start: datetime
    billing_cycle_end: datetime
    base_data_allowance_gb: float
    current_data_balance_gb: float
    data_used_gb: float
    base_amount: float
    total_amount_due: float
    status: PostpaidStatus
    secondary_numbers: List[SecondaryNumberResponse] = []
    user_role: str = "primary_owner"

    class Config:
        from_attributes = True

class PostpaidBillResponse(BaseModel):
    activation_id: int
    billing_cycle_start: datetime
    billing_cycle_end: datetime
    base_amount: float
    addon_charges: float = 0.0
    total_amount_due: float
    due_date: datetime

    class Config:
        from_attributes = True

class DataAddonPurchaseRequest(BaseModel):
    activation_id: int
    plan_id: int 

    @validator('plan_id')
    def validate_plan_id(cls, v):
        if v <= 0:
            raise ValueError('Plan ID must be positive')
        return v

class SecondaryNumberRequest(BaseModel):
    activation_id: int
    phone_number: str

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if not v.isdigit() or len(v) < 10:
            raise ValueError('Phone number must contain only digits and be at least 10 characters long')
        return v

class PostpaidUsageResponse(BaseModel):
    activation_id: int
    data_used_gb: float
    current_data_balance_gb: float
    base_data_allowance_gb: float

    class Config:
        from_attributes = True

class BillPaymentRequest(BaseModel):
    activation_id: int
    payment_method: str

# ==========================================================
# ADMIN POSTPAID SCHEMAS
# ==========================================================

class PostpaidActivationFilter(BaseModel):
    plan_id: Optional[int] = None
    status: Optional[PostpaidStatus] = None
    customer_phone: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class PostpaidActivationDetailResponse(PostpaidActivationResponse):
    customer_id: int
    customer_name: str
    customer_phone: str
    data_addons: List[DataAddonResponse] = []

    class Config:
        from_attributes = True
        
