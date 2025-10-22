from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.dependencies import get_current_customer
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter()

@router.get("/my-notifications", response_model=List[NotificationResponse])
async def get_my_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    return notification_service.get_customer_notifications(
        current_customer.customer_id,
        skip,
        limit,
        unread_only
    )

@router.get("/unread-count")
async def get_unread_count(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    count = notification_service.get_unread_count(current_customer.customer_id)
    
    return {"unread_count": count}

@router.post("/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    notification = notification_service.get_notification_by_id(notification_id)
    
    # Verify notification belongs to current customer
    if notification.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this notification"
        )
    
    updated_notification = notification_service.mark_as_read(notification_id)
    
    return {
        "message": "Notification marked as read",
        "notification_id": notification_id
    }

@router.post("/mark-all-read")
async def mark_all_notifications_read(
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    count = notification_service.mark_all_as_read(current_customer.customer_id)
    
    return {
        "message": f"Marked {count} notifications as read",
        "read_count": count
    }

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_customer: dict = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    notification_service = NotificationService(db)
    notification = notification_service.get_notification_by_id(notification_id)
    
    # Verify notification belongs to current customer
    if notification.customer_id != current_customer.customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this notification"
        )
    
    notification_service.delete_notification(notification_id)
    return None