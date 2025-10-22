from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.crud.postpaid_activation_crud import PostpaidActivationCRUD
from app.crud.customer_crud import CustomerCRUD
from app.crud.plan_crud import PlanCRUD
from app.crud.postpaid_secondary_number_crud import PostpaidSecondaryNumberCRUD
from app.crud.postpaid_data_addon_crud import PostpaidDataAddonCRUD
from app.schemas.postpaid_activation import PostpaidActivationCreate, PostpaidSecondaryNumberCreate, PostpaidDataAddonCreate
from app.websockets import websocket_manager

class PostpaidActivationService:
    def __init__(self, db: Session):
        self.db = db
        self.activation_crud = PostpaidActivationCRUD(db)
        self.customer_crud = CustomerCRUD(db)
        self.plan_crud = PlanCRUD(db)
        self.secondary_number_crud = PostpaidSecondaryNumberCRUD(db)
        self.data_addon_crud = PostpaidDataAddonCRUD(db)
    
    def create_activation(self, customer_id: int, activation_data: PostpaidActivationCreate):
        # Verify customer exists
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Verify plan exists and is postpaid
        plan = self.plan_crud.get_by_id(activation_data.plan_id)
        if not plan or plan.plan_type != "postpaid":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Postpaid plan not found"
            )
        
        # Calculate billing cycle
        now = datetime.utcnow()
        billing_cycle_start = now.replace(day=1)  # Start from 1st of current month
        billing_cycle_end = (billing_cycle_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)  # Last day of month
        
        # Create activation
        activation_dict = activation_data.dict()
        activation_dict.update({
            "customer_id": customer_id,
            "billing_cycle_start": billing_cycle_start,
            "billing_cycle_end": billing_cycle_end,
            "base_data_allowance_gb": plan.data_allowance_gb or 0,
            "current_data_balance_gb": plan.data_allowance_gb or 0,
            "base_amount": plan.price,
            "total_amount_due": plan.price
        })
        
        activation = self.activation_crud.create(activation_dict)
        
        # Send notification
        try:
            websocket_manager.send_notification(
                customer_id,
                {
                    "type": "plan_activated",
                    "message": f"Your postpaid plan {plan.plan_name} has been activated",
                    "plan_name": plan.plan_name,
                    "billing_date": billing_cycle_end.isoformat()
                }
            )
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return activation
    
    def get_activation_by_id(self, activation_id: int):
        activation = self.activation_crud.get_by_id(activation_id)
        if not activation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Postpaid activation not found"
            )
        return activation
    
    def get_customer_activations(self, customer_id: int):
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return self.activation_crud.get_by_customer_id(customer_id)
    
    def add_secondary_number(self, activation_id: int, secondary_data: PostpaidSecondaryNumberCreate):
        activation = self.get_activation_by_id(activation_id)
        
        # Create secondary number
        secondary_dict = secondary_data.dict()
        secondary_dict["activation_id"] = activation_id
        
        secondary_number = self.secondary_number_crud.create(secondary_dict)
        
        # Update total amount due (add pro-rated amount)
        # This is a simplified calculation
        days_remaining = (activation.billing_cycle_end - datetime.utcnow()).days
        days_in_month = (activation.billing_cycle_end - activation.billing_cycle_start).days
        pro_rata_amount = (activation.base_amount / days_in_month) * days_remaining * 0.5  # 50% for secondary number
        
        activation.total_amount_due += pro_rata_amount
        self.db.commit()
        
        return secondary_number
    
    def add_data_addon(self, activation_id: int, addon_data: PostpaidDataAddonCreate):
        activation = self.get_activation_by_id(activation_id)
        
        # Create data addon
        addon_dict = addon_data.dict()
        addon_dict["activation_id"] = activation_id
        addon_dict["valid_until"] = activation.billing_cycle_end
        
        addon = self.data_addon_crud.create(addon_dict)
        
        # Update data balance and total amount due
        activation.current_data_balance_gb += addon.data_amount_gb
        activation.total_amount_due += addon.addon_price
        self.db.commit()
        
        return addon
    
    def update_data_usage(self, activation_id: int, data_used_gb: float):
        activation = self.get_activation_by_id(activation_id)
        
        if data_used_gb > activation.current_data_balance_gb:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient data balance"
            )
        
        updated_activation = self.activation_crud.update_data_usage(
            activation_id, 
            data_used_gb
        )
        
        # Check for low balance
        if updated_activation.current_data_balance_gb <= 2.0:  # 2 GB threshold
            try:
                websocket_manager.send_notification(
                    updated_activation.customer_id,
                    {
                        "type": "low_balance",
                        "message": "Your postpaid data balance is running low",
                        "remaining_data": float(updated_activation.current_data_balance_gb)
                    }
                )
            except Exception as e:
                print(f"WebSocket notification failed: {e}")
        
        return updated_activation
    
    def process_billing_cycle(self):
        # Get activations that need billing cycle reset
        activations_to_reset = self.activation_crud.get_activations_for_billing_reset()
        
        for activation in activations_to_reset:
            # Calculate new billing cycle
            new_cycle_start = activation.billing_cycle_end + timedelta(days=1)
            new_cycle_end = (new_cycle_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Reset data usage and balance
            activation.billing_cycle_start = new_cycle_start
            activation.billing_cycle_end = new_cycle_end
            activation.data_used_gb = 0.0
            activation.current_data_balance_gb = activation.base_data_allowance_gb
            activation.total_amount_due = activation.base_amount
            
            # Expire data addons
            self.data_addon_crud.expire_addons(activation.activation_id)
            
            # Send billing notification
            try:
                websocket_manager.send_notification(
                    activation.customer_id,
                    {
                        "type": "postpaid_due_date",
                        "message": f"Your postpaid bill for {activation.plan.plan_name} is now due",
                        "amount_due": float(activation.total_amount_due),
                        "due_date": new_cycle_start.isoformat()
                    }
                )
            except Exception as e:
                print(f"WebSocket notification failed: {e}")
        
        self.db.commit()
        return activations_to_reset