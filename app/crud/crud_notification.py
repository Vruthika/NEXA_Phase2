from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.models import Notification, Customer, NotificationType, NotificationChannel, AccountStatus
from app.schemas.notification import NotificationCreate

class CRUDNotification:
    def get_by_id(self, db: Session, notification_id: int):
        return db.query(Notification).filter(Notification.notification_id == notification_id).first()
    
    def get_customer_notifications(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100, 
                                 unread_only: bool = False):
        query = db.query(Notification).filter(Notification.customer_id == customer_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    def create_notification(self, db: Session, notification: NotificationCreate):
        db_notification = Notification(
            customer_id=notification.customer_id,
            title=notification.title,
            message=notification.message,
            type=notification.type,
            channel=notification.channel,
            status="pending"
        )
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    
    def create_bulk_notifications(self, db: Session, notifications: List[NotificationCreate]):
        """Create multiple notifications at once"""
        db_notifications = []
        for notification_data in notifications:
            db_notification = Notification(
                customer_id=notification_data.customer_id,
                title=notification_data.title,
                message=notification_data.message,
                type=notification_data.type,
                channel=notification_data.channel,
                status="pending"
            )
            db_notifications.append(db_notification)
            db.add(db_notification)
        
        db.commit()
        
        # Refresh all notifications to get their IDs
        for notification in db_notifications:
            db.refresh(notification)
        
        return db_notifications
    
    def mark_as_read(self, db: Session, notification_ids: List[int], customer_id: int):
        """Mark multiple notifications as read for a customer"""
        result = db.query(Notification).filter(
            Notification.notification_id.in_(notification_ids),
            Notification.customer_id == customer_id
        ).update({
            Notification.is_read: True
        }, synchronize_session=False)
        
        db.commit()
        return result
    
    def mark_all_as_read(self, db: Session, customer_id: int):
        """Mark all notifications as read for a customer"""
        result = db.query(Notification).filter(
            Notification.customer_id == customer_id,
            Notification.is_read == False
        ).update({
            Notification.is_read: True
        }, synchronize_session=False)
        
        db.commit()
        return result
    
    def update_notification_status(self, db: Session, notification_id: int, status: str, 
                                 delivery_mode: str = "real", sent_at: datetime = None):
        """Update notification status and delivery info"""
        notification = self.get_by_id(db, notification_id)
        if notification:
            notification.status = status
            notification.delivery_mode = delivery_mode
            if sent_at:
                notification.sent_at = sent_at
            else:
                notification.sent_at = datetime.utcnow()
            db.commit()
            db.refresh(notification)
        return notification
    
    def get_notification_stats(self, db: Session, customer_id: int):
        """Get notification statistics for a customer - shows received_today"""
        total_notifications = db.query(Notification).filter(
            Notification.customer_id == customer_id
        ).count()
        
        unread_count = db.query(Notification).filter(
            Notification.customer_id == customer_id,
            Notification.is_read == False
        ).count()
        
        # Notifications received today (by customer)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        received_today = db.query(Notification).filter(
            Notification.customer_id == customer_id,
            Notification.created_at >= today_start 
        ).count()
        
        # Count by type
        type_counts = db.query(
            Notification.type,
            func.count(Notification.notification_id)
        ).filter(
            Notification.customer_id == customer_id
        ).group_by(Notification.type).all()
        
        by_type = {ntype.value: count for ntype, count in type_counts}
        
        # Count by channel
        channel_counts = db.query(
            Notification.channel,
            func.count(Notification.notification_id)
        ).filter(
            Notification.customer_id == customer_id
        ).group_by(Notification.channel).all()
        
        by_channel = {nchannel.value: count for nchannel, count in channel_counts}
        
        return {
            "total_notifications": total_notifications,
            "unread_count": unread_count,
            "received_today": received_today,  
            "by_type": by_type,
            "by_channel": by_channel
        }

    def get_all_notifications(self, db: Session, skip: int = 0, limit: int = 100, 
                            customer_id: Optional[int] = None, 
                            type: Optional[NotificationType] = None,
                            channel: Optional[NotificationChannel] = None,
                            status: Optional[str] = None):
        """Get all notifications with filtering (for admin)"""
        query = db.query(Notification)
        
        if customer_id:
            query = query.filter(Notification.customer_id == customer_id)
        if type:
            query = query.filter(Notification.type == type)
        if channel:
            query = query.filter(Notification.channel == channel)
        if status:
            query = query.filter(Notification.status == status)
        
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_active_customers(self, db: Session):
        """Get all active customers for broadcast notifications"""
        return db.query(Customer).filter(
            Customer.account_status == AccountStatus.active,
            Customer.deleted_at.is_(None)
        ).all()

crud_notification = CRUDNotification()