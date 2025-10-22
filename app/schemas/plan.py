from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class PlanBase(BaseModel):
    plan_name: str
    plan_type: str
    is_topup: bool = False
    price: Decimal
    validity_days: int
    description: str
    data_allowance_gb: Optional[Decimal] = None
    daily_data_limit_gb: Optional[Decimal] = None
    talktime_allowance_minutes: Optional[int] = None
    sms_allowance: Optional[int] = None
    benefits: Optional[Dict[str, Any]] = None
    is_featured: bool = False
    status: str = "active"

class PlanCreate(PlanBase):
    category_id: int

class PlanUpdate(BaseModel):
    plan_name: Optional[str] = None
    price: Optional[Decimal] = None
    validity_days: Optional[int] = None
    description: Optional[str] = None
    data_allowance_gb: Optional[Decimal] = None
    daily_data_limit_gb: Optional[Decimal] = None
    talktime_allowance_minutes: Optional[int] = None
    sms_allowance: Optional[int] = None
    benefits: Optional[Dict[str, Any]] = None
    is_featured: Optional[bool] = None
    status: Optional[str] = None

class PlanResponse(PlanBase):
    plan_id: int
    category_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True