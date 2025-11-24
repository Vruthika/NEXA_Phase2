from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class PlanBase(BaseModel):
    category_id: int
    plan_name: str
    plan_type: str
    is_topup: bool = False
    price: float
    validity_days: int
    description: str
    data_allowance_gb: Optional[float] = None
    daily_data_limit_gb: Optional[float] = None
    talktime_allowance_minutes: Optional[int] = None
    sms_allowance: Optional[int] = None
    benefits: Optional[List[str]] = None
    max_secondary_numbers: int = 0 
    is_featured: bool = False

class PlanCreate(PlanBase):
    category_id: int
    plan_name: str
    plan_type: str
    is_topup: bool = False
    price: float
    validity_days: int
    description: str
    data_allowance_gb: Optional[float] = None
    daily_data_limit_gb: Optional[float] = None
    talktime_allowance_minutes: Optional[int] = None
    sms_allowance: Optional[int] = None
    benefits: Optional[List[str]] = None
    max_secondary_numbers: int = 0
    is_featured: bool = False

class PlanUpdate(BaseModel):
    category_id: Optional[int] = None
    plan_name: Optional[str] = None
    plan_type: Optional[str] = None
    is_topup: Optional[bool] = None
    price: Optional[float] = None
    validity_days: Optional[int] = None
    description: Optional[str] = None
    data_allowance_gb: Optional[float] = None
    daily_data_limit_gb: Optional[float] = None
    talktime_allowance_minutes: Optional[int] = None
    sms_allowance: Optional[int] = None
    benefits: Optional[List[str]] = None
    max_secondary_numbers: int = 0
    is_featured: Optional[bool] = None
    status: Optional[str] = None

class PlanResponse(PlanBase):
    plan_id: int
    category_id: int
    plan_name: str
    plan_type: str
    is_topup: bool
    price: float
    validity_days: int
    description: str
    data_allowance_gb: Optional[float]
    daily_data_limit_gb: Optional[float]
    talktime_allowance_minutes: Optional[int]
    sms_allowance: Optional[int]
    benefits: Optional[List[str]] = None
    max_secondary_numbers: int = 0
    is_featured: bool
    status: str
    created_at: Optional[datetime] = None   
    updated_at: Optional[datetime] = None  

    class Config:
        from_attributes = True