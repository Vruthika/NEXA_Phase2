from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import Customer
from app.core.auth import get_current_customer
from app.schemas.notification import NotificationResponse, NotificationStats, MarkAsReadRequest
from app.crud.crud_notification import crud_notification

router = APIRouter(prefix="/customer/notifications", tags=["Customer Notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_my_notifications(
    unread_only: bool = Query(False, description="Show only unread notifications"),
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get current customer's notifications
    """
    notifications = crud_notification.get_customer_notifications(
        db, current_customer.customer_id, unread_only=unread_only
    )
    return notifications

@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get notification statistics for customer
    """
    stats = crud_notification.get_notification_stats(db, current_customer.customer_id)
    return NotificationStats(**stats)

@router.post("/mark-read")
async def mark_notifications_as_read(
    read_request: MarkAsReadRequest,
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Mark specific notifications as read
    """
    count = crud_notification.mark_as_read(db, read_request.notification_ids, current_customer.customer_id)
    return {"message": f"Marked {count} notifications as read"}

@router.post("/mark-all-read")
async def mark_all_notifications_as_read(
    current_customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Mark all notifications as read for current customer
    """
    count = crud_notification.mark_all_as_read(db, current_customer.customer_id)
    return {"message": f"Marked all {count} notifications as read"}
