from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    message: str
    type: str
    channel: str

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    notification_id: int
    customer_id: int
    is_read: bool
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True