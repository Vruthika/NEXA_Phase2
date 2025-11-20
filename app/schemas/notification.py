# app/schemas/notification.py
from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional, Union
from app.models.models import NotificationType, NotificationChannel

class NotificationBase(BaseModel):
    title: str
    message: str
    type: NotificationType
    channel: NotificationChannel

class NotificationCreate(NotificationBase):
    customer_id: int

class NotificationResponse(NotificationBase):
    notification_id: int
    customer_id: int
    is_read: bool
    status: str
    delivery_mode: str
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AdminNotificationCreate(BaseModel):
    title: str
    message: str
    type: NotificationType = NotificationType.promotional
    channel: NotificationChannel
    customer_ids: Optional[List[int]] = None  # Send to specific customers
    send_to_all: bool = False  # Send to all active customers

    @validator('customer_ids')
    def validate_customer_ids(cls, v, values):
        if values.get('send_to_all') and v:
            raise ValueError('Cannot specify customer_ids when send_to_all is True')
        return v

class NotificationStats(BaseModel):
    total_notifications: int
    unread_count: int
    received_today: int 
    by_type: dict
    by_channel: dict

class AdminNotificationStats(BaseModel):
    total_notifications: int
    sent_today: int  
    by_type: dict
    by_channel: dict
    by_status: dict

class MarkAsReadRequest(BaseModel):
    notification_ids: List[int]