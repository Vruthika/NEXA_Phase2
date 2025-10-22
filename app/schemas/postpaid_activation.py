from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class PostpaidActivationBase(BaseModel):
    plan_id: int
    primary_number: str

class PostpaidActivationCreate(PostpaidActivationBase):
    pass

class PostpaidActivationResponse(PostpaidActivationBase):
    activation_id: int
    customer_id: int
    billing_cycle_start: datetime
    billing_cycle_end: datetime
    base_data_allowance_gb: Decimal
    current_data_balance_gb: Decimal
    data_used_gb: Decimal
    base_amount: Decimal
    total_amount_due: Decimal
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostpaidSecondaryNumberCreate(BaseModel):
    phone_number: str
    customer_id: Optional[int] = None

class PostpaidDataAddonCreate(BaseModel):
    addon_name: str
    data_amount_gb: Decimal
    addon_price: Decimal