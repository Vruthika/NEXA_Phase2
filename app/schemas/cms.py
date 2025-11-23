from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, List
from datetime import datetime

# ============================================
# HEADER SCHEMAS
# ============================================

class HeaderBase(BaseModel):
    title: str
    description: str
    button_text: str
    image_url: str

class HeaderCreate(HeaderBase):
    pass

class HeaderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    button_text: Optional[str] = None
    image_url: Optional[str] = None

class HeaderResponse(HeaderBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# CAROUSEL SCHEMAS
# ============================================

class CarouselBase(BaseModel):
    title: str
    details: str
    price_text: str
    category_id: str 
    image_url: str
    cta_text: str
    order: int

class CarouselCreate(CarouselBase):
    pass

class CarouselUpdate(BaseModel):
    title: Optional[str] = None
    details: Optional[str] = None
    price_text: Optional[str] = None
    category_id: Optional[str] = None
    image_url: Optional[str] = None
    cta_text: Optional[str] = None
    order: Optional[int] = None

class CarouselResponse(CarouselBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
# ============================================
# FAQ SCHEMAS
# ============================================

class FAQBase(BaseModel):
    question: str
    answer: str
    image_url: Optional[str] = None
    order: int

class FAQCreate(FAQBase):
    pass

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    image_url: Optional[str] = None
    order: Optional[int] = None

class FAQResponse(FAQBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ============================================
# UTILITY SCHEMAS
# ============================================

class CMSListResponse(BaseModel):
    headers: List[HeaderResponse]
    carousels: List[CarouselResponse]
    faqs: List[FAQResponse]

class CMSReorderRequest(BaseModel):
    item_id: str
    new_order: int
    collection_type: str  # "header", "carousel", "faq"