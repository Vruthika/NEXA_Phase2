from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class ReferralProgramBase(BaseModel):
    referee_phone_number: str
    max_uses: int = 1

class ReferralProgramCreate(ReferralProgramBase):
    pass

class ReferralProgramResponse(ReferralProgramBase):
    referral_id: int
    referrer_customer_id: int
    referral_code: str
    status: str
    referee_customer_id: Optional[int]
    is_active: bool
    expires_at: datetime
    current_uses: int
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True