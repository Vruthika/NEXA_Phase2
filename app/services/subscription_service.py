from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.models import Subscription, SubscriptionActivationQueue, Customer, Plan

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
        
        # Find all expired BASE plans (is_topup=False) that are activated
        expired_base_plans = db.query(Subscription).filter(
            Subscription.expiry_date <= current_time,
            Subscription.activation_date.isnot(None),  # Only activated subscriptions
            Subscription.is_topup == False  # ONLY base plans, not topups
        ).all()
        
        processed_customers = set()
        
        for expired_base_plan in expired_base_plans:
            print(f"Processing expired BASE plan: {expired_base_plan.subscription_id} for customer {expired_base_plan.customer_id}")
            
            # Store customer and phone before deletion
            customer_id = expired_base_plan.customer_id
            phone_number = expired_base_plan.phone_number
            
            # Delete the expired base plan
            db.delete(expired_base_plan)
            db.commit()
            
            # Process the queue for this customer and phone number
            success = self.process_customer_queue(db, customer_id, phone_number)
            
            if success:
                processed_customers.add((customer_id, phone_number))
        
        # Also process expired TOPUPS separately (just delete them, don't activate queue)
        expired_topups = db.query(Subscription).filter(
            Subscription.expiry_date <= current_time,
            Subscription.activation_date.isnot(None),
            Subscription.is_topup == True  # Only topups
        ).all()
        
        for expired_topup in expired_topups:
            print(f"Deleting expired TOPUP: {expired_topup.subscription_id} for customer {expired_topup.customer_id}")
            db.delete(expired_topup)
            db.commit()
        
        # Also process queues for any customers who might have no active base plans but have queued items
        # This handles cases where the last active base plan expired and we need to activate the next in queue
        customers_with_queues = db.query(
            SubscriptionActivationQueue.customer_id,
            SubscriptionActivationQueue.phone_number
        ).filter(
            SubscriptionActivationQueue.processed_at.is_(None)
        ).distinct().all()
        
        for customer_id, phone_number in customers_with_queues:
            if (customer_id, phone_number) not in processed_customers:
                # Check if this customer has any active BASE subscriptions for this phone
                active_base_plans = db.query(Subscription).filter(
                    Subscription.customer_id == customer_id,
                    Subscription.phone_number == phone_number,
                    Subscription.expiry_date > current_time,
                    Subscription.is_topup == False  # Only base plans
                ).count()
                
                if active_base_plans == 0:
                    # No active base subscription, process the queue
                    self.process_customer_queue(db, customer_id, phone_number)
        
        return len(processed_customers)
    
    def process_customer_queue(self, db: Session, customer_id: int, phone_number: str):
        """Process the activation queue for a specific customer and phone number - ONLY for base plans"""
        current_time = datetime.utcnow()
        
        # Get the first item in queue (position 1) for BASE plans only
        queue_item = db.query(SubscriptionActivationQueue).join(
            Subscription, SubscriptionActivationQueue.subscription_id == Subscription.subscription_id
        ).filter(
            SubscriptionActivationQueue.customer_id == customer_id,
            SubscriptionActivationQueue.phone_number == phone_number,
            SubscriptionActivationQueue.processed_at.is_(None),
            SubscriptionActivationQueue.queue_position == 1,
            Subscription.is_topup == False  # Only process base plans from queue
        ).first()
        
        if queue_item:
            print(f"Activating queued BASE plan: {queue_item.subscription_id}")
            
            # Get the subscription
            subscription = db.query(Subscription).filter(
                Subscription.subscription_id == queue_item.subscription_id
            ).first()
            
            if subscription and not subscription.is_topup:  # Double check it's a base plan
                # Activate the subscription by setting activation date and recalculating expiry
                subscription.activation_date = current_time
                
                # Recalculate expiry date based on plan validity from current time
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
                
                # Shift all other queue positions down by 1 for this customer and phone number
                db.query(SubscriptionActivationQueue).filter(
                    SubscriptionActivationQueue.customer_id == customer_id,
                    SubscriptionActivationQueue.phone_number == phone_number,
                    SubscriptionActivationQueue.processed_at.is_(None),
                    SubscriptionActivationQueue.queue_position > 1
                ).update({
                    SubscriptionActivationQueue.queue_position: SubscriptionActivationQueue.queue_position - 1
                })
                
                db.commit()
                print(f"✅ Activated BASE plan {subscription.subscription_id} from queue")
                return True
        
        return False

subscription_service = SubscriptionService()