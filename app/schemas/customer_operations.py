from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.models import AccountStatus, TransactionType, PaymentMethod, PaymentStatus

class CustomerProfileResponse(BaseModel):
    customer_id: int
    phone_number: str
    full_name: str
    profile_picture_url: Optional[str] = None
    account_status: AccountStatus
    last_active_plan_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CustomerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_picture_url: Optional[str] = None

class CustomerTransactionResponse(BaseModel):
    transaction_id: int
    plan_name: str
    recipient_phone_number: str
    transaction_type: TransactionType
    original_amount: float
    discount_amount: float
    final_amount: float
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    transaction_date: datetime

    class Config:
        from_attributes = True

class CustomerSubscriptionResponse(BaseModel):
    subscription_id: int
    plan_name: str
    phone_number: str
    is_topup: bool
    activation_date: datetime
    expiry_date: datetime
    data_balance_gb: Optional[float] = None
    daily_data_limit_gb: Optional[float] = None
    daily_data_used_gb: Optional[float] = None
    status: str  # active or expired

    class Config:
        from_attributes = True

class CustomerQueueResponse(BaseModel):
    queue_id: int
    plan_name: str
    phone_number: str
    queue_position: int
    expected_activation_date: datetime
    expected_expiry_date: datetime

    class Config:
        from_attributes = True

class PlanResponseForCustomer(BaseModel):
    plan_id: int
    category_name: str
    plan_name: str
    plan_type: str
    is_topup: bool
    price: float
    validity_days: int
    description: str
    data_allowance_gb: Optional[float] = None
    daily_data_limit_gb: Optional[float] = None
    talktime_allowance_minutes: Optional[int] = None
    sms_allowance: Optional[int] = None
    benefits: Optional[List[str]] = None
    is_featured: bool
    has_active_offer: bool = False
    offer_id: Optional[int] = None
    offer_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    offer_valid_until: Optional[str] = None

    class Config:
        from_attributes = True

class OfferResponseForCustomer(BaseModel):
    offer_id: int
    plan_name: str
    offer_name: str
    description: Optional[str] = None
    original_price: float
    discounted_price: float
    discount_percentage: float
    valid_from: str
    valid_until: str

    class Config:
        from_attributes = True

class RechargeRequest(BaseModel):
    plan_id: int
    offer_id: Optional[int] = None
    recipient_phone_number: str
    payment_method: PaymentMethod

class RechargeResponse(BaseModel):
    transaction_id: int
    plan_name: str
    final_amount: float
    payment_status: PaymentStatus
    message: str