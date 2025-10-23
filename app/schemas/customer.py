from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CustomerLogin(BaseModel):
    phone_number: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str