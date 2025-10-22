from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.crud.subscription_crud import SubscriptionCRUD
from app.crud.transaction_crud import TransactionCRUD
from app.crud.plan_crud import PlanCRUD
from app.crud.customer_crud import CustomerCRUD
from app.crud.subscription_activation_queue_crud import SubscriptionActivationQueueCRUD
from app.schemas.subscription import SubscriptionCreate
from app.websockets import websocket_manager

class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.subscription_crud = SubscriptionCRUD(db)
        self.transaction_crud = TransactionCRUD(db)
        self.plan_crud = PlanCRUD(db)
        self.customer_crud = CustomerCRUD(db)
        self.queue_crud = SubscriptionActivationQueueCRUD(db)
    
    def create_subscription(self, customer_id: int, subscription_data: SubscriptionCreate):
        # Verify customer exists
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Verify transaction exists and belongs to customer
        transaction = self.transaction_crud.get_by_id(subscription_data.transaction_id)
        if not transaction or transaction.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found or does not belong to customer"
            )
        
        # Verify plan exists
        plan = self.plan_crud.get_by_id(subscription_data.plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
        
        # Calculate activation and expiry dates
        activation_date = datetime.utcnow()
        expiry_date = activation_date + timedelta(days=plan.validity_days)
        
        # Create subscription
        subscription_dict = subscription_data.dict()
        subscription_dict.update({
            "customer_id": customer_id,
            "activation_date": activation_date,
            "expiry_date": expiry_date,
            "data_balance_gb": plan.data_allowance_gb,
            "daily_data_limit_gb": plan.daily_data_limit_gb,
            "last_daily_reset": activation_date
        })
        
        subscription = self.subscription_crud.create(subscription_dict)
        
        # Update customer's last active plan date
        self.customer_crud.update_last_active_plan_date(customer_id)
        
        # Send WebSocket notification
        try:
            websocket_manager.send_notification(
                customer_id,
                {
                    "type": "plan_activated",
                    "message": f"Your {plan.plan_name} plan has been activated",
                    "plan_name": plan.plan_name,
                    "expiry_date": expiry_date.isoformat()
                }
            )
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return subscription
    
    def get_subscription_by_id(self, subscription_id: int):
        subscription = self.subscription_crud.get_by_id(subscription_id)
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        return subscription
    
    def get_customer_subscriptions(self, customer_id: int):
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return self.subscription_crud.get_by_customer_id(customer_id)
    
    def update_data_usage(self, subscription_id: int, data_used_gb: float):
        subscription = self.get_subscription_by_id(subscription_id)
        
        # Check daily data limit
        if (subscription.daily_data_limit_gb and 
            subscription.daily_data_used_gb + data_used_gb > subscription.daily_data_limit_gb):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Daily data limit exceeded"
            )
        
        # Check total data balance
        if (subscription.data_balance_gb and 
            data_used_gb > subscription.data_balance_gb):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient data balance"
            )
        
        updated_subscription = self.subscription_crud.update_data_usage(subscription_id, data_used_gb)
        
        # Send low balance notification if applicable
        if (updated_subscription.data_balance_gb and 
            updated_subscription.data_balance_gb <= 1.0):  # 1 GB threshold
            try:
                websocket_manager.send_notification(
                    updated_subscription.customer_id,
                    {
                        "type": "low_balance",
                        "message": "Your data balance is running low",
                        "remaining_data": float(updated_subscription.data_balance_gb)
                    }
                )
            except Exception as e:
                print(f"WebSocket notification failed: {e}")
        
        return updated_subscription
    
    def reset_daily_usage(self, subscription_id: int):
        subscription = self.get_subscription_by_id(subscription_id)
        return self.subscription_crud.reset_daily_usage(subscription_id)
    
    def queue_subscription_activation(self, customer_id: int, subscription_id: int, phone_number: str):
        subscription = self.get_subscription_by_id(subscription_id)
        
        # Check if subscription belongs to customer
        if subscription.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to queue this subscription"
            )
        
        # Get current queue position
        existing_queues = self.queue_crud.get_by_phone_number(phone_number)
        queue_position = len(existing_queues) + 1
        
        # Create queue entry
        queue_data = {
            "subscription_id": subscription_id,
            "customer_id": customer_id,
            "phone_number": phone_number,
            "expected_activation_date": subscription.expiry_date,
            "expected_expiry_date": subscription.expiry_date + timedelta(days=subscription.plan.validity_days),
            "queue_position": queue_position
        }
        
        queue_entry = self.queue_crud.create(queue_data)
        
        # Send notification
        try:
            websocket_manager.send_notification(
                customer_id,
                {
                    "type": "plan_queued",
                    "message": f"Your {subscription.plan.plan_name} plan has been queued for activation",
                    "plan_name": subscription.plan.plan_name,
                    "queue_position": queue_position
                }
            )
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return queue_entry
    
    def process_queued_subscriptions(self, phone_number: str):
        # Get the next subscription in queue for this phone number
        next_queue = self.queue_crud.get_next_in_queue(phone_number)
        
        if not next_queue:
            return None
        
        # Activate the queued subscription
        subscription = next_queue.subscription
        subscription.activation_date = datetime.utcnow()
        subscription.expiry_date = next_queue.expected_expiry_date
        
        self.db.commit()
        
        # Mark queue as processed
        self.queue_crud.mark_processed(next_queue.queue_id)
        
        # Update queue positions for remaining entries
        remaining_queues = self.queue_crud.get_by_phone_number(phone_number)
        for i, queue in enumerate(remaining_queues, 1):
            self.queue_crud.update_queue_position(queue.queue_id, i)
        
        # Send notification
        try:
            websocket_manager.send_notification(
                subscription.customer_id,
                {
                    "type": "plan_activated",
                    "message": f"Your queued {subscription.plan.plan_name} plan has been activated",
                    "plan_name": subscription.plan.plan_name,
                    "expiry_date": subscription.expiry_date.isoformat()
                }
            )
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return subscription