from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ActiveTopupBase(BaseModel):
    phone_number: str
    base_subscription_id: int
    topup_plan_id: int
    transaction_id: int
    topup_data_gb: Decimal
    activation_date: datetime
    expiry_date: datetime

class ActiveTopupCreate(ActiveTopupBase):
    pass

class ActiveTopupResponse(ActiveTopupBase):
    topup_id: int
    customer_id: int
    data_remaining_gb: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True