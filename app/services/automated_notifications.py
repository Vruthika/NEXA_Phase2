# app/services/automated_notifications.py
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.models import NotificationType, NotificationChannel
from app.services.notification_service import notification_service

class AutomatedNotifications:
    def trigger_automated_notification(self, db: Session, customer_id: int, 
                                     notification_type: NotificationType, title: str, message: str,
                                     channel: NotificationChannel = NotificationChannel.push):
        """Base method to trigger automated notifications"""
        from app.schemas.notification import NotificationCreate
        
        notification_data = NotificationCreate(
            customer_id=customer_id,
            title=title,
            message=message,
            type=notification_type,
            channel=channel
        )
        
        return notification_service.create_and_send_notification(db, notification_data)
    
    def trigger_plan_expiry_notification(self, db: Session, customer_id: int, plan_name: str, expiry_date: datetime):
        """Trigger notification when plan is about to expire - Use SMS"""
        title = "📅 Plan Expiry Reminder"
        message = f"Your {plan_name} plan will expire on {expiry_date.strftime('%d %b %Y')}. Recharge now to continue uninterrupted services."
        
        return self.trigger_automated_notification(
            db, customer_id, NotificationType.plan_expiry, title, message, "sms"
        )
    
    def trigger_recharge_success_notification(self, db: Session, customer_id: int, plan_name: str, amount: float):
        """Trigger notification after successful recharge - Use SMS"""
        title = "✅ Recharge Successful"
        message = f"Your recharge of ₹{amount} for {plan_name} has been completed successfully. Enjoy your services!"
        
        return self.trigger_automated_notification(
            db, customer_id, NotificationType.payment_success, title, message, "sms"
        )
    
    def trigger_low_balance_notification(self, db: Session, customer_id: int, current_balance_mb: float):
        """Trigger notification when data balance is low (< 200MB) - Use SMS"""
        title = "⚠️ Low Data Balance"
        message = f"Your data balance is low ({current_balance_mb:.0f} MB remaining). Consider purchasing a top-up to avoid service interruption."
        
        return self.trigger_automated_notification(
            db, customer_id, NotificationType.low_balance, title, message, "sms"
        )
    
    def trigger_referral_bonus_notification(self, db: Session, customer_id: int, discount_percentage: float):
        """Trigger notification when referral bonus is earned - Use SMS"""
        title = "🎉 Referral Bonus Earned"
        message = f"Congratulations! You've earned a {discount_percentage}% discount on your next recharge through our referral program."
        
        return self.trigger_automated_notification(
            db, customer_id, NotificationType.referral_bonus, title, message, "sms"
        )
    
    def trigger_plan_activated_notification(self, db: Session, customer_id: int, plan_name: str):
        """Trigger notification when plan is activated - Use SMS"""
        title = "🚀 Plan Activated"
        message = f"Your {plan_name} plan has been successfully activated. Enjoy high-speed data and unlimited calls!"
        
        return self.trigger_automated_notification(
            db, customer_id, NotificationType.plan_activated, title, message, "sms"
        )
    
    def trigger_plan_queued_notification(self, db: Session, customer_id: int, plan_name: str, queue_position: int, activation_date: datetime):
        """Trigger notification when plan is queued - Use SMS"""
        title = "⏳ Plan Queued"
        message = f"Your {plan_name} plan is queued (position {queue_position}) and will activate on {activation_date.strftime('%d %b %Y')}."
        
        return self.trigger_automated_notification(
            db, customer_id, NotificationType.plan_queued, title, message, "sms"
        )
    
    def trigger_data_exhausted_notification(self, db: Session, customer_id: int, plan_name: str):
        """Trigger notification when data is completely exhausted - Use SMS"""
        title = "📊 Data Exhausted"
        message = f"Your {plan_name} plan data has been fully used. Please recharge to continue using data services."
        
        return self.trigger_automated_notification(
            db, customer_id, NotificationType.data_exhausted, title, message, "sms"
        )
    
    def trigger_daily_limit_reached_notification(self, db: Session, customer_id: int, plan_name: str):
        """Trigger notification when daily data limit is reached - Use SMS"""
        title = "📈 Daily Limit Reached"
        message = f"Your daily data limit for {plan_name} has been reached. Data speeds may be reduced until tomorrow."
        
        return self.trigger_automated_notification(
            db, customer_id, NotificationType.daily_limit_reached, title, message, "sms"
        )

# Global instance
automated_notifications = AutomatedNotifications()