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
        query = db.query(Subscription).filter(Subscription.expiry_date > datetime.utcnow())
        if customer_id:
            query = query.filter(Subscription.customer_id == customer_id)
        return query.all()
    
    def get_subscription_history(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100):
        return db.query(Subscription).filter(
            Subscription.customer_id == customer_id
        ).order_by(Subscription.created_at.desc()).offset(skip).limit(limit).all()
    
    def force_activate_subscription(self, db: Session, subscription_id: int):
        """Force activate a subscription (admin override)"""
        subscription = self.get_subscription(db, subscription_id)
        if subscription:
            subscription.activation_date = datetime.utcnow()
            # Set expiry based on validity days from plan
            plan = db.query(Plan).filter(Plan.plan_id == subscription.plan_id).first()
            if plan:
                subscription.expiry_date = datetime.utcnow() + timedelta(days=plan.validity_days)
            db.commit()
            db.refresh(subscription)
        return subscription
    
    def force_deactivate_subscription(self, db: Session, subscription_id: int):
        """Force deactivate a subscription (admin override)"""
        subscription = self.get_subscription(db, subscription_id)
        if subscription:
            subscription.expiry_date = datetime.utcnow()
            db.commit()
            db.refresh(subscription)
        return subscription
    
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
            expected_activation_date=current_time,  # Will be updated when activated
            expected_expiry_date=current_time + timedelta(days=plan.validity_days),
            queue_position=queue_position
        )
        
        db.add(queue_item)
        db.commit()
        db.refresh(queue_item)
        return queue_item
    
    def process_queue(self, db: Session, customer_id: int):
        """Process the activation queue for a customer when current subscription expires"""
        # Get the next item in queue (position 1)
        next_item = db.query(SubscriptionActivationQueue).filter(
            SubscriptionActivationQueue.customer_id == customer_id,
            SubscriptionActivationQueue.processed_at.is_(None),
            SubscriptionActivationQueue.queue_position == 1
        ).first()
        
        if next_item:
            # Activate this subscription
            subscription = db.query(Subscription).filter(
                Subscription.subscription_id == next_item.subscription_id
            ).first()
            
            if subscription:
                current_time = datetime.utcnow()
                subscription.activation_date = current_time
                subscription.expiry_date = next_item.expected_expiry_date
                
                # Mark queue item as processed
                next_item.processed_at = current_time
                
                # Shift all other queue positions down by 1
                db.query(SubscriptionActivationQueue).filter(
                    SubscriptionActivationQueue.customer_id == customer_id,
                    SubscriptionActivationQueue.processed_at.is_(None),
                    SubscriptionActivationQueue.queue_position > 1
                ).update({
                    SubscriptionActivationQueue.queue_position: SubscriptionActivationQueue.queue_position - 1
                })
                
                db.commit()
                return subscription
        
        return None
    
    def remove_from_queue(self, db: Session, queue_id: int):
        """Remove an item from the activation queue"""
        queue_item = db.query(SubscriptionActivationQueue).filter(
            SubscriptionActivationQueue.queue_id == queue_id
        ).first()
        
        if queue_item:
            # Get the position of the item being removed
            position = queue_item.queue_position
            
            # Delete the item
            db.delete(queue_item)
            
            # Shift all items with higher positions down by 1
            db.query(SubscriptionActivationQueue).filter(
                SubscriptionActivationQueue.customer_id == queue_item.customer_id,
                SubscriptionActivationQueue.processed_at.is_(None),
                SubscriptionActivationQueue.queue_position > position
            ).update({
                SubscriptionActivationQueue.queue_position: SubscriptionActivationQueue.queue_position - 1
            })
            
            db.commit()
            return True
        
        return False

crud_subscription = CRUDSubscription()