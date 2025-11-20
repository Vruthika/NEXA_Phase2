# app/services/notification_service.py
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import logging
from app.models.models import Notification, NotificationChannel, Customer
from app.crud.crud_notification import crud_notification
from app.schemas.notification import NotificationCreate

# Configure logging
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.sms_simulation_enabled = True
    
    def send_notification(self, db: Session, notification: Notification):
        """
        Send notification based on channel
        - SMS: Log to console in Jio/Airtel format (simulation)
        - Push: Send real push notification
        """
        try:
            customer = db.query(Customer).filter(
                Customer.customer_id == notification.customer_id
            ).first()
            
            if not customer:
                logger.error(f"Customer not found for notification: {notification.notification_id}")
                crud_notification.update_notification_status(
                    db, notification.notification_id, "failed"
                )
                return False
            
            if notification.channel == NotificationChannel.sms:
                return self._send_sms_simulation(db, notification, customer)
            elif notification.channel == NotificationChannel.push:
                return self._send_push_notification(db, notification, customer)
            else:
                logger.error(f"Unknown notification channel: {notification.channel}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending notification {notification.notification_id}: {str(e)}")
            crud_notification.update_notification_status(
                db, notification.notification_id, "failed"
            )
            return False
    
    def _send_sms_simulation(self, db: Session, notification: Notification, customer: Customer):
        """Simulate SMS by logging to console in simplified telecom format"""
        try:
            from datetime import datetime
            current_time = datetime.now()  
            formatted_time = current_time.strftime('%d-%m-%Y %I:%M %p')
            
            provider = "NEXA"
            
            # Format message based on notification type
            sms_message = self._format_sms_message(notification, provider, formatted_time)
            
            # SIMPLIFIED DESIGN - Cleaner, more professional look
            print("\n" + "─" * 40)
            print(f"📱 SMS from {provider}")
            print("─" * 40)
            print(f"To: {customer.phone_number}")
            print(f"Time: {formatted_time}")
            print("─" * 40)
            print(sms_message)
            print("─" * 40)
            print("✅ Delivered")
            print("─" * 40 + "\n")
            
            # Log to file as well
            logger.info(f"SMS Simulation - Provider: {provider}, To: {customer.phone_number}, "
                    f"Time: {formatted_time}, Message: {notification.message}")
            
            # Update notification status
            crud_notification.update_notification_status(
                db, notification.notification_id, "sent", "simulated"
            )
            return True
            
        except Exception as e:
            logger.error(f"SMS simulation failed for notification {notification.notification_id}: {str(e)}")
            crud_notification.update_notification_status(
                db, notification.notification_id, "failed", "simulated"
            )
            return False
    
    def _format_sms_message(self, notification: Notification, provider: str, time: str) -> str:
        """Format notification message in telecom SMS style"""
        
        # Different formats for different notification types
        if notification.type.value == "payment_success":
            return f"""Dear Customer,

Your recharge of ₹{self._extract_amount(notification.message)} is successful. 
Balance will be updated shortly.

Thank you for choosing {provider}."""

        elif notification.type.value == "plan_expiry":
            return f"""Dear Customer,

Your current plan will expire soon. 
Please recharge to continue uninterrupted services.

- {provider}"""

        elif notification.type.value == "plan_activated":
            return f"""Dear Customer,

Your plan has been successfully activated. 
Enjoy high-speed data & unlimited calls.

- {provider}"""

        elif notification.type.value == "plan_queued":
            return f"""Dear Customer,

Your recharge is successful. 
Plan is queued and will auto-activate after current plan expires.

- {provider}"""

        elif notification.type.value == "low_balance":
            return f"""Dear Customer,

Your data balance is low. 
Buy data pack to avoid service interruption.

- {provider}"""

        elif notification.type.value == "referral_bonus":
            return f"""Dear Customer,

Congratulations! You earned referral bonus. 
Use it on your next recharge.

- {provider}"""

        elif notification.type.value == "postpaid_due_date":
            return f"""Dear Customer,

Your postpaid bill is due. 
Please pay to avoid late charges.

- {provider}"""

        else:
            # Default format for other notifications
            return f"""Dear Customer,

{notification.message}

- {provider}"""
    
    def _extract_amount(self, message: str) -> str:
        """Extract amount from message for payment success notifications"""
        import re
        amount_match = re.search(r'₹(\d+\.?\d*)', message)
        if amount_match:
            return amount_match.group(1)
        return "0.00"
    
    def _send_push_notification(self, db: Session, notification: Notification, customer: Customer):
        """Send real push notification"""
        try:
            # TODO: Integrate with actual push notification service (FCM/APNs)
            # For now, we'll simulate success but log it
            
            logger.info(f"PUSH Notification - To: {customer.customer_id}, "
                       f"Customer: {customer.full_name}, "
                       f"Title: {notification.title}, "
                       f"Message: {notification.message}")
            
            
            # Simulate successful push delivery
            crud_notification.update_notification_status(
                db, notification.notification_id, "sent", "real"
            )
            return True
            
        except Exception as e:
            logger.error(f"Push notification failed for notification {notification.notification_id}: {str(e)}")
            crud_notification.update_notification_status(
                db, notification.notification_id, "failed", "real"
            )
            return False
    
    def send_bulk_notifications(self, db: Session, notifications: List[Notification]):
        """Send multiple notifications"""
        results = []
        for notification in notifications:
            success = self.send_notification(db, notification)
            results.append({
                "notification_id": notification.notification_id,
                "customer_id": notification.customer_id,
                "success": success
            })
        return results
    
    def create_and_send_notification(self, db: Session, notification_data: NotificationCreate):
        """Create notification and send it immediately"""
        notification = crud_notification.create_notification(db, notification_data)
        if notification:
            success = self.send_notification(db, notification)
            return notification, success
        return None, False
    
    def trigger_automated_notification(self, db: Session, customer_id: int, 
                                     notification_type: str, title: str, message: str,
                                     channel: str = "push"):
        """Trigger automated notifications for system events"""
        notification_data = NotificationCreate(
            customer_id=customer_id,
            title=title,
            message=message,
            type=notification_type,
            channel=channel
        )
        
        return self.create_and_send_notification(db, notification_data)

# Global instance
notification_service = NotificationService()