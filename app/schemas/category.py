from pydantic import BaseModel
from datetime import datetime

class CategoryBase(BaseModel):
    category_name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    category_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True