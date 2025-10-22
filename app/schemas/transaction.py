from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class TransactionBase(BaseModel):
    plan_id: int
    recipient_phone_number: str
    transaction_type: str
    payment_method: str
    offer_id: Optional[int] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(TransactionBase):
    transaction_id: int
    customer_id: int
    original_amount: Decimal
    discount_amount: Decimal
    discount_type: Optional[str]
    final_amount: Decimal
    payment_status: str
    transaction_date: datetime
    
    class Config:
        from_attributes = True

class TransactionUpdate(BaseModel):
    payment_status: Optional[str] = None