from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.postpaid_activation import PostpaidActivation
from datetime import datetime, timedelta

class PostpaidActivationCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, activation_id: int) -> PostpaidActivation:
        return self.db.query(PostpaidActivation).filter(PostpaidActivation.activation_id == activation_id).first()
    
    def get_by_customer_id(self, customer_id: int):
        return self.db.query(PostpaidActivation).filter(PostpaidActivation.customer_id == customer_id).all()
    
    def get_by_phone_number(self, phone_number: str):
        return self.db.query(PostpaidActivation).filter(PostpaidActivation.primary_number == phone_number).first()
    
    def get_activations_for_billing_reset(self):
        # Get activations where billing cycle has ended
        return self.db.query(PostpaidActivation).filter(
            PostpaidActivation.billing_cycle_end <= datetime.utcnow()
        ).all()
    
    def get_active_activations(self):
        return self.db.query(PostpaidActivation).filter(
            PostpaidActivation.status == 'active'
        ).all()
    
    def create(self, activation_data: dict) -> PostpaidActivation:
        activation = PostpaidActivation(**activation_data)
        self.db.add(activation)
        self.db.commit()
        self.db.refresh(activation)
        return activation
    
    def update(self, activation_id: int, activation_data: dict) -> PostpaidActivation:
        activation = self.get_by_id(activation_id)
        if activation:
            for key, value in activation_data.items():
                setattr(activation, key, value)
            self.db.commit()
            self.db.refresh(activation)
        return activation
    
    def update_data_usage(self, activation_id: int, data_used_gb: float) -> PostpaidActivation:
        activation = self.get_by_id(activation_id)
        if activation:
            activation.data_used_gb += data_used_gb
            activation.current_data_balance_gb -= data_used_gb
            if activation.current_data_balance_gb < 0:
                activation.current_data_balance_gb = 0
            self.db.commit()
            self.db.refresh(activation)
        return activation
    
    def update_status(self, activation_id: int, status: str) -> PostpaidActivation:
        activation = self.get_by_id(activation_id)
        if activation:
            activation.status = status
            self.db.commit()
            self.db.refresh(activation)
        return activation