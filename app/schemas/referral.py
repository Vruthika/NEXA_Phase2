from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.models import ReferralStatus

class ReferralProgramBase(BaseModel):
    expires_at: datetime
    max_uses: int = 1

class ReferralProgramCreate(ReferralProgramBase):
    pass

class ReferralProgramResponse(BaseModel):
    referral_id: int
    referrer_customer_id: int
    referee_phone_number: str
    referral_code: str
    status: ReferralStatus
    referee_customer_id: Optional[int]
    is_active: bool
    expires_at: datetime
    max_uses: int
    current_uses: int
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReferralDiscountResponse(BaseModel):
    discount_id: int
    referral_id: int
    customer_id: int
    discount_percentage: float
    is_used: bool
    valid_until: datetime
    created_at: datetime
    used_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReferralUsageLogResponse(BaseModel):
    log_id: int
    referral_id: int
    used_by_phone: str
    used_by_customer_id: Optional[int]
    used_at: datetime

    class Config:
        from_attributes = True

class ReferralStatsResponse(BaseModel):
    referral_code: str
    total_uses: int
    successful_referrals: int
    max_uses: int
    expires_at: datetime
    is_active: bool
    status: ReferralStatus

class ReferralApplyRequest(BaseModel):
    referral_code: str

class ReferralApplyResponse(BaseModel):
    success: bool
    message: str
    discount_percentage: Optional[float] = None

# ADD THE MISSING REFERRALCONFIG SCHEMA
class ReferralConfig(BaseModel):
    referrer_discount_percentage: float = 30.0
    referee_discount_percentage: float = 10.0
    default_expiry_days: int = 30
    default_max_uses: int = 1

class SystemReferralStats(BaseModel):
    total_referral_programs: int
    active_referral_programs: int
    total_referral_uses: int
    status_stats: dict
    top_referrers: List[dict]