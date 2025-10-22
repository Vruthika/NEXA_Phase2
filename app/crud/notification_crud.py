from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.notification import Notification
from datetime import datetime

class NotificationCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, notification_id: int) -> Notification:
        return self.db.query(Notification).filter(Notification.notification_id == notification_id).first()
    
    def get_by_customer_id(self, customer_id: int, skip: int = 0, limit: int = 50, unread_only: bool = False):
        query = self.db.query(Notification).filter(Notification.customer_id == customer_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_unread_count(self, customer_id: int):
        return self.db.query(Notification).filter(
            and_(
                Notification.customer_id == customer_id,
                Notification.is_read == False
            )
        ).count()
    
    def get_unsent_notifications(self):
        return self.db.query(Notification).filter(Notification.sent_at.is_(None)).all()
    
    def create(self, notification_data: dict) -> Notification:
        notification = Notification(**notification_data)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def mark_as_read(self, notification_id: int) -> Notification:
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
        return notification
    
    def mark_all_as_read(self, customer_id: int) -> int:
        notifications = self.db.query(Notification).filter(
            and_(
                Notification.customer_id == customer_id,
                Notification.is_read == False
            )
        ).all()
        
        for notification in notifications:
            notification.is_read = True
        
        self.db.commit()
        return len(notifications)
    
    def mark_as_sent(self, notification_id: int) -> Notification:
        notification = self.get_by_id(notification_id)
        if notification:
            notification.sent_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(notification)
        return notification
    
    def delete(self, notification_id: int) -> bool:
        notification = self.get_by_id(notification_id)
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        return False