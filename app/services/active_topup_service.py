from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from app.crud.active_topup_crud import ActiveTopupCRUD
from app.crud.customer_crud import CustomerCRUD
from app.crud.subscription_crud import SubscriptionCRUD
from app.crud.plan_crud import PlanCRUD
from app.crud.transaction_crud import TransactionCRUD
from app.schemas.active_topup import ActiveTopupCreate
from app.websockets import websocket_manager

class ActiveTopupService:
    def __init__(self, db: Session):
        self.db = db
        self.topup_crud = ActiveTopupCRUD(db)
        self.customer_crud = CustomerCRUD(db)
        self.subscription_crud = SubscriptionCRUD(db)
        self.plan_crud = PlanCRUD(db)
        self.transaction_crud = TransactionCRUD(db)
    
    def create_active_topup(self, customer_id: int, topup_data: ActiveTopupCreate):
        # Verify customer exists
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Verify base subscription exists and belongs to customer
        subscription = self.subscription_crud.get_by_id(topup_data.base_subscription_id)
        if not subscription or subscription.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Base subscription not found or does not belong to customer"
            )
        
        # Verify topup plan exists and is a topup
        topup_plan = self.plan_crud.get_by_id(topup_data.topup_plan_id)
        if not topup_plan or not topup_plan.is_topup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topup plan not found or is not a topup plan"
            )
        
        # Verify transaction exists and belongs to customer
        transaction = self.transaction_crud.get_by_id(topup_data.transaction_id)
        if not transaction or transaction.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found or does not belong to customer"
            )
        
        # Create active topup
        topup_dict = topup_data.dict()
        topup_dict.update({
            "customer_id": customer_id,
            "data_remaining_gb": topup_data.topup_data_gb
        })
        
        topup = self.topup_crud.create(topup_dict)
        
        # Send notification
        try:
            websocket_manager.send_notification(
                customer_id,
                {
                    "type": "topup_activated",
                    "message": f"Your data topup of {topup_data.topup_data_gb}GB has been added",
                    "topup_data_gb": float(topup_data.topup_data_gb)
                }
            )
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return topup
    
    def get_topup_by_id(self, topup_id: int):
        topup = self.topup_crud.get_by_id(topup_id)
        if not topup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Topup not found"
            )
        return topup
    
    def get_customer_topups(self, customer_id: int):
        customer = self.customer_crud.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        return self.topup_crud.get_by_customer_id(customer_id)
    
    def update_data_usage(self, topup_id: int, data_used_gb: float):
        topup = self.get_topup_by_id(topup_id)
        
        if data_used_gb > topup.data_remaining_gb:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient topup data balance"
            )
        
        updated_topup = self.topup_crud.update_data_usage(topup_id, data_used_gb)
        
        # Send notification if topup is exhausted
        if updated_topup.status.value == "exhausted":
            try:
                websocket_manager.send_notification(
                    updated_topup.customer_id,
                    {
                        "type": "topup_exhausted",
                        "message": "Your data topup has been fully used",
                        "topup_id": topup_id
                    }
                )
            except Exception as e:
                print(f"WebSocket notification failed: {e}")
        
        return updated_topup
    
    def activate_topup(self, topup_id: int):
        topup = self.get_topup_by_id(topup_id)
        
        if topup.activation_date > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topup is not yet ready for activation"
            )
        
        updated_topup = self.topup_crud.update_status(topup_id, "active")
        
        # Send notification
        try:
            websocket_manager.send_notification(
                updated_topup.customer_id,
                {
                    "type": "topup_activated",
                    "message": "Your data topup is now active",
                    "topup_id": topup_id,
                    "data_remaining_gb": float(updated_topup.data_remaining_gb)
                }
            )
        except Exception as e:
            print(f"WebSocket notification failed: {e}")
        
        return updated_topup