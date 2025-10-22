from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from app.crud.notification_crud import NotificationCRUD
from app.crud.customer_crud import CustomerCRUD
from app.schemas.notification import NotificationCreate

class NotificationService:
    def __init__(self, db: Session):
        self.db = db
        self.notification_crud = NotificationCRUD(db)
        self.customer_crud = CustomerCRUD(db)
    
    def create_notification(self, customer_id: int, notification_type: str, title: str, message: str, channel: str = "push"):
        # Verify customer exists
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        notification_data = {
            "customer_id": customer_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "channel": channel,
            "sent_at": datetime.utcnow()
        }
        
        return self.notification_crud.create(notification_data)
    
    def get_notification_by_id(self, notification_id: int):
        notification = self.notification_crud.get_by_id(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        return notification
    
    def get_customer_notifications(self, customer_id: int, skip: int = 0, limit: int = 50, unread_only: bool = False):
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return self.notification_crud.get_by_customer_id(customer_id, skip, limit, unread_only)
    
    def get_unread_count(self, customer_id: int):
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return self.notification_crud.get_unread_count(customer_id)
    
    def mark_as_read(self, notification_id: int):
        notification = self.get_notification_by_id(notification_id)
        return self.notification_crud.mark_as_read(notification_id)
    
    def mark_all_as_read(self, customer_id: int):
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        return self.notification_crud.mark_all_as_read(customer_id)
    
    def delete_notification(self, notification_id: int):
        notification = self.get_notification_by_id(notification_id)
        return self.notification_crud.delete(notification_id)
    
    def get_unsent_notifications(self):
        return self.notification_crud.get_unsent_notifications()
    
    def mark_as_sent(self, notification_id: int):
        notification = self.get_notification_by_id(notification_id)
        return self.notification_crud.mark_as_sent(notification_id)