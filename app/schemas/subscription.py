from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class SubscriptionBase(BaseModel):
    phone_number: str
    plan_id: int
    transaction_id: int
    is_topup: bool = False

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    data_balance_gb: Optional[Decimal] = None
    daily_data_used_gb: Optional[Decimal] = None
    last_daily_reset: Optional[datetime] = None

class SubscriptionResponse(SubscriptionBase):
    subscription_id: int
    customer_id: int
    activation_date: datetime
    expiry_date: datetime
    data_balance_gb: Optional[Decimal]
    daily_data_limit_gb: Optional[Decimal]
    daily_data_used_gb: Decimal
    last_daily_reset: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True