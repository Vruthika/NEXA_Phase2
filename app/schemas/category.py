from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class CategoryBase(BaseModel):
    category_name: str

class CategoryCreate(CategoryBase):
    category_name: str

class CategoryResponse(CategoryBase):
    category_id: int
    category_name: str

    created_at: Optional[datetime] = None  # Make optional

    class Config:
        from_attributes = True