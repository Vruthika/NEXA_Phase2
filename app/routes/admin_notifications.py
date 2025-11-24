from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.models import Admin, Notification, NotificationType, NotificationChannel
from app.core.auth import get_current_admin
from app.schemas.notification import NotificationResponse, AdminNotificationCreate
from app.crud.crud_notification import crud_notification
from app.services.notification_service import notification_service

router = APIRouter(prefix="/notifications", tags=["Admin Notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_all_notifications(
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    notification_type: Optional[NotificationType] = Query(None, description="Filter by type"),
    channel: Optional[NotificationChannel] = Query(None, description="Filter by channel"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: Get all notifications with filtering options
    """
    notifications = crud_notification.get_all_notifications(
        db, customer_id=customer_id, 
        type=notification_type, channel=channel, status=status
    )
    return notifications

@router.post("/send")
async def send_admin_notification(
    notification_data: AdminNotificationCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: Send notification to one or multiple customers
    """
    from app.schemas.notification import NotificationCreate
    
    notifications_to_send = []
    
    if notification_data.send_to_all:
        # Send to all active customers
        customers = crud_notification.get_active_customers(db)
        for customer in customers:
            notification_create = NotificationCreate(
                customer_id=customer.customer_id,
                title=notification_data.title,
                message=notification_data.message,
                type=notification_data.type,
                channel=notification_data.channel
            )
            notifications_to_send.append(notification_create)
    else:
        # Send to specific customers
        if not notification_data.customer_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either specify customer_ids or set send_to_all=True"
            )
        
        for customer_id in notification_data.customer_ids:
            notification_create = NotificationCreate(
                customer_id=customer_id,
                title=notification_data.title,
                message=notification_data.message,
                type=notification_data.type,
                channel=notification_data.channel
            )
            notifications_to_send.append(notification_create)
    
    if not notifications_to_send:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No customers found to send notifications"
        )
    
    # Create notifications in bulk
    notifications = crud_notification.create_bulk_notifications(db, notifications_to_send)
    
    # Send notifications
    results = notification_service.send_bulk_notifications(db, notifications)
    
    successful = sum(1 for result in results if result["success"])
    failed = len(results) - successful
    
    return {
        "message": f"Notifications sent successfully to {successful} customers, {failed} failed",
        "total_sent": len(notifications),
        "successful": successful,
        "failed": failed,
        "results": results
    }

@router.get("/stats")
async def get_admin_notification_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Admin: Get system-wide notification statistics - shows sent_today
    """
    # Get total notifications
    total_notifications = db.query(Notification).count()
    
    # Notifications sent today (by system)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    sent_today = db.query(Notification).filter(Notification.sent_at >= today_start).count()
    
    # Count by type
    type_counts = db.query(
        Notification.type,
        func.count(Notification.notification_id)
    ).group_by(Notification.type).all()
    
    by_type = {ntype.value: count for ntype, count in type_counts}
    
    # Count by channel
    channel_counts = db.query(
        Notification.channel,
        func.count(Notification.notification_id)
    ).group_by(Notification.channel).all()
    
    by_channel = {nchannel.value: count for nchannel, count in channel_counts}
    
    # Count by status
    status_counts = db.query(
        Notification.status,
        func.count(Notification.notification_id)
    ).group_by(Notification.status).all()
    
    by_status = {status: count for status, count in status_counts}
    
    return {
        "total_notifications": total_notifications,
        "sent_today": sent_today, 
        "by_type": by_type,
        "by_channel": by_channel,
        "by_status": by_status
    }
    
@router.get("/automated-stats")
async def get_automated_notification_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get statistics about automated notifications"""
    from sqlalchemy import func
    
    # Count by type for automated notifications
    automated_types = [
        "plan_expiry", "low_balance", "payment_success", 
        "referral_bonus", "plan_activated", "plan_queued"
    ]
    
    type_counts = db.query(
        Notification.type,
        func.count(Notification.notification_id)
    ).filter(
        Notification.type.in_(automated_types)
    ).group_by(Notification.type).all()
    
    # Recent automated notifications
    recent_automated = db.query(Notification).filter(
        Notification.type.in_(automated_types)
    ).order_by(Notification.created_at.desc()).limit(10).all()
    
    return {
        "automated_by_type": {ntype: count for ntype, count in type_counts},
        "recent_automated": [
            {
                "notification_id": n.notification_id,
                "customer_id": n.customer_id,
                "type": n.type,
                "title": n.title,
                "created_at": n.created_at
            } for n in recent_automated
        ]
    }