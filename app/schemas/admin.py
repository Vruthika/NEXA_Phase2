from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class AdminBase(BaseModel):
    name: str
    phone_number: str
    email: EmailStr

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None

class AdminResponse(AdminBase):
    admin_id: int
    created_at: Optional[datetime] = None  
    updated_at: Optional[datetime] = None  

    class Config:
        from_attributes = True

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminChangePassword(BaseModel):
    current_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str