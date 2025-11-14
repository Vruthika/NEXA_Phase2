# app/services/subscription_service.py
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.models import Subscription, SubscriptionActivationQueue, Customer

class SubscriptionService:
    
    def get_next_queue_position(self, db: Session, customer_id: int, phone_number: str) -> int:
        """Get the next available queue position for a customer"""
        last_position = db.query(
            SubscriptionActivationQueue.queue_position
        ).filter(
            SubscriptionActivationQueue.customer_id == customer_id,
            SubscriptionActivationQueue.phone_number == phone_number,
            SubscriptionActivationQueue.processed_at.is_(None)
        ).order_by(
            SubscriptionActivationQueue.queue_position.desc()
        ).first()
        
        return (last_position[0] + 1) if last_position else 1
    
    def process_expired_subscriptions(self, db: Session):
        """Automatically process expired subscriptions and activate queued plans"""
        current_time = datetime.utcnow()
        
        # Find all expired subscriptions
        expired_subscriptions = db.query(Subscription).filter(
            Subscription.expiry_date <= current_time,
            Subscription.activation_date.isnot(None)  # Only process activated subscriptions
        ).all()
        
        for expired_sub in expired_subscriptions:
            print(f"Processing expired subscription: {expired_sub.subscription_id} for customer {expired_sub.customer_id}")
            
            # Delete the expired subscription
            db.delete(expired_sub)
            db.commit()
            
            # Process the queue for this customer and phone number
            self.process_customer_queue(db, expired_sub.customer_id, expired_sub.phone_number)
    
    def process_customer_queue(self, db: Session, customer_id: int, phone_number: str):
        """Process the activation queue for a specific customer and phone number"""
        current_time = datetime.utcnow()
        
        # Get the first item in queue (position 1)
        queue_item = db.query(SubscriptionActivationQueue).filter(
            SubscriptionActivationQueue.customer_id == customer_id,
            SubscriptionActivationQueue.phone_number == phone_number,
            SubscriptionActivationQueue.processed_at.is_(None),
            SubscriptionActivationQueue.queue_position == 1
        ).first()
        
        if queue_item:
            print(f"Activating queued subscription: {queue_item.subscription_id}")
            
            # Get the subscription
            subscription = db.query(Subscription).filter(
                Subscription.subscription_id == queue_item.subscription_id
            ).first()
            
            if subscription:
                # Activate the subscription by setting activation date and recalculating expiry
                subscription.activation_date = current_time
                
                # Recalculate expiry date based on plan validity from current time
                from app.models.models import Plan
                plan = db.query(Plan).filter(Plan.plan_id == subscription.plan_id).first()
                if plan:
                    subscription.expiry_date = current_time + timedelta(days=plan.validity_days)
                
                # Set last daily reset
                subscription.last_daily_reset = current_time
                
                # Mark queue item as processed
                queue_item.processed_at = current_time
                
                # Update customer's last_active_plan_date
                customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
                if customer:
                    customer.last_active_plan_date = current_time
                    customer.days_inactive = 0
                    customer.inactivity_status_updated_at = current_time
                
                # Shift all other queue positions down by 1
                db.query(SubscriptionActivationQueue).filter(
                    SubscriptionActivationQueue.customer_id == customer_id,
                    SubscriptionActivationQueue.phone_number == phone_number,
                    SubscriptionActivationQueue.processed_at.is_(None),
                    SubscriptionActivationQueue.queue_position > 1
                ).update({
                    SubscriptionActivationQueue.queue_position: SubscriptionActivationQueue.queue_position - 1
                })
                
                db.commit()
                print(f"✅ Activated subscription {subscription.subscription_id} from queue")
                return True
        
        return False
    
    def process_expired_subscriptions(self, db: Session):
        """Automatically process expired subscriptions and activate queued plans"""
        current_time = datetime.utcnow()
        
        # Find all expired subscriptions
        expired_subscriptions = db.query(Subscription).filter(
            Subscription.expiry_date <= current_time,
            Subscription.activation_date.isnot(None)  # Only process activated subscriptions
        ).all()
        
        processed_customers = set()
        
        for expired_sub in expired_subscriptions:
            print(f"Processing expired subscription: {expired_sub.subscription_id} for customer {expired_sub.customer_id}")
            
            # Store customer and phone before deletion
            customer_id = expired_sub.customer_id
            phone_number = expired_sub.phone_number
            
            # Delete the expired subscription
            db.delete(expired_sub)
            db.commit()
            
            # Process the queue for this customer and phone number
            success = self.process_customer_queue(db, customer_id, phone_number)
            
            if success:
                processed_customers.add((customer_id, phone_number))
        
        # Also process queues for any customers who might have no active subscriptions but have queued items
        # This handles cases where the last active subscription expired and we need to activate the next in queue
        customers_with_queues = db.query(
            SubscriptionActivationQueue.customer_id,
            SubscriptionActivationQueue.phone_number
        ).filter(
            SubscriptionActivationQueue.processed_at.is_(None)
        ).distinct().all()
        
        for customer_id, phone_number in customers_with_queues:
            if (customer_id, phone_number) not in processed_customers:
                # Check if this customer has any active subscriptions for this phone
                active_subs = db.query(Subscription).filter(
                    Subscription.customer_id == customer_id,
                    Subscription.phone_number == phone_number,
                    Subscription.expiry_date > current_time
                ).count()
                
                if active_subs == 0:
                    # No active subscription, process the queue
                    self.process_customer_queue(db, customer_id, phone_number)
        
        return len(processed_customers)
            
subscription_service = SubscriptionService()