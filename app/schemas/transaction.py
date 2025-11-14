# app/schemas/transaction.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.models import TransactionType, PaymentMethod, PaymentStatus, DiscountType

class TransactionBase(BaseModel):
    customer_id: int
    plan_id: int
    offer_id: Optional[int] = None
    recipient_phone_number: str
    transaction_type: TransactionType
    original_amount: float
    discount_amount: float = 0.0
    discount_type: Optional[DiscountType] = None
    final_amount: float
    payment_method: PaymentMethod
    payment_status: PaymentStatus

class TransactionResponse(TransactionBase):
    transaction_id: int
    transaction_date: datetime
    
    # Include related data
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    plan_name: Optional[str] = None
    offer_name: Optional[str] = None

    class Config:
        from_attributes = True

class TransactionFilter(BaseModel):
    customer_id: Optional[int] = None
    customer_phone: Optional[str] = None
    plan_id: Optional[int] = None
    transaction_type: Optional[TransactionType] = None
    payment_status: Optional[PaymentStatus] = None
    payment_method: Optional[PaymentMethod] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

class TransactionExportRequest(TransactionFilter):
    export_format: str = "csv"  # csv or json