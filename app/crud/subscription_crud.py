from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.subscription import Subscription
from datetime import datetime, timedelta

class SubscriptionCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, subscription_id: int) -> Subscription:
        return self.db.query(Subscription).filter(Subscription.subscription_id == subscription_id).first()
    
    def get_by_customer_id(self, customer_id: int):
        return self.db.query(Subscription).filter(Subscription.customer_id == customer_id).all()
    
    def get_by_phone_number(self, phone_number: str):
        return self.db.query(Subscription).filter(Subscription.phone_number == phone_number).all()
    
    def get_active_subscriptions(self, customer_id: int):
        return self.db.query(Subscription).filter(
            and_(
                Subscription.customer_id == customer_id,
                Subscription.expiry_date > datetime.utcnow()
            )
        ).all()
    
    def get_expiring_subscriptions(self, days_before: int = 1):
        cutoff_date = datetime.utcnow() + timedelta(days=days_before)
        return self.db.query(Subscription).filter(
            and_(
                Subscription.expiry_date <= cutoff_date,
                Subscription.expiry_date > datetime.utcnow()
            )
        ).all()
    
    def create(self, subscription_data: dict) -> Subscription:
        subscription = Subscription(**subscription_data)
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        return subscription
    
    def update_data_usage(self, subscription_id: int, data_used_gb: float) -> Subscription:
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.daily_data_used_gb += data_used_gb
            if subscription.data_balance_gb is not None:
                subscription.data_balance_gb -= data_used_gb
            self.db.commit()
            self.db.refresh(subscription)
        return subscription
    
    def reset_daily_usage(self, subscription_id: int) -> Subscription:
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.daily_data_used_gb = 0.0
            subscription.last_daily_reset = datetime.utcnow()
            self.db.commit()
            self.db.refresh(subscription)
        return subscription
    
    def expire_subscription(self, subscription_id: int) -> Subscription:
        subscription = self.get_by_id(subscription_id)
        if subscription:
            subscription.expiry_date = datetime.utcnow()
            self.db.commit()
            self.db.refresh(subscription)
        return subscription