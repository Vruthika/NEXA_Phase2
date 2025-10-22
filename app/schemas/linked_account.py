from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class LinkedAccountBase(BaseModel):
    linked_phone_number: str
    linked_customer_id: Optional[int] = None

class LinkedAccountCreate(LinkedAccountBase):
    pass

class LinkedAccountResponse(LinkedAccountBase):
    linked_account_id: int
    primary_customer_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True