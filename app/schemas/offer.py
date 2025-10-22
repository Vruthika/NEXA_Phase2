from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class OfferBase(BaseModel):
    plan_id: int
    discounted_price: Decimal
    valid_from: datetime
    valid_until: datetime

class OfferCreate(OfferBase):
    pass

class OfferUpdate(BaseModel):
    discounted_price: Optional[Decimal] = None
    valid_until: Optional[datetime] = None

class OfferResponse(OfferBase):
    offer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True