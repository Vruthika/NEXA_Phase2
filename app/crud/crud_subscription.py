# app/crud/crud_subscription.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import List, Optional
from app.models.models import Subscription, SubscriptionActivationQueue, Customer, Plan

class CRUDSubscription:
    # Subscription methods
    def get_subscription(self, db: Session, subscription_id: int):
        return db.query(Subscription).filter(Subscription.subscription_id == subscription_id).first()
    
    def get_active_subscriptions(self, db: Session, customer_id: Optional[int] = None):
        current_time = datetime.utcnow()
        query = db.query(Subscription).filter(
            Subscription.expiry_date > current_time,
            Subscription.activation_date.isnot(None),
            Subscription.activation_date <= current_time
        )
        if customer_id:
            query = query.filter(Subscription.customer_id == customer_id)
        return query.all()
    
    def get_subscription_history(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100):
        return db.query(Subscription).filter(
            Subscription.customer_id == customer_id
        ).order_by(Subscription.created_at.desc()).offset(skip).limit(limit).all()
    
    # Activation Queue methods
    def get_activation_queue(self, db: Session, customer_id: Optional[int] = None):
        query = db.query(SubscriptionActivationQueue).filter(
            SubscriptionActivationQueue.processed_at.is_(None)
        ).order_by(SubscriptionActivationQueue.queue_position)
        
        if customer_id:
            query = query.filter(SubscriptionActivationQueue.customer_id == customer_id)
        
        return query.all()
    
    def get_queue_position(self, db: Session, customer_id: int):
        """Get the next available queue position for a customer"""
        last_position = db.query(
            db.func.max(SubscriptionActivationQueue.queue_position)
        ).filter(
            SubscriptionActivationQueue.customer_id == customer_id,
            SubscriptionActivationQueue.processed_at.is_(None)
        ).scalar()
        
        return (last_position or 0) + 1
    
    def add_to_queue(self, db: Session, subscription_id: int, customer_id: int, phone_number: str, plan_id: int):
        """Add a subscription to the activation queue"""
        plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
        if not plan:
            return None
        
        queue_position = self.get_queue_position(db, customer_id)
        current_time = datetime.utcnow()
        
        queue_item = SubscriptionActivationQueue(
            subscription_id=subscription_id,
            customer_id=customer_id,
            phone_number=phone_number,
            expected_activation_date=current_time,
            expected_expiry_date=current_time + timedelta(days=plan.validity_days),
            queue_position=queue_position
        )
        
        db.add(queue_item)
        db.commit()
        db.refresh(queue_item)
        return queue_item

crud_subscription = CRUDSubscription()