from pydantic import BaseModel, validator, field_validator
from datetime import datetime, date
from typing import Optional
import enum

class OfferStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    expired = "expired"

class OfferBase(BaseModel):
    plan_id: int
    offer_name: str
    description: Optional[str] = None
    discounted_price: float
    valid_from: str   
    valid_until: str  

    @validator('valid_from', 'valid_until', pre=True)
    def validate_date_format(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%d.%m.%Y %H:%M')
        
        try:
            datetime.strptime(v, '%d.%m.%Y %H:%M')
            return v
        except ValueError:
            raise ValueError('Date must be in format "DD.MM.YYYY HH:MM"')
    
    @validator('valid_until')
    def validate_dates(cls, v, values):
        if 'valid_from' in values and v:
            try:
                valid_from = datetime.strptime(values['valid_from'], '%d.%m.%Y %H:%M')
                valid_until = datetime.strptime(v, '%d.%m.%Y %H:%M')
                if valid_until <= valid_from:
                    raise ValueError('valid_until must be after valid_from')
            except (ValueError, TypeError):
                pass
        return v

class OfferCreate(OfferBase):
    pass

class OfferCreateWithDiscount(BaseModel):
    plan_id: int
    offer_name: str
    description: Optional[str] = None
    discount_percentage: float
    valid_from: str
    valid_until: str

    @validator('discount_percentage')
    def validate_discount_percentage(cls, v):
        if v <= 0 or v >= 100:
            raise ValueError('Discount percentage must be between 0 and 100')
        return v

    @validator('valid_from', 'valid_until', pre=True)
    def validate_date_format(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%d.%m.%Y %H:%M')
        
        try:
            datetime.strptime(v, '%d.%m.%Y %H:%M')
            return v
        except ValueError:
            raise ValueError('Date must be in format "DD.MM.YYYY HH:MM"')
    
    @validator('valid_until')
    def validate_dates(cls, v, values):
        if 'valid_from' in values and v:
            try:
                valid_from = datetime.strptime(values['valid_from'], '%d.%m.%Y %H:%M')
                valid_until = datetime.strptime(v, '%d.%m.%Y %H:%M')
                if valid_until <= valid_from:
                    raise ValueError('valid_until must be after valid_from')
            except (ValueError, TypeError):
                pass
        return v

class OfferUpdate(BaseModel):
    offer_name: Optional[str] = None
    description: Optional[str] = None
    discounted_price: Optional[float] = None
    valid_from: Optional[str] = None
    valid_until: Optional[str] = None

    @validator('valid_from', 'valid_until', pre=True)
    def validate_date_format(cls, v):
        if v is not None:
            if isinstance(v, datetime):
                return v.strftime('%d.%m.%Y %H:%M')
            try:
                datetime.strptime(v, '%d.%m.%Y %H:%M')
            except ValueError:
                raise ValueError('Date must be in format "DD.MM.YYYY HH:MM"')
        return v

class OfferResponse(OfferBase):
    offer_id: int
    status: OfferStatus
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        
    @validator('valid_from', 'valid_until', pre=True)
    def format_dates_for_response(cls, v):
        if isinstance(v, datetime):
            return v.strftime('%d.%m.%Y %H:%M')
        return v

class DiscountCalculationResponse(BaseModel):
    original_price: float
    discount_percentage: float
    discounted_price: float
    amount_saved: float

    class Config:
        from_attributes = True