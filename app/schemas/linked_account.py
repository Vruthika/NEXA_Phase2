from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List

class LinkedAccountBase(BaseModel):
    linked_phone_number: str

    @validator('linked_phone_number')
    def validate_phone_number(cls, v):
        if not v.isdigit() or len(v) < 10:
            raise ValueError('Phone number must contain only digits and be at least 10 characters long')
        return v

class LinkedAccountCreate(LinkedAccountBase):
    primary_customer_id: int

class LinkedAccountResponse(BaseModel):
    linked_account_id: int
    primary_customer_id: int
    linked_phone_number: str
    linked_customer_id: Optional[int] = None
    created_at: datetime
    
    # Additional details
    primary_customer_name: Optional[str] = None
    linked_customer_name: Optional[str] = None
    is_registered_user: bool = False

    class Config:
        from_attributes = True

class LinkedAccountDetailResponse(LinkedAccountResponse):
    # Subscription details for the linked number
    active_subscriptions: List[dict] = []
    total_spent: float = 0.0

class RechargeLinkedRequest(BaseModel):
    linked_account_id: int
    plan_id: int
    offer_id: Optional[int] = None
    payment_method: str

class RechargeLinkedResponse(BaseModel):
    transaction_id: int
    linked_phone_number: str
    plan_name: str
    final_amount: float
    message: str

    class Config:
        from_attributes = True